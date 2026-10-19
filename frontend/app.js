
const API_URL = "/api/users";

const form = document.getElementById("user-form");
const userIdInput = document.getElementById("user-id");
const nameInput = document.getElementById("name");
const emailInput = document.getElementById("email");
const usersBody = document.getElementById("users-body");
const message = document.getElementById("message");
const emptyMessage = document.getElementById("empty-message");
const submitBtn = document.getElementById("submit-btn");
const cancelBtn = document.getElementById("cancel-btn");

let usersCache = [];

function showMessage(text, isError = false) {
  message.textContent = text;
  message.className = isError ? "error" : "success";
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }

  return data;
}

async function loadUsers() {
  try {
    usersCache = await apiRequest(API_URL);
    usersBody.replaceChildren();

    for (const user of usersCache) {
      const row = document.createElement("tr");

      for (const value of [user.id, user.name, user.email]) {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.appendChild(cell);
      }

      const actions = document.createElement("td");

      const editBtn = document.createElement("button");
      editBtn.textContent = "Edit";
      editBtn.className = "edit";
      editBtn.addEventListener("click", () => editUser(user.id));

      const deleteBtn = document.createElement("button");
      deleteBtn.textContent = "Delete";
      deleteBtn.className = "delete";
      deleteBtn.addEventListener("click", () => deleteUser(user.id));

      actions.append(editBtn, deleteBtn);
      row.appendChild(actions);
      usersBody.appendChild(row);
    }

    emptyMessage.textContent =
      usersCache.length === 0 ? "No users registered yet." : "";

  } catch (error) {
    emptyMessage.textContent = "Unable to load users.";
    showMessage(error.message, true);
  }
}

function resetForm() {
  form.reset();
  userIdInput.value = "";
  submitBtn.textContent = "Add User";
  cancelBtn.hidden = true;
  document.getElementById("form-title").textContent =
    "Add New User";
}

function editUser(id) {
  const user = usersCache.find(u => u.id === id);
  if (!user) return;

  userIdInput.value = user.id;
  nameInput.value = user.name;
  emailInput.value = user.email;

  submitBtn.textContent = "Update User";
  cancelBtn.hidden = false;
  document.getElementById("form-title").textContent =
    "Edit User";

  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function deleteUser(id) {
  if (!confirm("Are you sure you want to delete this user?")) {
    return;
  }

  try {
    await apiRequest(`${API_URL}/${id}`, {
      method: "DELETE"
    });

    showMessage("User deleted successfully.");
    resetForm();
    await loadUsers();
  } catch (error) {
    showMessage(error.message, true);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const id = userIdInput.value;

  const payload = {
    name: nameInput.value.trim(),
    email: emailInput.value.trim()
  };

  try {
    submitBtn.disabled = true;

    await apiRequest(id ? `${API_URL}/${id}` : API_URL, {
      method: id ? "PUT" : "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    resetForm();
    await loadUsers();
    showMessage(id ? "User updated successfully." :
                     "User added successfully.");

  } catch (error) {
    showMessage(error.message, true);
  } finally {
    submitBtn.disabled = false;
  }
});

cancelBtn.addEventListener("click", resetForm);

document.getElementById("refresh-btn")
  .addEventListener("click", loadUsers);

loadUsers();
