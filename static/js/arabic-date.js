document.addEventListener("DOMContentLoaded", function () {
  const digits = { "0": "٠", "1": "١", "2": "٢", "3": "٣", "4": "٤", "5": "٥", "6": "٦", "7": "٧", "8": "٨", "9": "٩" };
  document.querySelectorAll("[data-date]").forEach(function (el) {
    el.textContent = el.textContent.replace(/[0-9]/g, function (char) { return digits[char]; });
  });
});
