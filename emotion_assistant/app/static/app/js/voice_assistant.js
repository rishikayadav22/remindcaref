document.addEventListener("DOMContentLoaded", function () {

    const voiceBtn = document.getElementById("voiceBtn");
    const statusText = document.getElementById("assistantStatus");

    if (!voiceBtn || !statusText) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        statusText.innerText = "❌ Voice Assistant not supported";
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;

    voiceBtn.addEventListener("click", () => {
        statusText.innerText = "🎙 Listening...";
        recognition.start();
    });

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        statusText.innerText = "You said: " + text;
        sendToBackend(text);
    };

    recognition.onerror = (event) => {
        statusText.innerText = "❌ Error: " + event.error;
    };

    function sendToBackend(text) {
        fetch("/voice-assistant/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ message: text })
        })
        .then(res => res.json())
        .then(data => speak(data.reply));
    }

    function speak(text) {
        const speech = new SpeechSynthesisUtterance(text);
        speech.lang = "en-US";
        window.speechSynthesis.speak(speech);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            document.cookie.split(";").forEach(cookie => {
                const c = cookie.trim();
                if (c.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(c.substring(name.length + 1));
                }
            });
        }
        return cookieValue;
    }
});
