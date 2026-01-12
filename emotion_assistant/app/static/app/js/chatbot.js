function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    addMessage("You", message);
    input.value = "";

    fetch("/chatbot/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({ message })
    })
    .then(res => res.json())
    .then(data => addMessage("AI", data.reply))
    .catch(() => addMessage("AI", "Something went wrong."));
}

function addMessage(sender, text) {
    const box = document.getElementById("chat-box");
    box.innerHTML += `<p><strong>${sender}:</strong> ${text}</p>`;
    box.scrollTop = box.scrollHeight;
}

function getCSRFToken() {
    return document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken"))
        ?.split("=")[1];
}
