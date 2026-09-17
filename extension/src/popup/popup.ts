// AI Master Tutor - Popup UI Controller

interface InspectionResponse {
  detected: boolean;
  platform: string;
  title: string;
  charCount: number;
}

interface IngestResponse {
  success: boolean;
  data?: unknown;
  error?: string;
}

const displayTitle = document.getElementById("display-title") as HTMLDivElement;
const metricPlatform = document.getElementById("metric-platform") as HTMLSpanElement;
const metricChars = document.getElementById("metric-chars") as HTMLSpanElement;
const badgePlatform = document.getElementById("badge-platform") as HTMLDivElement;
const btnExtract = document.getElementById("btn-extract") as HTMLButtonElement;

const panelLoading = document.getElementById("panel-loading") as HTMLDivElement;
const panelSuccess = document.getElementById("panel-success") as HTMLDivElement;
const panelError = document.getElementById("panel-error") as HTMLDivElement;
const errorMessage = document.getElementById("error-message") as HTMLDivElement;
const btnRetry = document.getElementById("btn-retry") as HTMLButtonElement;

let activeTabId: number | null = null;

function resetPanels(): void {
  panelLoading.className = "status-panel";
  panelSuccess.className = "status-panel";
  panelError.className = "status-panel";
}

async function inspectActiveTab(): Promise<void> {
  resetPanels();
  btnExtract.disabled = true;

  try {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tabs || tabs.length === 0 || !tabs[0].id) {
      displayTitle.textContent = "No se detectó pestaña activa.";
      return;
    }

    activeTabId = tabs[0].id;

    // Send check message to content script
    chrome.tabs.sendMessage(
      activeTabId,
      { action: "CHECK_CONTENT" },
      (response: InspectionResponse) => {
        if (chrome.runtime.lastError || !response) {
          displayTitle.textContent = "Sin contenido detectable o página restringida.";
          metricPlatform.textContent = "Plataforma: N/A";
          metricChars.textContent = "0 caracteres";
          return;
        }

        displayTitle.textContent = response.title || "Material sin título";
        metricPlatform.textContent = `Plataforma: ${response.platform.toUpperCase()}`;
        metricChars.textContent = `${response.charCount.toLocaleString()} caracteres`;

        badgePlatform.textContent = response.platform.toUpperCase();
        badgePlatform.className = "badge-status active";

        if (response.detected && response.charCount > 30) {
          btnExtract.disabled = false;
        } else {
          displayTitle.textContent = "Contenido insuficiente para extraer.";
        }
      }
    );
  } catch (err) {
    displayTitle.textContent = "Error al comunicarse con la pestaña.";
  }
}

async function triggerExtraction(): Promise<void> {
  if (!activeTabId) return;

  btnExtract.disabled = true;
  resetPanels();
  panelLoading.className = "status-panel loading";

  // 1. Request full extracted payload from content script
  chrome.tabs.sendMessage(
    activeTabId,
    { action: "EXTRACT_CONTENT" },
    (payload) => {
      if (chrome.runtime.lastError || !payload) {
        panelLoading.className = "status-panel";
        panelError.className = "status-panel error";
        errorMessage.textContent = "Error al leer el DOM de la página activa.";
        btnExtract.disabled = false;
        return;
      }

      // 2. Delegate HTTP POST request to background worker
      chrome.runtime.sendMessage(
        { action: "SEND_TO_BACKEND", payload },
        (response: IngestResponse) => {
          panelLoading.className = "status-panel";

          if (response && response.success) {
            panelSuccess.className = "status-panel success";
            btnExtract.textContent = "Ingesta Completada";
          } else {
            panelError.className = "status-panel error";
            errorMessage.textContent =
              response?.error || "Error de red desconocido al conectar con FastAPI.";
            btnExtract.disabled = false;
          }
        }
      );
    }
  );
}

document.addEventListener("DOMContentLoaded", () => {
  inspectActiveTab();

  btnExtract.addEventListener("click", triggerExtraction);
  btnRetry.addEventListener("click", triggerExtraction);
});
