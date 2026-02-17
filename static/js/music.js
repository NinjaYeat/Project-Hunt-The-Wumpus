document.addEventListener("DOMContentLoaded", function () {

    const music = new Audio("/static/audio/nojisuma-red_eyes-223645.mp3");

    music.loop = true;
    music.volume = 0.3;

    // pour ne pas bloquer le nav
    window.addEventListener("click", function () {
        music.play();
    }, { once: true });

});