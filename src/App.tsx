import coyoteLogo from "./assets/coyote_logo.png";
import "./App.css";

function App() {
  return (
    <>
      <div>
        <a href="">
          <img src={coyoteLogo} className="logo" alt="Vite logo" />
        </a>
      </div>
      <h1>Coyote AI</h1>
      <div className="card">
        <p>Welcome to Coyote AI</p>
      </div>
    </>
  );
}

export default App;
