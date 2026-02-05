function carregarJSON(nome) {
  return fetch("site/dados/" + nome)
    .then((r) => r.json())
    .catch(() => null);
}

function formatarMoeda(v) {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function formatarNumero(v) {
  return v.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
}

function formatarNumeroInteiro(v) {
  return v.toLocaleString("pt-BR", { maximumFractionDigits: 0 });
}

function formatarPercentual(v) {
  return v.toFixed(1).replace(".", ",") + "%";
}

function aplicarCorPosNeg(el, valor) {
  el.classList.remove("positivo", "negativo");
  if (valor > 0) el.classList.add("positivo");
  if (valor < 0) el.classList.add("negativo");
}

// ===================== METAS POR MÊS =====================
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

Promise.all([
  carregarJSON("kpi_faturamento.json"),
  carregarJSON("kpi_quantidade_pedidos.json"),
  carregarJSON("kpi_ticket_medio.json"),
  carregarJSON("kpi_kg_total.json"),
  carregarJSON("kpi_preco_medio.json"),
]).then(([fat, qtd, ticket, kg, preco]) => {
  if (!fat || !qtd || !ticket || !kg) {
    console.error("Erro ao carregar alguns KPIs:", { fat, qtd, ticket, kg, preco });
    return;
  }

  // Descobre o mês a partir da data_atual (formato dd/mm/aaaa)
  let mes = 1;
  if (fat.data_atual && typeof fat.data_atual === "string" && fat.data_atual.length >= 5) {
    mes = Number(fat.data_atual.substring(3, 5));
  }

  const metasMes = METAS[mes];

  /* ================= SLIDE 1 – FATURAMENTO ================= */
  document.getElementById("fatQtdAtual").innerText = qtd.atual + " pedidos";
  document.getElementById("fatValorAtual").innerText = formatarMoeda(fat.atual);
  document.getElementById("fatDataAtual").innerText =
    "de " + fat.inicio_mes + " até " + fat.data_atual;

  document.getElementById("fatQtdAnterior").innerText =
    qtd.ano_anterior + " pedidos";
  document.getElementById("fatValorAnterior").innerText = formatarMoeda(
    fat.ano_anterior
  );
  document.getElementById("fatDataAnterior").innerText =
    "de " + fat.inicio_mes_anterior + " até " + fat.data_ano_anterior;

  const elFatVar = document.getElementById("fatVariacao");
  const pfFat = fat.variacao >= 0 ? "▲" : "▼";
  elFatVar.innerText =
    pfFat +
    " " +
    formatarPercentual(Math.abs(fat.variacao)) +
    " vs ano anterior";
  aplicarCorPosNeg(elFatVar, fat.variacao);

  // Meta de faturamento
  if (metasMes) {
    const metaFat = metasMes.fat;
    const metaFatPerc = (fat.atual / metaFat) * 100;

    document.getElementById("fatMetaValor").innerText =
      "Meta mês: " + formatarMoeda(metaFat);

    const elFatMetaPerc = document.getElementById("fatMetaPerc");
    elFatMetaPerc.innerText =
      "🎯 " + metaFatPerc.toFixed(1).replace(".", ",") + "% da meta";

    elFatMetaPerc.classList.remove("meta-ok", "meta-atencao", "meta-ruim");
    if (metaFatPerc >= 100) elFatMetaPerc.classList.add("meta-ok");
    else if (metaFatPerc >= 80) elFatMetaPerc.classList.add("meta-atencao");
    else elFatMetaPerc.classList.add("meta-ruim");
  } else {
    document.getElementById("fatMetaValor").innerText = "Meta mês: --";
    document.getElementById("fatMetaPerc").innerText = "🎯 -- % da meta";
  }

  /* ================= SLIDE 2 – KG TOTAL ================= */
  const elKgVar = document.getElementById("kgVariacao");
  const pfKG = kg.variacao >= 0 ? "▲" : "▼";

  document.getElementById("kgQtdAtual").innerText = qtd.atual + " pedidos";
  document.getElementById("kgValorAtual").innerText =
    formatarNumeroInteiro(kg.atual) + " kg";
  document.getElementById("kgDataAtual").innerText =
    "de " + fat.inicio_mes + " até " + fat.data_atual;

  document.getElementById("kgQtdAnterior").innerText =
    qtd.ano_anterior + " pedidos";
  document.getElementById("kgValorAnterior").innerText =
    formatarNumeroInteiro(kg.ano_anterior) + " kg";
  document.getElementById("kgDataAnterior").innerText =
    "de " + fat.inicio_mes_anterior + " até " + fat.data_ano_anterior;

  elKgVar.innerText =
    pfKG +
    " " +
    formatarPercentual(Math.abs(kg.variacao)) +
    " vs ano anterior";
  aplicarCorPosNeg(elKgVar, kg.variacao);

  if (metasMes) {
    const metaKG = metasMes.kg;
    const metaKGperc = (kg.atual / metaKG) * 100;

    document.getElementById("kgMetaValor").innerText =
      "Meta mês: " + formatarNumero(metaKG) + " kg";

    const elKgMetaPerc = document.getElementById("kgMetaPerc");
    elKgMetaPerc.innerText =
      "🎯 " + metaKGperc.toFixed(1).replace(".", ",") + "% da meta";

    elKgMetaPerc.classList.remove("meta-ok", "meta-atencao", "meta-ruim");
    if (metaKGperc >= 100) elKgMetaPerc.classList.add("meta-ok");
    else if (metaKGperc >= 80) elKgMetaPerc.classList.add("meta-atencao");
    else elKgMetaPerc.classList.add("meta-ruim");
  } else {
    document.getElementById("kgMetaValor").innerText = "Meta mês: --";
    document.getElementById("kgMetaPerc").innerText = "🎯 -- % da meta";
  }

  /* ================= SLIDE 3 – TICKET MÉDIO ================= */
  const elTicketVar = document.getElementById("ticketVariacao");
  const pfT = ticket.variacao >= 0 ? "▲" : "▼";

  document.getElementById("ticketAtual").innerText = formatarMoeda(
    ticket.atual
  );
  document.getElementById("ticketAnterior").innerText = formatarMoeda(
    ticket.ano_anterior
  );

  document.getElementById("ticketQtdAtual").innerText =
    qtd.atual + " pedidos no período";
  document.getElementById("ticketQtdAnterior").innerText =
    qtd.ano_anterior + " pedidos no período";

  elTicketVar.innerText =
    pfT +
    " " +
    formatarPercentual(Math.abs(ticket.variacao)) +
    " vs ano anterior";
  aplicarCorPosNeg(elTicketVar, ticket.variacao);

  /* ================= SLIDE 4 – PREÇO MÉDIO ================= */
  if (preco) {
    document.getElementById("precoMedioKG").innerText =
      "R$ " + preco.preco_medio_kg.toLocaleString("pt-BR");
    document.getElementById("precoMedioM2").innerText =
      "R$ " + preco.preco_medio_m2.toLocaleString("pt-BR");

    document.getElementById("precoDataKG").innerText =
      "Atualizado até " + preco.data;
    document.getElementById("precoDataM2").innerText =
      "Atualizado até " + preco.data;
  } else {
    document.getElementById("precoMedioKG").innerText = "--";
    document.getElementById("precoMedioM2").innerText = "--";
    document.getElementById("precoDataKG").innerText = "--";
    document.getElementById("precoDataM2").innerText = "--";
  }
});
