Okay, this is a valuable exercise. By combining the structured plan (PRD, Task List) with the practical execution (chat history), we can create a powerful guide for future AI assistants working on this specific codebase.

Here is the distilled guide:

---

**Guide for AI Assistants: Adding New Features/Pages to This Website**

**Version:** 1.0
**Date:** 2024-07-26

**1. Purpose**

This document provides guidelines and best practices for AI assistants tasked with adding new features or pages to this website. Its goal is to ensure consistency, maintainability, and efficient development by leveraging existing patterns and structures identified during the implementation of the "Explain Like I'm \_\_\_\_" feature.

**2. General Workflow & Approach**

- **Primacy of PRD & Task List:** Always start with the provided Product Requirements Document (PRD) and the Step-by-Step Task List. These documents outline the specific requirements and intended implementation sequence.
- **Sequential Task Execution:** Process tasks one by one as outlined in the task list.
- **Update Work Tracker:** After successfully completing each task (or sub-task if granular), update the corresponding checkbox in the `work-tracker.md` file.
- **Frequent Check-ins:** Check in with the user after completing each numbered task in the list. This allows for course correction and feedback.
- **Codebase Analysis:** Before implementing, briefly search the codebase for existing components, services, or patterns relevant to the current task (e.g., using `shadcn/ui` components, API service structure, backend blueprint patterns).
- **PRD Synchronization:** If necessary deviations from the PRD occur (e.g., due to technical constraints or user clarification), **notify the user** and, if instructed, update the PRD to reflect the actual implementation.

**3. Frontend Development Considerations (React / Vite)**

- **3.1. Routing & Page Structure:**
  - New pages typically reside in `/frontend/src/pages/`.
  - Use `React.lazy()` for new page components in `/frontend/src/App.tsx` for code splitting.
  - Add new routes within the main `<Routes>` block in `/frontend/src/App.tsx`.
  - Determine if the route needs protection via `/frontend/src/components/PrivateRoute.tsx` based on PRD requirements (check if user authentication is needed). Public pages are added directly to `<Routes>`.
- **3.2. UI Components (`shadcn/ui` & Tailwind):**
  - **Leverage Existing Library:** Heavily utilize the pre-installed `shadcn/ui` components located in `/frontend/src/components/ui/`. Check this directory first for needed elements (e.g., `Button`, `Input`, `Card`, `Skeleton`, `Dialog`, `Toast`, `Alert`).
  - **Styling:** Use Tailwind CSS utility classes exclusively for styling. Maintain visual consistency by referencing the styles of existing pages like `/frontend/src/pages/Landing.tsx` or components within `/frontend/src/autodraft/`. Refer to `/frontend/src/index.css` for base styles and theme variables.
  - **Responsiveness:** Implement responsive design using Tailwind's modifiers (`sm:`, `md:`, `lg:`, etc.). Ensure layouts adapt gracefully (e.g., multi-column grids stacking to single column on mobile).
- **3.3. State Management:**
  - For simple component state, use React's `useState` hook (ref: `ExplainPage.tsx`, `Entry.tsx`).
  - For more complex, shared state within a feature, consider using React Context (`useContext`) similar to the pattern in `/frontend/src/autodraft/WorkContext.tsx`.
- **3.4. API Integration:**
  - **Service Location:** Create feature-specific API service files under `/frontend/src/[feature_name]/services/api.tsx` (e.g., `/frontend/src/explain/services/api.tsx`). Avoid adding unrelated services to `/frontend/src/autodraft/services/api.tsx`.
  - **Axios Instance:** **Use the shared `axiosInstance`** located at `/frontend/src/autodraft/utils/axiosInstance.tsx`. This ensures consistent base URLs, credential handling, and importantly, the established request/response interceptors (like the 401 handler). _Do not create new, feature-specific Axios instances unless explicitly justified._
  - **Type Safety:** Define TypeScript interfaces for API request payloads and response structures within the service file.
- **3.5. Error Handling (UI):**
  - **General API/Server Errors:** Use the `useToast` hook (`/frontend/src/hooks/use-toast.ts`) to display non-blocking notifications for errors like 5xx or network issues. Ensure the `Toaster` component (`/frontend/src/components/ui/toaster.tsx`) is rendered in `App.tsx`. Use `variant: "destructive"`.
  - **Input Validation Errors:** Display simple, inline error messages directly near the input fields (e.g., a `<p>` tag with `text-destructive` class).
  - **Specific Inline Errors:** For errors related to a specific part of the UI (if applicable, e.g., one of multiple items failing to load), use the `Alert` component (`/frontend/src/components/ui/alert.tsx`) with `variant="destructive"`.
- **3.6. Loading States:**
  - Use boolean flags (e.g., `isLoading`) in state to control UI feedback.
  - Disable buttons/inputs during loading states.
  - Display loading indicators clearly. Good options include:
    - The `Skeleton` component (`/frontend/src/components/ui/skeleton.tsx`) for text/content placeholders.
    - Spinners like `Loader2` from `lucide-react` (used in `ReportEditor.tsx`).
  - Accompany indicators with user-friendly text (e.g., "Loading...", "Processing...").

**4. Backend Development Considerations (Flask)**

- **4.1. Structure & Blueprints:**
  - Organize routes by feature using Flask Blueprints. Create a new directory `/backend/[feature_name]/` and a `routes.py` file within it (e.g., `/backend/explain/routes.py`).
  - Define the blueprint in `routes.py` using a feature-specific name and URL prefix (e.g., `explain_bp = Blueprint("explain", __name__, url_prefix="/explain")`).
  - Register the new blueprint within the main `api_bp` in `/backend/__init__.py`.
- **4.2. Routing & Authentication:**
  - Define routes within the blueprint file using decorators (e.g., `@explain_bp.route("/", methods=["POST"])`).
  - Specify HTTP methods (`methods=["GET", "POST"]`).
  - Apply `@jwt_required()` decorator (imported from `flask_jwt_extended`) to routes requiring user authentication. Public routes should omit this decorator. Reference `backend/routes.py` and `backend/speech/routes.py` for examples.
- **4.3. Request Handling & Validation:**
  - Use `request.get_json()` to parse incoming JSON data. Handle cases where data might be missing or not JSON.
  - Perform **rigorous validation** on all input parameters (check for existence, correct type, non-emptiness, length constraints, valid values).
  - Log validation steps and failures (`logger.warning`).
- **4.4. Error Handling & Responses:**
  - **Standard Format:** Return JSON responses consistently. For errors, use the established format: `jsonify({"success": False, "error": {"message": "Specific error message", "details": "Optional further details"}}), HTTP_STATUS_CODE`. Reference examples in `poppy_bp`, `speech_bp`, `explain_bp`.
  - **Status Codes:** Use appropriate HTTP status codes (e.g., 400 for bad requests/validation errors, 401 for unauthorized, 404 for not found, 500 for internal server errors, 503 for service unavailable).
  - **Logging:** Log errors comprehensively using `logger.error(..., exc_info=True)` within `except` blocks.
- **4.5. Configuration & Secrets:**
  - Access configuration values (like API keys) securely via `current_app.config.get('CONFIG_KEY')`.
  - Define these keys in `/backend/config.py` and load them from environment variables (`.env` file or OS environment). **Never hardcode secrets.**
- **4.6. Logging:**
  - Import and use the logger configured in `/backend/extensions.py`: `from backend.extensions import create_logger; logger = create_logger(__name__)`.
  - Log key events: request received (`INFO`), processing steps (`DEBUG`), validation failures (`WARNING`), errors (`ERROR`).
- **4.7. LLM/External Service Integration:**
  - Check for existing utilities or clients first (e.g., `/backend/speech/openai_client.py`, `/backend/openai_utils.py`).
  - Initialize clients using API keys from `current_app.config`.
  - Wrap external API calls in `try...except` blocks, handling potential API errors, network issues, and parsing problems. Log interactions and errors.
- **4.8. Database Interaction (If Required):**
  - If the feature requires database interaction, define models in a `models.py` within the feature directory (e.g., `/backend/[feature_name]/models.py`) or use/extend shared models from `/backend/models.py`.
  - Use SQLAlchemy patterns established in the project (ref: `backend/autodraft/models.py`, `backend/speech/models.py`).
  - Import `db` from `/backend/extensions.py`.
  - Interact with the database within route functions or dedicated service functions. Use sessions (`db.session.add()`, `db.session.commit()`, `db.session.rollback()`).

**5. Key Files & Directories to Reference**

- `/frontend/src/components/ui/`: Core `shadcn/ui` components.
- `/frontend/src/App.tsx`: Routing setup.
- `/frontend/src/services/api.tsx` (Pattern): Location for feature-specific API services.
- `/frontend/src/autodraft/utils/axiosInstance.tsx`: Shared Axios instance **to be used**.
- `/frontend/src/hooks/use-toast.ts`: For frontend notifications.
- `/frontend/src/index.css`: Tailwind base/theme configuration.
- `/backend/__init__.py`: Blueprint registration.
- `/backend/config.py`: Configuration loading.
- `/backend/extensions.py`: Shared extensions (logger, db, jwt).
- `/backend/models.py`: Shared database models.
- `/backend/[feature_name]/routes.py` (Pattern): Feature-specific backend routes.
- `/backend/speech/openai_client.py` (Example): OpenAI integration pattern.
- `/backend/sidequest/` (Reference): Complete SideQuest backend implementation example.

**6. SideQuest Backend Implementation Reference**

The SideQuest backend (`/backend/sidequest/`) serves as a comprehensive example of implementing a complete feature backend following the patterns outlined in this guide:

**Key Implementation Highlights:**

- **Blueprint Architecture**: Clean separation with `sidequest_bp` registered in main app
- **Service Layer Pattern**: Business logic separated into dedicated service classes
- **Database Models**: Comprehensive models with proper relationships and JSON fields
- **External API Integration**: OpenAI integration with robust fallback systems
- **Error Handling**: Comprehensive validation and error responses
- **Authentication**: JWT-based protection for all user-specific endpoints
- **Logging**: Detailed logging for debugging and monitoring

**Reference Files:**

- `/backend/sidequest/models.py`: Database models and enums
- `/backend/sidequest/services.py`: Business logic and external API integration
- `/backend/sidequest/routes.py`: REST API endpoints and request handling
- `/backend/sidequest/__init__.py`: Package initialization and exports

**7. Final Checklist Before Completing Feature**

- Does the implementation meet all requirements in the PRD?
- Is the work tracker fully updated and accurate?
- Is the code consistent with the patterns outlined in this guide?
- Has frontend responsiveness been tested?
- Has backend validation and error handling been thoroughly implemented?
- Is logging sufficient for debugging and monitoring?
- Are secrets handled securely?
- Have unnecessary console logs or debugging statements been removed?

By following these guidelines, you can contribute effectively and consistently to the development of this website. Remember to prioritize clarity, reuse existing patterns, and communicate frequently.

---
