import "./App.css";

import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Suspense, lazy } from "react";

import AuthPage from "./pages/AuthPage";
import { AuthProvider } from "./contexts/AuthContext";
import Landing from "./pages/Landing";
import Login from "./pages/LoginPage";
import NavBar from "./components/NavBar";
import NotFound from "./pages/NotFound";
import Privacy from "./pages/Privacy";
import PrivateRoute from "./components/PrivateRoute";
import { ThemeProvider } from "./components/theme-provider";

// Lazy load components
const Autodraft = lazy(() => import("./autodraft/pages/Autodraft"));
const Boids = lazy(() => import("./boids/pages/Boids"));
const Games = lazy(() => import("./games/pages/Games"));
const GravityQuest = lazy(() => import("./games/GravityQuest/GravityQuest"));
const Pet = lazy(() => import("./pet/pages/Pet"));
const Poeltl = lazy(() => import("./poeltl/pages/Poeltl"));

// Loading component
const LoadingFallback = () => (
  <div className="flex h-screen w-screen items-center justify-center">
    <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
  </div>
);

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
      <AuthProvider>
        <BrowserRouter>
          <div className="min-h-screen bg-background">
            <NavBar />
            <main className="container mx-auto p-4">
              <Suspense fallback={<LoadingFallback />}>
                <Routes>
                  <Route path="/" element={<Landing />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/auth" element={<AuthPage />} />
                  <Route path="/privacy" element={<Privacy />} />
                  <Route element={<PrivateRoute />}>
                    <Route path="/autodraft" element={<Autodraft />} />
                    <Route path="/boids" element={<Boids />} />
                    <Route path="/games" element={<Games />} />
                    <Route
                      path="/games/gravity-quest"
                      element={<GravityQuest />}
                    />
                    <Route path="/pet" element={<Pet />} />
                    <Route path="/poeltl" element={<Poeltl />} />
                  </Route>
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </Suspense>
            </main>
          </div>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
