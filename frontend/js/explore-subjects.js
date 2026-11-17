/**
 * Explore Subjects is a holder page for now -- there's no real subject
 * list or search behind it yet. This just gives clicking "Search" (or
 * clicking one of the subject cards below) honest, visible feedback
 * ("coming soon") instead of the page doing nothing and leaving the
 * user wondering if it's broken.
 *
 * TODO(subjects-feature): replace this with a real search against
 * whatever subjects/categories list the app ends up having.
 */
const form = document.getElementById("subject-search-form");
const searchInput = document.getElementById("subject-search-input");
const note = document.getElementById("placeholder-note");
const subjectCards = document.querySelectorAll(".subject-card");

function showComingSoon() {
  note.textContent = "Subject search is coming soon — for now, jump into Start Learning to upload your own notes.";
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  showComingSoon();
});

// Clicking a subject card drops its name into the search bar and shows
// the same message, so the cards feel connected to the search above
// them rather than like a second, unrelated widget on the page.
subjectCards.forEach((card) => {
  card.addEventListener("click", () => {
    searchInput.value = card.dataset.subject;
    searchInput.focus();
    showComingSoon();
  });
});
