import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./AuthPages.css";
import { loginUser, API_URL } from "../api";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errMsg, setErrMsg] = useState("");
  const navigate = useNavigate();

  async function handleLogin(e) {
    e.preventDefault();
    const res = await loginUser(email, password);
    if (res.success) {
      localStorage.setItem("user_email", res.email);
      localStorage.setItem("user_id", res.user_id);
      localStorage.setItem("name", res.name);
      
      navigate("/dashboard");
    } else {
      setErrMsg(res.detail || "Login failed");
    }
  }

  function handleGoogleLogin() {
    window.location.href = `${API_URL}/auth/google/redirect`;
  }
  function handleFacebookLogin() {
    window.location.href = `${API_URL}/auth/facebook/redirect`;
  }
  function handleAppleLogin() {
    window.location.href = `${API_URL}/auth/apple/redirect`;
  }

  return (
    <div className="auth-container">
      <div className="auth-left">
        <div className="brand">
          <img src="/images/pulse.png" alt="Pulse Logo" />
          <h2>Pulse</h2>
        </div>

        <h1>Login</h1>

        <div className="form-group">
          <label>Enter your email address</label>
          <input 
            type="text"
            placeholder="ex: john@gmail.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Enter your Password</label>
          <input 
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <a className="forgot-password" href="/forgot">Forgot Password?</a>

        <button className="btn-primary" onClick={handleLogin}>Login</button>
        {errMsg && <p style={{ color: "red", marginTop: "0.5rem" }}>{errMsg}</p>}

        <span className="or-continue">or continue with</span>
        {/* <div className="social-logins">
          <img src="/images/Facebook.png" alt="Facebook" onClick={handleFacebookLogin} />
          <img src="/images/apple.png" alt="Apple" onClick={handleAppleLogin} />
          <img src="/images/google.png" alt="Google" onClick={handleGoogleLogin} />
        </div> */}

        <div className="switch-auth">
          Don’t have an account? <a href="/signup">Register</a>
        </div>
      </div>

      <div className="auth-right"></div>
    </div>
  );

}

export default LoginPage;
