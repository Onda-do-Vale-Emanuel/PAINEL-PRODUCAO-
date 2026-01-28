let slideAtual = 0;
const slides = document.querySelectorAll(".slide");

setInterval(() => {
  slides[slideAtual].classList.remove("ativo");
  slideAtual = (slideAtual + 1) % slides.length;
  slides[slideAtual].classList.add("ativo");
}, 10000);
