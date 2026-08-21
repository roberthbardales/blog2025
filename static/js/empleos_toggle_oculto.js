(function () {
  var forms = document.querySelectorAll("form.js-toggle-oculto");
  if (!forms.length) return;

  function actualizarTotal(cambio) {
    var el = document.getElementById("total-ofertas");
    if (!el) return;
    var n = parseInt(el.textContent, 10);
    if (!isNaN(n)) el.textContent = n + cambio;
  }

  Array.prototype.forEach.call(forms, function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = form.querySelector("button");
      if (btn) btn.disabled = true;

      fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { "X-Requested-With": "XMLHttpRequest" }
      })
        .then(function (resp) {
          if (!resp.ok) throw new Error("HTTP " + resp.status);
          return resp.json();
        })
        .then(function () {
          actualizarTotal(-1);
          var tr = form.closest("tr");
          if (tr) {
            tr.style.transition = "opacity 0.3s ease";
            tr.style.opacity = "0";
            setTimeout(function () { tr.remove(); }, 300);
          } else {
            form.closest("td").remove();
          }
        })
        .catch(function () {
          if (btn) btn.disabled = false;
          form.submit();
        });
    });
  });
})();
