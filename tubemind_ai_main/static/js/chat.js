// =============================
// CHAT UI OPEN / CLOSE
// =============================
const btn = document.getElementById("chat-btn");
const box = document.getElementById("chat-box");
const closeBtn = document.getElementById("chat-close");

btn.onclick = () => {
    box.style.display = "flex";
};

closeBtn.onclick = () => {
    box.style.display = "none";
};


// =============================
// TEXT TO SPEECH (FIXED)
// =============================
function speakText(text) {
    if (!window.speechSynthesis) return;

    window.speechSynthesis.cancel();

    const speech = new SpeechSynthesisUtterance(text);

    const lang = document.getElementById("chat-lang")?.value || "en-US";
    speech.lang = lang;
    speech.rate = 1;
    speech.pitch = 1;

    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(v => v.lang.includes(lang));
    if (preferred) speech.voice = preferred;

    window.speechSynthesis.speak(speech);
}


// =============================
// CHAT SEND WITH TYPING + TTS (FIXED)
// =============================
let isSending = false;

document.getElementById("chat-send").onclick = async () => {

    if (isSending) return;
    isSending = true;

    const input = document.getElementById("chat-input");
    const msg = input.value.trim();
    const lang = document.getElementById("chat-lang").value;

    if (!msg) {
        isSending = false;
        return;
    }

    const body = document.getElementById("chat-messages");

    // USER MESSAGE
    body.innerHTML += `<div class='msg user'>${msg}</div>`;
    input.value = "";
    body.scrollTop = body.scrollHeight;

    // BOT MESSAGE
    let botMsgEl = document.createElement("div");
    botMsgEl.classList.add("msg", "bot");
    botMsgEl.innerHTML = "Typing...";
    body.appendChild(botMsgEl);

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg, language: lang })
        });

        const data = await res.json();
        const fullReply = data.reply || "⚠️ No response";

        // TYPING EFFECT
        let index = 0;
        botMsgEl.innerHTML = "";

        function typeChar() {
            if (index < fullReply.length) {
                botMsgEl.innerHTML += fullReply.charAt(index);
                index++;
                body.scrollTop = body.scrollHeight;
                setTimeout(typeChar, 15);
            } else {
                speakText(fullReply); // 🔊 speak after complete
            }
        }

        typeChar();

    } catch (err) {
        botMsgEl.innerHTML = "⚠️ Error fetching response";
        console.error(err);
    }

    isSending = false;
};


// =============================
// SPEECH TO TEXT (FIXED)
// =============================
const micBtn = document.getElementById("chat-mic-btn");
const inputField = document.getElementById("chat-input");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

let recognition;
let isListening = false;

if (SpeechRecognition && micBtn) {

    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    micBtn.onclick = () => {

        if (isListening) {
            recognition.stop();
            micBtn.innerText = "🎤";
            isListening = false;
        } else {
            recognition.lang = document.getElementById("chat-lang").value || "en-US";
            recognition.start();
            micBtn.innerText = "🛑";
            isListening = true;
        }
    };

    recognition.onstart = () => {
        console.log("🎤 Listening...");
    };

    recognition.onresult = (event) => {
        let transcript = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }

        inputField.value = transcript;
    };

    recognition.onend = () => {
        console.log("🎤 Stopped");

        if (inputField.value.trim()) {
            document.getElementById("chat-send").click();
        }

        micBtn.innerText = "🎤";
        isListening = false;
    };

    recognition.onerror = (event) => {
        console.error("Speech error:", event.error);

        if (event.error === "not-allowed") {
            alert("Microphone permission denied.");
        }

        micBtn.innerText = "🎤";
        isListening = false;
    };
}


// =============================
// ASK PAGE SUPPORT (ADDED FIX)
// =============================
function startAskMic() {

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert("Speech not supported");
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;

    recognition.start();

    recognition.onresult = (event) => {
        const speech = event.results[0][0].transcript;

        const input = document.getElementById("question-input");
        if (input) {
            input.value = speech;

            // auto trigger ask
            if (typeof askStreaming === "function") {
                askStreaming();
            }
        }
    };

    recognition.onerror = () => {
        alert("Mic error");
    };
}


// =============================
// EXISTING FUNCTIONS (UNCHANGED)
// =============================
async function sendMessage() {
    const input = document.getElementById("chat-input");
    const question = input.value.trim();

    if (!question) return;

    const response = await fetch("/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question})
    });

    const data = await response.json();

    displayMessage(question, "user");
    displayMessage(data.answer || data.error, "bot");

    input.value = "";
}

function displayMessage(text, type) {
    const body = document.getElementById("chat-messages");

    const msg = document.createElement("div");
    msg.classList.add("msg", type);
    msg.innerText = text;

    body.appendChild(msg);
    body.scrollTop = body.scrollHeight;
}

async function loadTranscript() {
    const url = document.getElementById("url").value;

    const loader = document.getElementById("loader");
    loader.innerText = "⏳ Processing video... please wait";

    const res = await fetch("/transcript", {
        method: "POST",
        body: new URLSearchParams({ url })
    });

    const data = await res.json();

    if (data.error) {
        loader.innerText = "❌ " + data.error;
    } else {
        loader.innerText = "✅ Transcript ready!";
    }
}