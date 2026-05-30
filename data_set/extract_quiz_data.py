"""
extract_quiz_data.py
═══════════════════
Parse all 27 Excel files from the 3 quiz datasets and generate:
  1. quiz_data.json         — normalized JSON with all topics & questions
  2. aptitudeData.ts        — ready-to-use TypeScript data file

Excel structure (wide format, repeating headers):
  Col 0: Main Topic (integer id)
  Col 1: Topic ID  (e.g. "1.1")
  Col 2: Topic Name (e.g. "Percentage")
  Col 3..8:   Q1, Opt1, Opt2, Opt3, Opt4, Correct
  Col 9..14:  Q2, Opt1, Opt2, Opt3, Opt4, Correct
  ...
  Col (3 + (n-1)*6) .. (3 + n*6 - 1):  Qn block

The repeating column names (Opt1, Opt2, ...) are handled by reading
positionally — we never rely on header names after col 2.
"""

import json
import os
import openpyxl

# ── File mappings ──
# (filepath, category_key, category_label)
DATASETS = [
    # Quantitative
    (r"Quantitative_extracted\Quantitative\1.1 Percentage.xlsx", "quantitative", "Quantitative Aptitude"),
    (r"Quantitative_extracted\Quantitative\1.2 Ratio_and_Proportion.xlsx", "quantitative", "Quantitative Aptitude"),
    (r"Quantitative_extracted\Quantitative\1.3 Time_and_Work.xlsx", "quantitative", "Quantitative Aptitude"),
    (r"Quantitative_extracted\Quantitative\1.4 Profit_and_Loss.xlsx", "quantitative", "Quantitative Aptitude"),
    (r"Quantitative_extracted\Quantitative\1.5 Number_Series.xlsx", "quantitative", "Quantitative Aptitude"),
    (r"Quantitative_extracted\Quantitative\1.6 Linear_Equation.xlsx", "quantitative", "Quantitative Aptitude"),
    (r"Quantitative_extracted\Quantitative\1.7 Quadratic_Equations.xlsx", "quantitative", "Quantitative Aptitude"),
    (r"Quantitative_extracted\Quantitative\1.8 HCF_LCM.xlsx", "quantitative", "Quantitative Aptitude"),
    (r"Quantitative_extracted\Quantitative\1.9 Partnership.xlsx", "quantitative", "Quantitative Aptitude"),
    (r"Quantitative_extracted\Quantitative\1.11 Simple_Interest.xlsx", "quantitative", "Quantitative Aptitude"),
    (r"Quantitative_extracted\Quantitative\1.12 Compound_Interest.xlsx", "quantitative", "Quantitative Aptitude"),
    (r"Quantitative_extracted\Quantitative\1.13 Progressions_AP_GP.xlsx", "quantitative", "Quantitative Aptitude"),
    (r"Quantitative_extracted\Quantitative\1.14 Logarithms.xlsx", "quantitative", "Quantitative Aptitude"),
    (r"Quantitative_extracted\Quantitative\1.15 Averages.xlsx", "quantitative", "Quantitative Aptitude"),
    # Data Interpretation
    (r"2_Data_Interpretation\2 Data Interpretation\2.1 Bar_Graphs.xlsx", "data_interpretation", "Data Interpretation"),
    (r"2_Data_Interpretation\2 Data Interpretation\2.2 Line_Charts.xlsx", "data_interpretation", "Data Interpretation"),
    (r"2_Data_Interpretation\2 Data Interpretation\2.3 Histogram.xlsx", "data_interpretation", "Data Interpretation"),
    (r"2_Data_Interpretation\2 Data Interpretation\2.4 Pie_Charts.xlsx", "data_interpretation", "Data Interpretation"),
    (r"2_Data_Interpretation\2 Data Interpretation\2.5 Caselets.xlsx", "data_interpretation", "Data Interpretation"),
    (r"2_Data_Interpretation\2 Data Interpretation\2.6 Data_Sets_Rows_and_Column.xlsx", "data_interpretation", "Data Interpretation"),
    # Logical Reasoning
    (r"3_Logical_Reasoning\3 Logical Reasoning\3.1 Coding_Decoding.xlsx", "logical_reasoning", "Logical Reasoning"),
    (r"3_Logical_Reasoning\3 Logical Reasoning\3.2 Blood_Relations.xlsx", "logical_reasoning", "Logical Reasoning"),
    (r"3_Logical_Reasoning\3 Logical Reasoning\3.3 Seating_Arrangement.xlsx", "logical_reasoning", "Logical Reasoning"),
    (r"3_Logical_Reasoning\3 Logical Reasoning\3.4 Syllogism.xlsx", "logical_reasoning", "Logical Reasoning"),
    (r"3_Logical_Reasoning\3 Logical Reasoning\3.5 Direction_Sense.xlsx", "logical_reasoning", "Logical Reasoning"),
    (r"3_Logical_Reasoning\3 Logical Reasoning\3.6 Logical_Puzzles.xlsx", "logical_reasoning", "Logical Reasoning"),
    (r"3_Logical_Reasoning\3 Logical Reasoning\3.7 Series_Completion.xlsx", "logical_reasoning", "Logical Reasoning"),
]

# Map file topic names → seed_topics.py names + icons + levels
# (excel_topic_name → { name, icon, level })
TOPIC_META = {
    "Percentage":           {"name": "Percentage",          "icon": "📊", "level": "Beginner"},
    "Ratio_and_Proportion": {"name": "Ratio and Proportion","icon": "⚖️", "level": "Beginner"},
    "Time_and_Work":        {"name": "Time and Work",       "icon": "⏱️", "level": "Intermediate"},
    "Profit_and_Loss":      {"name": "Profit and Loss",     "icon": "💰", "level": "Beginner"},
    "Number_Series":        {"name": "Number Series",       "icon": "🔢", "level": "Intermediate"},
    "Linear_Equation":      {"name": "Linear Equations",    "icon": "📏", "level": "Beginner"},
    "Quadratic_Equations":  {"name": "Quadratic Equations", "icon": "📐", "level": "Intermediate"},
    "HCF_LCM":             {"name": "HCF and LCM",         "icon": "🧮", "level": "Beginner"},
    "Partnership":          {"name": "Partnership",         "icon": "🤝", "level": "Intermediate"},
    "Simple_Interest":      {"name": "Simple Interest",     "icon": "🏦", "level": "Beginner"},
    "Compound_Interest":    {"name": "Compound Interest",   "icon": "📈", "level": "Intermediate"},
    "Progressions_AP_GP":   {"name": "Progressions (AP/GP)","icon": "📊", "level": "Intermediate"},
    "Logarithms":           {"name": "Logarithms",          "icon": "📝", "level": "Intermediate"},
    "Averages":             {"name": "Averages",            "icon": "📉", "level": "Beginner"},
    # Data Interpretation
    "Bar_Graphs":           {"name": "Bar Graphs",          "icon": "📊", "level": "Beginner"},
    "Line_Charts":          {"name": "Line Charts",         "icon": "📈", "level": "Beginner"},
    "Histogram":            {"name": "Histogram",           "icon": "📊", "level": "Intermediate"},
    "Pie_Charts":           {"name": "Pie Charts",          "icon": "🥧", "level": "Beginner"},
    "Caselets":             {"name": "Caselets",            "icon": "📑", "level": "Advanced"},
    "Data_Sets_Rows_and_Column": {"name": "Data Tables",   "icon": "📋", "level": "Beginner"},
    # Logical Reasoning
    "Coding_Decoding":      {"name": "Coding and Decoding", "icon": "🔐", "level": "Beginner"},
    "Blood_Relations":      {"name": "Blood Relations",     "icon": "👨‍👩‍👦", "level": "Intermediate"},
    "Seating_Arrangement":  {"name": "Seating Arrangement", "icon": "💺", "level": "Intermediate"},
    "Syllogism":            {"name": "Syllogisms",          "icon": "🧠", "level": "Intermediate"},
    "Direction_Sense":      {"name": "Direction Sense",     "icon": "🧭", "level": "Beginner"},
    "Logical_Puzzles":      {"name": "Logical Puzzles",     "icon": "🧩", "level": "Advanced"},
    "Series_Completion":    {"name": "Series Completion",   "icon": "🔢", "level": "Beginner"},
}


def parse_excel(filepath: str) -> list[dict]:
    """
    Parse a single Excel file positionally.
    Returns list of question dicts: {text, options[], correctAnswer}
    
    Column layout per question block (6 cols each):
      [Q_text, Opt1, Opt2, Opt3, Opt4, CorrectAnswer]
    First 3 columns are: MainTopic, TopicID, TopicName
    So questions start at column index 3.
    """
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    ws = wb.active
    
    questions = []
    
    # Read data row (row 2 — row 1 is headers)
    for row in ws.iter_rows(min_row=2, values_only=True):
        cells = list(row)
        if len(cells) < 9:  # Need at least: 3 meta + 6 for one question
            continue
            
        # Skip empty rows
        if cells[0] is None and cells[2] is None:
            continue
        
        # Parse question blocks starting at col 3
        col = 3
        while col + 5 < len(cells):
            q_text = cells[col]
            opt1   = cells[col + 1]
            opt2   = cells[col + 2]
            opt3   = cells[col + 3]
            opt4   = cells[col + 4]
            correct = cells[col + 5]
            
            # Stop if we hit empty question text
            if q_text is None or str(q_text).strip() == "":
                col += 6
                continue
            
            questions.append({
                "text": str(q_text).strip(),
                "options": [
                    str(opt1).strip() if opt1 is not None else "",
                    str(opt2).strip() if opt2 is not None else "",
                    str(opt3).strip() if opt3 is not None else "",
                    str(opt4).strip() if opt4 is not None else "",
                ],
                "correctAnswer": str(correct).strip() if correct is not None else "",
            })
            
            col += 6
    
    wb.close()
    return questions


def extract_topic_key(filepath: str) -> str:
    """Extract the topic key from filename, e.g. '1.1 Percentage.xlsx' → 'Percentage'"""
    basename = os.path.basename(filepath)
    name = os.path.splitext(basename)[0]
    # Remove the leading number like "1.1 " or "2.3 "
    parts = name.split(" ", 1)
    if len(parts) == 2:
        return parts[1]
    return name


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    all_topics = []
    global_question_id = 1
    
    for idx, (rel_path, category_key, category_label) in enumerate(DATASETS, start=1):
        filepath = os.path.join(base_dir, rel_path)
        
        if not os.path.exists(filepath):
            print(f"  ⚠️  File not found: {filepath}")
            continue
        
        topic_key = extract_topic_key(rel_path)
        meta = TOPIC_META.get(topic_key, {
            "name": topic_key.replace("_", " "),
            "icon": "📘",
            "level": "Beginner"
        })
        
        print(f"  [{idx:2d}/27] Parsing: {meta['name']} ({rel_path})...", end="")
        
        questions = parse_excel(filepath)
        
        # Assign unique IDs
        for q in questions:
            q["id"] = global_question_id
            global_question_id += 1
        
        topic = {
            "id": idx,
            "name": meta["name"],
            "icon": meta["icon"],
            "level": meta["level"],
            "category": category_key,
            "categoryLabel": category_label,
            "hasQuiz": True,
            "questionCount": len(questions),
            "questions": questions,
        }
        
        all_topics.append(topic)
        print(f" {len(questions)} questions ✓")
    
    # ── Merge AI generated questions if available ──
    ai_json_path = os.path.join(base_dir, "ai_quiz_data.json")
    if os.path.exists(ai_json_path):
        try:
            with open(ai_json_path, "r", encoding="utf-8") as f:
                ai_data = json.load(f)
            
            for t in all_topics:
                topic_name = t["name"]
                if topic_name in ai_data:
                    ai_qs = ai_data[topic_name]
                    for ai_q in ai_qs:
                        t["questions"].append({
                            "id": global_question_id,
                            "text": ai_q.get("text", ""),
                            "options": ai_q.get("options", []),
                            "correctAnswer": ai_q.get("correctAnswer", "")
                        })
                        global_question_id += 1
                    t["questionCount"] = len(t["questions"])
            print(f"\n✅ Merged AI-generated questions from ai_quiz_data.json")
        except Exception as e:
            print(f"\n❌ Error loading AI quiz data: {e}")

    # ── Save JSON ──
    json_path = os.path.join(base_dir, "quiz_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_topics, f, indent=2, ensure_ascii=False)
    
    total_q = sum(t["questionCount"] for t in all_topics)
    print(f"\n✅ Saved {len(all_topics)} topics to quiz_data.json")
    print(f"   Total questions: {total_q}")
    
    # ── Generate TypeScript ──
    generate_typescript(all_topics, base_dir)


def escape_js(s: str) -> str:
    """Escape a string for use inside a JS single-quoted string literal.
    
    IMPORTANT: Backslashes must be escaped FIRST, then quotes.
    Otherwise: A's → A\\'s (broken) instead of A\\'s → A\\'s (correct).
    """
    s = s.replace("\\", "\\\\")   # 1. Escape backslashes first
    s = s.replace("'", "\\'")     # 2. Then escape single quotes
    s = s.replace("\n", " ")      # 3. Remove newlines
    s = s.replace("\r", "")       # 4. Remove carriage returns
    s = s.replace("₹", "Rs.")     # 5. Replace ₹ with Rs. for safety
    return s


def generate_typescript(topics: list[dict], base_dir: str):
    """Generate the aptitudeData.ts file for the frontend."""
    
    ts_path = os.path.join(
        base_dir, "..", "ai-trainer", "frontend", "src", "data", "aptitudeData.ts"
    )
    
    lines = []
    lines.append("import type { Topic, Question } from '../types/learning';")
    lines.append("")
    lines.append("// ═══════════════════════════════════════════════════════════")
    lines.append("// AUTO-GENERATED from extract_quiz_data.py — DO NOT EDIT")
    lines.append(f"// {len(topics)} topics, {sum(t['questionCount'] for t in topics)} questions")
    lines.append("// ═══════════════════════════════════════════════════════════")
    lines.append("")
    
    # ── TOPICS array ──
    lines.append("export const TOPICS: Topic[] = [")
    for t in topics:
        # Escape single quotes in name
        name = t['name'].replace("'", "\\'")
        lines.append("  {")
        lines.append(f"    id: {t['id']},")
        lines.append(f"    name: '{name}',")
        lines.append(f"    category: '{t['category']}',")
        lines.append(f"    categoryLabel: '{t['categoryLabel']}',")
        lines.append(f"    hasQuiz: true,")
        lines.append(f"    definition: '',")
        lines.append(f"    description: '',")
        lines.append(f"    videoUrl: '',")
        lines.append(f"    level: '{t['level']}',")
        lines.append(f"    icon: '{t['icon']}',")
        lines.append("  },")
    lines.append("];")
    lines.append("")
    
    # ── QUESTIONS array ──
    lines.append("export const QUESTIONS: Question[] = [")
    for t in topics:
        lines.append(f"  // ── {t['name']} (Topic {t['id']}) ── {t['questionCount']} questions")
        for q in t["questions"]:
            text = escape_js(q['text'])
            correct = escape_js(q['correctAnswer'])
            opts = ", ".join(
                f"'{escape_js(o)}'" for o in q['options']
            )
            lines.append(
                f"  {{ id: {q['id']}, topicId: {t['id']}, "
                f"text: '{text}', "
                f"options: [{opts}], "
                f"correctAnswer: '{correct}' }},"
            )
    lines.append("];")
    lines.append("")
    
    # ── Helper functions ──
    lines.append("// ── Helper functions ──")
    lines.append("")
    lines.append("export const getTopicById = (id: number): Topic | undefined => {")
    lines.append("  return TOPICS.find(topic => topic.id === id);")
    lines.append("};")
    lines.append("")
    lines.append("export const getQuestionsByTopicId = (topicId: number): Question[] => {")
    lines.append("  return QUESTIONS.filter(q => q.topicId === topicId);")
    lines.append("};")
    lines.append("")
    lines.append("export const getTopicsByLevel = (level: Topic['level']): Topic[] => {")
    lines.append("  return TOPICS.filter(topic => topic.level === level);")
    lines.append("};")
    lines.append("")
    lines.append("export const getTopicsByCategory = (category: string): Topic[] => {")
    lines.append("  return TOPICS.filter(topic => topic.category === category);")
    lines.append("};")
    lines.append("")
    lines.append("/**")
    lines.append(" * Get a random subset of questions for a quiz attempt.")
    lines.append(" * @param topicId - topic to get questions for")
    lines.append(" * @param count   - number of questions (default 10)")
    lines.append(" */")
    lines.append("export const getRandomQuestions = (topicId: number, count: number = 10): Question[] => {")
    lines.append("  const all = getQuestionsByTopicId(topicId);")
    lines.append("  const shuffled = [...all].sort(() => Math.random() - 0.5);")
    lines.append("  return shuffled.slice(0, Math.min(count, all.length));")
    lines.append("};")
    lines.append("")
    lines.append("// ── Local storage helpers for progress ──")
    lines.append("const PROGRESS_KEY = 'aptitude-progress';")
    lines.append("")
    lines.append("export const saveProgress = (topicId: number, score: number): void => {")
    lines.append("  const stored = localStorage.getItem(PROGRESS_KEY);")
    lines.append("  const progress: Record<number, { bestScore: number; attempts: number; completed: boolean }> =")
    lines.append("    stored ? JSON.parse(stored) : {};")
    lines.append("")
    lines.append("  const existing = progress[topicId] || { bestScore: 0, attempts: 0, completed: false };")
    lines.append("  progress[topicId] = {")
    lines.append("    bestScore: Math.max(existing.bestScore, score),")
    lines.append("    attempts: existing.attempts + 1,")
    lines.append("    completed: true")
    lines.append("  };")
    lines.append("")
    lines.append("  localStorage.setItem(PROGRESS_KEY, JSON.stringify(progress));")
    lines.append("};")
    lines.append("")
    lines.append("export const getProgress = (topicId: number): { bestScore: number; attempts: number; completed: boolean } | null => {")
    lines.append("  const stored = localStorage.getItem(PROGRESS_KEY);")
    lines.append("  if (!stored) return null;")
    lines.append("")
    lines.append("  const progress = JSON.parse(stored);")
    lines.append("  return progress[topicId] || null;")
    lines.append("};")
    lines.append("")
    lines.append("export const getAllProgress = (): Record<number, { bestScore: number; attempts: number; completed: boolean }> => {")
    lines.append("  const stored = localStorage.getItem(PROGRESS_KEY);")
    lines.append("  return stored ? JSON.parse(stored) : {};")
    lines.append("};")
    lines.append("")
    
    with open(ts_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"✅ Generated aptitudeData.ts at {ts_path}")
    print(f"   {len(topics)} topics, {sum(t['questionCount'] for t in topics)} questions")


if __name__ == "__main__":
    print("=" * 60)
    print("  Quiz Data Extractor")
    print("  Parsing 27 Excel files → JSON + TypeScript")
    print("=" * 60)
    print()
    main()
