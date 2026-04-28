document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.querySelector("[data-menu-toggle]");
  const menu = document.querySelector("[data-menu]");
  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      menu.classList.toggle("open");
    });
  }

  window.setTimeout(function () {
    document.querySelectorAll(".flash").forEach(function (node) {
      node.style.opacity = "0";
      node.style.transition = "opacity 0.4s ease";
      setTimeout(function () { node.remove(); }, 400);
    });
  }, 5000);
});
