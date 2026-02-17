document.addEventListener("DOMContentLoaded", () => {
    const musicVolume = document.getElementById('musicVolume');
    const volumeValue= document.getElementById('volume');
    const playMusicBtn = document.getElementById("playMusic");
    const pauseMusicBtn = document.getElementById("pauseMusic");

    const brightness = document.getElementById('brightness');
    const brightnessValue = document.getElementById('brightnessValue');


    musicVolume.addEventListener('input', (e) => {
        volumeValue.textContent = `${e.target.value}%`;
        music.volume = e.target.value / 100;
    });


    brightness.addEventListener('input', (e)=> {
        brightnessValue.textContent = `${e.target.value}%`;
        document.body.style.filter = `brightness(${e.target.value}%)`;
    });


    playMusicBtn.addEventListener("click", () => music.play());
    pauseMusicBtn.addEventListener("click", () => music.pause());

})