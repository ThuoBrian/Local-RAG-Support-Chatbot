(() => {
    "use strict";

    const WELCOME_TEXT =
        "Hello! I'm the **IT Support Knowledge Assistant**. " +
        "I can answer questions based on the support model trained.\n\n" +
        "Ask me about procedures, troubleshooting steps, or any documented IT processes.";

    const messagesEl = document.getElementById("messages");
    const chatForm = document.getElementById("chat-form");
    const messageInput = document.getElementById("message-input");
    const sendBtn = document.getElementById("send-btn");
    const newChatBtn = document.getElementById("new-chat-btn");
    const emptyState = document.getElementById("empty-state");

    let sessionId = sessionStorage.getItem("session_id") || generateSessionId();
    if (!sessionStorage.getItem("session_id")) {
        sessionStorage.setItem("session_id", sessionId);
    }
    let isStreaming = false;

    // Auto-resize textarea
    messageInput.addEventListener("input", () => {
        messageInput.style.height = "auto";
        messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
        updateSendButton();
    });

    // Send button state
    function updateSendButton() {
        sendBtn.disabled = !messageInput.value.trim() || isStreaming;
    }

    // Enter to send (Shift+Enter for newline)
    messageInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event("submit"));
        }
    });

    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = messageInput.value.trim();
        if (!text || isStreaming) return;
        messageInput.value = "";
        messageInput.style.height = "auto";
        updateSendButton();
        addUserMessage(text);
        streamResponse(text);
    });

    // Suggestion chips
    document.querySelectorAll(".suggestion-card").forEach((chip) => {
        chip.addEventListener("click", () => {
            const query = chip.getAttribute("data-query");
            messageInput.value = query;
            messageInput.style.height = "auto";
            messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
            updateSendButton();
            chatForm.dispatchEvent(new Event("submit"));
        });
    });

    newChatBtn.addEventListener("click", () => {
        sessionId = generateSessionId();
        sessionStorage.setItem("session_id", sessionId);
        while (messagesEl.firstChild) {
            messagesEl.removeChild(messagesEl.firstChild);
        }
        if (emptyState) {
            emptyState.classList.remove("hidden");
            messagesEl.appendChild(emptyState);
        }
        addAssistantMessage(WELCOME_TEXT);
        messageInput.focus();
    });

    function generateSessionId() {
        return crypto.randomUUID ? crypto.randomUUID() : "sess-" + Date.now() + "-" + Math.random().toString(36).slice(2);
    }

    function hideEmptyState() {
        if (emptyState && !emptyState.classList.contains("hidden")) {
            emptyState.classList.add("hidden");
        }
    }

    function addUserMessage(text) {
        hideEmptyState();
        const wrapper = document.createElement("div");
        wrapper.className = "message-wrapper user";
        const bubble = document.createElement("div");
        bubble.className = "message-bubble";
        bubble.textContent = text;
        wrapper.appendChild(bubble);
        messagesEl.appendChild(wrapper);
        scrollToBottom();
    }

    function addAssistantMessage(content) {
        hideEmptyState();
        const wrapper = document.createElement("div");
        wrapper.className = "message-wrapper assistant";
        const bubble = document.createElement("div");
        bubble.className = "message-bubble";
        bubble.innerHTML = DOMPurify.sanitize(marked.parse(content));
        wrapper.appendChild(bubble);
        messagesEl.appendChild(wrapper);
        scrollToBottom();
        return wrapper;
    }

    function createStreamingAssistant() {
        hideEmptyState();
        const wrapper = document.createElement("div");
        wrapper.className = "message-wrapper assistant";

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";
        wrapper.appendChild(bubble);

        // Typing indicator
        const typing = document.createElement("div");
        typing.className = "typing-indicator";
        typing.innerHTML = "<span></span><span></span><span></span>";
        bubble.appendChild(typing);

        messagesEl.appendChild(wrapper);
        scrollToBottom();
        return { wrapper, bubble, typing };
    }

    async function streamResponse(message) {
        isStreaming = true;
        updateSendButton();

        const { wrapper, bubble, typing } = createStreamingAssistant();
        let currentSources = null;
        let fullText = "";
        let currentEvent = "";

        function processLine(line) {
            const trimmed = line.replace(/\r$/, "");
            if (trimmed.startsWith("event: ")) {
                currentEvent = trimmed.slice(7);
            } else if (trimmed.startsWith("data: ")) {
                const data = trimmed.slice(6);

                if (currentEvent === "sources") {
                    currentSources = JSON.parse(data);
                } else if (currentEvent === "token") {
                    const token = JSON.parse(data);
                    fullText += token;

                    if (typing && typing.parentNode) {
                        typing.remove();
                    }

                    bubble.innerHTML = DOMPurify.sanitize(marked.parse(fullText));
                    scrollToBottom();
                } else if (currentEvent === "error") {
                    if (typing && typing.parentNode) {
                        typing.remove();
                    }
                    bubble.className = "message-bubble error-bubble";
                    bubble.textContent = JSON.parse(data);
                    scrollToBottom();
                } else if (currentEvent === "done") {
                    if (typing && typing.parentNode) {
                        typing.remove();
                    }
                    if (fullText) {
                        bubble.innerHTML = DOMPurify.sanitize(marked.parse(fullText));
                    }
                }
            }
        }

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message, session_id: sessionId }),
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop() || "";

                for (const line of lines) {
                    processLine(line);
                }
            }

            // Process any remaining buffer content
            if (buffer.startsWith("data: ")) {
                processLine(buffer);
            }
        } catch (err) {
            if (typing && typing.parentNode) {
                typing.remove();
            }
            bubble.className = "message-bubble error-bubble";
            bubble.textContent = "Connection error. Please try again.";
        } finally {
            isStreaming = false;
            updateSendButton();
            messageInput.focus();
            scrollToBottom();
        }
    }

    function scrollToBottom() {
        const threshold = 100;
        const nearBottom =
            messagesEl.scrollHeight - messagesEl.scrollTop - messagesEl.clientHeight < threshold;
        if (nearBottom) {
            messagesEl.scrollTop = messagesEl.scrollHeight;
        }
    }

    // Show welcome message on load
    addAssistantMessage(WELCOME_TEXT);
    messageInput.focus();
})();
