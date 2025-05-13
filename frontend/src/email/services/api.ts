import axiosInstance from "../../utils/axiosInstance";

export interface Email {
  id: string;
  sender: string;
  subject: string;
  snippet: string;
  is_unread: boolean;
}

/**
 * Helper function to implement retry logic with exponential backoff
 * @param fn The async function to retry
 * @param maxRetries Maximum number of retry attempts
 * @param retryDelay Initial delay in ms (will be doubled each retry)
 * @returns Promise with the result of the function
 */
const withRetry = async <T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  retryDelay = 1000
): Promise<T> => {
  let lastError: Error = new Error("Unknown error occurred");

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error: unknown) {
      if (error instanceof Error) {
        lastError = error;

        // Only retry on timeout or network errors
        const isTimeout =
          ("code" in error && error.code === "ECONNABORTED") ||
          error.message?.includes("timeout") ||
          error.message?.includes("Network Error");

        if (attempt >= maxRetries || !isTimeout) {
          throw error;
        }
      } else {
        // If not an Error object, convert it to one
        lastError = new Error(String(error));
        if (attempt >= maxRetries) {
          throw lastError;
        }
      }

      console.log(
        `Retry attempt ${attempt + 1}/${maxRetries} after ${retryDelay}ms`
      );

      // Wait before retrying
      await new Promise((resolve) => setTimeout(resolve, retryDelay));

      // Exponential backoff - double the delay for next attempt
      retryDelay *= 2;
    }
  }

  throw lastError;
};

/**
 * Fetch emails from connected Gmail account
 * @returns Promise with array of email objects
 */
export const fetchEmails = async (): Promise<Email[]> => {
  return withRetry(async () => {
    try {
      const response = await axiosInstance.get("/email/fetch", {
        timeout: 30000, // 30 second timeout (adjust as needed)
      });
      return response.data.emails || [];
    } catch (error) {
      console.error("Error fetching emails:", error);
      throw error;
    }
  });
};

/**
 * Delete selected emails by ID
 * @param emailIds Array of email IDs to delete
 * @returns Promise with success status
 */
export const deleteEmails = async (emailIds: string[]): Promise<boolean> => {
  return withRetry(async () => {
    try {
      const response = await axiosInstance.post("/email/delete", {
        email_ids: emailIds,
      });
      return response.data.success || false;
    } catch (error) {
      console.error("Error deleting emails:", error);
      throw error;
    }
  });
};
