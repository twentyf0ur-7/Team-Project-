const API = "http://localhost:8000"

if (!localStorage.getItem("token")) {
  window.location.href = "login.html"
}

const tasksEl = document.getElementById("tasks")
const title = document.getElementById("title")
const desc = document.getElementById("desc")

function getToken() {
  return localStorage.getItem("token")
}

async function loadTasks() {
  try {
    const res = await fetch(API + "/tasks", {
      headers: { Authorization: "Bearer " + getToken() }
    })

    if (!res.ok) throw new Error()

    const tasks = await res.json()
    tasksEl.innerHTML = ""

    if (tasks.length === 0) {
      tasksEl.innerHTML = "<li>No tasks yet</li>"
      return
    }

    tasks.forEach(t => {
      tasksEl.innerHTML += `
        <li class="${t.completed ? "done" : ""}">
          <strong>${t.title}</strong><br>
          <small>${t.description || ""}</small><br>
          <button onclick="complete(${t.id})">Done</button>
          <button onclick="del(${t.id})">Delete</button>
        </li>
      `
    })
  } catch {
    tasksEl.innerHTML = "<li>Error loading tasks</li>"
  }
}

async function addTask() {
  if (!title.value) return alert("Title required")

  await fetch(API + "/tasks", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + getToken()
    },
    body: JSON.stringify({
      title: title.value,
      description: desc.value
    })
  })

  title.value = ""
  desc.value = ""
  loadTasks()
}

async function del(id) {
  await fetch(API + `/tasks/${id}`, {
    method: "DELETE",
    headers: { Authorization: "Bearer " + getToken() }
  })
  loadTasks()
}

async function complete(id) {
  await fetch(API + `/tasks/${id}/complete`, {
    method: "PATCH",
    headers: { Authorization: "Bearer " + getToken() }
  })
  loadTasks()
}

function logout() {
  localStorage.removeItem("token")
  window.location.replace("login.html")
}

async function addToCart(id, name, price) {
        const token = localStorage.getItem("token");

        await fetch(API + "/cart/add", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + token, //
          },
          body: JSON.stringify({ product_id: id, quantity: 1 }),
        });

        loadUserCart();
      }

loadTasks()