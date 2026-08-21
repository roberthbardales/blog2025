(function () {
  var KEY = "empleos_last_guardados_visit";
  var rows = document.querySelectorAll("tr[data-created]");
  if (!rows.length) return;

  var last = parseInt(localStorage.getItem(KEY) || "0", 10);
  var now = Date.now();

  Array.prototype.forEach.call(rows, function (tr) {
    var ts = Date.parse(tr.getAttribute("data-created"));
    if (isNaN(ts) || ts <= last) return;

    tr.classList.add("bg-emerald-50/60");

    var cell = tr.querySelector(".js-title-cell");
    if (cell && !cell.querySelector(".badge-nueva")) {
      var badge = document.createElement("span");
      badge.className = "badge-nueva inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-emerald-100 text-emerald-700 ml-2 align-middle";
      badge.innerHTML = '<i class="fas fa-plus-circle mr-1"></i>Nueva';
      cell.appendChild(badge);
    }
  });

  localStorage.setItem(KEY, String(now));
})();
