/* Ficha diária: soma automática do VALOR no "Valor total em relatório" e Enter desce uma linha. */
(function () {
  const form = document.getElementById("ficha");
  if (!form) return;
  const total = document.getElementById("valor_total");

  const num = (s) => {
    s = (s || "").toString().trim().replace(/\s|R\$/g, "");
    if (s.includes(",")) s = s.replace(/\./g, "").replace(",", ".");
    const n = parseFloat(s);
    return isNaN(n) ? null : n;
  };
  const fmt = (n) => n.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  function soma() {
    let t = 0, algum = false;
    form.querySelectorAll('[data-f="valor"]').forEach((i) => {
      const n = num(i.value);
      if (n !== null) { t += n; algum = true; }
    });
    return algum ? t : null;
  }

  // Se o total salvo for diferente da soma, ele foi digitado à mão: não sobrescrever.
  const s0 = soma(), t0 = num(total.value);
  if (t0 !== null && (s0 === null || Math.abs(t0 - s0) > 0.005)) total.dataset.manual = "1";

  form.addEventListener("input", (e) => {
    if (e.target === total) { total.dataset.manual = total.value.trim() ? "1" : "0"; return; }
    if (e.target.matches('[data-f="valor"]') && total.dataset.manual !== "1") {
      const s = soma();
      total.value = s === null ? "" : fmt(s);
    }
  });

  form.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" || !e.target.matches("input[data-c]")) return;
    e.preventDefault();
    const lista = Array.from(form.querySelectorAll('input[data-c="' + e.target.dataset.c + '"]'));
    const prox = lista[lista.indexOf(e.target) + (e.shiftKey ? -1 : 1)];
    if (prox) { prox.focus(); prox.select(); }
  });
})();
