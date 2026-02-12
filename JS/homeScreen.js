const btn = document.getElementById("playBtn");

btn.addEventListener("click", function () {
  const sound = new Audio("../Audio/dragon-studio-deep-sea-growl-401721.mp3");
  sound.play();

  setTimeout(function () {
    window.location.href = "login.html";
  }, 1500);
});
