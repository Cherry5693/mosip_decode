// Use same-origin by default so the app works when served from the backend
// (recommended in Codespaces: open backend preview on port 8000).
const BASE_URL = window.location.origin;

// Handle OCR Extract
const extractForm = document.getElementById("extractForm");
if (extractForm) {
  extractForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("file");
    const file = fileInput?.files?.[0];
    if (!file) {
      alert("Please upload a file first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("docType", extractForm.elements["docType"]?.value || "generic");
    formData.append("language", extractForm.elements["language"]?.value || "eng");
    formData.append("use_handwriting", extractForm.elements["use_handwriting"]?.checked ? "true" : "false");
    formData.append("prefer_trocr", extractForm.elements["prefer_trocr"]?.checked ? "true" : "false");

    try {
      const response = await fetch(`${BASE_URL}/api/ocr/extract`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Extracted data:", data);

      // show results in page
      const out = document.getElementById("verifyOut") || document.getElementById("output");
      if (out) out.innerText = JSON.stringify(data, null, 2);
      document.getElementById("results").style.display = "block";
    } catch (err) {
      console.error("Extract failed", err);
      const out = document.getElementById("verifyOut") || document.getElementById("output");
      if (out) out.innerText = "Error: " + err.message;
      else alert("Extract failed: " + err.message);
    }
  });
}

// Basic verify handler — only active if the verify form provides a file input
const verifyForm = document.getElementById("verifyForm");
if (verifyForm) {
  verifyForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const submittedFields = document.getElementById("submittedFields")?.value;
    const verifyFileInput = document.getElementById("verifyFile");
    const file = verifyFileInput?.files?.[0];

    if (!file) {
      alert("Please provide a file for verification (use the main upload first).");
      return;
    }
    if (!submittedFields) {
      alert("Provide submitted fields JSON in the hidden input before verifying.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("submittedFields", submittedFields);
    formData.append("docType", verifyForm.elements["docType"]?.value || "generic");
    formData.append("language", verifyForm.elements["language"]?.value || "eng");
    formData.append("prefer_trocr", verifyForm.elements["prefer_trocr"]?.checked ? "true" : "false");

    try {
      const response = await fetch(`${BASE_URL}/api/ocr/verify`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      const data = await response.json();
      const out = document.getElementById("verifyOut") || document.getElementById("verifyOutput");
      if (out) out.innerText = JSON.stringify(data, null, 2);
    } catch (err) {
      console.error("Verify failed", err);
      const out = document.getElementById("verifyOut") || document.getElementById("verifyOutput");
      if (out) out.innerText = "Error: " + err.message;
      else alert("Verify failed: " + err.message);
    }
  });
}
