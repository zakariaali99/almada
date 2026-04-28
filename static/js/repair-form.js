(function () {
  function recalcRow(row) {
    const qty = parseFloat(row.querySelector(".item-quantity").value || "0");
    const price = parseFloat(row.querySelector(".item-price").value || "0");
    row.querySelector(".item-total").value = (qty * price).toFixed(2);
  }

  function recalcGrandTotal() {
    let total = 0;
    document.querySelectorAll(".repair-item-row").forEach(function (row) {
      total += parseFloat(row.querySelector(".item-total").value || "0");
    });
    const grand = document.getElementById("grand-total");
    if (grand) grand.textContent = total.toFixed(2);
  }

  function syncProduct(row) {
    const type = row.querySelector(".item-type").value;
    const productSelect = row.querySelector(".item-product");
    const priceType = row.querySelector(".item-price-type").value;
    Array.from(productSelect.options).forEach(function (option) {
      if (!option.value) return;
      option.hidden = option.dataset.type !== type;
    });
    const selected = productSelect.options[productSelect.selectedIndex];
    if (selected && selected.value) {
      row.querySelector(".item-description").value = selected.dataset.description || "";
      if (priceType === "wholesale") row.querySelector(".item-price").value = selected.dataset.wholesale || "0";
      if (priceType === "retail") row.querySelector(".item-price").value = selected.dataset.retail || "0";
    }
    recalcRow(row);
    recalcGrandTotal();
  }

  function wireRow(row) {
    row.querySelectorAll(".item-quantity, .item-price").forEach(function (input) {
      input.addEventListener("input", function () {
        recalcRow(row);
        recalcGrandTotal();
      });
    });
    row.querySelector(".item-type").addEventListener("change", function () { syncProduct(row); });
    row.querySelector(".item-price-type").addEventListener("change", function () { syncProduct(row); });
    row.querySelector(".item-product").addEventListener("change", function () { syncProduct(row); });
    row.querySelector(".remove-item-row").addEventListener("click", function () {
      const tbody = row.closest("tbody");
      if (tbody.querySelectorAll(".repair-item-row").length > 1) {
        row.remove();
        recalcGrandTotal();
      }
    });
    syncProduct(row);
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".repair-item-row").forEach(wireRow);
    const addBtn = document.getElementById("add-item-row");
    if (addBtn) {
      addBtn.addEventListener("click", function () {
        const tbody = document.querySelector("#repair-items-table tbody");
        const clone = tbody.querySelector(".repair-item-row").cloneNode(true);
        clone.querySelectorAll("input").forEach(function (input) {
          if (input.name === "item_id[]") input.value = "";
          else if (input.classList.contains("item-quantity")) input.value = "1";
          else if (input.classList.contains("item-total") || input.classList.contains("item-price")) input.value = "0";
          else input.value = "";
        });
        clone.querySelectorAll("select").forEach(function (select) { select.selectedIndex = 0; });
        tbody.appendChild(clone);
        wireRow(clone);
      });
    }
    recalcGrandTotal();
  });
})();
