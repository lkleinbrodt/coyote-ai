import coyoteLogo from "./assets/coyote_logo.png";
import cheffrey from "./assets/chef_hat_stamp.png";
import guitarpic from "./assets/guitarpic.png";
import "./App.css";

function App() {
  // Function to handle image click
  const handleImageClick = (url: string | URL | undefined) => {
    window.open(url, "_blank"); // Open link in a new tab
  };

  return (
    <>
      <div>
        <a href="">
          <img src={coyoteLogo} className="logo" alt="Vite logo" />
        </a>
      </div>
      <h1>Coyote AI</h1>
      <div className="container">
        <div className="image-container">
          <h3>Cheffrey</h3>
          <img
            src={cheffrey}
            className="logo"
            alt="Cheffrey"
            onClick={() => handleImageClick("https://www.cheffrey.org/")}
          />
        </div>
        <div className="image-container">
          <h3>GuitarPic</h3>
          <img src={guitarpic} className="logo" alt="GuitarPic" />
        </div>
      </div>
    </>
  );
}

export default App;
