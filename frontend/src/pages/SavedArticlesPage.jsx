import React, { useEffect, useState } from "react";
import DashboardLayout from "../components/DashboardLayout";
import { getSavedArticles } from "../api";

function SavedArticlesPage() {
  const [articles, setArticles] = useState([]);

  useEffect(() => {
    const email = localStorage.getItem("user_email");
    console.log("User email from localStorage:", email);
    if (email) {
      getSavedArticles(email).then((res) => {
        if (res.success) {
          setArticles(res.articles);
        } else {
          console.error("Failed to fetch articles:", res.message);
        }
      });
    } else {
      console.warn("No user_email found in localStorage!");
    }
  }, []);

  return (
    <DashboardLayout>
      <h2>Saved Articles</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
        {articles.map((art) => (
          <div
            key={art.id}
            style={{ background: "#fff", padding: "1rem",width: "320px",
              borderRadius: "8px",
              boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
              overflow: "hidden",}}
          >
             <a href={art.url} target="_blank" rel="noopener noreferrer">
        <img
          src={art.image || "default-thumbnail.jpg"}
          alt={art.title}
          style={{ width: "100%", height: "180px", objectFit: "cover" }}
        />
      </a>
      <h4 style={{ margin: "0.5rem 0", color: "#333" }}>{art.title}</h4>
      <p style={{ fontSize: "0.9rem", color: "#666" }}>{art.summary}</p>
      <small style={{ color: "#999" }}>{art.date}</small>
      <a
        href={art.url}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          display: "block",
          marginTop: "0.5rem",
          color: "#007bff",
          textDecoration: "none",
        }}
      >
        Read Full Article
      </a>
          </div>
        ))}
      </div>
    </DashboardLayout>
  );
}

export default SavedArticlesPage;
