

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.router import classify

TEST_CASES = [
    ("What is the weather in Athens tomorrow?", "weather"),
    ("Θα κάνει ζέστη στη Θεσσαλονίκη αυτή την εβδομάδα;", "weather"),
    ("What's the rain forecast for Patras?", "weather"),
    ("What are the latest smartphone price trends?", "search"),
    ("Υπάρχουν πρόσφατα νέα για τιμές laptop;", "search"),
    ("Any recent news on electronics import tariffs?", "search"),
    ("What is the warranty period for laptops?", "rag"),
    ("Ποια είναι η πολιτική επιστροφών σας;", "rag"),
    ("How does the loyalty points program work?", "rag"),
    ("What's the click and collect pickup window?", "rag"),
    ("What were total sales last month?", "sql"),
    ("Ποιο κατάστημα είχε τα περισσότερα έσοδα;", "sql"),
    ("How many smartphones have we sold in Athens?", "sql"),
    ("Explain what LangGraph is.", "general"),
]


def main():
    correct = 0
    rows = []
    for message, expected in TEST_CASES:
        actual = classify(message)
        match = actual == expected
        correct += match
        rows.append((message, expected, actual, "✅" if match else "❌"))

    print(f"{'#':<3}{'Message':<55}{'Expected':<10}{'Actual':<10}Match")
    for i, (msg, exp, act, mark) in enumerate(rows, 1):
        print(f"{i:<3}{msg[:53]:<55}{exp:<10}{act:<10}{mark}")

    print(f"\nAccuracy: {correct}/{len(TEST_CASES)} ({100*correct/len(TEST_CASES):.0f}%)")


if __name__ == "__main__":
    main()
