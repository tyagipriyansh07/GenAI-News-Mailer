import React from "react";
import "./Dashboard.css";

function Topbar() {
  // Make sure these keys match what you store at login/signup
  const userName = localStorage.getItem("name") || "User";
  // IMPORTANT: change this to "user_email", so it matches the login code
  const userEmail = localStorage.getItem("user_email") || "marksmith@devops.com";

  return (
    <div className="topbar-container">
      {/* <div className="search-box">
        <input type="text" placeholder="Search" />
      </div> */}
      <div className="user-info">
        <img src="/images/user-avatar.png" alt="User Avatar" className="user-avatar" />
        <div>
          <p className="user-name">{userName}</p>
          <p className="user-email">{userEmail}</p>
        </div>
        {/* <div className="notification-bell">
          <img src="/images/bell-icon.jpg" alt="Notifications" />
        </div> */}
      </div>
    </div>
  );
}

export default Topbar;
