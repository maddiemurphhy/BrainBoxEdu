/**
 * Login page behavior.
 *
 * Right now this is a MOCK login: it validates the form and pretends
 * to call a server (with a short fake delay), but there's no real
 * backend auth wired up yet. Every spot that will need to change once
 * real login exists is marked with "TODO(real-auth)" so it's easy to
 * find later with a quick search.
 */

// Grabbing every element we'll need once, up top, instead of
// re-querying the DOM each time -- small performance habit, but
// mostly it just makes the code below easier to read.
const form = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const emailError = document.getElementById("email-error");
const passwordError = document.getElementById("password-error");
const formError = document.getElementById("form-error");
const submitButton = document.getElementById("submit-button");
const togglePasswordButton = document.getElementById("toggle-password");

// --- Show/hide password -------------------------------------------------

togglePasswordButton.addEventListener("click", () => {
  const isHidden = passwordInput.type === "password";
  passwordInput.type = isHidden ? "text" : "password";
  togglePasswordButton.textContent = isHidden ? "Hide" : "Show";
  togglePasswordButton.setAttribute("aria-label", isHidden ? "Hide password" : "Show password");
});

// --- Validation ----------------------------------------------------------

function validateEmail(value) {
  if (!value.trim()) return "Email is required.";
  // A simple, deliberately loose check -- good enough to catch typos
  // like a missing "@" without trying to be a full email-spec validator.
  const looksLikeEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
  if (!looksLikeEmail) return "Enter a valid email address.";
  return null;
}

function validatePassword(value) {
  if (!value) return "Password is required.";
  if (value.length < 6) return "Password must be at least 6 characters.";
  return null;
}

function showFieldError(inputEl, errorEl, message) {
  if (message) {
    inputEl.classList.add("invalid");
    errorEl.textContent = message;
  } else {
    inputEl.classList.remove("invalid");
    errorEl.textContent = "";
  }
}

// --- Form submit ----------------------------------------------------------

form.addEventListener("submit", async (event) => {
  event.preventDefault(); // stop the browser's default full-page form submit

  formError.hidden = true;

  const emailMessage = validateEmail(emailInput.value);
  const passwordMessage = validatePassword(passwordInput.value);

  showFieldError(emailInput, emailError, emailMessage);
  showFieldError(passwordInput, passwordError, passwordMessage);

  if (emailMessage || passwordMessage) {
    return; // stop here -- don't even attempt "login" with invalid input
  }

  setLoading(true);

  try {
    // TODO(real-auth): replace this mock with something like:
    //   const response = await fetch("http://127.0.0.1:8000/auth/login", {
    //     method: "POST",
    //     headers: { "Content-Type": "application/json" },
    //     body: JSON.stringify({ email: emailInput.value, password: passwordInput.value }),
    //   });
    //   if (!response.ok) { throw new Error("Invalid email or password."); }
    //   const data = await response.json();  // e.g. { token: "..." }
    const result = await mockLoginRequest(emailInput.value, passwordInput.value);
    showSuccess(result.email);
  } catch (err) {
    formError.textContent = err.message || "Something went wrong. Please try again.";
    formError.hidden = false;
  } finally {
    setLoading(false);
  }
});

/**
 * Pretends to be a network call to a login endpoint. Resolves after a
 * short delay so the loading state is actually visible, instead of
 * flashing by instantly -- that's useful for seeing what the UI feels
 * like once a real, slightly-slower network request is in its place.
 *
 * TODO(real-auth): delete this function entirely once a real endpoint exists.
 */
function mockLoginRequest(email, password) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Simple fake rule just so there's something to see both
      // success AND failure with while testing: any password that
      // literally contains the word "wrong" simulates a failed login.
      if (password.toLowerCase().includes("wrong")) {
        reject(new Error("Incorrect email or password."));
      } else {
        resolve({ email });
      }
    }, 900);
  });
}

function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  submitButton.textContent = isLoading ? "Logging in…" : "Log in";
}

function showSuccess(email) {
  // TODO(real-auth): sessionStorage is a stand-in for a real session/token
  // until real auth exists -- dashboard.js checks this same flag before
  // showing anything.
  sessionStorage.setItem("bbe_logged_in", "1");
  sessionStorage.setItem("bbe_user_email", email);
  window.location.href = "dashboard.html";
}
