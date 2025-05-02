AI Agent Task List: Implement "Explain Like I'm \_\_\_\_" Feature

Goal: Build the "Explain Like I'm \_\_\_\_" feature as specified in PRD Version 1.1.
Instructions: Process these tasks sequentially. Mark each task as complete upon successful implementation. Refer to the PRD (v1.1) sections provided for detailed requirements and context.

Phase 1: Frontend Development (React / Vite)

Task 1: Setup Page Component and Routing [PRD 4.1.1]

[x] 1.1: Create the page component file: /frontend/src/pages/ExplainPage.tsx.

[x] 1.2: Define a basic functional component structure within ExplainPage.tsx.

[x] 1.3: Import lazy from React in /frontend/src/App.tsx.

[x] 1.4: Lazy load the ExplainPage component in /frontend/src/App.tsx (similar to Autodraft, Boids, etc.).

[x] 1.5: Add a new <Route path="/explain" element={<ExplainPage />} /> within the main <Routes> block in /frontend/src/App.tsx. Ensure it's publicly accessible (outside any PrivateRoute).

[x] 1.6: Verify the route works by navigating to /explain (it should render the basic component).

Task 2: Implement UI Layout and Input Elements [PRD 4.1.2, 4.1.3, 4.1.7]

[x] 2.1: In ExplainPage.tsx, implement the main container div using Tailwind for padding and max-width (similar to Landing.tsx or Autodraft).

[x] 2.2: Add the user input section:

[x] 2.2.1: Import and use the Input component from /frontend/src/components/ui/input.tsx. Add a placeholder like "Enter a topic...".

[x] 2.2.2: Import and use the Button component from /frontend/src/components/ui/button.tsx. Set the label to "Explain It!".

[x] 2.2.3: Style the input and button using Tailwind to be visually appealing and consistent with the site theme. Arrange them logically (e.g., input followed by button).

[x] 2.3: Implement the 4-column layout section below the input:

[x] 2.3.1: Use CSS Flexbox or Grid via Tailwind classes (e.g., grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4). Ensure responsiveness (stacking on smaller screens).

[x] 2.3.2: For each of the 4 columns:

[x] 2.3.2.1: Import and use the Card component from /frontend/src/components/ui/card.tsx.

[x] 2.3.2.2: Inside the Card, use CardHeader and CardTitle to display the complexity level titles: "Curious Child", "Student", "Professional", "World-Class Expert".

[x] 2.3.2.3: Inside the Card, add an empty CardContent section. This will later hold explanations or loaders.

Task 3: Implement State Management [PRD 4.1.4]

[x] 3.1: In ExplainPage.tsx, define state variables using useState:

[x] topic (string, initial value: '')

[x] isLoading (boolean, initial value: false - this might evolve to an object per level if finer control is needed, but start simple)

[x] explanations (object, initial value: { child: '', student: '', professional: '', expert: '' })

[x] error (string or null, initial value: null - this might evolve to an object per level)

[x] 3.2: Link the topic state to the Input component's value and onChange handler.

Task 4: Frontend API Integration [PRD 4.1.5]

[x] 4.1: Define a new async function getExplanations(topic: string) within /frontend/src/explain/services/api.tsx (create this file if it doesn't exist).

[x] 4.2: Inside getExplanations, import and use axiosInstance from /frontend/src/autodraft/utils/axiosInstance.tsx.

[x] 4.3: Implement a POST request to the backend endpoint /api/explain with the payload { topic }.

[x] 4.4: Ensure the function returns the data on success (e.g., response.data) and throws or handles errors appropriately.

Task 5: Implement Interaction Logic & Data Fetching [PRD 4.1.2, 4.1.4, 4.1.5]

[x] 5.1: Create an async function handleExplainSubmit in ExplainPage.tsx.

[x] 5.2: Attach handleExplainSubmit to the onClick event of the "Explain It!" button.

[x] 5.3: Inside handleExplainSubmit:

[x] 5.3.1: Perform basic validation: if topic is empty, set an error state briefly or show a toast, then return. Clear previous errors/explanations.

[x] 5.3.2: Set isLoading state to true.

[x] 5.3.3: Disable the input field and button (use the isLoading state).

[x] 5.3.4: Call the getExplanations(topic) service function within a try...catch block.

[x] 5.3.5: On success (within try):

[x] 5.3.5.1: Update the explanations state with the data received from the API (e.g., response.data.data.explanations).

[x] 5.3.5.2: Clear any previous error state.

[x] 5.3.6: On failure (within catch):

[x] 5.3.6.1: Set the error state with an appropriate message (e.g., "Failed to fetch explanations.").

[x] 5.3.6.2: Clear the explanations state.

[x] 5.3.6.3: Log the error to the console.

[x] 5.3.7: In a finally block:

[x] 5.3.7.1: Set isLoading state back to false.

[x] 5.3.7.2: Re-enable the input field and button.

Task 6: Display Loading States and Explanations [PRD 4.1.4, 4.1.3]

[x] 6.1: In the CardContent for each of the 4 columns:

[x] 6.1.1: If isLoading is true, render a loading indicator:

[x] Import and use the Skeleton component (/frontend/src/components/ui/skeleton.tsx) to mimic text lines.

[x] Alternatively, import and use Loader2 from lucide-react with animate-spin.

[x] Add the corresponding "fun" loading text (e.g., "Thinking like a child...").

[x] 6.1.2: If isLoading is false AND the corresponding explanation exists in the explanations state (e.g., explanations.child), render the explanation text.

[x] 6.1.3: If isLoading is false AND there's an error for this specific level (if implementing per-level errors later), display the error message using the Alert component. For V1, global error handled by Toast.

Task 7: Implement Frontend Error Display [PRD 4.1.6, 8]

[x] 7.1: Ensure the Toaster component from /frontend/src/components/ui/toaster.tsx is present in /frontend/src/App.tsx.

[x] 7.2: Import useToast from /frontend/src/hooks/use-toast.ts in ExplainPage.tsx.

[x] 7.3: Modify the catch block in handleExplainSubmit (Task 5.3.6) to call toast({ title: "Error", description: "Could not fetch explanations.", variant: "destructive" }); instead of (or in addition to) setting local error state for general API failures.

[x] 7.4: Implement the simple inline validation message for empty input (Task 5.3.1).

Task 8: Frontend Styling and Responsiveness Polish [PRD 4.1.7, 6]

[x] 8.1: Review the entire ExplainPage.tsx component and apply Tailwind classes consistently for spacing, typography, borders, and colors, matching the site's theme (index.css).

[x] 8.2: Test the page layout on various screen sizes (mobile, tablet, desktop) and adjust Tailwind responsive modifiers (e.g., md:, lg:) as needed to ensure columns stack correctly and content remains readable.

Phase 2: Backend Development (Flask)

Task 9: Setup Backend Route and Blueprint [PRD 4.2.1]

[x] 9.1: Create a new file /backend/explain/routes.py (if an explain blueprint doesn't exist).

[x] 9.2: In routes.py, import necessary modules (Blueprint, jsonify, request, current_app, logger).

[x] 9.3: Define a new blueprint: explain_bp = Blueprint("explain", **name**, url_prefix="/explain").

[x] 9.4: Register this blueprint in /backend/**init**.py under the /api prefix: api_bp.register_blueprint(explain_bp).

[x] 9.5: Define the route function: @explain_bp.route("/", methods=["POST"]). Name the function explain_topic. Ensure no @jwt_required.

Task 10: Implement Request Handling and Validation [PRD 4.2.2]

[x] 10.1: Inside explain_topic, get the JSON data: data = request.get_json(). Handle potential None case.

[x] 10.2: Extract the topic: topic = data.get("topic") if data else None.

[x] 10.3: Add logging for the request: logger.info(f"Explain request received for topic: {topic[:50]}...")

[x] 10.4: Implement validation:

[x] Check if topic exists and is a non-empty string.

[x] Check if topic length is within a reasonable limit (e.g., <= 500 chars).

[x] If validation fails, log a warning (logger.warning) and return a 400 error using the standard JSON format: jsonify({"success": False, "error": {"message": "Invalid topic provided."}}), 400.

Task 11: Implement LLM Integration

[x] 11.1: Import OpenAI client and initialize it with the API key from environment variables

[x] 11.2: Create a detailed prompt template for generating explanations at different complexity levels

[x] 11.3: Implement the OpenAI API call with proper error handling

[x] 11.4: Parse and validate the response to ensure it contains all required explanation levels

[x] 11.5: Add comprehensive logging for API calls and responses

Task 12: Handle LLM Response and Format Output

[x] 12.1: Parse the LLM response using json.loads() and handle potential parsing errors

[x] 12.2: Validate the response structure to ensure all required explanation levels are present

[x] 12.3: Add content validation for each explanation (type, length, non-empty)

[x] 12.4: Include metadata in the response (token usage, model information)

[x] 12.5: Format error responses with detailed messages for different failure cases

Task 13: Backend Logging and Configuration [PRD 4.2.5, 11.1]

[ ] 13.1: Ensure comprehensive logging is implemented throughout the explain_topic function as detailed in previous steps (request received, validation results, LLM interaction, errors). Use appropriate log levels (INFO, DEBUG, WARNING, ERROR).

[ ] 13.2: Add documentation (e.g., comments in config.py or a README section) explaining the need for the LLM_API_KEY environment variable.

Phase 3: Testing and Refinement

Task 14: Backend Testing

[ ] 14.1: Use a tool like curl or Postman to send valid POST requests to /api/explain with different topics. Verify 200 responses with the correct JSON structure.

[ ] 14.2: Send invalid requests (missing topic, empty topic, overly long topic). Verify 400 responses with the correct error JSON.

[ ] 14.3: (If possible) Simulate LLM API errors (e.g., by providing an invalid key temporarily). Verify 500/503 responses with the correct error JSON.

[ ] 14.4: Check backend logs for correct logging messages during tests.

Task 15: Frontend Testing

[ ] 15.1: Test the happy path: Enter various topics, click "Explain It!", verify loading states appear, and explanations render correctly in all four columns.

[ ] 15.2: Test input validation: Try submitting an empty topic, verify the inline error message appears.

[ ] 15.3: Test general error handling: Temporarily break the backend endpoint or network connection, submit a topic, verify the Toast error notification appears.

[ ] 15.4: Test responsiveness: Resize the browser window or use browser developer tools to simulate different devices (mobile, tablet, desktop). Verify columns stack correctly and UI remains usable.

[ ] 15.5: Test with long explanations: Ensure text wraps correctly within the CardContent.

[ ] 15.6: Test edge case topics (e.g., very obscure, potentially sensitive - though LLM should handle safety). Observe behavior.

Task 16: Final Review and Code Cleanup

[ ] 16.1: Review all new frontend code (ExplainPage.tsx, changes in api.tsx, App.tsx) for clarity, consistency, and adherence to React/TypeScript best practices. Remove console logs.

[ ] 16.2: Review all new backend code (tools/routes.py, changes in **init**.py, config.py) for clarity, consistency, error handling, logging, and adherence to Flask best practices.

[ ] 16.3: Ensure consistency with the PRD requirements.

This task list provides a granular breakdown suitable for an AI agent to follow, execute, and track progress against the PRD.
