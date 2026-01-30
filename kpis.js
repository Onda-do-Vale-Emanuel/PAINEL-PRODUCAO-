// ======================================================
// FUNÇÕES AUXILIARES
// ======================================================
function carregarJSON(nome) {
  return fetch("site/dados/" + nome)
    .then((resp) => resp.json())
    .catch(() => null);
}

function moeda(v) {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function numero(v) {
  return v.toLocaleString("pt-BR", { maximumFractionDigits: 0 });
}

function percentual(v) {
  return v.toFixed(1).replace(".", ",") + "%";
}

// ======================================================
// METAS
// ======================================================
const METAS = {
  1: { kg: 100000, fat: 1324746.56 },
  2: { kg: 100000, fat: 1324746.56 },
  3: { kg: 120000, fat: 1598757.69 },
  4: { kg: 130000, fat: 1910459.23 },
  5: { kg: 130000, fat: 1892998.21 },
  6: { kg: 130000, fat: 1892995.74 },
  7: { kg: 150000, fat: 2199365.46 },
  8: { kg: 150000, fat: 2199350.47 },
  9: { kg: 150000, fat: 2199340.46 },
  10: { kg: 150000, fat: 2199335.81 },
  11: { kg: 150000, fat: 2199360.62 },
  12: { kg: 98000, fat: 1409516.02 },
};

// ======================================================
// CARREGAR JSONs
// ======================================================
Promise.all([
  carregarJSON("kpi_faturamento.json"),
  carregarJSON("kpi_quantidade_pedidos.json"),
  carregarJSON("kpi_ticket_medio.json"),
  carregarJSON("kpi_kg_total.json"),
  carregarJSON("kpi_preco_medio.json"),
]).then(([fat, qtd, ticket, kg, preco]) => {
  if (!fat || !qtd || !ticket || !kg) return;

  const dataRef = fat.data_atual;
  const mes = Number(dataRef.split("/")[1]);
  const meta = METAS[mes];

  // ----------------------------------------------------------
  // SLIDE 1 – FATURAMENTO
  // ----------------------------------------------------------
  document.getElementById("fatQtdAtual").innerText =
    qtd.atual + " pedidos";

  document.getElementById("fatValorAtual").innerText =
    moeda(fat.atual);

  document.getElementById("fatDataAtual").innerText =
    `de 01/${dataRef.substring(3)} até ${dataRef}`;

  document.getElementById("fatQtdAnterior").innerText =
    qtd.ano_anterior + " pedidos";

  document.getElementById("fatValorAnterior").innerText =
    moeda(fat.ano_anterior);

  document.getElementById("fatDataAnterior").innerText =
    `de 01/${fat.data_ano_anterior.substring(3)} até ${fat.data_ano_anterior}`;

  const fatVar = fat.variacao;
  document.getElementById("fatVariacao").innerText =
    `${fatVar >= 0 ? "▲" : "▼"} ${percentual(Math.abs(fatVar))} vs ano anterior`;

  document.getElementById("fatMetaValor").innerText =
    "Meta mês: " + moeda(meta.fat);

  document.getElementById("fatMetaPerc").innerText =
    `🎯 ${percentual(fat.atual / meta.fat * 100)} da meta`;

  // ----------------------------------------------------------
  // SLIDE 2 – KG TOTAL
  // ----------------------------------------------------------
  document.getElementById("kgQtdAtual").innerText =
    qtd.atual + " pedidos";

  document.getElementById("kgValorAtual").innerText =
    numero(kg.atual) + " kg";

  document.getElementById("kgDataAtual").innerText =
    `de 01/${dataRef.substring(3)} até ${dataRef}`;

  document.getElementById("kgQtdAnterior").innerText =
    qtd.ano_anterior + " pedidos";

  document.getElementById("kgValorAnterior").innerText =
    numero(kg.ano_anterior) + " kg";

  document.getElementById("kgDataAnterior").innerText =
    `de 01/${fat.data_ano_anterior.substring(3)} até ${fat.data_ano_anterior}`;

  document.getElementById("kgVariacao").innerText =
    `${kg.variacao >= 0 ? "▲" : "▼"} ${percentual(Math.abs(kg.variacao))} vs ano anterior`;

  document.getElementById("kgMetaValor").innerText =
    "Meta mês: " + numero(meta.kg) + " kg";

  document.getElementById("kgMetaPerc").innerText =
    `🎯 ${percentual(kg.atual / meta.kg * 100)} da meta`;

  // ----------------------------------------------------------
  // SLIDE 3 – TICKET MÉDIO
  // ----------------------------------------------------------
  document.getElementById("ticketAtual").innerText =
    moeda(ticket.atual);

  document.getElementById("ticketAnterior").innerText =
    moeda(ticket.ano_anterior);

  document.getElementById("ticketQtdAtual").innerText =
    qtd.atual + " pedidos no período";

  document.getElementById("ticketQtdAnterior").innerText =
    qtd.ano_anterior + " pedidos no período";

  document.getElementById("ticketVariacao").innerText =
    `${ticket.variacao >= 0 ? "▲" : "▼"} ${percentual(Math.abs(ticket.variacao))}`;

  // ----------------------------------------------------------
  // SLIDE 5 – PREÇOS MÉDIOS
  // ----------------------------------------------------------
  if (preco) {
    document.getElementById("precoKg").innerText =
      moeda(preco.preco_medio_kg);
    document.getElementById("precoKgInfo").innerText =
      numero(preco.total_kg) + " kg no período";

    document.getElementById("precoM2").innerText =
      moeda(preco.preco_medio_m2);
    document.getElementById("precoM2Info").innerText =
      numero(preco.total_m2) + " m² no período";
  }
});
