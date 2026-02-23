// Créé immédiatement, accessible partout dès le chargement du script
window.music = new Audio("/static/audio/nojisuma-red_eyes-223645.mp3");
window.music.loop = true;
window.music.volume = 0.3;

// Premier clic sur la page = démarrage (contourne l'autoplay policy des navigateurs)
window.addEventListener("click", function () {
    window.music.play();
}, { once: true });