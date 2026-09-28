import React from "react";
import { Link, useLocation } from "react-router-dom";
import "./Dashboard.css";

function Sidebar() {
  const location = useLocation();

  const menuItems = [
    { name: "Dashboard", path: "/dashboard", icon: "/images/e1.svg" },
    { name: "Preferences Setup", path: "/preferencespage", icon: "/images/e2.svg" },
    { name: "Saved Articles", path: "/saved-articles", icon: "/images/e3.svg" },
    { name: "Feedback", path: "/dashboard#feedback", icon: "/images/e4.svg" }
  ];

  const footerItems = [
    // { name: "Unsubscribe", path: "/unsubscribe", icon: "/images/card.png" },
    // { name: "Settings", path: "/settings", icon: "/images/setting-2.png" },
    { name: "Logout", path: "/logout", icon: "/images/e5.svg" },
  ];
  const isFeedbackLinkActive = 
  location.pathname === "/dashboard" && location.hash === "#feedback";


  return (
    <div className="sidebar-container">
      <div>
        <div className="sidebar-logo">
          <img src="/images/pulse.png" alt="Logo" />
          <h2>Pulse</h2>
        </div>
        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <Link
            to={item.path.split('#')[0]}
            className={
              (location.pathname === item.path.split('#')[0] && !item.path.includes('#feedback')) 
                ? "sidebar-link active"
                : isFeedbackLinkActive && item.path.includes('#feedback')
                  ? "sidebar-link active"
                  : "sidebar-link"
            }
            onClick={() => {
              if (item.path.includes("#feedback")) {
                const feedbackSection = document.getElementById("feedback");
                if (feedbackSection) {
                  feedbackSection.scrollIntoView({ behavior: "smooth" });
                }
              }
            }}
          >
            <img src={item.icon} alt={`${item.name} icon`} className="sidebar-icon" />
            {item.name}
          </Link>
          
          ))}
        </nav>
      </div>
      <div className="sidebar-footer">
        {footerItems.map((item) => (
          <Link key={item.path} to={item.path} className="sidebar-link">
            <img src={item.icon} alt={`${item.name} icon`} className="sidebar-icon" />
            {item.name}
          </Link>
        ))}
      </div>
    </div>
  );
}

export default Sidebar;
