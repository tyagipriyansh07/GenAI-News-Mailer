import React, { useState } from "react";
import { useSearchParams } from "react-router-dom";
import "./AuthPages.css";
import { resetPassword } from "../api";

function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const [newPass, setNewPass] = useState("");
  const [msg, setMsg] = useState("");

  async function handleReset(e) {
    e.preventDefault();
    const res = await resetPassword(token, newPass);
    if (res.success) {
      setMsg("Password reset successfully! You can now log in.");
    } else {
      setMsg(res.detail || "Something went wrong.");
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-left">
        <div className="brand">
          <img src="/images/pulse.png" alt="Pulse Logo"/>
          <h2>Pulse</h2>
        </div>

        <h1>Reset Password</h1>
        <div className="form-group">
          <label>New Password:</label>
          <input 
            type="password"
            value={newPass}
            onChange={(e) => setNewPass(e.target.value)}
          />
        </div>
        <button className="btn-primary" onClick={handleReset}>
          Update Password
        </button>
        {msg && <p>{msg}</p>}
      </div>
      <div className="auth-right"></div>
    </div>
  );
}

export default ResetPasswordPage;
