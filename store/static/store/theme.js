// dark <-> light theme toggle (persisted)
(function () {
  var KEY = "rog-theme";
  function apply(t) {
    document.querySelectorAll(".rog").forEach(function (el) { el.setAttribute("data-theme", t); });
    try { localStorage.setItem(KEY, t); } catch (e) {}
  }
  window.addEventListener("DOMContentLoaded", function () {
    var saved = "dark";
    try { saved = localStorage.getItem(KEY) || "dark"; } catch (e) {}
    apply(saved);
    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var cur = document.querySelector(".rog").getAttribute("data-theme");
        apply(cur === "dark" ? "light" : "dark");
      });
    });
  });
})();
