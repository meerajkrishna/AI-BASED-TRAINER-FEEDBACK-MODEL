import json
import os
import time
import re
import sys
import google.generativeai as genai

# Import TOPIC_META from the existing script to know exactly what topics to target
from extract_quiz_data import TOPIC_META

DATA_FILE = r"p:\mega_project\data_set\ai_quiz_data.json"
ENV_PATH = r"p:\mega_project\ai-trainer\backend\.env"

# 1. Parse API keys
api_keys = []
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEYS="):
                keys_str = line.split("=", 1)[1].strip().strip('"').strip("'")
                api_keys = [k.strip() for k in keys_str.split(",") if k.strip()]
            elif line.startswith("GEMINI_API_KEY=") and not api_keys:
                keys_str = line.split("=", 1)[1].strip().strip('"').strip("'")
                if keys_str: api_keys = [k.strip() for k in keys_str.split(",") if k.strip()]

if not api_keys:
    print("ERROR: No GEMINI_API_KEYS found in backend .env")
    sys.exit(1)

current_key_idx = 0
genai.configure(api_key=api_keys[current_key_idx])
model = genai.GenerativeModel('gemini-2.5-flash')

def rotate_key():
    global current_key_idx
    if current_key_idx < len(api_keys) - 1:
        current_key_idx += 1
        genai.configure(api_key=api_keys[current_key_idx])
        print(f"[*] Rotated to API key index {current_key_idx}")
        return True
    return False

def generate_batch(topic_name: str, batch_num: int) -> list:
    prompt = f"""You are an expert aptitude test creator.
Generate EXACTLY 25 multiple-choice questions for the aptitude topic: "{topic_name}".
Batch {batch_num}.

STRICT CONSTRAINTS:
1. Difficulty: Medium.
2. Context: Scenarios for CS students (servers, code, data, tech).
3. Length: VERY SHORT & DIRECT. Max 1-2 sentences. No fluff.
4. Options: Exactly 4 options.
5. Correct Answer: Must match one option text exactly.
6. Format: Raw JSON array only. No markdown.

REQUIRED JSON FORMAT:
[
  {{
    "text": "4 servers process 20 requests/sec. Total requests per min?",
    "options": ["1200", "4800", "80", "240"],
    "correctAnswer": "4800"
  }},
  ... (24 more)
]
"""
    max_attempts = len(api_keys) * 2
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = model.generate_content(prompt)
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                raise Exception(f"Prompt blocked by safety settings: {response.prompt_feedback.block_reason}")
                
            text = response.text.strip()
            
            # Clean possible markdown wrap
            if text.startswith("```json"): text = text[7:]
            elif text.startswith("```"): text = text[3:]
            if text.endswith("```"): text = text[:-3]
            text = text.strip()
            
            # Parse JSON
            data = json.loads(text)
            if not isinstance(data, list):
                raise ValueError("AI did not return a JSON array.")
                
            # Validate basic structure for the first element
            if len(data) > 0:
                if "text" not in data[0] or "options" not in data[0] or "correctAnswer" not in data[0]:
                    raise ValueError("JSON array elements missing required fields.")
                    
            return data

        except json.JSONDecodeError as e:
            print(f"  [!] JSON Parse Error: {e}")
            attempt += 1
            time.sleep(2)
        except Exception as e:
            err_msg = str(e).lower()
            
            # 429 Handling: Distinction between Rate Limit (Temporary) and Quota Exhaustion (Daily)
            if "429" in err_msg or "quota" in err_msg or "too many requests" in err_msg:
                print(f"  [!] Rate limit reached for key {current_key_idx}. Waiting 60s to retry...")
                time.sleep(60) # Wait a full minute for the RPM window to reset
                
                # Try this key one more time before rotating
                attempt += 1
                if attempt % 2 == 0: # Every 2nd rate limit hit, rotate key
                    print(f"  [!] Still limited. Rotating API key...")
                    if not rotate_key():
                        print(f"  [!] No more keys to rotate.")
                        raise Exception("All API keys exhausted.")
                continue
            else:
                print(f"  [!] Unexpected API Error: {err_msg}")
                attempt += 1
                time.sleep(5)
    
    raise Exception(f"Failed to generate batch {batch_num} for {topic_name} after {max_attempts} attempts.")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate AI quiz data.")
    parser.add_argument("--limit", type=int, default=0, help="Number of topics to limit generation to")
    args = parser.parse_args()
    
    print("=" * 60)
    print(f" AI Quiz Generator (50 Qs/Topic) - Using {len(api_keys)} API keys")
    print("=" * 60)

    # Load existing AI data if we are resuming
    existing_data = {}
    if os.path.exists(DATA_FILE):
        print(f"[*] Checking for existing progress in {DATA_FILE}...")
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
                count = sum(len(qs) for qs in existing_data.values())
                print(f"[*] Loaded {len(existing_data)} topics and {count} total questions.")
            except Exception as e:
                print(f"[ERROR] Found {DATA_FILE} but could not parse it: {e}")
                print("[!] Stopping to prevent overwriting your existing data. Please fix the JSON file!")
                sys.exit(1)
    else:
        print(f"[*] No existing progress file found. Starting fresh.")

    # Get the 27 topics from extract_quiz_data's TOPIC_META
    topics_list = [t_meta["name"] for t_meta in TOPIC_META.values()]
    
    if args.limit > 0:
        topics_list = topics_list[:args.limit]
        
    total = len(topics_list)
    
    # Calculate how many we actually need to do
    to_generate = []
    for topic_name in topics_list:
        if topic_name not in existing_data or len(existing_data[topic_name]) < 50:
            to_generate.append(topic_name)
    
    if not to_generate:
        print(f"\n[✓] ALL {total} TOPICS ARE ALREADY COMPLETE (50 questions each)!")
        return

    print(f"\n[*] Resuming generation. {len(to_generate)} topics remaining out of {total}.\n")

    for idx, topic_name in enumerate(topics_list, start=1):
        if topic_name in existing_data and len(existing_data[topic_name]) >= 50:
            print(f"[{idx}/{total}] [SKIPPING] {topic_name} (Already has 50 questions)")
            continue
            
        print(f"[{idx}/{total}] Generating 50 questions for: {topic_name}...")
        
        all_qs = []
        try:
            # Batch 1
            print("  -> Fetching Batch 1 (25 questions)...")
            batch1 = generate_batch(topic_name, 1)
            all_qs.extend(batch1)
            print(f"     ✅ Received {len(batch1)} questions.")
            time.sleep(10) # Longer delay to avoid immediate 429
            
            # Batch 2
            print("  -> Fetching Batch 2 (25 questions)...")
            batch2 = generate_batch(topic_name, 2)
            all_qs.extend(batch2)
            print(f"     ✅ Received {len(batch2)} questions.")
            time.sleep(10)
            
            existing_data[topic_name] = all_qs
            
            # Incremental save
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=2)
                
            print(f"[*] Saved {len(all_qs)} total questions for {topic_name}")
            
        except Exception as e:
            print(f"\n[FATAL ERROR generating for {topic_name}]: {e}")
            break

    print("\n" + "=" * 60)
    print(" DONE")
    print("=" * 60)

if __name__ == "__main__":
    main()
