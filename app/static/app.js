(function () {
  "use strict";

  const form = document.getElementById("chat-form");
  const input = document.getElementById("question");
  const messages = document.getElementById("messages");
  const emptyState = document.getElementById("empty-state");
  const submitBtn = form.querySelector("button");

  document.querySelectorAll(".examples button").forEach((btn) => {
    btn.addEventListener("click", () => {
      input.value = btn.dataset.q;
      form.dispatchEvent(new Event("submit"));
    });
  });

  function addMessage(role, text) {
    const el = document.createElement("div");
    el.className = `msg ${role}`;
    el.textContent = text;
    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
    return el;
  }

  function addSources(sources) {
    if (!sources || !sources.length) return;
    const el = document.createElement("div");
    el.className = "sources";
    el.innerHTML = sources
      .map((s) => `<span class="tag">source: ${s}</span>`)
      .join("");
    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
  }

  async function sendQuestion(question) {
    if (emptyState) emptyState.remove();
    addMessage("user", question);
    submitBtn.disabled = true;

    const assistantEl = addMessage("assistant", "");
    const cursor = document.createElement("span");
    cursor.className = "cursor";
    assistantEl.appendChild(cursor);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let fullText = "";
      let pendingSources = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const payload = line.slice(6);
          if (payload === "[DONE]") continue;

          const event = JSON.parse(payload);
          if (event.type === "text") {
            fullText += event.text;
            assistantEl.textContent = fullText;
            assistantEl.appendChild(cursor);
            messages.scrollTop = messages.scrollHeight;
          } else if (event.type === "sources") {
            pendingSources = event.sources;
          } else if (event.type === "error") {
            assistantEl.remove();
            addMessage("error", event.message);
          }
        }
      }

      addSources(pendingSources);
    } catch (err) {
      addMessage("error", "Erreur réseau : impossible de contacter le serveur.");
    } finally {
      cursor.remove();
      submitBtn.disabled = false;
    }
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const question = input.value.trim();
    if (!question) return;
    input.value = "";
    sendQuestion(question);
  });
})();
