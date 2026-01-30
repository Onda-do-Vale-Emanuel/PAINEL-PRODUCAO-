// ======================================================
// FUNÇÕES AUXILIARES
// ======================================================
function carregarJSON(nome) {
  return fetch("site/dados/" + nome)
    .then((resp) => {
      if (!resp.ok) {
        throw new Error("Erro ao carregar " + nome);
      }
      return resp.json();
    })
    .catch((err) => {
      console.error(err);
      return null;
    });
}

function formatarMoeda(valor) {
  return valor.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
  });
}

function formatarNumero(valor) {
  return valor.toLocaleString("pt-BR", {
    maximumFractionDigits: 2,
  });
}

function formatarPercentual(valor) {
  return valor.toFixed(1).toString().replace(".", ",") + "%";
}

function aplicarCorPosNeg(elemento, valor) {
  elemento.classList.remove("positivo", "negativo");
  if (valor > 0) elemento.classList.add("positivo");
  if (valor < 0) elemento.classList.add("negativo");
}

// ======================================================
// METAS POR MÊS (FATURAMENTO e KG) – opção A
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

function obterMetaMes(dataBR) {
  // dataBR: "29/01/2026"
  if (!dataBR) {
    return METAS[1];
  }
  const partes = dataBR.split("/");
  if (partes.length !== 3) {
    return METAS[1];
  }
  const mes = Number(partes[1]);
  return METAS[mes] || METAS[1];
}

// ======================================================
// CARREGAR TODOS OS KPIs
// ======================================================
Promise.all([
  carregarJSON("kpi_faturamento.json"),
  carregarJSON("kpi_quantidade_pedidos.json"),
  carregarJSON("kpi_ticket_medio.json"),
  carregarJSON("kpi_kg_total.json"),
]).then(([fat, qtd, ticket, kg]) => {
  if (!fat || !qtd || !ticket || !kg) {
    console.error("Algum JSON não foi carregado corretamente.");
    return;
  }

  // --------------------------------------------------
  // SLIDE 1 – FATURAMENTO COM IPI
  // --------------------------------------------------
  const dataRef = fat.data_atual; // "29/01/2026"
  const metasMes = obterMetaMes(dataRef);

  const fatAtual = fat.atual;
  const fatAnterior = fat.ano_anterior;
  const fatVar = fat.variacao;

  const qtdAtual = qtd.atual;
  const qtdAnterior = qtd.ano_anterior;

  // Cards principais
  document.getElementById("fatQtdAtual").innerText =
    qtdAtual.toLocaleString("pt-BR") + " pedidos";
  document.getElementById("fatValorAtual").innerText =
    formatarMoeda(fatAtual) + " (com IPI)";
  document.getElementById("fatDataAtual").innerText =
    "de 01/" + dataRef.substring(3) + " até " + dataRef;

  document.getElementById("fatQtdAnterior").innerText =
    qtdAnterior.toLocaleString("pt-BR") + " pedidos";
  document.getElementById("fatValorAnterior").innerText =
    formatarMoeda(fatAnterior) + " (com IPI)";
  document.getElementById("fatDataAnterior").innerText =
    "de 01/" +
    fat.data_ano_anterior.substring(3) +
    " até " +
    fat.data_ano_anterior;

  // Variação
  const elFatVar = document.getElementById("fatVariacao");
  const prefixoFat = fatVar >= 0 ? "▲" : "▼";
  elFatVar.innerText =
    `${prefixoFat} ${formatarPercentual(Math.abs(fatVar))} vs ano anterior`;
  aplicarCorPosNeg(elFatVar, fatVar);

  // Meta faturamento (usando tabela de metas)
  const metaFat = metasMes.fat;
  const percMetaFat = (fatAtual / metaFat) * 100;

  document.getElementById("fatMetaValor").innerText =
    "Meta mês: " + formatarMoeda(metaFat);
  const elFatMetaPerc = document.getElementById("fatMetaPerc");
  elFatMetaPerc.innerText =
    "🎯 " + formatarPercentual(percMetaFat) + " da meta";

  elFatMetaPerc.classList.remove("meta-ok", "meta-atencao", "meta-ruim");
  if (percMetaFat >= 100) {
    elFatMetaPerc.classList.add("meta-ok");
  } else if (percMetaFat >= 80) {
    elFatMetaPerc.classList.add("meta-atencao");
  } else {
    elFatMetaPerc.classList.add("meta-ruim");
  }

  // --------------------------------------------------
  // SLIDE 2 – KG TOTAL (COM 🎯 % DA META)
  // --------------------------------------------------
  const kgAtual = kg.atual;
  const kgAnterior = kg.ano_anterior;
  const kgVar = kg.variacao;

  const metaKg = metasMes.kg;
  const percMetaKg = (kgAtual / metaKg) * 100;

  document.getElementById("kgQtdAtual").innerText =
    qtdAtual.toLocaleString("pt-BR") + " pedidos";
  document.getElementById("kgValorAtual").innerText =
    formatarNumero(kgAtual) + " kg";
  document.getElementById("kgDataAtual").innerText =
    "de 01/" + dataRef.substring(3) + " até " + dataRef;

  document.getElementById("kgQtdAnterior").innerText =
    qtdAnterior.toLocaleString("pt-BR") + " pedidos";
  document.getElementById("kgValorAnterior").innerText =
    formatarNumero(kgAnterior) + " kg";
  document.getElementById("kgDataAnterior").innerText =
    "de 01/" +
    fat.data_ano_anterior.substring(3) +
    " até " +
    fat.data_ano_anterior;

  const elKgVar = document.getElementById("kgVariacao");
  const prefixoKg = kgVar >= 0 ? "▲" : "▼";
  elKgVar.innerText =
    `${prefixoKg} ${formatarPercentual(Math.abs(kgVar))} vs ano anterior`;
  aplicarCorPosNeg(elKgVar, kgVar);

  // 🎯 % da meta no SLIDE 2 (igual estilo do slide 1)
  document.getElementById("kgMetaValor").innerText =
    "Meta mês: " + formatarNumero(metaKg) + " kg";

  const elKgMetaPerc = document.getElementById("kgMetaPerc");
  elKgMetaPerc.innerText =
    "🎯 " + formatarPercentual(percMetaKg) + " da meta";

  elKgMetaPerc.classList.remove("meta-ok", "meta-atencao", "meta-ruim");
  if (percMetaKg >= 100) {
    elKgMetaPerc.classList.add("meta-ok");
  } else if (percMetaKg >= 80) {
    elKgMetaPerc.classList.add("meta-atencao");
  } else {
    elKgMetaPerc.classList.add("meta-ruim");
  }

  // --------------------------------------------------
  // SLIDE 3 – TICKET MÉDIO
  // --------------------------------------------------
  const ticketAtual = ticket.atual;
  const ticketAnterior = ticket.ano_anterior;
  const ticketVar = ticket.variacao;

  document.getElementById("ticketAtual").innerText =
    formatarMoeda(ticketAtual);
  document.getElementById("ticketAnterior").innerText =
    formatarMoeda(ticketAnterior);

  document.getElementById("ticketQtdAtual").innerText =
    qtdAtual.toLocaleString("pt-BR") + " pedidos no período";
  document.getElementById("ticketQtdAnterior").innerText =
    qtdAnterior.toLocaleString("pt-BR") + " pedidos no período";

  const elTicketVar = document.getElementById("ticketVariacao");
  const prefixoTicket = ticketVar >= 0 ? "▲" : "▼";
  elTicketVar.innerText =
    `${prefixoTicket} ${formatarPercentual(Math.abs(ticketVar))} vs ano anterior`;
  aplicarCorPosNeg(elTicketVar, ticketVar);
});
