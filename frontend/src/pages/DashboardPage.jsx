// src/pages/DashboardPage.jsx
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import DashboardLayout from "../components/DashboardLayout";
import { getSavedArticles } from "../api";  // Ensure this is correctly imported

function DashboardPage() {
  // Pull name and email from localStorage
  const [userName, setUserName] = useState(localStorage.getItem("name") || "User");
  const [userEmail, setUserEmail] = useState(localStorage.getItem("user_email") || "");
  const [rating, setRating] = useState(0);      // State for star rating
  const [feedback, setFeedback] = useState(""); // State for feedback comment
  const [articles, setArticles] = useState([]); // For saved articles

  const submitFeedback = async () => {
    const userEmail = localStorage.getItem("user_email");
    if (!userEmail || rating === 0 || feedback.trim() === "") {
      alert("Please provide a rating and comment before submitting.");
      return;
    }

    try {
      const response = await fetch("/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: userEmail,  // Include email in the payload
          rating,
          comment: feedback,
        }),
      });

      const result = await response.json();
      if (result.success) {
        alert("Feedback submitted successfully!");
        setRating(0);
        setFeedback("");
      }
    } catch (error) {
      console.error("Error submitting feedback:", error);
    }
  };

  useEffect(() => {
    // Scroll to feedback section if URL contains #feedback
    if (window.location.hash === "#feedback") {
      document.getElementById("feedback").scrollIntoView({ behavior: "smooth" });
    }

    // Fetch saved articles
    async function fetchData() {
      if (userEmail) {
        const artRes = await getSavedArticles(userEmail);
        if (artRes.success) {
          const reversed = [...artRes.articles].reverse();
          setArticles(reversed.slice(0, 4));
        }
      }
    }
    fetchData();
  }, [userEmail]);

  return (
    <DashboardLayout>
      {/* Preferences Section */}
      <div className="preferences-section">
        <h2>Welcome {userName},</h2>
        <div className="preferences-card">
          <h3>Preferences Settings</h3>
          <p>Customize your news topics, delivery time, and content format preferences.</p>
          <Link to="/preferencespage" className="update-preferences-btn">
            Update Preferences →
          </Link>
        </div>
      </div>

      {/* Saved Articles Section */}
      <section style={{ marginTop: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
  <h2>Saved Articles</h2>
  <Link to="/saved-articles" className="see-all-link">See all &gt;</Link>
</div>

        <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
          {articles.map((art) => (
            <div
              key={art.id}
              style={{
                background: "#fff",
                padding: "1rem",
                width: "250px",
                borderRadius: "8px",
                boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
                overflow: "hidden",
              }}
            >
              <a href={art.url} target="_blank" rel="noopener noreferrer">
                <img
                  src={art.image || "default-thumbnail.jpg"}
                  alt={art.title}
                  style={{ width: "100%", height: "180px", objectFit: "cover" }}
                />
              </a>
              <h4 style={{ margin: "0.5rem 0", color: "#333" }}>{art.title}</h4>
              <p className="article-summary">{art.summary}</p>
              <small style={{ color: "#999" }}>{art.date}</small>
              <a
                href={art.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "block",
                  marginTop: "0.5rem",
                  color: "#6176D2",
                  textDecoration: "none",
                }}
              >
                Read Full Article
              </a>
            </div>
          ))}
          {articles.length === 0 && <p>No saved articles yet.</p>}
        </div>
      </section>
      <h2 style={{ marginTop: "2rem" }}>Feedback</h2>

      {/* Feedback Section */}
      <section id="feedback" className="feedback-section" >
        <p>Rate Your Experience</p>
        <div className="rating-stars">
          {[...Array(5)].map((_, i) => (
            <span
              key={i}
              className={i < rating ? "star filled" : "star"}
              onClick={() => setRating(i + 1)}
            >
              ★
            </span>
          ))}
        </div>
        <textarea
          rows={3}
          maxLength={200}
          className="feedback-input"
          placeholder="Enter your feedback or comments here that you wish to be incorporated in the news mail..."
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
        />
        <div className="feedback-counter">{feedback.length}/200</div>
        <button className="submit-feedback-btn" onClick={submitFeedback}>
          Submit Feedback
        </button>
      </section>
    </DashboardLayout>
  );
}

export default DashboardPage;
