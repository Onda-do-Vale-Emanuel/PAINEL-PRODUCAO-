document.addEventListener("DOMContentLoaded", () => {
  const slides = Array.from(document.querySelectorAll(".slide"));
  let index = 0;

  function mostrarSlide(i) {
    slides.forEach((s, idx) => {
      if (idx === i) s.classList.add("active");
      else s.classList.remove("active");
    });
  }

  mostrarSlide(index);

  setInterval(() => {
    index = (index + 1) % slides.length;
    mostrarSlide(index);
  }, 8000);
});
