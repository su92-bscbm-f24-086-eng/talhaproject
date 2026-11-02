"""
chatbot.py
Purpose : Brain of the Cricket Facts Bot. It loads the knowledge base from a
          JSON file, cleans the user's message, fixes small spelling mistakes,
          finds the best matching question using TF-IDF + cosine similarity
          and returns the answer.
Author  : YOUR NAME (ROLL NUMBER)
Date    : 2026
"""

import json
import random
import re
from pathlib import Path
from difflib import get_close_matches

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# If the best similarity score is below this value, the bot uses a fallback reply.
CONFIDENCE_THRESHOLD = 0.45

# Common words that do not help to identify the question (removed before matching).
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "of", "in", "on", "at", "to",
    "for", "and", "or", "me", "my", "you", "your", "i", "it", "do", "does",
    "did", "can", "could", "please", "tell", "about", "what", "who", "which",
    "how", "many", "much", "when", "where", "with", "by", "from", "give",
    "there", "has", "have", "had", "cricket", "cricketer", "s",
}


def find_knowledge_base(kb_path: str) -> Path:
    """Locate the knowledge base file, whatever folder the app is started from.

    Looks at the given path, then next to chatbot.py, then in the current folder,
    and finally searches the project for any 'knowledge_base.json' (any letter case).
    Raises a clear FileNotFoundError if the file is missing.
    """
    here = Path(__file__).resolve().parent
    candidates = [Path(kb_path), here / "data" / "knowledge_base.json",
                  Path.cwd() / "data" / "knowledge_base.json"]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    for file in here.rglob("*"):                       # last try: search whole project
        if file.is_file() and file.name.lower() == "knowledge_base.json":
            return file
    raise FileNotFoundError(
        "knowledge_base.json not found. Upload the folder 'data' (with "
        "knowledge_base.json inside it) next to app.py in your repository.")


# ---------------------------------------------------------------------------
# Text pre-processing functions
# ---------------------------------------------------------------------------
def clean_text(text: str) -> str:
    """Convert text to lower case, remove punctuation and extra spaces.

    Input : raw user text, e.g. "  Who has the MOST runs in ODIs??? "
    Output: cleaned text, e.g. "who has the most runs in odis"
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)   # keep only letters, digits, spaces
    text = re.sub(r"\s+", " ", text).strip()   # collapse multiple spaces
    return text


def simple_stem(word: str) -> str:
    """Make a word singular so 'runs' and 'run' match (very light stemming)."""
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"                 # centuries -> century
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]                       # wickets -> wicket
    return word


def tokenize(text: str) -> list:
    """Clean the text, remove stop words and stem every word.

    If every word is a stop word (e.g. "who are you"), the stop words are kept
    so that the sentence is not empty.
    """
    words = clean_text(text).split()
    useful = [w for w in words if w not in STOP_WORDS]
    if not useful:                             # keep original words if nothing is left
        useful = words
    return [simple_stem(w) for w in useful]


# ---------------------------------------------------------------------------
# Chatbot class
# ---------------------------------------------------------------------------
class CricketChatbot:
    """Retrieval-based chatbot: finds the stored question most similar to the user's."""

    def __init__(self, kb_path: str = "data/knowledge_base.json"):
        """Load the knowledge base and train the TF-IDF model.

        Input : path of the JSON knowledge base file.
        """
        with open(find_knowledge_base(kb_path), "r", encoding="utf-8") as file:
            self.kb = json.load(file)

        # Build parallel lists: one entry for every stored pattern (question).
        self.pattern_texts = []    # processed text of each pattern
        self.pattern_tags = []     # intent tag that each pattern belongs to
        for intent in self.kb["intents"]:
            for pattern in intent["patterns"]:
                self.pattern_texts.append(" ".join(tokenize(pattern)))
                self.pattern_tags.append(intent["tag"])

        # Vocabulary of known words, used for spelling correction.
        self.vocabulary = sorted({w for t in self.pattern_texts for w in t.split()})

        # TF-IDF turns each pattern into a numeric vector (unigrams + bigrams).
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2),
                                          token_pattern=r"(?u)\b\w+\b")
        self.pattern_vectors = self.vectorizer.fit_transform(self.pattern_texts)

        # Quick lookup: tag -> intent data (responses).
        self.intents_by_tag = {i["tag"]: i for i in self.kb["intents"]}

    def correct_spelling(self, tokens: list) -> list:
        """Replace unknown words by the closest known word (fixes small typos).

        Input : list of tokens, e.g. ["sachn", "tendulkr"]
        Output: corrected tokens, e.g. ["sachin", "tendulkar"]
        """
        corrected = []
        for word in tokens:
            if word in self.vocabulary or word.isdigit() or len(word) < 4:
                corrected.append(word)         # known / number / too short: keep
            else:
                close = get_close_matches(word, self.vocabulary, n=1, cutoff=0.8)
                corrected.append(close[0] if close else word)
        return corrected

    def get_response(self, user_text: str) -> dict:
        """Main function: take a user message and return the bot's reply.

        Output: dict with keys 'reply', 'intent' and 'confidence'.
        """
        # 1. Empty message
        if not user_text or not user_text.strip():
            return {"reply": "Please type a question about cricket.",
                    "intent": "empty_input", "confidence": 0.0}

        # 2. Message without any letters (only numbers or symbols)
        if not re.search(r"[A-Za-z]", user_text):
            return {"reply": "I can only understand questions written in words. "
                             "Please type a cricket question, for example: "
                             "'Who has scored the most runs in ODIs?'",
                    "intent": "invalid_input", "confidence": 0.0}

        # 3. Pre-process: clean, remove stop words, stem, fix spelling
        tokens = self.correct_spelling(tokenize(user_text))
        processed = " ".join(tokens)

        # 4. Convert to a TF-IDF vector and compare with all stored patterns
        user_vector = self.vectorizer.transform([processed])
        scores = cosine_similarity(user_vector, self.pattern_vectors)[0]
        best_index = int(scores.argmax())
        confidence = float(scores[best_index])

        # 5. Low similarity -> polite fallback
        if confidence < CONFIDENCE_THRESHOLD:
            return {"reply": random.choice(self.kb["fallback_responses"]),
                    "intent": "fallback", "confidence": round(confidence, 2)}

        # 6. Good match -> pick a response of the matched intent
        tag = self.pattern_tags[best_index]
        reply = random.choice(self.intents_by_tag[tag]["responses"])
        return {"reply": reply, "intent": tag, "confidence": round(confidence, 2)}

    def get_greeting(self) -> str:
        """Return the welcome message shown when the app starts."""
        return ("Assalam-o-Alaikum! Welcome to the Cricket Facts Bot. "
                "Ask me about cricket players, records and World Cups. "
                "Try one of the sample questions in the sidebar.")


# Simple command-line test: python chatbot.py
if __name__ == "__main__":
    bot = CricketChatbot()
    print(bot.get_greeting())
    while True:
        message = input("You: ")
        if message.lower() in ("quit", "exit"):
            break
        print("Bot:", bot.get_response(message)["reply"])
