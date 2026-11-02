# Cricket Player and Records Facts Bot

A simple Python chatbot with a Streamlit web interface that answers questions about
cricket players, batting and bowling records, World Cups and Pakistani cricket stars.

**Student Name:** Your Name
**Roll Number:** Your Roll Number
**Course / Section / Instructor:** Your Course, Your Section, Your Instructor

## Features
- Chat-style interface (`st.chat_message`, `st.chat_input`) with history kept in `st.session_state`
- Friendly greeting when the app starts and polite fallback for unknown questions
- Understands greetings and farewells (hello, salam, bye, Allah Hafiz, thank you)
- Handles different wording, upper/lower case and extra punctuation
- Tolerates small spelling mistakes (for example "sachn tendulkr")
- Sidebar with description, sample questions and a **Clear Chat** button
- Extra feature: shows the **predicted intent and confidence score** for every reply
- Knowledge base stored in an external JSON file (66 intents, 279 question patterns)

## Technologies Used
Python 3.10+, Streamlit (interface), scikit-learn (TF-IDF and cosine similarity),
difflib and re from the Python standard library, JSON (knowledge base).

## Project Structure
```
RollNumber_Name_Chatbot/
|-- app.py                  # Streamlit interface
|-- chatbot.py              # Chatbot logic (pre-processing + matching)
|-- data/knowledge_base.json# Intents, patterns and answers
|-- tests/test_chatbot.py   # 20 automatic test cases
|-- requirements.txt
|-- README.md
|-- screenshots/            # interface screenshot
`-- docs/                   # report, viva slides, diagrams
```

## Installation
```
pip install -r requirements.txt
```

## Run the Application
```
streamlit run app.py
```
Then open the link shown in the terminal (usually http://localhost:8501).

## Run the Tests
```
python tests/test_chatbot.py
```

## Sample Questions
- Who has scored the most runs in ODIs?
- What is the highest score in Test cricket?
- Who has taken the most Test wickets?
- Tell me about Babar Azam
- Who won the 1992 World Cup?
- Who bowled the fastest ball?
- Hello / Salam / Bye / Allah Hafiz

## How It Works (short)
1. The user types a question.
2. The text is cleaned (lower case, punctuation removed), stop words are removed and words are made singular.
3. Unknown words are corrected using the closest known word (difflib).
4. The question is converted to a TF-IDF vector and compared with all stored questions using cosine similarity.
5. If the best score is 0.45 or more, the answer of that intent is shown; otherwise a fallback reply is shown.

## How to Add a New Question
Open `data/knowledge_base.json`, add a new item in `"intents"` with a `tag`, a list of
`patterns` (ways the user may ask) and a list of `responses`. Restart the app.

## Screenshot
![Interface](screenshots/interface.png)

## Note
Cricket records are accurate up to 2025 and may change after new matches.
