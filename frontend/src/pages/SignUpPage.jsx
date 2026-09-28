import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./AuthPages.css";
import { signUpUser } from "../api";

function SignUpPage() {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [errMsg, setErrMsg] = useState("");
  const navigate = useNavigate();

  async function handleSignUp(e) {
    e.preventDefault();
    if (password !== confirmPwd) {
      setErrMsg("Passwords do not match!");
      return;
    }
    const res = await signUpUser(email, password, name);
    if (res.success) {
      navigate("/");
    } else {
      setErrMsg(res.detail || "Sign-up failed");
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-left">
        <div className="brand">
          <img src="/images/pulse.png" alt="Pulse Logo"/>
          <h2>Pulse</h2>
        </div>

        <h1>Sign-Up</h1>

        <div className="form-group">
         <label>Enter your name</label>
         <input 
           type="text"
           placeholder="John Doe"
           value={name}
           onChange={(e) => setName(e.target.value)}
         />
       </div>


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

        <div className="form-group">
          <label>Confirm Password</label>
          <input 
            type="password"
            placeholder="Confirm Password"
            value={confirmPwd}
            onChange={(e) => setConfirmPwd(e.target.value)}
          />
        </div>

        <button className="btn-primary" onClick={handleSignUp}>Sign-Up</button>
        {errMsg && <p style={{ color: "red", marginTop: "0.5rem" }}>{errMsg}</p>}

        <span className="or-continue">or continue with</span>
        {/* <div className="social-logins">
          <img src="/images/Facebook.png" alt="Facebook" />
          <img src="/images/apple.png" alt="Apple" />
          <img src="/images/google.png" alt="Google" />
        </div> */}

        <div className="switch-auth">
          Already have an account? <a href="/">Login</a>
        </div>
      </div>

      <div className="auth-right"></div>
    </div>
  );
}

export default SignUpPage;
