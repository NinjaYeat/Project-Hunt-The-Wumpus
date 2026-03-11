document.addEventListener("DOMContentLoaded", () => {

    // Éléments 
    let musicVolumeSlider = document.getElementById("musicVolume");
    let musicVolumeDisplay = document.getElementById("musicVolumeDisplay");
    let playMusicBtn = document.getElementById("playMusic");
    let pauseMusicBtn = document.getElementById("pauseMusic");

    let brightnessSlider = document.getElementById("brightness");
    let brightnessDisplay = document.getElementById("brightnessDisplay");

    let saveBtn = document.getElementById("saveBtn");
    let closeBtn = document.getElementById("closeBtn");

    // Fonction luminosité via overlay 
    function applyBrightness(val) {
        val = parseInt(val);
        let overlay = document.getElementById("brightness-overlay");
        if (!overlay) {
            overlay = document.createElement("div");
            overlay.id = "brightness-overlay";
            overlay.style.cssText = "position:fixed;inset:0;pointer-events:none;z-index:9999;transition:background 0.1s;";
            document.body.appendChild(overlay);
        }
        if (val < 100) {
            overlay.style.background = `rgba(0,0,0,${(100 - val) / 100})`;
        } else if (val > 100) {
            overlay.style.background = `rgba(255,255,255,${(val - 100) / 100})`;
        } else {
            overlay.style.background = "transparent";
        }
    }

    // Charger les valeurs sauvegardées 
    let savedVolume     = localStorage.getItem("musicVolume");
    let savedBrightness = localStorage.getItem("brightness");

    if (savedVolume !== null) {
        musicVolumeSlider.value = savedVolume;
        musicVolumeDisplay.textContent = `${savedVolume}%`;
        if (window.music) window.music.volume = savedVolume / 100;
    } else {
        musicVolumeDisplay.textContent = `${musicVolumeSlider.value}%`;
    }

    if (savedBrightness !== null) {
        brightnessSlider.value = savedBrightness;
        brightnessDisplay.textContent = `${savedBrightness}%`;
        applyBrightness(savedBrightness);
    } else {
        brightnessDisplay.textContent = `${brightnessSlider.value}%`;
    }

    // Volume music
    musicVolumeSlider.addEventListener("input", (e) => {
        const val = e.target.value;
        musicVolumeDisplay.textContent = `${val}%`;
        if (window.music) window.music.volume = val / 100;
    });

    // Play / Pause 
    playMusicBtn.addEventListener("click", () => {
        if (window.music) window.music.play();
    });

    pauseMusicBtn.addEventListener("click", () => {
        if (window.music) window.music.pause();
    });

    // Luminosité 
    brightnessSlider.addEventListener("input", (e) => {
        brightnessDisplay.textContent = `${e.target.value}%`;
        applyBrightness(e.target.value);
    });

    // Gérer la sauvegarde
    saveBtn.addEventListener("click", () => {
        localStorage.setItem("musicVolume", musicVolumeSlider.value);
        localStorage.setItem("brightness", brightnessSlider.value);

        saveBtn.textContent = "Sauvegardé ✓";
        setTimeout(() => saveBtn.textContent = "Sauvegarder", 1500);
    });

    // Fermer (bouton ✕) 
    closeBtn.addEventListener("click", () => {
        window.history.back();
    });

});