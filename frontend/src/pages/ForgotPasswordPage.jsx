import React, { useState } from "react";
import "./AuthPages.css";
import { forgotPassword } from "../api";

function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    const res = await forgotPassword(email);
    if (res.success) {
      setMsg("Check your email for a reset link!");
    } else {
      setMsg(res.detail || "Something went wrong");
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-left">
        <div className="brand">
          <img src="/images/pulse.png" alt="Pulse Logo"/>
          <h2>Pulse</h2>
        </div>

        <h1>Forgot Password</h1>
        <div className="form-group">
          <label>Enter your account's email:</label>
          <input 
            type="text"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <button className="btn-primary" onClick={handleSubmit}>
          Send Reset Link
        </button>
        {msg && <p>{msg}</p>}
      </div>
      <div className="auth-right"></div>
    </div>
  );
}

export default ForgotPasswordPage;
