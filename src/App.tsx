import coyoteLogo from "./assets/coyote_logo.png";
import "./App.css";
import { useState } from "react";

function App() {
  const [count, setCount] = useState(0);

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
        <button onClick={() => setCount(count + 1)}>Count: {count}</button>
      </div>
    </>
  );
}

export default App;
