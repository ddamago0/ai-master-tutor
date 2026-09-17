// AI Master Tutor - DOM Content Extractor (Content Script Runtime)

const LMS_CONTENT_SELECTORS = [
  "#region-main",
  ".course-content",
  ".activity-information",
  "[role='main']",
  "#divContenido",
  ".contenido-clase",
  ".q10-content",
  "#content.ic-Layout-contentMain",
  "#main",
  "main",
  "article",
];

const NOISE_SELECTORS = [
  "nav",
  "header",
  "footer",
  "aside",
  "script",
  "style",
  "noscript",
  "iframe",
  "svg",
  "button",
  "form",
  ".nav",
  ".navbar",
  ".sidebar",
  ".menu",
  ".breadcrumb",
  ".breadcrumbs",
  ".pagination",
  ".footer",
  ".popover",
  ".modal",
  ".user-profile",
  ".block-myoverview",
  ".drawer",
];

function detectPlatform() {
  const host = window.location.hostname.toLowerCase();
  const html = document.documentElement.innerHTML;

  if (
    host.includes("moodle") ||
    document.body.classList.contains("format-topics") ||
    document.body.classList.contains("format-weeks") ||
    document.getElementById("region-main") !== null ||
    html.includes("moodle")
  ) {
    return "moodle";
  }

  if (
    host.includes("q10") ||
    document.querySelector(".q10-content") !== null ||
    document.getElementById("divContenido") !== null
  ) {
    return "q10";
  }

  if (host.includes("instructure") || document.getElementById("breadcrumbs") !== null) {
    return "canvas";
  }

  return "manual";
}

function extractPageTitle() {
  const h1 = document.querySelector("main h1, #region-main h1, .page-header-headings h1, h1");
  if (h1 && h1.textContent && h1.textContent.trim()) {
    return h1.textContent.trim();
  }

  let title = document.title || "Material de Estudio";
  title = title.split(/[|\-–:]/)[0].trim();
  return title || "Material de Estudio";
}

function extractCleanDOMText() {
  let targetElement = null;
  let selectorUsed = "body";

  for (const selector of LMS_CONTENT_SELECTORS) {
    const el = document.querySelector(selector);
    if (el && (el.textContent?.trim().length || 0) > 100) {
      targetElement = el;
      selectorUsed = selector;
      break;
    }
  }

  if (!targetElement) {
    targetElement = document.body;
  }

  const clone = targetElement.cloneNode(true);

  for (const noiseSelector of NOISE_SELECTORS) {
    const noiseNodes = clone.querySelectorAll(noiseSelector);
    noiseNodes.forEach((node) => node.remove());
  }

  const rawText = clone.innerText || clone.textContent || "";
  const clean = rawText
    .replace(/\r\n|\r/g, "\n")
    .replace(/[ \t]+/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  return { text: clean, selectorUsed };
}

chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
  if (request.action === "CHECK_CONTENT") {
    const { text } = extractCleanDOMText();
    sendResponse({
      detected: text.length > 50,
      platform: detectPlatform(),
      title: extractPageTitle(),
      charCount: text.length,
    });
    return true;
  }

  if (request.action === "EXTRACT_CONTENT") {
    const { text, selectorUsed } = extractCleanDOMText();
    const platform = detectPlatform();
    const title = extractPageTitle();

    sendResponse({
      title: title,
      rawContent: text,
      sourceType: platform,
      sourceUrl: window.location.href,
      metadata: {
        extractedAt: new Date().toISOString(),
        host: window.location.hostname,
        selectorUsed: selectorUsed,
        charCount: text.length,
      },
    });
    return true;
  }
});
