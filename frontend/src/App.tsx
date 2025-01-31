import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.min.js";

import { BrowserRouter, Route, Routes } from "react-router-dom";

import AuthPage from "./pages/AuthPage";
import { AuthProvider } from "./contexts/AuthContext";
import Autodraft from "./autodraft/pages/Autodraft";
import Boids from "./boids/pages/Boids";
import Landing from "./pages/Landing";
import Login from "./pages/LoginPage";
import NavBar from "./components/NavBar";
import NotFound from "./pages/NotFound";
import Poeltl from "./poeltl/pages/Poeltl";
import Privacy from "./pages/Privacy";
import PrivateRoute from "./components/PrivateRoute";
import { ThemeProvider } from "./components/theme-provider";

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
      <BrowserRouter>
        <AuthProvider>
          <div className="app-container">
            <NavBar />
            <div className="content-container">
              <Routes>
                <Route path="/" element={<Landing />} />
                <Route path="/login" element={<Login />} />
                <Route path="/privacy" element={<Privacy />} />
                <Route path="/auth" element={<AuthPage />} />
                <Route element={<PrivateRoute />}>
                  <Route path="/poeltl" element={<Poeltl />} />
                  <Route path="/autodraft" element={<Autodraft />} />
                  <Route path="/boids" element={<Boids />} />
                </Route>
                <Route path="*" element={<NotFound />} />
              </Routes>
            </div>
          </div>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
