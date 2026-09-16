// Background service worker for extension event dispatching
chrome.runtime.onInstalled.addListener(() => {
  console.log("[AI Master Tutor] Background service worker initialized");
});
