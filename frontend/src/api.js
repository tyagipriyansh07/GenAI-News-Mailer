export const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";


export async function loginUser(email, password) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await response.json();

  if (data.success) {
    // Save user_email to localStorage on successful login
    localStorage.setItem("user_email", email);
    localStorage.setItem("user_id", data.user_id); // If needed elsewhere
  } else {
    console.error("Login failed:", data.message);
  }

  return data;
}

export async function signUpUser(email, password, name) {
  const response = await fetch(`${API_URL}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  });
  const data = await response.json();

  if (data.success) {
    localStorage.setItem("user_email", email);
    localStorage.setItem("user_id", data.user_id);
  } else {
    console.error("Signup failed:", data.message);
  }

  return data;
}


export async function forgotPassword(email) {
  const response = await fetch(`${API_URL}/auth/forgot_password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  return response.json();
}

export async function resetPassword(token, new_password) {
  const response = await fetch(`${API_URL}/auth/reset_password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password }),
  });
  return response.json();
}

// export async function getAnalytics(userEmail) {
//   const res = await fetch(`${API_URL}/analytics?user_email=${encodeURIComponent(userEmail)}`);

//   return res.json();
// }

// IMPORTANT: pass the email to the query param user_email
export async function getSavedArticles(userEmail) {
  const response = await fetch(
    `${API_URL}/articles/saved?user_email=${encodeURIComponent(userEmail)}`
  );
  const data = await response.json();
  return data;
}

export async function getPreferences(userEmail) {
  const res = await fetch(`${API_URL}/preferences?user_email=${encodeURIComponent(userEmail)}`);
  return res.json();
}

export async function savePreferences(userEmail, prefsObj) {
  const response = await fetch(`${API_URL}/preferences?user_email=${encodeURIComponent(userEmail)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(prefsObj),
  });
  return response.json();
}

export async function submitFeedback(userEmail, rating, comment) {
  const response = await fetch(`${API_URL}/feedback?user_email=${userEmail}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rating, comment }),
  });
  return response.json();
}
