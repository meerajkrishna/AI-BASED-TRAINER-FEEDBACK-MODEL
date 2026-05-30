import pandas as pd

# Read Aptitude Fixed
df_fixed = pd.read_excel('Aptitude_Fixed.xlsx')
print("=== APTITUDE FIXED ===")
print("Shape:", df_fixed.shape)
print("Columns:", df_fixed.columns.tolist())
print()
for idx, row in df_fixed.iterrows():
    print(f"--- Topic {row['Topic ID']}: {row['Topic']} ---")
    for col in df_fixed.columns:
        val = str(row[col])
        print(f"  {col}: {val[:300] if len(val) > 300 else val}")
    print()

print("\n" + "="*80 + "\n")

# Read Aptitude Quiz
df_quiz = pd.read_excel('Aptitude_Quiz.xlsx')
print("=== APTITUDE QUIZ ===")
print("Shape:", df_quiz.shape)
print("Columns:", df_quiz.columns.tolist())
print()
for idx, row in df_quiz.iterrows():
    print(f"--- Topic {row['Topic ID']}: {row['Topic']} ---")
    for col in df_quiz.columns:
        if pd.notna(row[col]):
            val = str(row[col])
            print(f"  {col}: {val[:150] if len(val) > 150 else val}")
    print()
