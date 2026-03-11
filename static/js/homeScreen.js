document.addEventListener("DOMContentLoaded", () => {
  console.log(" homeScreen.js chargé");

  let startBtn = document.getElementById("startBtn");
  let classementBtn = document.getElementById("classementBtn");

  if (!startBtn || !classementBtn) {
    console.error(" startBtn ou classementBtn introuvable (IDs manquants dans le HTML)");
    return;
  }

  function playAndGo(e) {
    e.preventDefault();

    let targetUrl = e.currentTarget.getAttribute("href");
    let soundUrl = e.currentTarget.dataset.sound;

    console.log(" targetUrl =", targetUrl);
    console.log(" soundUrl =", soundUrl);

    let sound = new Audio(soundUrl);
    sound.currentTime = 0;

    sound.play()
      .then(() => {
        setTimeout(() => {
          window.location.href = targetUrl;
        }, 2000);
      })
      .catch((err) => {
        console.error("Audio bloqué / erreur:", err);
        // Si son bloqué, on redirige quand même
        window.location.href = targetUrl;
      });
  }

  startBtn.addEventListener("click", playAndGo);
  classementBtn.addEventListener("click", playAndGo);
});
