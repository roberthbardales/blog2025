(function () {
  var KEY = "empleos_keywords_history";
  var MAX = 10;
  var container = document.getElementById("keywords-history");
  if (!container) return;

  var input = document.getElementById("keyword") || document.querySelector('input[name="search"]');
  var form = container.closest("form");

  function getHistory() {
    try {
      var raw = JSON.parse(localStorage.getItem(KEY));
      return Array.isArray(raw) ? raw.filter(function (k) { return typeof k === "string" && k.trim(); }) : [];
    } catch (e) {
      return [];
    }
  }

  function saveHistory(list) {
    localStorage.setItem(KEY, JSON.stringify(list));
  }

  function renderChips() {
    container.innerHTML = "";
    var history = getHistory();
    if (!history.length) {
      container.classList.add("hidden");
      return;
    }
    container.classList.remove("hidden");

    var label = document.createElement("span");
    label.className = "text-xs text-slate-400";
    label.textContent = "Recientes:";
    container.appendChild(label);

    history.forEach(function (kw) {
      var chip = document.createElement("span");
      chip.className = "inline-flex items-center rounded-full bg-blue-50 border border-blue-100 overflow-hidden";

      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "pl-3 pr-1.5 py-1 text-xs font-medium text-blue-600 hover:bg-blue-100 transition";
      btn.textContent = kw;
      btn.title = "Usar esta búsqueda";
      btn.addEventListener("click", function () {
        input.value = kw;
        input.focus();
      });

      var del = document.createElement("button");
      del.type = "button";
      del.className = "pl-1 pr-2.5 py-1 text-blue-300 hover:text-red-500 transition";
      del.innerHTML = '<i class="fas fa-times text-[10px]"></i>';
      del.title = "Eliminar del historial";
      del.setAttribute("aria-label", "Eliminar " + kw);
      del.addEventListener("click", function () {
        saveHistory(getHistory().filter(function (k) { return k.toLowerCase() !== kw.toLowerCase(); }));
        renderChips();
      });

      chip.appendChild(btn);
      chip.appendChild(del);
      container.appendChild(chip);
    });
  }

  if (form) {
    form.addEventListener("submit", function () {
      var kw = input.value.trim();
      if (!kw) return;
      var history = getHistory().filter(function (k) { return k.toLowerCase() !== kw.toLowerCase(); });
      history.unshift(kw);
      saveHistory(history.slice(0, MAX));
    });
  }

  renderChips();
})();
