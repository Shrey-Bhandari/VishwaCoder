// Language translations
const translations = {
  en: {
    title: "AI-Driven Leaf Health Assessment",
    subtitle: "Damage Quantification • Leaf Area Index • Recommendations",
    selectLanguage: "Select Language",
    model1Title: "Multi-Crop Analysis",
    model1Desc: "Advanced detection for fruits, vegetables & field crops",
    model2Title: "Staple Crops Analysis",
    model2Desc: "Specialized for major grain and cash crops",
    model3Title: "Banana Crop Analysis",
    model3Desc: "Specialized banana disease detection and analysis",
    uploadImage: "Upload Leaf Image",
    analyzeButton: "🔍 Analyze Leaf Health",
    resultsTitle: "Analysis Results",
    healthStatus: "Health Status",
    damagePercent: "Damage Percentage",
    severity: "Severity Level",
    leafAreaIndex: "Leaf Area Index (LAI)",
    detectedDisease: "Detected Disease",
    recommendation: "Treatment Recommendation",
    voiceReport: "🔊 Hear Voice Report",
    footer: "© 2025 Smart AgriTech Platform | Empowering Farmers with AI",
    analyzing: "🔄 Analyzing...",
    uploadFirst: "Please upload an image first!",
    viewNewWindow: "📊 View in New Window",
    exportPDF: "📄 Export PDF",
  },
  hi: {
    title: "एआई-संचालित पत्ती स्वास्थ्य मूल्यांकन",
    subtitle: "क्षति मात्रा निर्धारण • पत्ती क्षेत्र सूचकांक • सिफारिशें",
    selectLanguage: "भाषा चुनें",
    model1Title: "बहु-फसल विश्लेषण",
    model1Desc: "फलों, सब्जियों और खेतों की फसलों के लिए उन्नत पहचान",
    model2Title: "मुख्य फसल विश्लेषण",
    model2Desc: "प्रमुख अनाज और नकदी फसलों के लिए विशेष",
    model3Title: "केला फसल विश्लेषण",
    model3Desc: "विशेष केला रोग पहचान और विश्लेषण",
    uploadImage: "पत्ती की तस्वीर अपलोड करें",
    analyzeButton: "🔍 पत्ती स्वास्थ्य का विश्लेषण करें",
    resultsTitle: "विश्लेषण परिणाम",
    healthStatus: "स्वास्थ्य स्थिति",
    damagePercent: "क्षति प्रतिशत",
    severity: "गंभीरता स्तर",
    leafAreaIndex: "पत्ती क्षेत्र सूचकांक (LAI)",
    detectedDisease: "पहचाना गया रोग",
    recommendation: "उपचार सिफारिश",
    voiceReport: "🔊 आवाज रिपोर्ट सुनें",
    footer:
      "© 2025 स्मार्ट कृषि तकनीक प्लेटफॉर्म | एआई के साथ किसानों को सशक्त बनाना",
    analyzing: "🔄 विश्लेषण हो रहा है...",
    uploadFirst: "कृपया पहले एक तस्वीर अपलोड करें!",
    viewNewWindow: "📊 नई विंडो में देखें",
    exportPDF: "📄 पीडीएफ निर्यात करें",
  },
  mr: {
    title: "एआय-चालित पानांचे आरोग्य मूल्यमापन",
    subtitle: "नुकसान प्रमाण • पान क्षेत्र निर्देशांक • शिफारसी",
    selectLanguage: "भाषा निवडा",
    model1Title: "बहु-पीक विश्लेषण",
    model1Desc: "फळे, भाज्या आणि शेतातील पिकांसाठी प्रगत ओळख",
    model2Title: "मुख्य पीक विश्लेषण",
    model2Desc: "प्रमुख धान्य आणि नगदी पिकांसाठी विशेष",
    model3Title: "केळी पीक विश्लेषण",
    model3Desc: "विशेष केळी रोग ओळख आणि विश्लेषण",
    uploadImage: "पानाचा फोटो अपलोड करा",
    analyzeButton: "🔍 पानांच्या आरोग्याचे विश्लेषण करा",
    resultsTitle: "विश्लेषण परिणाम",
    healthStatus: "आरोग्य स्थिती",
    damagePercent: "नुकसान टक्केवारी",
    severity: "तीव्रता पातळी",
    leafAreaIndex: "पान क्षेत्र निर्देशांक (LAI)",
    detectedDisease: "ओळखला गेलेला रोग",
    recommendation: "उपचार शिफारस",
    voiceReport: "🔊 आवाज अहवाल ऐका",
    footer:
      "© 2025 स्मार्ट कृषी तंत्रज्ञान प्लॅटफॉर्म | एआयसह शेतकऱ्यांना सक्षम करणे",
    analyzing: "🔄 विश्लेषण सुरू आहे...",
    uploadFirst: "कृपया प्रथम प्रतिमा अपलोड करा!",
    viewNewWindow: "📊 नवीन विंडोमध्ये पहा",
    exportPDF: "📄 पीडीएफ निर्यात करा",
  },
};

let currentLang = "en";
let selectedModel = null;
let analysisResults = null;

// Initialize page
document.addEventListener("DOMContentLoaded", function () {
  updateContent();
});

function changeLanguage(lang) {
  currentLang = lang;
  updateContent();
}

function updateContent() {
  const t = translations[currentLang];

  // Update main content
  document.getElementById("main-title").textContent = t.title;
  document.getElementById("main-subtitle").textContent = t.subtitle;
  document.getElementById("lang-label").textContent = t.selectLanguage;

  // Update model cards
  document.getElementById("model1-title").textContent = t.model1Title;
  document.getElementById("model1-desc").textContent = t.model1Desc;
  document.getElementById("model2-title").textContent = t.model2Title;
  document.getElementById("model2-desc").textContent = t.model2Desc;
  document.getElementById("model3-title").textContent = t.model3Title;
  document.getElementById("model3-desc").textContent = t.model3Desc;

  // Update upload sections
  document.querySelectorAll(".upload-label").forEach((el) => {
    el.textContent = t.uploadImage;
  });
  document.querySelectorAll(".analyze-btn").forEach((el) => {
    if (!el.disabled) {
      el.textContent = t.analyzeButton;
    }
  });

  // Update results section labels
  document.getElementById("health-label").textContent = t.healthStatus;
  document.getElementById("damage-label").textContent = t.damagePercent;
  document.getElementById("severity-label").textContent = t.severity;
  document.getElementById("lai-label").textContent = t.leafAreaIndex;
  document.getElementById("disease-label").textContent = t.detectedDisease;
  document.getElementById("recommendation-label").textContent =
    t.recommendation;

  if (document.getElementById("voice-btn")) {
    document.getElementById("voice-btn").textContent = t.voiceReport;
  }

  document.getElementById("footer-text").textContent = t.footer;

  // Update results if visible
  if (analysisResults) {
    document.getElementById("results-title").textContent = t.resultsTitle;
  }
}

function selectModel(modelId) {
  selectedModel = modelId;

  // Hide all upload sections
  document.querySelectorAll(".upload-section").forEach((section) => {
    section.classList.add("hidden");
  });

  // Remove active state from all cards
  document.querySelectorAll(".model-card").forEach((card) => {
    card.classList.remove("ring-4", "ring-emerald-400", "bg-emerald-50");
    card.classList.add("bg-white");
  });

  // Show selected upload section and highlight card
  document.getElementById(`upload-${modelId}`).classList.remove("hidden");
  const selectedCard = document.getElementById(`card-${modelId}`);
  selectedCard.classList.add("ring-4", "ring-emerald-400", "bg-emerald-50");
  selectedCard.classList.remove("bg-white");

  // Hide results
  document.getElementById("results-section").classList.add("hidden");
  analysisResults = null;
}

function analyzeLeaf(modelId) {
  const fileInput = document.getElementById(`file-${modelId}`);
  if (!fileInput.files.length) {
    alert(translations[currentLang].uploadFirst);
    return;
  }

  // Show loading state
  const analyzeBtn = document.getElementById(`btn-${modelId}`);
  analyzeBtn.innerHTML = translations[currentLang].analyzing;
  analyzeBtn.disabled = true;

  // Here you would integrate with your actual ML model
  // For now, this is a placeholder that shows the UI structure

  // Simulate API call delay
  setTimeout(() => {
    // TODO: Replace this with actual API call to your ML model
    // Example API call structure:
    /*
    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    formData.append('model', modelId);
    
    fetch('/api/analyze-leaf', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      displayResults(data);
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Analysis failed. Please try again.');
    })
    .finally(() => {
      analyzeBtn.innerHTML = translations[currentLang].analyzeButton;
      analyzeBtn.disabled = false;
    });
    */

    // For demonstration purposes, showing UI structure
    alert("Integration point: Connect your trained .h5 model here");

    analyzeBtn.innerHTML = translations[currentLang].analyzeButton;
    analyzeBtn.disabled = false;
  }, 1000);
}

function displayResults(results) {
  analysisResults = results;

  // Update result values
  document.getElementById("health-value").textContent =
    results.healthStatus || "-";
  document.getElementById("damage-value").textContent = results.damagePercentage
    ? `${results.damagePercentage}%`
    : "-";
  document.getElementById("severity-value").textContent =
    results.severityLevel || "-";
  document.getElementById("lai-value").textContent =
    results.leafAreaIndex || "-";
  document.getElementById("disease-value").textContent =
    results.detectedDisease || "None detected";
  document.getElementById("recommendation-value").textContent =
    results.recommendation || "-";

  // Show results section
  document.getElementById("results-section").classList.remove("hidden");
  document
    .getElementById("results-section")
    .scrollIntoView({ behavior: "smooth" });
}

function speakResults() {
  if ("speechSynthesis" in window && analysisResults) {
    const text = `Health Status: ${analysisResults.healthStatus}. Damage: ${analysisResults.damagePercentage} percent. Severity: ${analysisResults.severityLevel}. Recommendation: ${analysisResults.recommendation}`;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang =
      currentLang === "hi" ? "hi-IN" : currentLang === "mr" ? "mr-IN" : "en-US";
    speechSynthesis.speak(utterance);
  } else {
    alert("Speech synthesis not supported in this browser");
  }
}

function openResultsWindow() {
  if (!analysisResults) {
    alert("No results to display");
    return;
  }

  const resultsWindow = window.open(
    "",
    "_blank",
    "width=800,height=600,scrollbars=yes,resizable=yes"
  );
  const t = translations[currentLang];

  resultsWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>${t.resultsTitle}</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <style>
        @media print {
          .no-print { display: none; }
        }
      </style>
    </head>
    <body class="bg-gray-50 p-8">
      <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-800 mb-2">${
            t.resultsTitle
          }</h1>
          <p class="text-gray-600">Generated on ${new Date().toLocaleDateString()}</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div class="bg-blue-50 p-6 rounded-lg">
            <h3 class="font-semibold text-gray-700 mb-2">${t.healthStatus}</h3>
            <p class="text-2xl font-bold text-blue-600">${
              analysisResults.healthStatus || "-"
            }</p>
          </div>
          
          <div class="bg-red-50 p-6 rounded-lg">
            <h3 class="font-semibold text-gray-700 mb-2">${t.damagePercent}</h3>
            <p class="text-2xl font-bold text-red-600">${
              analysisResults.damagePercentage
                ? analysisResults.damagePercentage + "%"
                : "-"
            }</p>
          </div>
          
          <div class="bg-yellow-50 p-6 rounded-lg">
            <h3 class="font-semibold text-gray-700 mb-2">${t.severity}</h3>
            <p class="text-2xl font-bold text-yellow-600">${
              analysisResults.severityLevel || "-"
            }</p>
          </div>
          
          <div class="bg-green-50 p-6 rounded-lg">
            <h3 class="font-semibent text-gray-700 mb-2">${t.leafAreaIndex}</h3>
            <p class="text-2xl font-bold text-green-600">${
              analysisResults.leafAreaIndex || "-"
            }</p>
          </div>
        </div>
        
        <div class="mb-8">
          <h3 class="font-semibold text-gray-700 mb-2">${t.detectedDisease}</h3>
          <p class="text-lg text-purple-600 font-medium">${
            analysisResults.detectedDisease || "None detected"
          }</p>
        </div>
        
        <div class="mb-8">
          <h3 class="font-semibold text-gray-700 mb-2">${t.recommendation}</h3>
          <p class="text-gray-800 leading-relaxed">${
            analysisResults.recommendation || "-"
          }</p>
        </div>
        
        <div class="text-center no-print">
          <button onclick="window.print()" class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg mr-4">Print Results</button>
          <button onclick="window.close()" class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-2 rounded-lg">Close Window</button>
        </div>
      </div>
    </body>
    </html>
  `);

  resultsWindow.document.close();
}

function exportToPDF() {
  if (!analysisResults) {
    alert("No results to export");
    return;
  }

  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();
  const t = translations[currentLang];

  // Add title
  doc.setFontSize(20);
  doc.setFont(undefined, "bold");
  doc.text(t.resultsTitle, 20, 20);

  // Add date
  doc.setFontSize(12);
  doc.setFont(undefined, "normal");
  doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 20, 35);

  // Add results
  let yPosition = 55;

  // Health Status
  doc.setFont(undefined, "bold");
  doc.text(`${t.healthStatus}:`, 20, yPosition);
  doc.setFont(undefined, "normal");
  doc.text(analysisResults.healthStatus || "-", 80, yPosition);
  yPosition += 15;

  // Damage Percentage
  doc.setFont(undefined, "bold");
  doc.text(`${t.damagePercent}:`, 20, yPosition);
  doc.setFont(undefined, "normal");
  doc.text(
    analysisResults.damagePercentage
      ? `${analysisResults.damagePercentage}%`
      : "-",
    80,
    yPosition
  );
  yPosition += 15;

  // Severity Level
  doc.setFont(undefined, "bold");
  doc.text(`${t.severity}:`, 20, yPosition);
  doc.setFont(undefined, "normal");
  doc.text(analysisResults.severityLevel || "-", 80, yPosition);
  yPosition += 15;

  // Leaf Area Index
  doc.setFont(undefined, "bold");
  doc.text(`${t.leafAreaIndex}:`, 20, yPosition);
  doc.setFont(undefined, "normal");
  doc.text(analysisResults.leafAreaIndex || "-", 80, yPosition);
  yPosition += 15;

  // Detected Disease
  doc.setFont(undefined, "bold");
  doc.text(`${t.detectedDisease}:`, 20, yPosition);
  doc.setFont(undefined, "normal");
  doc.text(analysisResults.detectedDisease || "None detected", 80, yPosition);
  yPosition += 20;

  // Recommendation
  doc.setFont(undefined, "bold");
  doc.text(`${t.recommendation}:`, 20, yPosition);
  yPosition += 10;
  doc.setFont(undefined, "normal");

  // Split long recommendation text
  const recommendation = analysisResults.recommendation || "-";
  const splitText = doc.splitTextToSize(recommendation, 170);
  doc.text(splitText, 20, yPosition);

  // Footer
  yPosition = 280;
  doc.setFontSize(10);
  doc.setFont(undefined, "italic");
  doc.text(
    "© 2025 Smart AgriTech Platform | AI-Powered Leaf Health Assessment",
    20,
    yPosition
  );

  // Save the PDF
  doc.save(
    `leaf-analysis-results-${new Date().toISOString().split("T")[0]}.pdf`
  );
}
