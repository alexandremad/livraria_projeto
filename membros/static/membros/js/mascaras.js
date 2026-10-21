/* Cadastro de membros: so numeros em CPF, RG e telefones, com mascara automatica. */
(function () {
  const digitos = (s) => (s || "").replace(/\D/g, "");

  const mascaras = {
    cpf: (d) => {
      d = d.slice(0, 11);
      if (d.length > 9) return d.slice(0, 3) + "." + d.slice(3, 6) + "." + d.slice(6, 9) + "-" + d.slice(9);
      if (d.length > 6) return d.slice(0, 3) + "." + d.slice(3, 6) + "." + d.slice(6);
      if (d.length > 3) return d.slice(0, 3) + "." + d.slice(3);
      return d;
    },
    tel: (d) => {
      d = d.slice(0, 11);
      if (d.length > 10) return "(" + d.slice(0, 2) + ") " + d.slice(2, 7) + "-" + d.slice(7);
      if (d.length > 6) return "(" + d.slice(0, 2) + ") " + d.slice(2, 6) + "-" + d.slice(6);
      if (d.length > 2) return "(" + d.slice(0, 2) + ") " + d.slice(2);
      if (d.length > 0) return "(" + d;
      return "";
    },
    numeros: (d) => d.slice(0, 15),
  };

  document.querySelectorAll("input[data-mascara]").forEach((el) => {
    const mascara = mascaras[el.dataset.mascara];
    if (!mascara) return;
    const aplicar = () => {
      const novo = mascara(digitos(el.value));
      if (novo !== el.value) el.value = novo;
    };
    aplicar(); // formata o valor que ja vem do banco (ao editar)
    el.addEventListener("input", aplicar);
    // bloqueia letras e simbolos na hora de digitar
    el.addEventListener("keypress", (e) => {
      if (e.key.length === 1 && !/\d/.test(e.key) && !e.ctrlKey && !e.metaKey) e.preventDefault();
    });
  });
})();
