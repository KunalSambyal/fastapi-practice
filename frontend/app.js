// Backend API Base URL
const API_BASE_URL = "http://127.0.0.1:8000";

// DOM Elements
const alertBox = document.getElementById("alert-box");
const tabNav = document.getElementById("tab-nav");
const headerSubtitle = document.getElementById("header-subtitle");

const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const forgotForm = document.getElementById("forgot-form");
const otpForm = document.getElementById("otp-form");
const profileCard = document.getElementById("profile-card");

// Switch between views (login, register, forgot-password, otp, profile)
function switchView(viewName) {
  clearAlert();

  // Hide all views
  loginForm.classList.add("hidden");
  registerForm.classList.add("hidden");
  forgotForm.classList.add("hidden");
  otpForm.classList.add("hidden");
  profileCard.classList.add("hidden");

  // Reset tab buttons
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach((tab) => tab.classList.remove("active"));

  if (viewName === "login") {
    loginForm.classList.remove("hidden");
    tabNav.classList.remove("hidden");
    tabs[0].classList.add("active");
    headerSubtitle.textContent = "Welcome back! Please enter your details.";
  } else if (viewName === "register") {
    registerForm.classList.remove("hidden");
    tabNav.classList.remove("hidden");
    tabs[1].classList.add("active");
    headerSubtitle.textContent = "Create an account to get started.";
  } else if (viewName === "forgot-password") {
    forgotForm.classList.remove("hidden");
    tabNav.classList.add("hidden");
    headerSubtitle.textContent = "Reset your password";
  } else if (viewName === "otp") {
    otpForm.classList.remove("hidden");
    tabNav.classList.add("hidden");
    headerSubtitle.textContent = "Verify OTP & set new password";
  } else if (viewName === "profile") {
    profileCard.classList.remove("hidden");
    tabNav.classList.add("hidden");
    headerSubtitle.textContent = "Your account dashboard";
  }
}

// Show alert banner (type: 'success', 'error', 'info')
function showAlert(message, type = "error") {
  alertBox.className = `alert ${type}`;
  alertBox.textContent = message;
  alertBox.classList.remove("hidden");
}

function clearAlert() {
  alertBox.classList.add("hidden");
  alertBox.textContent = "";
}

// -------------------------------------------------------------
// 1. REGISTER HANDLER (POST /auth/register)
// -------------------------------------------------------------
async function handleRegister(event) {
  event.preventDefault();
  clearAlert();

  const username = document.getElementById("reg-username").value.trim();
  const email = document.getElementById("reg-email").value.trim();
  const password = document.getElementById("reg-password").value;
  const regBtn = document.getElementById("reg-btn");

  regBtn.disabled = true;
  regBtn.textContent = "Creating Account...";

  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
        email: email,
        password: password,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      // Handle validation errors or duplicate conflicts from FastAPI
      const errorMsg = data.detail || (Array.isArray(data.detail) ? data.detail[0].msg : "Registration failed.");
      showAlert(errorMsg, "error");
      return;
    }

    showAlert("Registration successful! You can now log in.", "success");
    registerForm.reset();
    setTimeout(() => {
      switchView("login");
      document.getElementById("login-username").value = username;
    }, 1500);

  } catch (error) {
    showAlert("Could not connect to the backend server. Is FastAPI running?", "error");
  } finally {
    regBtn.disabled = false;
    regBtn.textContent = "Create Account";
  }
}

// -------------------------------------------------------------
// 2. LOGIN HANDLER (POST /auth/login)
// -------------------------------------------------------------
async function handleLogin(event) {
  event.preventDefault();
  clearAlert();

  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value;
  const loginBtn = document.getElementById("login-btn");

  loginBtn.disabled = true;
  loginBtn.textContent = "Logging in...";

  try {
    // OAuth2PasswordRequestForm expects form-encoded body (x-www-form-urlencoded)
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      const errorMsg = data.detail || "Login failed. Check your credentials.";
      showAlert(errorMsg, "error");
      return;
    }

    // Save JWT token in browser storage
    localStorage.setItem("access_token", data.access_token);
    showAlert("Login successful!", "success");
    loginForm.reset();

    // Fetch user details from protected /auth/me route
    await fetchUserProfile(data.access_token);

  } catch (error) {
    showAlert("Could not connect to the backend server. Is FastAPI running?", "error");
  } finally {
    loginBtn.disabled = false;
    loginBtn.textContent = "Log In";
  }
}

// -------------------------------------------------------------
// 3. FETCH PROFILE (GET /auth/me)
// -------------------------------------------------------------
async function fetchUserProfile(token) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      localStorage.removeItem("access_token");
      switchView("login");
      return;
    }

    const userData = await response.json();
    document.getElementById("user-id").textContent = userData.id;
    document.getElementById("user-username").textContent = userData.username;
    document.getElementById("user-email").textContent = userData.email;

    switchView("profile");
  } catch (error) {
    showAlert("Failed to load user profile.", "error");
  }
}

// -------------------------------------------------------------
// 4. FORGOT PASSWORD HANDLER (POST /auth/forgot-password)
// (Template for your backend implementation)
// -------------------------------------------------------------
async function handleForgotPassword(event) {
  event.preventDefault();
  clearAlert();

  const email = document.getElementById("forgot-email").value.trim();
  const forgotBtn = document.getElementById("forgot-btn");

  forgotBtn.disabled = true;
  forgotBtn.textContent = "Sending OTP...";

  try {
    // When you implement POST /auth/forgot-password in FastAPI:
    const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email }),
    });

    const data = await response.json();

    if (!response.ok) {
      const errorMsg = data.detail || "Failed to send reset OTP.";
      showAlert(errorMsg, "error");
      return;
    }

    showAlert("OTP sent successfully to your email!", "success");
    setTimeout(() => {
      switchView("otp");
      document.getElementById("otp-email").value = email;
    }, 1500);

  } catch (error) {
    // If backend endpoint is not implemented yet, inform user
    showAlert("Backend endpoint 'POST /auth/forgot-password' is not implemented yet. Ready for you to build!", "info");
    setTimeout(() => {
      switchView("otp");
      document.getElementById("otp-email").value = email;
    }, 2000);
  } finally {
    forgotBtn.disabled = false;
    forgotBtn.textContent = "Send OTP";
  }
}

// -------------------------------------------------------------
// 5. VERIFY OTP & RESET PASSWORD (POST /auth/reset-password)
// (Template for your backend implementation)
// -------------------------------------------------------------
async function handleVerifyOtpAndReset(event) {
  event.preventDefault();
  clearAlert();

  const email = document.getElementById("otp-email").value.trim();
  const otp = document.getElementById("otp-code").value.trim();
  const newPassword = document.getElementById("otp-new-password").value;
  const confirmPassword = document.getElementById("otp-confirm-password").value;
  const otpBtn = document.getElementById("otp-btn");

  if (newPassword !== confirmPassword) {
    showAlert("Passwords do not match.", "error");
    return;
  }

  otpBtn.disabled = true;
  otpBtn.textContent = "Resetting Password...";

  try {
    // When you implement POST /auth/reset-password in FastAPI:
    const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email,
        otp: otp,
        new_password: newPassword,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      const errorMsg = data.detail || "Failed to reset password. Invalid OTP.";
      showAlert(errorMsg, "error");
      return;
    }

    showAlert("Password reset successful! Please log in with your new password.", "success");
    otpForm.reset();
    setTimeout(() => {
      switchView("login");
    }, 1500);

  } catch (error) {
    showAlert("Backend endpoint 'POST /auth/reset-password' is not implemented yet. Ready for you to build!", "info");
  } finally {
    otpBtn.disabled = false;
    otpBtn.textContent = "Reset Password";
  }
}

// -------------------------------------------------------------
// 6. LOGOUT HANDLER
// -------------------------------------------------------------
function handleLogout() {
  localStorage.removeItem("access_token");
  switchView("login");
  showAlert("You have been logged out.", "info");
}

// Check session on page load
window.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("access_token");
  if (token) {
    fetchUserProfile(token);
  } else {
    switchView("login");
  }
});
