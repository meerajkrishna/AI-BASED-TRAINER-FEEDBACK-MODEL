import pandas as pd
import json

# Read Aptitude Fixed
df_fixed = pd.read_excel('Aptitude_Fixed.xlsx')
print("=== APTITUDE FIXED ===")
print("Shape:", df_fixed.shape)
print("Columns:", list(df_fixed.columns))
print("\nFirst row sample:")
for col in df_fixed.columns:
    val = str(df_fixed.iloc[0][col])
    print(f"  {col}: {val[:300] if len(val) > 300 else val}")

print("\n" + "="*80 + "\n")

# Read Aptitude Quiz
df_quiz = pd.read_excel('Aptitude_Quiz.xlsx')
print("=== APTITUDE QUIZ ===")
print("Shape:", df_quiz.shape)
print("Columns:", list(df_quiz.columns))
print("\nFirst row sample:")
for col in df_quiz.columns:
    val = str(df_quiz.iloc[0][col])
    if pd.notna(df_quiz.iloc[0][col]):
        print(f"  {col}: {val[:200] if len(val) > 200 else val}")

print("\n\n=== ALL TOPICS ===")
for idx, row in df_fixed.iterrows():
    topic_id = row.get('Topic ID', 0)
    topic_name = row.get('Topic Name', 'Unknown')
    print(f"Topic {topic_id}: {topic_name}")
