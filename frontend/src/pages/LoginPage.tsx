import "./LoginPage.css";

const Login = () => {
  const handleSignIn = () => {
    window.location.href = "http://127.0.0.1:5002/authorize/google";
  };

  return (
    <div className="loginContainer">
      <button className="signInButton" onClick={handleSignIn}>
        Sign In with Google
      </button>
    </div>
  );
};

export default Login;
