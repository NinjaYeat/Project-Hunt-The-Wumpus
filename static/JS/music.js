const music = new Audio("../Audio/nojisuma-red_eyes-223645.mp3"); 

music.loop = true; 
music.volume = 0.3;

window.addEventListener("click", () => {
    music.play();
}, {once : true});