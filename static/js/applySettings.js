// Applique les settings sauvegardés dès le chargement de chaque page

// Luminosité via overlay (évite les conflits CSS avec body/filter) 
const savedBrightness = localStorage.getItem("brightness");
if (savedBrightness !== null) {
    const val = parseInt(savedBrightness); // 50 à 150

    const overlay = document.createElement("div");
    overlay.id = "brightness-overlay";
    overlay.style.cssText = "position:fixed;inset:0;pointer-events:none;z-index:9999;transition:background 0.3s;";

    if (val < 100) {
        const opacity = (100 - val) / 100;
        overlay.style.background = `rgba(0,0,0,${opacity})`;
    } else if (val > 100) {
        const opacity = (val - 100) / 100;
        overlay.style.background = `rgba(255,255,255,${opacity})`;
    }

    document.body.appendChild(overlay);
}

// Volume musique 
const savedVolume = localStorage.getItem("musicVolume");
if (savedVolume !== null && window.music) {
    window.music.volume = savedVolume / 100;
}