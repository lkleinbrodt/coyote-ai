Okay, I've analyzed your codebase structure, key files, and the "Guide for AI Assistants". Based on this, I've refined the PRD and Task List to be more specific and aligned with your established patterns.

Here are the key improvements:

- **Specific File Paths:** Updated paths for new components and services to match your structure (e.g., `/backend/email/routes.py`, `/frontend/src/pages/EmailAssistantPage.tsx`, `/frontend/src/email/services/api.ts`).
- **Component References:** Explicitly mentioned using specific `shadcn/ui` components found in your codebase (e.g., `Table`, `Checkbox`, `Button`, `Input`, `Skeleton`, `Toast`).
- **Shared Utilities:** Emphasized using the shared `axiosInstance` and `create_logger`.
- **Backend Patterns:** Reinforced using Flask Blueprints, `@jwt_required()`, and the established JSON error response format.
- **Frontend Patterns:** Reinforced using `React.lazy`, `PrivateRoute`, `useEffect`, `useState`, and `useToast`.
- **Gmail Auth:** Clarified that Gmail auth (credential/token handling) needs to happen server-side within the Flask endpoints.
- **Clarity:** Added minor clarifications based on existing code examples (e.g., state management suggestions, loading indicators like `Loader2`).

---

**Revised Project Plan: Email Assistant Page**

**1. Product Requirements Document (PRD) - v1.1**

- **1.1. Goal:** Create a new page (`/email-assistant`) within the existing React/Flask application to allow users to view, filter, and delete emails from their linked Gmail account.
- **1.2. Key Features:**
  - **New Page:** A dedicated, authenticated route `/email-assistant` in `/frontend/src/App.tsx` using `React.lazy()` with `/frontend/src/pages/EmailAssistantPage.tsx` and wrapped in `PrivateRoute`.
  - **Backend Endpoints (Flask):**
    - Create a new blueprint in `/backend/email/routes.py` with a `/api/email` URL prefix.
    - `/fetch` (GET): Retrieves a list of recent emails (e.g., latest 100) using the provided Python Gmail functions. Requires JWT authentication (`@jwt_required()`). Handles Gmail API authentication server-side using `credentials.json` and managing `token.json` on the server.
    - `/delete` (POST): Accepts a JSON payload `{"email_ids": ["id1", ...]}` and deletes them using the provided Python Gmail functions. Requires JWT authentication (`@jwt_required()`).
  - **Email Display:**
    - Show emails in a `shadcn/ui Table` component (ref: `/frontend/src/components/ui/table.tsx`).
    - Columns: Checkbox (for selection), Sender, Subject, Snippet.
    - Visually distinguish unread emails (e.g., bold text on the table row).
  - **Selection:**
    - Allow users to select individual emails via `shadcn/ui Checkbox` (ref: `/frontend/src/components/ui/checkbox.tsx`).
    - Provide a "Select All" checkbox in the table header.
    - Visually indicate selected rows (e.g., apply `bg-muted/50` style to `TableRow`).
  - **Filtering:**
    - Provide a `shadcn/ui Input` component (ref: `/frontend/src/components/ui/input.tsx`) to filter the _currently displayed_ email list by sender (client-side filtering).
  - **Deletion:**
    - A `shadcn/ui Button` (ref: `/frontend/src/components/ui/button.tsx`) labeled "Delete Selected", enabled only when emails are selected.
    - Triggers the `/api/email/delete` backend endpoint.
  - **User Feedback:**
    - Display loading states using `shadcn/ui Skeleton` components (ref: `/frontend/src/components/ui/skeleton.tsx`) while emails are being fetched.
    - Disable the deletion button during deletion and show a loading indicator (e.g., `Loader2` from `lucide-react` as seen in `ReportEditor.tsx`).
    - Use `useToast` hook (ref: `/frontend/src/hooks/use-toast.ts`) for success messages (e.g., "Emails deleted") and errors (e.g., "Failed to fetch emails", "Failed to delete emails"), ensuring the `Toaster` is rendered in `App.tsx`.
- **1.3. Backend Integration:**
  - Utilize the provided Python functions (`authenticate_gmail`, `get_emails`, `delete_emails`) within the Flask routes.
  - The Flask backend must manage the Gmail authentication flow server-side. `credentials.json` must be present on the server. `token.json` will be created/managed server-side (ensure it's stored appropriately, possibly outside version control if sensitive).
  - All backend routes for this feature must be protected using `@jwt_required()` and use the logger from `backend.extensions.create_logger`.
- **1.4. Frontend Design & UX:**
  - Use existing `shadcn/ui` components and Tailwind CSS for styling, maintaining consistency with the application's theme (`/frontend/src/index.css`).
  - Ensure basic responsiveness for the table and controls.
  - Filtering should provide instant feedback (client-side).
  - After successful deletion, the email list should automatically refresh.
- **1.5. Non-Functional Requirements:**
  - **Security:** JWT protection on backend routes. Secure handling of Gmail credentials/tokens _on the server_.
  - **Error Handling:** Graceful handling of API errors on both frontend (using `Toast`) and backend (returning standard JSON error format, ref: `speech/routes.py`).
  - **Performance:** Use loading indicators (`Skeleton`, button disabling, spinners) for asynchronous operations. Client-side filtering for responsiveness with the initial email list.

**2. Step-by-Step Task List - v1.1**

_(Instructions for AI: Follow these steps sequentially. Update `work-tracker.md` after each numbered task. Check in with the user after tasks marked with `[CHECK-IN]`.)_

1.  **Backend: Setup Blueprint & Routes:**
    - Create a new directory `/backend/email/` and file `/backend/email/routes.py`.
    - Define a Flask Blueprint `email_bp` in `routes.py` with `url_prefix="/email"`.
    - Define placeholder routes: `/fetch` (GET) and `/delete` (POST). Apply `@jwt_required()` to both.
    - Register `email_bp` within the main `api_bp` in `/backend/__init__.py`.
    - Import and initialize logger: `from backend.extensions import create_logger; logger = create_logger(__name__)`.
2.  **Frontend: Setup Page & Routing:**
    - Create the page component `/frontend/src/pages/EmailAssistantPage.tsx`. Add basic placeholder content (e.g., `<h1>Email Assistant</h1>`).
    - In `/frontend/src/App.tsx`, add a new route `/email-assistant` using `React.lazy()` for `EmailAssistantPage`. Wrap it with `PrivateRoute`.
    - **[CHECK-IN 1]** _Goal: Basic backend blueprint and frontend page structure/routing exist and are accessible._
3.  **Backend: Implement Email Fetching:**
    - In `/backend/email/routes.py`, implement the `/fetch` route logic.
    - Integrate the provided Python functions: `authenticate_gmail` (call this within the route to get the service object) and `get_recent_emails` (or `get_emails`).
    - Ensure `credentials.json` is accessible by the server. `authenticate_gmail` will handle `token.json` management.
    - Fetch ~100 recent emails.
    - Return the list of emails as JSON (ensure fields like `id`, `sender`, `subject`, `snippet`, `is_unread` are included).
    - Implement error handling (Gmail API errors, auth issues) using `try...except`. Log errors using `logger.error(..., exc_info=True)`. Return JSON error responses in the standard format (`{"success": False, "error": {"message": ...}}`) with appropriate HTTP status codes (e.g., 500, 503).
4.  **Frontend: API Service for Fetching:**
    - Create the API service file `/frontend/src/email/services/api.ts`.
    - Add a function `fetchEmails()` that uses the **shared `axiosInstance`** from `/frontend/src/utils/axiosInstance.tsx` to call the backend `/api/email/fetch` endpoint.
    - Define TypeScript interfaces for the email data structure returned by the backend (e.g., `interface Email { id: string; sender: string; subject: string; snippet: string; is_unread: boolean; }`).
5.  **Frontend: Display Emails:**
    - In `EmailAssistantPage.tsx`, use `useEffect` hook to call `fetchEmails()` on component mount.
    - Implement loading state (`useState<boolean>(false)`): Show `Skeleton` components (e.g., multiple rows mimicking the table) while fetching.
    - On successful fetch, display the emails using `shadcn/ui` `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableCell` components. Columns: Checkbox (empty for now), Sender, Subject, Snippet.
    - Apply visual styling (e.g., `font-bold`) to rows representing unread emails based on the `is_unread` flag.
    - Handle API errors using `useToast` with `variant: "destructive"`.
    - **[CHECK-IN 2]** _Goal: Emails are fetched from the backend (Gmail) and displayed in a styled table with loading state._
6.  **Frontend: Implement Selection:**
    - Add state to track selected email IDs (e.g., `useState<Set<string>>(new Set())`).
    - Implement the `shadcn/ui Checkbox` component in each table row. Clicking it should add/remove the email's `id` from the selected state.
    - Implement the "Select All" checkbox in the `TableHead`. Clicking it should select/deselect all _currently visible_ emails.
    - Apply a visual style (e.g., `data-[state=selected]:bg-muted` on `TableRow`) to indicate selected rows.
7.  **Frontend: Add Delete Button:**
    - Add a "Delete Selected" `shadcn/ui Button` above or below the table.
    - Disable the button if the selected emails set is empty (`selectedEmails.size === 0`).
8.  **Backend: Implement Email Deletion:**
    - In `/backend/email/routes.py`, implement the `/delete` route logic.
    - Expect a JSON payload: `{"email_ids": ["id1", "id2", ...]}`. Use `request.get_json()`.
    - Validate the input payload (check `email_ids` exists and is a list). Log validation failures (`logger.warning`).
    - Call the `delete_emails` Python function with the provided list of IDs (ensure the Gmail `service` object is obtained via `authenticate_gmail`).
    - Return a JSON response indicating success or failure based on the result from `delete_emails`. Use the standard format (`{"success": True/False, "message": ...}`). Log errors.
9.  **Frontend: API Service for Deletion:**
    - Add a function `deleteEmails(emailIds: string[])` to `/frontend/src/email/services/api.ts`.
    - This function should use the shared `axiosInstance` to make a POST request to `/api/email/delete` with the `emailIds` array in the request body (`{ email_ids: emailIds }`).
10. **Frontend: Wire Up Deletion Logic:**
    - In `EmailAssistantPage.tsx`, add an `onClick` handler to the "Delete Selected" button.
    - Implement a loading state for deletion (e.g., `useState<boolean>(false)` for `isDeleting`).
    - Inside the handler:
      - Set `isDeleting` to `true`, disable the button.
      - Convert the selected emails `Set` to an array.
      - Call the `deleteEmails` API service function.
      - On success:
        - Show a success `Toast` ("Emails deleted successfully").
        - Clear the selection state (`setSelectedEmails(new Set())`).
        - Re-fetch the email list by calling `fetchEmails()` again.
      - On failure:
        - Show an error `Toast` using the message from the backend response.
      - Finally (in `.finally()` block): Set `isDeleting` back to `false`.
    - **[CHECK-IN 3]** _Goal: Users can select one or more emails, click delete, see feedback, and the list updates._
11. **Frontend: Implement Client-Side Filtering:**
    - Add a `shadcn/ui Input` component above the table for "Filter by Sender".
    - Add state to store the filter query (e.g., `useState<string>('')`).
    - Add state to store the _original_ list of fetched emails (e.g., `useState<Email[]>([])`).
    - When the filter input changes, update the filter query state.
    - Use `React.useMemo` or a similar approach to derive the `displayedEmails` list by filtering the original email list based on the sender matching the filter query (case-insensitive). If the filter query is empty, `displayedEmails` should be the original list.
    - Ensure the `Table` component renders the `displayedEmails` list.
    - _(Self-correction: "Select All" should select/deselect all items in the `displayedEmails` list, not the original full list)._
    - **[CHECK-IN 4]** _Goal: Users can type in the filter input, and the email table updates instantly to show only matching senders._
12. **Final Review & Cleanup:**
    - Review code for consistency with the "Guide for AI Assistants" and existing patterns in `autodraft`, `speech`, `explain` features.
    - Test responsiveness of the page elements.
    - Verify backend validation and error handling.
    - Check sufficiency of backend logging.
    - Remove any `console.log` statements or debugging artifacts.
    - Manually test all functionalities (initial load, loading states, display, selection, select all with/without filter, deletion, filtering, error toasts).
    - Ensure `work-tracker.md` is fully updated.
    - **[FINAL CHECK-IN]** _Goal: Feature complete, tested, and aligns with project standards._

---

This revised plan should give your AI assistant much more specific guidance based on your actual codebase. Let me know if you need any further adjustments!
