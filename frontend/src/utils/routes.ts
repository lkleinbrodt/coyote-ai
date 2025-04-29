// Create a new file to store valid routes
export const VALID_REDIRECT_PATHS = [
  "/",
  "/poeltl",
  "/autodraft",
  "/boids",
  "/tower-builder",
  "/games",
  "/games/shoot-the-creeps",
  "/games/gravity-quest",
];

export const isValidRedirectPath = (path: string): boolean => {
  return (
    VALID_REDIRECT_PATHS.includes(path) ||
    VALID_REDIRECT_PATHS.some((validPath) => path.startsWith(validPath + "/"))
  );
};
