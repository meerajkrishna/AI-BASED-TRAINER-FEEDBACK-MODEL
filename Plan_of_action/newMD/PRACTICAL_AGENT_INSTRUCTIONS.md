# How to Instruct the Agent: Practical Guide

## Quick Reference: What Agent Got Right vs. Wrong

### The Agent's Good Work (Keep This)
✅ Sprint 0 security fixes — exactly as planned
✅ Sprint 1 routing improvements — keep as-is
✅ Sprint 2 voice quality fixes — correct approach
✅ Sprint 3 polish work — maintain this

### The Agent's Wrong Move (Fix This)
❌ Do NOT delete InterviewSession.tsx
   Instead: Rewrite it as a state machine (keep the file)

### What Agent Completely Missed (Add This)
❌ Auth module fixes (BUG-01, BUG-02) — Week 1
❌ Aptitude module creation (BUG-03, BUG-14) — Week 2
❌ Custom hook creation plan (4 hooks) — Week 3
❌ Full Results page (Week 6)
❌ Dashboard real APIs (Week 7)

---

## Copy-Paste Instructions for Your Agent

### **Instruction Set #1: The Complete Overview (Give This First)**

```
You have created an excellent 4-sprint plan focused on the Interview module.
However, this project has 5 modules and 16 bugs total, not just Interview.

Your plan covers ~10 bugs for the Interview module only.
You need to expand to cover ALL 16 bugs across 5 modules in 7 weeks.

HERE IS WHAT TO DO:

1. KEEP YOUR WORK:
   - All of Sprint 0 (backend security)
   - All of Sprint 1 (routing)
   - All of Sprint 2 (voice quality)
   - All of Sprint 3 (polish)

2. REMOVE YOUR WORK:
   - Do NOT delete InterviewSession.tsx
   - Instead: Rewrite it as a state machine (Section 8.4 of blueprint)
   - Keep the same file and route

3. ADD TO YOUR PLAN:
   - Week 1: Auth module fixes (add before your Sprint 0)
   - Week 2: Aptitude backend (add after Week 1)
   - Week 3: Create 4 custom hooks (add after Week 2)
   - Weeks 4-6: Your sprints integrated here (with additions)
   - Week 7: Dashboard real APIs (add at end)

STRUCTURE YOUR FINAL PLAN AS:

WEEK 1 (Auth)
├─ Your Sprint 0 security fixes
├─ NEW: BUG-01 name validation
├─ NEW: BUG-02 serializer validation
├─ NEW: BUG-11 hardcoded URLs
└─ NEW: BUG-12 token storage

WEEK 2 (Aptitude)
├─ NEW: AptitudeTopic models
├─ NEW: AptitudeQuestion models
├─ NEW: Random question API with ORDER BY ?
├─ NEW: Database seeder from CSV
└─ NEW: Learning module (same pattern)

WEEK 3 (Hooks)
├─ NEW: Create useTTS.ts (TTS with Chrome fix)
├─ NEW: Create useSTT.ts (Web Speech API)
├─ NEW: Create useSilenceDetector.ts (3s silence)
└─ NEW: Create useInterviewSession.ts (localStorage)

WEEK 4 (Interview Backend)
├─ Your Sprint 0 backend work
├─ NEW: Detailed submit-all endpoint spec
└─ NEW: Gemini evaluation prompts

WEEK 5 (Interview UI)
├─ Your Sprint 1 routing work
├─ Your Sprint 2 voice quality work
├─ NEW: Rewrite InterviewSession.tsx (NOT delete)
└─ NEW: Create 7 missing interview components

WEEK 6 (Results + PDF)
├─ Your Sprint 3 polish work
├─ NEW: PDF generator with jsPDF
└─ NEW: Results page components

WEEK 7 (Dashboard)
├─ NEW: Connect dashboard to real APIs
├─ NEW: Score trend charts
└─ NEW: Real-time statistics

For each task, I will provide exact code from the blueprint.
Section references are given (e.g., "Blueprint Section 6.2").

Now I'll provide the detailed week-by-week breakdown...
```

---

### **Instruction Set #2: Week 1 Details (Auth Module)**

```
WEEK 1: AUTH MODULE FIXES + SECURITY HARDENING

KEEP from your plan:
✅ Move openai_service.py to correct location
✅ Update google-generativeai to >=0.8.0
✅ Fix answer_text AttributeError in submit_all
✅ Add security fixes (file validation, rate limiting, etc.)
✅ Delete dead endpoints (submit_answer, transcribe)
✅ Delete whisper_service.py

ADD to your plan (NEW BUG FIXES):

1. BUG-01: Name Validation in Register.tsx
   File: frontend/src/components/auth/Register.tsx
   
   Add this to the Register component:
   const [nameError, setNameError] = useState('');
   const NAME_REGEX = /^[a-zA-Z\s'\-]{2,50}$/;
   
   Update the fullName input onChange handler:
   onChange={(e) => {
     const val = e.target.value;
     if (/^[a-zA-Z\s'\-]*$/.test(val) || val === '') {
       setFormData({ ...formData, fullName: val });
       if (val.length > 0 && !NAME_REGEX.test(val)) {
         setNameError('Name must be 2-50 letters only.');
       } else {
         setNameError('');
       }
     }
   }}
   
   TEST: Type "123abc" in fullName → should be blocked
          Type "John Doe" → should be accepted

2. BUG-02: Name Validation in Serializer
   File: backend/apps/accounts/serializers.py
   
   Add to RegisterSerializer.validate():
   import re
   
   def validate(self, data):
       # Validate name format
       name_fields = ['first_name', 'last_name']
       for field in name_fields:
           value = data.get(field, '').strip()
           if value and not re.match(r"^[a-zA-Z\s'\-]{1,50}$", value):
               raise serializers.ValidationError({
                   field: f'{field.replace("_", " ").title()} must contain only letters.'
               })
       # ... rest of existing validations
   
   TEST: POST /auth/register/ with first_name='123@$' → should return 400

3. BUG-11: Replace Hardcoded URLs
   Files: 
   - frontend/src/services/api.ts
   - frontend/src/services/interviewAPI.ts
   
   Replace: 'http://localhost:8000/api'
   With: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
   
   Create file: frontend/.env
   Content:
   VITE_API_BASE_URL=http://localhost:8000/api
   
   TEST: Change .env to different URL → app should use new URL

4. BUG-12: Unify Token Storage
   File: frontend/src/store/authStore.ts
   
   Ensure both access and refresh tokens stored in same place.
   Either both in Zustand OR both in localStorage, not split.
   Update authService.ts to read from same source.
   
   TEST: Login, refresh page → user should still be logged in

5. BUG-13: Update Gemini Version
   File: backend/requirements.txt
   
   Replace: google-generativeai==0.3.0
   With: google-generativeai>=0.8.0
   
   Run: pip install --upgrade google-generativeai
   
   TEST: Django runserver should not throw import errors

WEEK 1 DELIVERABLE:
✅ All name validation working (frontend + backend)
✅ All environment variables configured
✅ All security hardening in place
✅ Gemini API working with latest version
```

---

### **Instruction Set #3: Week 2 Details (Aptitude Module)**

```
WEEK 2: APTITUDE & LEARNING BACKEND

This entire week is NEW — not in your sprint plan.

1. Create Aptitude Models
   File: backend/apps/aptitude/models.py
   
   Create these models (exact code in Blueprint Section 7.2):
   - AptitudeTopic
     - name (CharField, unique)
     - icon (CharField)
     - description, learning_html, video_url
     - difficulty, order, is_active
   
   - AptitudeQuestion
     - topic (FK to AptitudeTopic)
     - question_text
     - option_a, option_b, option_c, option_d
     - correct_answer (CharField 'A'/'B'/'C'/'D')
     - explanation, difficulty, is_active
   
   - QuizAttempt
     - user (FK to CustomUser)
     - topic (FK to AptitudeTopic)
     - score (0-100)
     - total_questions, correct_answers
     - time_taken_seconds
     - answers (JSONField)
     - attempted_at
   
   TEST: python manage.py makemigrations && python manage.py migrate

2. Create Aptitude API Views
   File: backend/apps/aptitude/views.py
   
   Create endpoint: GET /api/aptitude/questions/
   Parameters: topic_id, count (default 10)
   
   Key requirement: Use order_by('?') for random selection
   Do NOT return correct_answer in response
   
   Code skeleton:
   @api_view(['GET'])
   @permission_classes([IsAuthenticated])
   def get_questions(request):
       topic_id = request.query_params.get('topic_id')
       count = int(request.query_params.get('count', 10))
       
       qs = AptitudeQuestion.objects.filter(
           topic_id=topic_id, is_active=True
       ).order_by('?')[:min(count, 20)]
       
       return Response(list(qs.values(
           'id', 'question_text', 'option_a', 'option_b', 
           'option_c', 'option_d'
       )))
   
   TEST: Call GET /api/aptitude/questions/?topic_id=1&count=10
         Call it twice → different question order both times

3. Create Database Seeder
   File: data_set/seed_aptitude.py (create new file)
   
   Read from: data_set/aptitude_quiz.csv
   Import into: AptitudeTopic and AptitudeQuestion
   
   Code in Blueprint Section 7.4
   
   Run: python manage.py shell < data_set/seed_aptitude.py
   
   TEST: Check database has 40+ AptitudeQuestion records

4. Create Learning Module
   File: backend/apps/learning/models.py
   
   Follow same pattern as aptitude:
   - LearningTopic (name, description, content_html, video_url, order)
   - Create views.py with GET /api/learning/topics/
   
   TEST: GET /api/learning/topics/ returns topics

5. Update Quiz.tsx Frontend
   File: frontend/src/pages/Quiz.tsx
   
   Replace: getQuestionsByTopicId(aptitudeData)
   With: axios.get('/api/aptitude/questions/', {params: {topic_id, count:10}})
   
   Handle response and update state
   
   TEST: Take quiz twice → different questions each time

WEEK 2 DELIVERABLE:
✅ 40+ questions in database
✅ Random question API working
✅ Quiz.tsx fetches from API
✅ Same quiz shows different questions each attempt
```

---

### **Instruction Set #4: Week 3 Details (Custom Hooks)**

```
WEEK 3: CREATE CUSTOM HOOKS FOR VOICE INTERVIEW

Create these 4 files (code fully provided in Blueprint Section 8.3):

1. Create: frontend/src/hooks/useTTS.ts
   Implements: Text-to-Speech with fixes for:
   - BUG-06: Chrome pause-resume (keep-alive interval every 5s)
   - BUG-07: Voice loading race condition (onvoiceschanged listener)
   
   Returns: { speak, stopSpeaking }
   
   Key features:
   - Wait for voices to load before speaking
   - Resume voice if paused (Chrome bug workaround)
   - Select best voice (Google > en-IN > en > default)
   
   TEST: Call useTTS.speak("Hello world")
         On first load, should use Google voice not robotic voice
         200-word text should NOT pause mid-sentence

2. Create: frontend/src/hooks/useSTT.ts
   Implements: Speech-to-Text with Web Speech API
   Replaces: Old MediaRecorder + Whisper approach (BUG-05)
   
   Returns: { transcript, isRecording, startRecording, stopRecording, resetTranscript }
   
   Key features:
   - Use browser's native Web Speech API (free, no server latency)
   - lang='en-IN' for Indian English accent
   - continuous=true for uninterrupted recording
   - interimResults=true for live transcript display
   
   TEST: Say "hello world" → live transcript appears as you speak
         Stop speaking → transcript complete and accurate

3. Create: frontend/src/hooks/useSilenceDetector.ts
   Implements: 3-second silence auto-advance
   Fixes: BUG-08 (no manual click needed)
   
   Returns: { startSilenceDetection, stopSilenceDetection, resetSilenceTimer }
   
   Key features:
   - 3 seconds of no new transcript = callback fires
   - Resets timer each time user speaks
   - Can be paused/resumed
   
   TEST: Speak 5 words, pause for 3s → onSilence callback fires
         Speak, pause 2s, speak again → timer resets

4. Create: frontend/src/hooks/useInterviewSession.ts
   Implements: localStorage backup of interview answers
   Fixes: BUG-09 (session survives page refresh)
   
   Returns: { saveSession, loadSession, saveAnswer, loadAllAnswers, clearSession }
   
   Key features:
   - Save each answer to localStorage immediately
   - Save current question index
   - Restore on page refresh
   - Clear after submission
   
   TEST: Start interview, answer 3 questions, refresh page
         → all 3 answers restored to state
         → can continue from question 4

WEEK 3 DELIVERABLE:
✅ All 4 hooks created and tested independently
✅ TTS reads clearly with correct voice
✅ STT transcribes speech in real-time
✅ Silence auto-advances after 3s
✅ Session restores after page refresh
```

---

### **Instruction Set #5: Weeks 4-7 Summary**

```
WEEK 4: INTERVIEW BACKEND (Keep Sprint 0 + Add Details)
- Keep all your security fixes from Sprint 0
- Add detailed submit-all endpoint spec (Blueprint Section 8.5)
- Add Gemini evaluation prompts (Blueprint Section 8.6)
- Verify: Scores returned as 0.0-10.0 from backend

WEEK 5: INTERVIEW UI (Keep Sprints 1-2 + Add Details)
- Keep your Sprint 1 routing improvements
- Keep your Sprint 2 voice quality fixes
- CRITICAL: Rewrite InterviewSession.tsx (do NOT delete)
- Implement 11-phase state machine (BROWSER_CHECK, MIC_PERMISSION, etc.)
- Create 7 missing interview components
- Wire in all 4 hooks from Week 3

WEEK 6: RESULTS + PDF (Keep Sprint 3 + Add Details)
- Keep your Sprint 3 polish work
- Add PDF generator (Blueprint Week 6)
- Install: npm install jspdf html2canvas
- Create ReportTemplate.tsx with id="interview-report-pdf"
- Add Download PDF button

WEEK 7: DASHBOARD (Entirely NEW)
- Connect dashboard to /api/interview/stats/
- Connect dashboard to /api/interview/history/
- Create charts with Recharts
- Display real user data instead of hardcoded values
- Test: Dashboard updates after each interview
```

---

## How to Give These Instructions to the Agent

### **Method 1: Paste Directly**
Copy the instruction sets above and paste into your agent interface with:

```
"I'm giving you detailed instructions for each week.
Follow them in order. Each section is self-contained.

WEEK 1: [Paste Instruction Set #2]
WEEK 2: [Paste Instruction Set #3]
WEEK 3: [Paste Instruction Set #4]
WEEKS 4-7: [Paste Instruction Set #5]

For code details, refer to Blueprint Sections provided.
Test after each week before moving to next week."
```

### **Method 2: Reference Document**
Provide the three generated files:

```
"These three documents form your complete instructions:

1. AGENT_INSTRUCTIONS_CLEAR_AND_ACTIONABLE.md — Main roadmap
2. EXECUTIVE_SUMMARY_PLAN_COMPARISON.md — Context
3. PLAN_COMPARISON_AND_CLARIFICATION.md — Detailed analysis

Start with the Executive Summary, then follow the Clear Instructions.
Week-by-week tasks are fully specified with file paths and code sections."
```

### **Method 3: Direct Conversation**
```
"Your 4-sprint plan is good but incomplete. We need to expand to 7 weeks.

Key changes:
1. Do NOT delete InterviewSession.tsx — rewrite it
2. Add Week 1 for Auth fixes (3 bugs)
3. Add Week 2 for Aptitude backend (3 bugs)
4. Add Week 7 for Dashboard (1 bug)
5. Integrate your 4 sprints into Weeks 4-6

I'm providing detailed instructions for each week.
What's your first question?"
```

---

## Critical Things Agent MUST Understand

1. **7 weeks, not 4 sprints**
   - Your work → Weeks 4, 5 (modified), 6
   - New work → Weeks 1, 2, 3, 7

2. **5 modules, not 1**
   - Auth, Aptitude, Learning, Interview, Dashboard

3. **16 bugs, not 10**
   - Agent's plan covers ~10
   - Your plan covers 16 total

4. **Rewrite, not delete**
   - "Rewrite InterviewSession.tsx as a state machine"
   - "Do NOT delete, keep the file and route"

5. **Each week must be tested**
   - Week 1 test: Register with invalid name → blocked
   - Week 2 test: Quiz shows different questions twice
   - Week 3 test: Each hook works independently
   - And so on...

---

## Final Instruction Template (Use This)

```
You created a focused 4-sprint plan for the Interview module.
The complete project has 5 modules and 16 bugs.

Here is the expanded 7-week plan that incorporates your work:

WEEKS 1-7 ROADMAP:
Week 1: Auth fixes (BUG-01, BUG-02, BUG-11, BUG-12)
Week 2: Aptitude backend (BUG-03, BUG-14, BUG-15)
Week 3: Custom hooks (BUG-05-09)
Week 4: Interview backend (your Sprint 0 + additions)
Week 5: Interview UI (your Sprint 1-2 + additions)
Week 6: Results/PDF (your Sprint 3 + additions)
Week 7: Dashboard (BUG-16)

YOUR TASKS:
- Expand your plan from 4 sprints to 7 weeks
- Add Week 1, 2, 7 work
- Integrate your sprints into Weeks 4-6
- Do NOT delete InterviewSession.tsx, rewrite it
- Test at end of each week

DETAILED INSTRUCTIONS FOR EACH WEEK ARE PROVIDED BELOW.

[Provide week-by-week instruction sets]

Start with Week 1. Test before moving to Week 2.
```

This is your practical instruction guide. Use it directly.
