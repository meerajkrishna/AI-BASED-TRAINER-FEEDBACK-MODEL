# AI Interview Module — Ultimate Implementation Plan

This plan comprehensively merges the official **AI Interview Implementation Guide PDF** (14 bugs) with the **Agent Code Audit** (security flaws, scaling issues, legacy cleanup). It is structured into **4 Sprints** to minimize errors and ensure functional dependencies are fixed in the correct order.

## Sprint 0: Critical Backend Unblock & Security

These tasks must be done first to ensure the backend server can start and process data without crashing.

### 1. BUG-C3: Move [openai_service.py](file:///p:/mega_project/ai-trainer/backend/services/openai_service.py)
The service import currently crashes Django.
* **Action:** Move [backend/services/openai_service.py](file:///p:/mega_project/ai-trainer/backend/services/openai_service.py) to `backend/apps/interview/services/`.
* **Action:** Update import in [backend/apps/interview/views.py](file:///p:/mega_project/ai-trainer/backend/apps/interview/views.py):
  ```python
  from .services.openai_service import generate_questions, evaluate_interview
  ```
* **Action:** Ensure [backend/apps/interview/services/__init__.py](file:///p:/mega_project/ai-trainer/backend/apps/interview/services/__init__.py) exists.

### 2. BUG-C4: Update `google-generativeai`
* **Action:** In [backend/requirements.txt](file:///p:/mega_project/ai-trainer/backend/requirements.txt), replace `google-generativeai==0.3.0` with `google-generativeai>=0.8.0`.
* **Action:** Instruct user to run `pip install --upgrade google-generativeai`.

### 3. BUG-M1: Fix `answer_text` bug in [submit_all](file:///p:/mega_project/ai-trainer/backend/apps/interview/views.py#601-738)
The [views.py](file:///p:/mega_project/ai-trainer/backend/apps/interview/views.py) [submit_all](file:///p:/mega_project/ai-trainer/backend/apps/interview/views.py#601-738) view crashes because `question.answer_text` does not exist on the [InterviewQuestion](file:///p:/mega_project/ai-trainer/backend/apps/interview/models.py#135-188) model.
* **Action:** Modify [views.py](file:///p:/mega_project/ai-trainer/backend/apps/interview/views.py) inside [submit_all](file:///p:/mega_project/ai-trainer/backend/apps/interview/views.py#601-738):
  ```python
  # Build index of submitted answers
  answers_by_index = {
      i: ans.get('answerText', ans.get('answer_text', '[No answer provided]'))
      for i, ans in enumerate(answers, start=1)
  }
  
  # When saving the InterviewAnswer object:
  'answer_text': answers_by_index.get(q_index, '[No answer provided]'),
  ```

### 4. Code Audit Backend Fixes (Robustness & Security)
* **Action:** In [views.py](file:///p:/mega_project/ai-trainer/backend/apps/interview/views.py) [start_interview](file:///p:/mega_project/ai-trainer/backend/apps/interview/views.py#118-219), change `total_questions=8` to `total_questions=len(raw_questions)`.
* **Action:** In [views.py](file:///p:/mega_project/ai-trainer/backend/apps/interview/views.py), harden pagination parsing to prevent `ValueError` crashes.
* **Action:** In [models.py](file:///p:/mega_project/ai-trainer/backend/apps/interview/models.py), add [('abandoned', 'Abandoned')](file:///p:/mega_project/ai-trainer/frontend/src/App.tsx#27-122) to `STATUS_CHOICES` for [InterviewSession](file:///p:/mega_project/ai-trainer/frontend/src/services/interviewAPI.ts#22-36).
* **Action:** In [serializers.py](file:///p:/mega_project/ai-trainer/backend/apps/interview/serializers.py) [validate_file](file:///p:/mega_project/ai-trainer/backend/apps/interview/serializers.py#20-32), ensure file size < 10MB and verify `content_type == 'application/pdf'` (not just [.pdf](file:///p:/mega_project/Plan_of_action/Copilot_Prompts_Guide.pdf) extension).
* **Action:** In [backend/.env](file:///p:/mega_project/ai-trainer/backend/.env), replace the hardcoded GEMINI_API_KEY with a placeholder string to secure the system.
* **Action:** In [settings.py](file:///p:/mega_project/ai-trainer/backend/ai_trainer/settings.py), add `DEFAULT_THROTTLE_CLASSES` (60/minute) for rate limiting AI endpoints.
* **Action:** Delete [backend/apps/interview/services/whisper_service.py](file:///p:/mega_project/ai-trainer/backend/apps/interview/services/whisper_service.py) entirely.
* **Action:** Delete dead endpoints ([submit_answer](file:///p:/mega_project/ai-trainer/backend/apps/interview/views.py#252-363), [end_interview](file:///p:/mega_project/ai-trainer/backend/apps/interview/views.py#365-450), [transcribe_audio](file:///p:/mega_project/ai-trainer/backend/apps/interview/views.py#568-595)) from [views.py](file:///p:/mega_project/ai-trainer/backend/apps/interview/views.py) and [urls.py](file:///p:/mega_project/ai-trainer/backend/apps/interview/urls.py).

---

## Sprint 1: Frontend Critical Routing & Flow

### 1. BUG-C1 & BUG-H2: Remove Dual Interview System
* **Action:** Delete [frontend/src/pages/InterviewSession.tsx](file:///p:/mega_project/ai-trainer/frontend/src/pages/InterviewSession.tsx) completely.
* **Action:** In [frontend/src/pages/AIInterviewLanding.tsx](file:///p:/mega_project/ai-trainer/frontend/src/pages/AIInterviewLanding.tsx), change navigation to point to the new system, passing the resumeId safely:
  ```typescript
  navigate('/interview', { state: { resumeId: resume?.id || selectedResumeId } });
  ```
* **Action:** In [frontend/src/App.tsx](file:///p:/mega_project/ai-trainer/frontend/src/App.tsx), remove the volatile [InterviewWrapper](file:///p:/mega_project/ai-trainer/frontend/src/App.tsx#21-26) function that relies on `localStorage`. Use `useLocation()` state directly, or just pass the component:
  ```tsx
  import { useLocation } from 'react-router-dom';
  // Define inline or route directly avoiding localStorage
  ```

### 2. BUG-C5: Implement `browserSupport.js`
* **Action:** Write the full browser support check script from PDF Section 4.3 into `frontend/src/utils/browserSupport.js` so that `BrowserCheck.jsx` doesn't throw a `ReferenceError`.

### 3. Audit FRONT-1 & FRONT-2: Double Scoring & URLs
* **Action:** In [frontend/src/pages/InterviewFeedback.tsx](file:///p:/mega_project/ai-trainer/frontend/src/pages/InterviewFeedback.tsx), remove the `* 10` multipliers on scores (backend already scales 0-10 up to 0-100).
* **Action:** In [frontend/src/services/interviewAPI.ts](file:///p:/mega_project/ai-trainer/frontend/src/services/interviewAPI.ts) and [api.ts](file:///p:/mega_project/ai-trainer/frontend/src/services/api.ts), replace `http://localhost:8000` with ``${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}``. (BUG-C6 is handled by deleting InterviewSession.tsx).

---

## Sprint 2: Voice Quality & State Fixes

### 1. BUG-M2: Stale Closure in [Interview.jsx](file:///p:/mega_project/ai-trainer/frontend/src/pages/Interview.jsx)
Silence detection fails to auto-advance because `handleSilence` closes over the initial React state.
* **Action:** In [Interview.jsx](file:///p:/mega_project/ai-trainer/frontend/src/pages/Interview.jsx), add a `phaseRef`:
  ```jsx
  const phaseRef = useRef(phase);
  useEffect(() => { phaseRef.current = phase; }, [phase]);
  // In handleSilence: 
  if (phaseRef.current === PHASES.RECORDING) { finalizeAnswer(); }
  ```

### 2. BUG-H3: Voices Load Race Condition in `useTTS.js`
Chrome doesn't load voices instantly, making the first question read with a robotic voice.
* **Action:** Wrap the `synth.current.speak(utter)` call in logic that checks if `getVoices().length > 0`. If not, hook into `onvoiceschanged` and apply a 2000ms timeout fallback. (Details in PDF 4.7).

### 3. BUG-H4: Recognition State Retry in `useSTT.js`
* **Action:** Export a `resetRecognition()` function from `useSTT.js` so [Interview.jsx](file:///p:/mega_project/ai-trainer/frontend/src/pages/Interview.jsx) / `MicPermission.jsx` can destroy and recreate the instance if the user later grants mic access after initially blocking it.

---

## Sprint 3: Polish & Validation

### 1. BUG-C2: `pdfGenerator.js` Signature
* **Action:** Update `frontend/src/utils/pdfGenerator.js` to accept the `results` object directly, and parse `candidateName` safely instead of crashing when replacing strings.

### 2. BUG-M3: PDF Target ID
* **Action:** In `frontend/src/components/results/ReportTemplate.jsx`, ensure the top-level element exactly matches `id="interview-report-pdf"`.

### 3. BUG-L1: `authStore.ts` Unification
* **Action:** Ensure [api.ts](file:///p:/mega_project/ai-trainer/frontend/src/services/api.ts) and `authStore.ts` read tokens from the exact same storage approach (preferentially Zustand persist).

### 4. Verification
* **Action:** Run end-to-end user journey in browser to ensure 100% stable phase transitions and precise Gemini-fed results.
