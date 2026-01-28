document.addEventListener("DOMContentLoaded", () => {

  /* =====================
     FUNÇÕES
  ====================== */

  function moeda(v) {
    if (v === undefined || v === null) return "--";
    return Number(v).toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL"
    });
  }

  function numero(v) {
    if (v === undefined || v === null) return "--";
    return Number(v).toLocaleString("pt-BR");
  }

  function percentual(atual, meta) {
    if (!meta || meta === 0) return "";
    const p = (atual / meta) * 100;
    const cls = p >= 100 ? "positivo" : "negativo";
    return `<span class="${cls}">${p.toFixed(1)}%</span>`;
  }

  function nomeMesAtual() {
    const meses = [
      "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
      "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"
    ];
    return meses[new Date().getMonth()];
  }

  /* =====================
     ELEMENTOS
  ====================== */

  const fatAtual  = document.getElementById("fatAtual");
  const fatAnterior = document.getElementById("fatAnterior");
  const fatMetaEl = document.getElementById("fatMeta");
  const fatPercEl = document.getElementById("fatPerc");
  const fatVariacao = document.getElementById("fatVariacao");

  const qtdAtual = document.getElementById("qtdAtual");
  const qtdAnterior = document.getElementById("qtdAnterior");

  const ticketAtual = document.getElementById("ticketAtual");
  const ticketAnterior = document.getElementById("ticketAnterior");

  const m2Atual = document.getElementById("m2Atual");
  const kgAtual = document.getElementById("kgAtual");

  /* =====================
     META (FIXA POR ENQUANTO)
  ====================== */

  const metaFaturamento = 1325000;
  const mesAtual = nomeMesAtual();
  fatMetaEl.innerText = `Meta ${mesAtual}: ${moeda(metaFaturamento)}`;

  /* =====================
     FATURAMENTO (COM IPI)
  ====================== */

  fetch("site/dados/kpi_faturamento.json")
    .then(r => r.json())
    .then(d => {
      fatAtual.innerText = moeda(d.atual);
      fatAnterior.innerText = `Anterior: ${moeda(d.ano_anterior)}`;
      fatPercEl.innerHTML = percentual(d.atual, metaFaturamento);

      if (d.variacao !== null) {
        const cls = d.variacao >= 0 ? "positivo" : "negativo";
        fatVariacao.innerHTML = `<span class="${cls}">${d.variacao}%</span>`;
      }
    });

  /* =====================
     QTD PEDIDOS
  ====================== */

  fetch("site/dados/kpi_quantidade_pedidos.json")
    .then(r => r.json())
    .then(d => {
      qtdAtual.innerText = numero(d.atual);
      qtdAnterior.innerText = `Anterior: ${numero(d.ano_anterior)}`;
    });

  /* =====================
     TICKET MÉDIO (DERIVADO)
  ====================== */

  Promise.all([
    fetch("site/dados/kpi_faturamento.json").then(r => r.json()),
    fetch("site/dados/kpi_quantidade_pedidos.json").then(r => r.json())
  ]).then(([fat, qtd]) => {
    if (qtd.atual > 0) {
      const ticket = fat.atual / qtd.atual;
      ticketAtual.innerText = moeda(ticket);
    }
  });

  /* =====================
     SLIDE 2 (PLACEHOLDER)
  ====================== */

  if (m2Atual) m2Atual.innerText = "--";
  if (kgAtual) kgAtual.innerText = "--";

});
