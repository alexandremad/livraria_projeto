/* Cálculo ao vivo (custo total = qtd. de vendas x valor unit.) e navegação por Enter. */
(function () {
  const num = (s) => {
    s = (s || "").toString().trim().replace(",", ".");
    const n = parseFloat(s);
    return isNaN(n) ? null : n;
  };
  const fmt = (n) => n.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  function valorDaLinha(lin) {
    if (lin.dataset.valor) return parseFloat(lin.dataset.valor);
    const i = lin.querySelector('[data-f="valor"]');
    return i ? num(i.value) : null;
  }

  function recalcLinha(lin) {
    const q = num(lin.querySelector('[data-f="qtd"]').value);
    const v = valorDaLinha(lin);
    const el = lin.querySelector('[data-f="custo"]');
    if (q === null || v === null || isNaN(v)) { el.textContent = ""; return 0; }
    const c = q * v;
    el.textContent = fmt(c);
    return c;
  }

  function recalcColuna(col) {
    let tq = 0, tc = 0;
    col.querySelectorAll(".lin[data-calc]").forEach((lin) => {
      tc += recalcLinha(lin);
      tq += num(lin.querySelector('[data-f="qtd"]').value) || 0;
    });
    col.querySelector('[data-f="tot-qtd"]').textContent = tq ? tq : "";
    col.querySelector('[data-f="tot-custo"]').textContent = tc ? fmt(tc) : "";
  }

  const form = document.getElementById("folha");
  if (!form) return;

  form.addEventListener("input", (e) => {
    if (!e.target.matches(".q")) return;
    const col = e.target.closest("[data-coluna]");
    if (col) recalcColuna(col);
  });

  // Enter desce para a mesma coluna da linha de baixo (agiliza o preenchimento)
  form.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" || !e.target.matches(".q")) return;
    e.preventDefault();
    const col = e.target.closest("[data-coluna]");
    const chave = e.target.name.split("_")[1];
    const lista = Array.from(col.querySelectorAll(".lin"))
      .map((l) => l.querySelector('.q[name$="_' + chave + '"]'))
      .filter(Boolean);
    const pos = lista.indexOf(e.target);
    const prox = lista[pos + (e.shiftKey ? -1 : 1)];
    if (prox) { prox.focus(); prox.select(); }
  });
})();
