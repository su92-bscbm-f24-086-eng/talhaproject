"""
test_chatbot.py
Purpose : Automatic test cases for the Cricket Facts Bot.
          Run with:  python tests/test_chatbot.py
Author  : YOUR NAME (ROLL NUMBER)
Date    : 2026
"""

import os
import sys

# Allow importing chatbot.py from the parent folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

from chatbot import CricketChatbot

# (test description, user input, expected intent)
TEST_CASES = [
    ("Normal question", "Who has scored the most runs in ODIs?", "most_odi_runs"),
    ("Upper case + punctuation", "WHO HAS SCORED THE MOST RUNS IN ODIS???", "most_odi_runs"),
    ("Different wording", "highest run scorer in one day internationals", "most_odi_runs"),
    ("Spelling mistake", "who is sachn tendulkr", "sachin"),
    ("Spelling mistake 2", "tell me about virat kholi", "kohli"),
    ("Greeting (English)", "hello", "greeting"),
    ("Greeting (Urdu)", "salam", "greeting"),
    ("Farewell", "Allah Hafiz", "farewell"),
    ("Thanks", "thank you", "thanks"),
    ("Highest Test score", "highest score in test cricket", "highest_test_score"),
    ("Wickets record", "most wickets in tests", "most_test_wickets"),
    ("Pakistani player", "who is babar azam", "babar"),
    ("World Cup question", "who won the 1992 world cup", "wc_1992"),
    ("Short query", "tendulkar", "sachin"),
    ("Fastest bowler", "fastest ball ever bowled", "fastest_delivery"),
    ("Unrelated question", "how do I make chicken karahi", "fallback"),
    ("Unknown topic", "who is the president of usa", "fallback"),
    ("Unknown cricket question", "who won pakistan super league", "fallback"),
    ("Empty message", "", "empty_input"),
    ("Only numbers", "12345", "invalid_input"),
]


def run_tests():
    """Run every test case and print a result table."""
    bot = CricketChatbot()
    passed = 0
    print(f"{'No':<3} {'Test':<26} {'Expected':<20} {'Actual':<20} {'Conf':<5} Result")
    print("-" * 85)
    for number, (name, text, expected) in enumerate(TEST_CASES, start=1):
        result = bot.get_response(text)
        ok = result["intent"] == expected
        passed += ok
        print(f"{number:<3} {name:<26} {expected:<20} {result['intent']:<20} "
              f"{result['confidence']:<5} {'PASS' if ok else 'FAIL'}")
    total = len(TEST_CASES)
    print("-" * 85)
    print(f"Passed {passed} of {total}  ->  accuracy = {passed / total * 100:.1f}%")


if __name__ == "__main__":
    run_tests()
