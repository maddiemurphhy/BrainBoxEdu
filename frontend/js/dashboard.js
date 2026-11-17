/**
 * Dashboard page behavior: upload a file -> see the confidence check ->
 * generate study questions -> view them. Talks to the real backend API
 * (FastAPI, deployed separately from this site).
 *
 * This page assumes a login already happened. Since login.js is still a
 * mock (see its own TODOs), "logged in" just means a sessionStorage flag
 * got set -- good enough to keep someone from landing here directly
 * without going through the login page first.
 */

const API_BASE = "https://brainboxedu-api.vercel.app";

// --- Gate: bounce back to login if we didn't come from a (mock) login ---
if (!sessionStorage.getItem("bbe_logged_in")) {
  window.location.href = "login.html";
}

document.getElementById("logout-button").addEventListener("click", () => {
  sessionStorage.removeItem("bbe_logged_in");
  sessionStorage.removeItem("bbe_document_id");
  window.location.href = "login.html";
});

// --- Elements -------------------------------------------------------------

const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const fileDropLabel = document.getElementById("file-drop-label");
const fileDropText = document.getElementById("file-drop-text");
const uploadButton = document.getElementById("upload-button");
const uploadError = document.getElementById("upload-error");

const confidenceCard = document.getElementById("confidence-card");
const confidenceFilename = document.getElementById("confidence-filename");
const confidenceBadge = document.getElementById("confidence-badge");
const confidenceMessage = document.getElementById("confidence-message");
const numQuestionsInput = document.getElementById("num-questions");
const generateButton = document.getElementById("generate-button");
const generateError = document.getElementById("generate-error");

const questionsCard = document.getElementById("questions-card");
const questionsList = document.getElementById("questions-list");
const uploadAnotherButton = document.getElementById("upload-another-button");

let currentDocumentId = null;

// --- Step 1: Upload ---------------------------------------------------

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) {
    fileDropText.textContent = file.name;
    fileDropLabel.classList.add("has-file");
    uploadButton.disabled = false;
  } else {
    fileDropText.textContent = "Choose a file…";
    fileDropLabel.classList.remove("has-file");
    uploadButton.disabled = true;
  }
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  uploadError.textContent = "";

  const file = fileInput.files[0];
  if (!file) return;

  setUploadLoading(true);

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE}/documents/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const body = await safeJson(response);
      throw new Error(body?.detail || "Upload failed. Please try again.");
    }

    const doc = await response.json();
    currentDocumentId = doc.id;
    sessionStorage.setItem("bbe_document_id", String(doc.id));

    showConfidenceResult(doc);
  } catch (err) {
    uploadError.textContent = err.message || "Something went wrong uploading that file.";
  } finally {
    setUploadLoading(false);
  }
});

function setUploadLoading(isLoading) {
  uploadButton.disabled = isLoading || !fileInput.files[0];
  uploadButton.textContent = isLoading ? "Uploading…" : "Upload";
}

// --- Step 2: Confidence check + generate -------------------------------

function showConfidenceResult(doc) {
  confidenceFilename.textContent = doc.filename;

  const isHigh = doc.confidence_level === "high";
  confidenceBadge.textContent = isHigh ? "High confidence" : "Low confidence";
  confidenceBadge.className = "confidence-badge " + (isHigh ? "high" : "low");
  confidenceMessage.textContent = doc.confidence_message || "";

  generateError.textContent = "";
  confidenceCard.hidden = false;
  questionsCard.hidden = true;
  confidenceCard.scrollIntoView({ behavior: "smooth", block: "start" });
}

generateButton.addEventListener("click", async () => {
  if (!currentDocumentId) return;
  generateError.textContent = "";

  const numQuestions = Math.max(1, Math.min(20, Number(numQuestionsInput.value) || 5));

  setGenerateLoading(true);

  try {
    const response = await fetch(
      `${API_BASE}/documents/${currentDocumentId}/questions/generate`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ num_questions: numQuestions }),
      }
    );

    if (!response.ok) {
      const body = await safeJson(response);
      throw new Error(body?.detail || "Couldn't generate questions. Please try again.");
    }

    const questions = await response.json();
    showQuestions(questions);
  } catch (err) {
    generateError.textContent = err.message || "Something went wrong generating questions.";
  } finally {
    setGenerateLoading(false);
  }
});

function setGenerateLoading(isLoading) {
  generateButton.disabled = isLoading;
  generateButton.textContent = isLoading ? "Generating…" : "Generate Questions";
}

// --- Step 3: Questions list --------------------------------------------

function showQuestions(questions) {
  questionsList.innerHTML = "";

  if (!questions.length) {
    questionsList.innerHTML =
      "<p>No grounded questions came back for this document -- try a file with more readable text.</p>";
  }

  questions.forEach((q, index) => {
    const item = document.createElement("div");
    item.className = "question-item";
    item.innerHTML = `
      <p class="question-text">${index + 1}. ${escapeHtml(q.question_text)}</p>
      <button type="button" class="btn-text reveal-answer-btn">Show answer</button>
      <div class="answer-block" hidden>
        <p class="answer-text">${escapeHtml(q.answer_text)}</p>
        <blockquote class="source-excerpt">"${escapeHtml(q.source_excerpt)}"</blockquote>
      </div>
    `;

    const revealButton = item.querySelector(".reveal-answer-btn");
    const answerBlock = item.querySelector(".answer-block");
    revealButton.addEventListener("click", () => {
      const isHidden = answerBlock.hidden;
      answerBlock.hidden = !isHidden;
      revealButton.textContent = isHidden ? "Hide answer" : "Show answer";
    });

    questionsList.appendChild(item);
  });

  questionsCard.hidden = false;
  questionsCard.scrollIntoView({ behavior: "smooth", block: "start" });
}

uploadAnotherButton.addEventListener("click", () => {
  currentDocumentId = null;
  sessionStorage.removeItem("bbe_document_id");

  fileInput.value = "";
  fileDropText.textContent = "Choose a file…";
  fileDropLabel.classList.remove("has-file");
  uploadButton.disabled = true;

  confidenceCard.hidden = true;
  questionsCard.hidden = true;
  uploadError.textContent = "";
  generateError.textContent = "";

  document.getElementById("upload-card").scrollIntoView({ behavior: "smooth", block: "start" });
});

// --- Small helpers -------------------------------------------------------

async function safeJson(response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
