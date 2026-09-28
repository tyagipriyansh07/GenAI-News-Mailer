import React, { useEffect, useState } from "react";
import DashboardLayout from "../components/DashboardLayout";
import { getPreferences, savePreferences } from "../api";
import "./PreferencesPage.css"; // We'll create a new CSS file for preferences

function PreferencesPage() {
  const userEmail = localStorage.getItem("user_email");
  const [name, setName] = useState("");
  const [contentFormat, setContentFormat] = useState("");
  const [deliveryFrequency, setDeliveryFrequency] = useState("");
  const [deliveryTime, setDeliveryTime] = useState("");
  
  const [topics, setTopics] = useState([]);   // e.g. ["Generative AI","Sports",...]
  const [goals, setGoals] = useState([]);     // e.g. ["Stay Updated", "Market Trends"]
  const [trends, setTrends] = useState([]);   // e.g. ["Emerging Technologies","Sustainability"]
  const [competitors, setCompetitors] = useState(["Open AI","Meta AI"]);
  const [keywords, setKeywords] = useState(["Open AI","Meta AI","Draft"]);
  const [isLoading, setIsLoading] = useState(false); // NEW: Loading state


  const allTopicOptions = [
    { label: "Generative AI", image: "/images/genai.jpg" },
    { label: "International Market", image: "/images/intl_mark.jpg" },
    { label: "Sports", image: "/images/sports.jpg" },
    { label: "Entertainment", image: "/images/ent.png" },
    { label: "Tech Innovation", image: "/images/tech_innov.jpg" },
    { label: "Space Exploration", image: "/images/space.jpg" },
    { label: "Politics", image: "/images/political.jpg" },
    { label: "Health", image: "/images/health_news.png" },
  ];

  const allGoalOptions = [
    "Stay Updated",
    "Industry Expertise",
    "Strategy Decisions",
    "Market Trends",
  ];

  const allTrendOptions = [
    "Emerging Technologies",
    "Market Analysis",
    "Consumer Behavior",
    "Sustainability",
  ];

  useEffect(() => {
    (async function fetchPrefs() {
      const res = await getPreferences(userEmail);
      if (res.success) {
        setName(res.name || "");
        setContentFormat(res.preferences.content_format || "Summary Articles");
        setDeliveryFrequency(res.preferences.frequency || "Weekly");
        setDeliveryTime(res.preferences.delivery_time || "Morning (8am to 10 am)");
        setTopics(res.preferences.topics || []);
        setGoals(res.preferences.goals || []);
        setTrends(res.preferences.industry_trends || []);
        setCompetitors(res.preferences.competitors || []);
        setKeywords(res.preferences.keywords || []);
      }
    })();
  }, [userEmail]);

  function handleTopicToggle(topicLabel) {
    if (topics.includes(topicLabel)) {
      setTopics(topics.filter(t => t !== topicLabel));
    } else {
      setTopics([...topics, topicLabel]);
    }
  }

  function handleGoalToggle(goal) {
    if (goals.includes(goal)) {
      setGoals(goals.filter(g => g !== goal));
    } else {
      setGoals([...goals, goal]);
    }
  }

  function handleTrendToggle(trend) {
    if (trends.includes(trend)) {
      setTrends(trends.filter(t => t !== trend));
    } else {
      setTrends([...trends, trend]);
    }
  }

  function handleCompetitorsChange(e) {
    // comma-separated
    const arr = e.target.value.split(",").map(s => s.trim()).filter(Boolean);
    setCompetitors(arr);
  }

  function handleKeywordsChange(e) {
    const arr = e.target.value.split(",").map(s => s.trim()).filter(Boolean);
    setKeywords(arr);
  }

  async function handleSave() {
    const prefsObj = {
      name,
      content_format: contentFormat,
      delivery_frequency: deliveryFrequency,
      delivery_time: deliveryTime,
      topics,
      goals,
      industry_trends: trends,
      competitors,
      keywords,
    };
    const res = await savePreferences(userEmail, prefsObj);
    if (res.success) {
      alert("Preferences saved!");
    }
  }

  async function handleInstantSend() {
       const userEmail = localStorage.getItem("user_email");
       if (!userEmail) {
         alert("No user logged in!");
         return;
       }
      setIsLoading(true); // Start loading

       try {
         const response = await fetch(`/articles/send_now?user_email=${userEmail}`,
           { method: "POST" }
         );
         const data = await response.json();
         if (data.success) {
           alert("Email sent! Check your inbox.");
         } else {
           alert("Failed to send instantly: " + data.message);
         }
       } catch (err) {
         console.error(err);
         alert("An error occurred trying to send instantly.");
       }finally {
        setIsLoading(false); // Stop loading
      }
     }
    

  return (
    <DashboardLayout>
      <div className="preferences-container">
        <h2 className="page-title">Preference Setup</h2>

        {/* Personal Information Card */}
        <div className="card personal-info-card">
          <h3>Personal information</h3>
          <div className="form-row">
            <label>Name:</label>
            <input
              type="text"
              placeholder="Enter your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="form-row">
            <label>Content Format:</label>
            <select
              value={contentFormat}
              onChange={(e) => setContentFormat(e.target.value)}
            >
              <option value="Summary Articles">Summary Articles</option>
              <option value="HTML">HTML</option>
              <option value="PDF">PDF</option>
            </select>
          </div>

          <div className="form-row">
            <label>Delivery Frequency:</label>
            <select
              value={deliveryFrequency}
              onChange={(e) => setDeliveryFrequency(e.target.value)}
            >
              <option value="Weekly">Weekly</option>
              <option value="Daily">Daily</option>
            </select>
          </div>

          <div className="form-row">
            <label>Delivery Time:</label>
            <select
              value={deliveryTime}
              onChange={(e) => setDeliveryTime(e.target.value)}
            >
              <option value="Morning (8am to 10 am)">Morning (8am to 10 am)</option>
              <option value="Afternoon (12pm to 2 pm)">Afternoon (12pm to 2 pm)</option>
              <option value="Evening (5pm to 7 pm)">Evening (5pm to 7 pm)</option>
            </select>
          </div>
        </div>

        {/* Interest Selection Card */}
        <div className="card interest-card">
          <h3>Interest Selection</h3>

          <div className="subsection">
            <h4>Content Topic Selection:</h4>
            <div className="topic-grid">
              {allTopicOptions.map((opt) => (
                <div
                  key={opt.label}
                  className={`topic-card ${topics.includes(opt.label) ? "selected" : ""}`}
                  onClick={() => handleTopicToggle(opt.label)}
                >
                  <img src={opt.image} alt={opt.label} />
                  <p>{opt.label}</p>
                  <div className="checkbox-overlay">
                    <input
                      type="checkbox"
                      readOnly
                      checked={topics.includes(opt.label)}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="subsection">
            <h4>Goals:</h4>
            <div className="checkbox-row">
              {allGoalOptions.map((goal) => (
                <label
                key={goal}
                className={`checkbox-label ${goals.includes(goal) ? "selected" : ""}`}
                onClick={() => handleGoalToggle(goal)}
            >
                <span className="checkbox-icon"></span>
                {goal}
            </label>
              ))}
            </div>
          </div>

          <div className="subsection">
            <h4>Industry Trends:</h4>
            <div className="checkbox-row">
              {allTrendOptions.map((tr) => (
                 <label
                 key={tr}
                 className={`checkbox-label ${trends.includes(tr) ? "selected" : ""}`}
                 onClick={() => handleTrendToggle(tr)}
             >
                 <span className="checkbox-icon"></span>
                 {tr}
             </label>
              ))}
            </div>
          </div>

          <div className="subsection">
            <label>Enter Competitors or other interests (comma-separated):</label>
            <input
              type="text"
              placeholder="List key competitors or areas of interest..."
              value={competitors.join(", ")}
              onChange={handleCompetitorsChange}
            />
          </div>

          <div className="subsection">
            <label>Keywords (comma-separated):</label>
            <input
              type="text"
              placeholder="eg. Blockchain, AI"
              value={keywords.join(", ")}
              onChange={handleKeywordsChange}
            />
          </div>
        </div>

        <div className="save-btn-container">
          <button onClick={handleSave} className="save-btn"> Save Preferences </button>
          <button onClick={handleInstantSend} className="instant-btn" disabled={isLoading}>
            {isLoading ? "Sending..." : "Send Me News Instantly"}
          </button>
          </div>

      </div>
    </DashboardLayout>
  );
}

export default PreferencesPage;
