// Create a new file to store valid routes
export const VALID_REDIRECT_PATHS = [
  "/",
  "/poeltl",
  // Add other valid protected routes here
];

export const isValidRedirectPath = (path: string): boolean => {
  return (
    VALID_REDIRECT_PATHS.includes(path) ||
    VALID_REDIRECT_PATHS.some((validPath) => path.startsWith(validPath + "/"))
  );
};