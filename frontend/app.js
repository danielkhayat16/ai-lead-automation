const API_URL = window.location.origin;

const form = document.querySelector("#lead-form");
const state = document.querySelector("#state");
const empty = document.querySelector("#empty");
const output = document.querySelector("#output");
const errorBox = document.querySelector("#error");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  state.textContent = "ANALYZING";
  errorBox.hidden = true;

  const data = Object.fromEntries(new FormData(form).entries());
  data.employees = data.employees ? Number(data.employees) : null;

  try {
    const response = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data),
    });

    if (!response.ok) throw new Error(`API returned ${response.status}`);

    const result = await response.json();
    document.querySelector("#priority").textContent = result.priority;
    document.querySelector("#category").textContent = result.category;
    document.querySelector("#budget").textContent =
      result.budget_eur ? `€${result.budget_eur.toLocaleString()}` : "Not provided";
    document.querySelector("#need").textContent = result.need;
    document.querySelector("#summary").textContent = result.summary;
    document.querySelector("#action").textContent = result.suggested_action;

    empty.hidden = true;
    output.hidden = false;
    state.textContent = "DONE";
  } catch (error) {
    output.hidden = true;
    empty.hidden = true;
    errorBox.hidden = false;
    errorBox.textContent =
      "Could not reach the API. Start the FastAPI backend first, then try again.";
    state.textContent = "ERROR";
  }
});
