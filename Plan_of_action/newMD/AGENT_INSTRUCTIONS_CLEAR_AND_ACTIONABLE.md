# AGENT IMPLEMENTATION INSTRUCTIONS — Clear & Actionable

## What Happened

1. **Your Blueprint** → Complete 7-week plan for ALL 5 modules (16 bugs)
2. **Agent Plan** → 4-sprint plan for INTERVIEW module only (10 bugs)
3. **Result** → Agent's plan is good but INCOMPLETE

---

## AGENT: THIS IS WHAT YOU NEED TO DO

### ❌ What Agent Got WRONG (Fix These First)

**Wrong #1: Do NOT Delete InterviewSession.tsx**

- Your plan: "Delete InterviewSession.tsx completely" ❌
- Correct: "Rewrite InterviewSession.tsx as a state machine" ✅
- Impact: Deleting breaks the entire routing; rewriting keeps the file and route intact

**Wrong #2: Narrowed Scope to Interview Only**

- Your plan covers: Interview module only
- Should cover: All 5 modules (Auth, Aptitude, Learning, Interview, Dashboard)
- Impact: 6 critical bugs remain unfixed

**Wrong #3: Missed Creating 4 Custom Hooks**

- Your plan: Assumes hooks exist
- Should do: Create hooks from scratch in Section 8.3 of blueprint
- Impact: Voice interview won't work without these

---

## CORRECTED IMPLEMENTATION PLAN: 7 WEEKS

### **WEEK 1: Auth Module Fixes**

**Your Sprint 0 + These Auth Fixes**

**Tasks:**

1. ✅ Move openai_service.py (your plan)
2. ✅ Update google-generativeai >=0.8.0 (your plan)
3. ✅ Fix answer_text AttributeError (your plan)
4. ✅ Security fixes (your plan)
5. **NEW:** BUG-01 — Name validation in Register.tsx
   - File: `frontend/src/components/auth/Register.tsx`
   - Add regex check: `/^[a-zA-Z\s'-]{2,50}$/`
   - Block numbers and symbols in fullName field
   - Code in Blueprint Section 6.2

6. **NEW:** BUG-02 — Name validation in Serializer
   - File: `backend/apps/accounts/serializers.py`
   - Add name field validation to validate() method
   - Same regex as frontend
   - Code in Blueprint Section 6.3

7. **NEW:** BUG-11 — Replace hardcoded URLs
   - Replace `http://localhost:8000` with `import.meta.env.VITE_API_BASE_URL`
   - Files: `frontend/src/services/api.ts`, `interviewAPI.ts`
   - Create `frontend/.env` with `VITE_API_BASE_URL=http://localhost:8000/api`

8. **NEW:** BUG-12 — Unify token storage (already in your Sprint 3, move to Week 1)
   - Ensure Zustand and localStorage use same approach
   - Code in Blueprint Section 6

**Test:** Register with "123abc" → blocked. Register with "John Doe" → accepted.

---

### **WEEK 2: Aptitude Module Backend**

**This Week Does NOT Exist in Agent Plan — Create from Blueprint**

**Tasks:**

1. **NEW:** BUG-03 — Move quiz from static file to database
   - Create `backend/apps/aptitude/models.py` with:
     - `AptitudeTopic` model
     - `AptitudeQuestion` model
     - `QuizAttempt` model
   - Code fully provided in Blueprint Section 7.2

2. **NEW:** Create random questions API
   - File: `backend/apps/aptitude/views.py`
   - Endpoint: `GET /api/aptitude/questions/?topic_id=1&count=10`
   - Use `order_by('?')` for random selection (Django's ORDER BY RANDOM())
   - Do NOT return `correct_answer` field (only after submit)
   - Code in Blueprint Section 7.3

3. **NEW:** Create database seeder
   - File: `data_set/seed_aptitude.py`
   - Import 20+ topics from `aptitude_quiz.csv`
   - Populate AptitudeQuestion table
   - Run once: `python manage.py shell < seed_aptitude.py`
   - Code in Blueprint Section 7.4

4. **NEW:** Update Quiz.tsx to use API
   - File: `frontend/src/pages/Quiz.tsx`
   - Replace: `getQuestionsByTopicId(aptitudeData)` → API call
   - Fetch: `GET /api/aptitude/questions/?topic_id=X&count=10`

5. **NEW:** BUG-14 — Learning module (same structure)
   - Create `backend/apps/learning/models.py`
   - Create `backend/apps/learning/views.py` with topic API
   - Code in Blueprint Section 7 (extend aptitude pattern)

**Test:** Take quiz twice → questions are different each time. At least 40 questions in database.

---

### **WEEK 3: Custom Hooks Creation**

**Agent Plan Mentions Hooks But Doesn't Plan Their Creation — Do Both**

**Tasks:**

1. **NEW:** Create src/hooks/useTTS.ts
   - Fixes BUG-06 (Chrome pause-resume) + BUG-07 (voice load race)
   - Code fully provided in Blueprint Section 8.3.1
   - Includes: onvoiceschanged listener, 5s keep-alive interval

2. **NEW:** Create src/hooks/useSTT.ts
   - Fixes BUG-05 (replace MediaRecorder with Web Speech API)
   - Code fully provided in Blueprint Section 8.3.2
   - Includes: continuous mode, interim results, error handling

3. **NEW:** Create src/hooks/useSilenceDetector.ts
   - Fixes BUG-08 (3-second silence auto-advance)
   - Code fully provided in Blueprint Section 8.3.3
   - Includes: resetSilenceTimer, active state management

4. **NEW:** Create src/hooks/useInterviewSession.ts
   - Fixes BUG-09 (localStorage backup of answers)
   - Code fully provided in Blueprint Section 8.3.4
   - Includes: save/load session, save answers, recovery on refresh

**Test:** Each hook works independently. TTS reads text clearly. STT transcribes speech. Silence detection works.

---

### **WEEK 4: Interview Backend Redesign**

**Your Sprint 0 Backend Fixes + Interview-Specific Additions**

**Tasks:**

1. ✅ BUG-M1 — Fix answer_text AttributeError (already in Sprint 0)
2. ✅ Security fixes (already in Sprint 0)
3. ✅ Rate limiting, file validation (already in Sprint 0)

**NEW additions:** 4. **NEW:** Create submit-all endpoint (BUG-04)

- File: `backend/apps/interview/views.py`
- Function: `submit_all_answers(request)`
- Accept: ALL 8 Q&A pairs in single request
- Call Gemini ONCE with all answers (not 8 separate calls)
- Return: overall_score, placement_readiness, summary, recommendations
- Code fully provided in Blueprint Section 8.5

5. **NEW:** Update Gemini prompts
   - File: `backend/apps/interview/services/gemini_service.py`
   - Add: `generate_all_questions()` → generate 8 questions at once
   - Add: `evaluate_full_interview()` → holistic evaluation of all 8 answers
   - Prompts fully provided in Blueprint Section 8.6
   - Ensure: Scores returned as 0.0-10.0 (backend will display as 0-100)

6. ✅ Delete dead endpoints (already in Sprint 0)
   - Remove: `submit_answer`, `end_interview`, `transcribe_audio`
   - Remove: `whisper_service.py`

7. ✅ Delete openai_service.py, move to correct location (already in Sprint 0)

**Test:** POST /api/interview/submit-all/ accepts 8 answers. Network tab shows 1 API call only. Response includes holistic evaluation.

---

### **WEEK 5: Interview UI — Complete Redesign**

**Your Sprint 1 + Sprint 2 Combined + Interview-Specific UI**

**Tasks:**

1. ✅ BUG-C1 — Remove dual interview system (your Sprint 1)
2. ✅ BUG-C5 — Implement browserSupport.js (your Sprint 1)
3. ✅ BUG-H2 — Safe resume navigation (your Sprint 1)
4. ✅ Remove hardcoded URLs (your Sprint 1)
5. ✅ BUG-M2 — Fix stale closure (your Sprint 2)
6. ✅ BUG-H3 — Voice load race condition (your Sprint 2)
7. ✅ BUG-H4 — Recognition reset (your Sprint 2)

**NEW additions:** 8. **CRITICAL:** Rewrite InterviewSession.tsx (NOT delete)

- File: `frontend/src/pages/InterviewSession.tsx` (keep file, rewrite contents)
- Implement 11-phase state machine:
  - BROWSER_CHECK, MIC_PERMISSION, LOADING_QUESTIONS, PRE_BRIEF
  - SPEAKING, COUNTDOWN, RECORDING, SAVING_ANSWER
  - REVIEW, SUBMITTING, RESULTS, ERROR
- Wire in all 4 hooks from Week 3
- Handle session recovery on refresh from localStorage
- Code fully provided in Blueprint Section 8.4

9. **NEW:** Create missing interview components:
   - `src/components/interview/BrowserCheck.tsx`
   - `src/components/interview/MicPermission.tsx`
   - `src/components/interview/PreBrief.tsx`
   - `src/components/interview/QuestionCard.tsx`
   - `src/components/interview/AnswerReview.tsx`
   - `src/components/interview/CountdownTimer.tsx`
   - `src/components/interview/LoadingScreen.tsx`
   - Specifications in Blueprint Section 8.3 and referenced in flow diagram

**Test:** Complete voice interview flow:

- Browser detects Web Speech API ✓
- Microphone permission request ✓
- Question reads aloud via TTS ✓
- 2-second countdown ✓
- User speaks, live transcript appears ✓
- 3 seconds silence → auto-advance ✓
- Answer saved to localStorage ✓
- All 8 Q&A pairs shown in review ✓
- Submit button sends all answers to /submit-all/ ✓

---

### **WEEK 6: Results Page + PDF Report**

**Your Sprint 3 Polish + Results Page**

**Tasks:**

1. ✅ BUG-C2 — Fix pdfGenerator.js signature (your Sprint 3)
2. ✅ BUG-M3 — PDF target ID verification (your Sprint 3)
3. ✅ BUG-L1 — Unify token storage (move to Week 1)

**NEW additions:** 4. **NEW:** Create PDF Generator

- File: `frontend/src/utils/pdfGenerator.ts`
- Use: jsPDF + html2canvas
- Install: `npm install jspdf html2canvas`
- Capture: `#interview-report-pdf` div
- Code fully provided in Blueprint (referenced in Week 6)

5. **NEW:** Create Results Components:
   - `src/components/results/ScoreGauge.tsx` (circular score display)
   - `src/components/results/QuestionFeedbackCard.tsx` (per-question breakdown)
   - `src/components/results/ReportTemplate.tsx` (full report layout with id="interview-report-pdf")

6. **NEW:** Create InterviewResults.tsx page
   - File: `frontend/src/pages/InterviewResults.tsx`
   - Display: overall_score, placement_readiness, summary
   - Display: all 8 Q&A pairs with individual feedback
   - Display: strengths, weaknesses, recommendations
   - Button: Download PDF

**Test:** Results page loads after interview. PDF downloads with all Q&A pairs and feedback. File opens correctly in PDF reader.

---

### **WEEK 7: Dashboard + Full System Integration**

**This Entire Week Does NOT Exist in Agent Plan — Create from Blueprint**

**Tasks:**

1. **NEW:** Connect Dashboard to Real APIs
   - File: `frontend/src/components/dashboard/DashboardHome.tsx`
   - Fetch: `GET /api/interview/stats/` → get total_interviews, average_score, best_score, by_type
   - Fetch: `GET /api/interview/history/` → get recent sessions
   - Fetch: `GET /aptitude/history/` → get aptitude scores per topic
   - Replace all hardcoded numbers with real API data

2. **NEW:** Add Score Trend Chart
   - Use Recharts (already in package.json)
   - Chart: Line chart of interview scores over time
   - Chart: Bar chart of scores by interview type

3. **NEW:** Implement Dashboard Endpoints (if not already exist)
   - File: `backend/apps/interview/views.py`
   - Endpoint: `GET /api/interview/stats/` → returns aggregate stats
   - Endpoint: `GET /api/interview/history/?page=1&page_size=10` → paginated sessions
   - Specifications in Blueprint Section 9.1

4. **NEW:** BUG-16 — Fix score scale consistency
   - Ensure backend returns scores 0-100 (or 0-10 and multiply by 10 at frontend)
   - Dashboard displays scores consistently
   - Code in Blueprint Section 16

5. **NEW:** Final Integration Testing
   - Test complete user journey: Register → Upload Resume → Interview → Results → Dashboard
   - Verify all 16 bugs are fixed
   - Check all test cases pass

**Test:** Dashboard shows real user statistics. Score trend chart updates after each interview. All numbers are accurate.

---

## Quick Checklist: What Agent MUST Do

### ✅ KEEP from Agent Plan

- Sprint 0 backend security fixes
- Sprint 0 gemini version upgrade
- Sprint 1 routing improvements
- Sprint 2 voice quality fixes
- Sprint 3 polish work

### ❌ REMOVE from Agent Plan

- **Do NOT delete InterviewSession.tsx** — rewrite it instead

### ➕ ADD to Agent Plan

- **Week 1:** Auth fixes (BUG-01, BUG-02, BUG-11, BUG-12)
- **Week 2:** Full Aptitude module creation (BUG-03, BUG-14, BUG-15)
- **Week 3:** Create all 4 custom hooks from scratch
- **Week 4:** Add Gemini prompts and submit-all endpoint details
- **Week 6:** Full Results page and PDF implementation
- **Week 7:** Dashboard with real APIs (BUG-16)

---

## How to Instruct Agent with This Document

**When giving agent these instructions, say:**

```
"You have created a good 4-sprint plan for the Interview module.
However, the complete project has 5 modules and 16 bugs.

Your plan covers only the Interview module (Sprints 0-3).
You must EXPAND to cover ALL 5 modules across 7 weeks.

I'm providing you a CORRECTED PLAN that integrates your work
with the missing modules.

Follow this plan EXACTLY:
- Keep your Sprint 0, 1, 2, 3 work AS-IS
- Expand to Weeks 1-7 as specified
- Do NOT delete InterviewSession.tsx, rewrite it instead
- Create all 4 hooks from scratch in Week 3
- Add full Aptitude backend in Week 2
- Add Dashboard real APIs in Week 7

All code is provided in the blueprint (Section references given).
Test after each week before moving to next week."
```

---

## Files to Reference When Instructing Agent

| Week | Key Files in Blueprint                                |
| ---- | ----------------------------------------------------- |
| 1    | Section 6 (Auth), Section 10 (Environment)            |
| 2    | Section 7 (Aptitude & Learning)                       |
| 3    | Section 8.3 (All 4 hooks)                             |
| 4    | Section 8.5 (Backend), Section 8.6 (Gemini prompts)   |
| 5    | Section 8.4 (State machine), Section 8.3 (Components) |
| 6    | Section 11 Week 6, PDF references                     |
| 7    | Section 9 (Dashboard), Section 11 Week 7              |

---

This document is your instruction template for the agent.
Use it directly or adapt it to your specific agent interface.
