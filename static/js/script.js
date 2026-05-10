document.addEventListener("DOMContentLoaded", function () {
  // --- Theme Toggle Logic ---
  const themeToggle = document.getElementById("themeToggle");
  const currentTheme = localStorage.getItem("theme") || "light";

  if (currentTheme === "dark") {
    document.documentElement.setAttribute("data-theme", "dark");
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      let theme = document.documentElement.getAttribute("data-theme");
      if (theme === "dark") {
        document.documentElement.setAttribute("data-theme", "light");
        localStorage.setItem("theme", "light");
      } else {
        document.documentElement.setAttribute("data-theme", "dark");
        localStorage.setItem("theme", "dark");
      }
    });
  }

  // --- Table Row Clickability ---
  const tableRows = document.querySelectorAll(".data-table tbody tr[data-href]");
  tableRows.forEach(row => {
    row.addEventListener("click", () => {
      window.location.href = row.dataset.href;
    });
  });

  // --- Count-Up Animation for Stats ---
  const statValues = document.querySelectorAll(".stat-value:not(.no-animate)");
  statValues.forEach(val => {
    const target = parseFloat(val.innerText.replace(/[^\d.-]/g, ''));
    if (isNaN(target)) return;
    
    let current = 0;
    const duration = 1000; // 1s
    const start = performance.now();
    
    const animate = (time) => {
      const progress = Math.min((time - start) / duration, 1);
      const eased = progress === 1 ? target : target * (1 - Math.pow(2, -10 * progress));
      
      if (val.querySelector("small")) {
        const smallText = val.querySelector("small").outerHTML;
        val.innerHTML = eased.toFixed(progress === 1 ? 2 : 0) + " " + smallText;
      } else {
        val.innerText = Math.floor(eased);
      }
      
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  });

  // --- Flash Messages Auto-Hide ---
  window.setTimeout(function () {
    document.querySelectorAll(".flash").forEach(function (node) {
      node.style.opacity = "0";
      node.style.transform = "translateY(-10px)";
      node.style.transition = "all 0.5s ease";
      setTimeout(function () { node.remove(); }, 500);
    });
  }, 5000);

  // --- Mobile Menu Toggle ---
  const menuToggle = document.getElementById('menuToggle');
  const sidebar = document.getElementById('sidebar');
  if (menuToggle && sidebar) {
    menuToggle.addEventListener('click', function() {
      sidebar.classList.toggle('open');
    });
    document.addEventListener('click', function(e) {
      if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== menuToggle && !menuToggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }
});

