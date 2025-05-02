Product Requirements Document: "Explain Like I'm \_\_\_\_" Feature

Version: 1.1
Date: 2024-07-26
Author: AI Assistant (based on user input and code review)

1. Introduction

1.1. Overview: This document specifies the requirements for a new single-page feature, "Explain Like I'm \_\_\_\_", integrated into the existing website. This feature leverages a Large Language Model (LLM) to generate explanations of user-provided topics at four distinct complexity levels.

1.2. Goal: To deliver an engaging, visually satisfying, and informative tool that enhances user understanding of various concepts by presenting information at multiple depths. This feature aims to seamlessly integrate with the current technology stack and design system.

1.3. Target Audience: General website visitors interested in learning or clarifying concepts.

1.4. Core Technologies: React (Vite), Flask, Supabase/Postgres, shadcn/ui, Tailwind CSS, Axios, LLM (e.g., Gemini/OpenAI).

2. Goals

Develop a user-friendly frontend page for topic submission and asynchronous display of explanations.

Create a reliable backend endpoint to process requests, interact securely with an LLM, and return structured explanations.

Visually render four explanations concurrently in distinct columns, providing immediate feedback and a dynamic feel.

Ensure technical and visual consistency with the existing codebase, leveraging established components and patterns (e.g., UI elements from /frontend/src/components/ui/, API structure from /frontend/src/autodraft/services/api.tsx, backend patterns from /backend/routes.py).

Implement clear loading states and user-friendly error handling, mirroring patterns like those in /frontend/src/hooks/use-toast.ts and /frontend/src/components/ui/alert.tsx.

3. User Stories

As a user, I want to type a concept into an input field and click a button to trigger the explanation process.

As a user, I expect to see the explanation presented in four clearly labeled columns, representing increasing complexity ("Curious Child", "Student", "Professional", "World-Class Expert").

As a user, I want to understand how the concept builds, so each explanation level should logically follow from the previous one.

As a user, I want a responsive experience, so I expect all four explanations to start generating simultaneously and appear in their columns as soon as they are ready.

As a user, I need visual feedback, so I want to see distinct loading indicators (e.g., spinners or skeletons with fun text) in each column during generation.

As a user, I appreciate consistency, so the page's look and feel should match the established design language of the site (ref: Landing.tsx, Autodraft components).

As a user, I need to know if something goes wrong, so I expect clear, non-disruptive error messages if any part of the process fails.

4. Functional Requirements

4.1. Frontend (React / Vite)

4.1.1. Component & Routing:

Implementation: Create a new page component at /frontend/src/pages/ExplainPage.tsx.

Routing: Add a route for /explain within the main <Routes> block in /frontend/src/App.tsx. Ensure it's publicly accessible (no PrivateRoute wrapper needed for V1). Reference routing setup in App.tsx.

4.1.2. User Input & Initiation:

Component: Utilize /frontend/src/components/ui/input.tsx for the topic input field.

Component: Utilize /frontend/src/components/ui/button.tsx for the submission button (label: "Explain It!").

Styling: Apply Tailwind classes to make these elements "fun and appealing," consistent with the site's aesthetic (ref: Landing.tsx styles).

Interaction: On button click:

Validate input (non-empty). Show a simple inline message if empty.

Disable input and button.

Call the API service function (see 4.1.5).

Reset explanation states and set loading states to true.

4.1.3. Layout & Display:

Structure: Use a main div container with Tailwind CSS for overall page layout.

Columns: Implement a 4-column layout using Flexbox or Grid. Reference existing responsive grid layouts (e.g., DataEditor.tsx, Games.tsx).

Column Headers: Each column requires a title: "Curious Child", "Student", "Professional", "World-Class Expert". Use appropriate text components (e.g., h3 or CardTitle).

Content Area: Use /frontend/src/components/ui/card.tsx (Card, CardHeader, CardContent) within each column to frame the title and the explanation or loading state. Ensure consistent padding and styling.

4.1.4. Asynchronous Loading & State Management:

State: Employ useState hooks (similar to Entry.tsx or ReportEditor.tsx) to manage: topic, isLoading, explanations (object with keys child, student, etc.), errors (object mapping levels to error messages, plus a global error). Consider useReducer if state logic becomes complex.

Loading Indicators: When isLoading is true for a specific level, display a loading indicator within its CardContent.

Use /frontend/src/components/ui/skeleton.tsx for text placeholders or a themed spinner (e.g., Loader2 from lucide-react as seen in ReportEditor.tsx).

Include a fun, context-specific message (e.g., "Thinking like a child...", "Consulting the experts...").

Updating Content: As explanations arrive from the backend, update the corresponding state and replace the loader with the text content. Re-enable input/button upon completion or final error.

4.1.5. API Integration:

Service Function: Define getExplanations(topic: string) in /frontend/src/autodraft/services/api.tsx (or a new more general file like /frontend/src/services/api.tsx).

Axios: Utilize the configured axiosInstance from /frontend/src/autodraft/utils/axiosInstance.tsx. Note: While this instance handles auth, the /api/explain endpoint itself will be public on the backend.

Request: Perform a POST request to /api/explain with the { topic } payload.

Response Handling: Process the JSON response (success or error) and update component state accordingly.

4.1.6. Error Handling (UI):

General Errors: For network errors or 5xx responses from the backend, use the toast function from /frontend/src/hooks/use-toast.ts (ensure Toaster from /frontend/src/components/ui/toaster.tsx is included in App.tsx). Example: toast({ title: "Error", description: "Could not fetch explanations.", variant: "destructive" });

Partial/Specific Errors: If the backend indicates failure for specific levels (V1 treats any backend issue as full failure, but for future): Use /frontend/src/components/ui/alert.tsx with variant="destructive" inside the relevant column's CardContent.

Input Errors: Display simple text validation messages near the input field for empty submissions.

4.1.7. Styling & Responsiveness:

Consistency: Strictly adhere to the Tailwind CSS configuration and theme variables defined in /frontend/src/index.css and managed by /frontend/src/components/theme-provider.tsx.

Responsiveness: Ensure columns stack vertically on smaller screens (e.g., using Tailwind's sm:, md:, lg: prefixes for grid/flex properties). Test on various screen sizes.

4.2. Backend (Flask)

4.2.1. API Endpoint:

Blueprint: Create a new Blueprint (e.g., tools_bp in a new backend/tools/routes.py) or add to an existing general-purpose one. Register it in backend/**init**.py. Follow the pattern of poppy_bp, speech_bp, autodraft_bp.

Route: Define POST /api/explain. Example: @tools_bp.route("/explain", methods=["POST"]).

Authentication: This endpoint should NOT use @jwt_required(). It is public.

4.2.2. Request Handling & Validation:

Parsing: Use request.get_json() to get the { "topic": "string" } payload.

Validation: Check if topic exists, is a non-empty string, and meets a reasonable length limit (e.g., 500 characters).

Error Response (Validation): If validation fails, return a 400 Bad Request using a consistent JSON structure. Reference poppy_bp error format: return jsonify({"success": False, "error": {"message": "Topic is required and cannot be empty."}}), 400.

Logging: Log incoming requests using the pattern from extensions.py: logger.info(f"Explain request received for topic: {topic}").

4.2.3. LLM Integration:

API Keys: Retrieve the LLM API key securely using current_app.config['LLM_API_KEY'] (defined via environment variables, similar to STRIPE_SECRET_KEY or MAIL_PASSWORD in config.py).

Prompting: Construct the detailed prompt as defined in Section 5.

LLM Client: Use the appropriate Python library (e.g., google-generativeai, openai). Use async/await if available and beneficial for non-blocking IO.

Error Handling (LLM Call): Wrap the LLM API call in a try...except block. Catch specific exceptions from the LLM library (e.g., API errors, connection errors, content safety flags). Log errors using logger.error.

4.2.4. Response Generation:

Parsing LLM Output: Extract the four explanations from the LLM's structured response. Handle potential parsing errors if the LLM doesn't adhere to the requested format.

Success Response: If successful, return a 200 OK with JSON:

{
"success": true,
"data": {
"explanations": {
"child": "...",
"student": "...",
"professional": "...",
"expert": "..."
}
}
}

Error Response (LLM/Internal): If the LLM call fails or any other internal error occurs, return a 500 Internal Server Error or 503 Service Unavailable. Use the consistent error format: return jsonify({"success": False, "error": {"message": "Failed to generate explanations due to LLM error."}}), 500. Log the detailed error internally. Decision for V1: Treat any LLM generation issue (partial or full) as a complete failure for this API call.

4.2.5. Logging: Employ detailed logging using the logger instance (create_logger from backend/extensions.py) for:

Request received (logger.info).

Validation success/failure (logger.debug/logger.warning).

LLM interaction start/end/success (logger.debug).

Errors encountered (LLM API, internal processing) (logger.error with exc_info=True where appropriate). (Ref: poppy_bp, speech_bp).

4.3. Database (Supabase/Postgres)

4.3.1. Usage: No database interaction is required for Version 1.0 of this feature. Explanations are ephemeral.

5. LLM Prompt Design

5.1. Goal: Generate four distinct, increasingly complex explanations for {topic}, where each level explicitly builds on the previous, returned in a structured JSON format.

5.2. Levels/Personas: "Curious Child", "Student", "Professional", "World-Class Expert" (definitions as per V1.0).

5.3. Core Prompt Instructions:

You are an expert educational AI assistant. Your task is to explain the topic "{topic}" at four specific levels of complexity, ensuring each level builds directly upon the concepts and language of the preceding level.

Your response MUST be a single JSON object containing ONLY the following keys: "child", "student", "professional", "expert". The value for each key should be the corresponding explanation string.

Target Audience Levels & Requirements:

1.  **child**: Explain like I'm a curious 5-8 year old. Use very simple terms, analogies, short sentences. Avoid jargon.
2.  **student**: Explain like I'm a high school or early college student. Assume understanding of the 'child' explanation. Introduce fundamental technical terms clearly. Build upon the child explanation.
3.  **professional**: Explain like I'm a professional working in a related field (but not necessarily an expert in _this_ topic). Assume understanding of the 'student' explanation. Use standard industry terminology. Focus on practical applications, mechanisms, or nuances. Build upon the student explanation.
4.  **expert**: Explain like I'm a world-class expert specializing in this field. Assume mastery of the 'professional' explanation. Be highly technical, precise, and discuss advanced concepts, complexities, limitations, or research frontiers. Build directly upon the professional explanation.

Tone: Informative, clear, engaging, and appropriate for each defined level.
Accuracy: Ensure factual correctness.
Safety: Avoid harmful, biased, or inappropriate content.

Generate the JSON response for the topic: "{topic}"
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
IGNORE_WHEN_COPYING_END

5.4. LLM Choice: Configurable via environment variable (LLM_PROVIDER, LLM_API_KEY), defaulting to Gemini Pro unless specified otherwise.

6. Visual Design & User Interface (UI/UX)

Consistency: Adhere strictly to the established design system (shadcn/ui, Tailwind theme). Reference components in /frontend/src/components/ui/ and general page layouts (Landing.tsx, Autodraft).

Engagement: Input field and button styling should invite interaction.

Feedback: Loading states must be unambiguous using Skeleton or themed spinners with level-specific text cues. Error states should be clear using Toast or inline Alert components.

Readability: Optimize text display within CardContent for comfortable reading (font, size, line-height, contrast).

Responsiveness: Implement fluid transitions from 4-column (desktop) to stacked 1-column (mobile) layouts using Tailwind's responsive modifiers.

7. Non-Functional Requirements

7.1. Performance: UI responsiveness during async operations is key. Aim for perceived completion (first explanations appearing) quickly, with full results within 10-15s (LLM dependent).

7.2. Security: Backend must protect LLM API keys. Basic input validation on backend.

7.3. Scalability: Backend endpoint should handle moderate concurrent load. Consider LLM rate limits.

7.4. Maintainability: Code should follow existing project structure and conventions (React hooks/context, Flask Blueprints, SQLAlchemy patterns (even if not used here), logging, error handling). Use TypeScript effectively.

8. Error Handling Strategy (Refined)

Frontend:

Input Validation: Inline text near input.

API Errors (5xx, Network): useToast hook -> Toast component (destructive variant).

API Errors (4xx Client Error, e.g., bad input reported by backend): useToast or inline Alert.

Partial/Specific Errors (Future): Inline Alert component within the affected column.

Backend:

Input Validation (400): jsonify({"success": False, "error": {"message": "..."}}), 400

LLM/Internal Errors (500/503): jsonify({"success": False, "error": {"message": "..."}}), 50x. Log details internally using logger.error(..., exc_info=True).

9. Out of Scope (Version 1.0)

(Same as Version 1.0: No auth for this page, no saving/history, no sharing, no editing, no follow-ups, no advanced animations, no user model selection, no caching).

10. Future Considerations

Backend caching layer (e.g., Redis) for common topics.

User authentication & history.

Copy-to-clipboard buttons for each explanation.

Sharing functionality.

User-defined personas.

LLM model selection dropdown.

Integration with billing system (UserBalance, Transaction models) if usage costs become significant or feature becomes premium. Monitor TransactionType.USAGE and SpeechOperation enums for potential patterns.

11. Open Questions

Confirm default LLM choice (Assume Gemini Pro).

12. Technical Integration Notes & References

Frontend:

Routing: /frontend/src/App.tsx

API Service: /frontend/src/autodraft/services/api.tsx (or new /frontend/src/services/api.tsx)

Axios Instance: /frontend/src/autodraft/utils/axiosInstance.tsx

UI Components: /frontend/src/components/ui/ (Card, Button, Input, Alert, Skeleton, Toast, etc.)

Styling: /frontend/src/index.css, /frontend/src/components/theme-provider.tsx, Tailwind CSS.

State Management: React Hooks (useState, useReducer), inspired by /frontend/src/autodraft/WorkContext.tsx.

Error Toasts: /frontend/src/hooks/use-toast.ts, /frontend/src/components/ui/toaster.tsx

Backend:

Routing/Blueprints: /backend/routes.py, /backend/**init**.py (follow patterns of poppy_bp, speech_bp).

Configuration: /backend/config.py (for LLM keys via current_app.config).

Logging: /backend/extensions.py (create_logger), used in routes.py, poppy_bp, etc.

JSON Responses: Follow structure used in poppy_bp, speech_bp for consistency, especially for errors.

LLM Client Libs: google-generativeai / openai.

Models (Reference Only): /backend/models.py, /backend/autodraft/models.py, /backend/speech/models.py, /backend/PoppyTracker/models.py (Understand existing data structures, even if not used here).

Database: No direct interaction for V1.
