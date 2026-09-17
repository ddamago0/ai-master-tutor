// AI Master Tutor - Background Service Worker (Runtime)

const BACKEND_INGEST_URL = "http://localhost:8000/api/v1/materials/ingest";

chrome.runtime.onInstalled.addListener(() => {
  console.log("[AI Master Tutor] Service Worker active");
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.action === "SEND_TO_BACKEND") {
    const payload = message.payload;

    fetch(BACKEND_INGEST_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title: payload.title,
        raw_content: payload.rawContent,
        source_type: payload.sourceType,
        source_url: payload.sourceUrl,
        metadata: payload.metadata,
      }),
    })
      .then(async (response) => {
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            errorData.detail || `Error HTTP ${response.status}: ${response.statusText}`
          );
        }
        return response.json();
      })
      .then((data) => {
        sendResponse({ success: true, data });
      })
      .catch((err) => {
        console.error("[AI Master Tutor] Ingest failed:", err);
        sendResponse({
          success: false,
          error:
            err.message.includes("Failed to fetch") || err.message.includes("NetworkError")
              ? "No se pudo conectar con el backend (http://localhost:8000). ¿Está encendido el servidor FastAPI?"
              : err.message,
        });
      });

    return true; // Keep message port open for async fetch
  }
});
