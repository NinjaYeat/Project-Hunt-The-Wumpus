document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".card__frame").forEach((card) => {
    card.style.transition = "transform 120ms ease";

    card.addEventListener("mousemove", (e) => {
      let r = card.getBoundingClientRect();
      let x = (e.clientX - r.left) / r.width - 0.5;
      let y = (e.clientY - r.top) / r.height - 0.5;
      card.style.transform = `translateY(-3px) rotateX(${(-y * 4)}deg) rotateY(${(x * 6)}deg)`;
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = "";
    });
  });
});
