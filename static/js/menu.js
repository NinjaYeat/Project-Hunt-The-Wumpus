document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".level_btn, .option_btn").forEach(btn => {
    btn.addEventListener("mouseenter", () => {
      btn.style.filter = "brightness(1.2)";
    });
    btn.addEventListener("mouseleave", () => {
      btn.style.filter = "";
    });
  });
});