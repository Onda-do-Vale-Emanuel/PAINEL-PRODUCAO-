function carregarJSON(nome) {
  return fetch("site/dados/" + nome)
    .then(r => r.json())
    .catch(() => null);
}

function formatarMoeda(v) {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function formatarNumero(v) {
  return v.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
}

function formatarPercentual(v) {
  return v.toFixed(1).replace(".", ",") + "%";
}

function aplicarCorPosNeg(el, valor) {
  el.classList.remove("positivo", "negativo");
  if (valor > 0) el.classList.add("positivo");
  if (valor < 0) el.classList.add("negativo");
}

/* ============================================================
   🟧 NOVA FUNÇÃO: CALCULA O INÍCIO DO PERÍODO CORRETO
   Usa a menor data real do mês disponível no JSON.
   ============================================================ */
function obterPrimeiraDataMes(dataStr, listaDatas) {
  const alvo = dataStr.substring(3); // pega "MM/YYYY"
  let primeira = null;

  for (const d of listaDatas) {
    if (!d) continue;

    if (d.substring(3) === alvo) {
      if (!primeira || d < primeira) primeira = d;
    }
  }
  return primeira ?? ("01/" + alvo);
}

Promise.all([
  carregarJSON("kpi_faturamento.json"),
  carregarJSON("kpi_quantidade_pedidos.json"),
  carregarJSON("kpi_ticket_medio.json"),
  carregarJSON("kpi_kg_total.json"),
  carregarJSON("kpi_preco_medio.json")
]).then(([fat, qtd, ticket, kg, preco]) => {

  /* ============================================================
     CAPTURA TODAS AS DATAS DISPONÍVEIS PARA CALCULAR O PERÍODO REAL
     ============================================================ */
  const datasPossiveis = [];

  if (fat?.data_atual) datasPossiveis.push(fat.data_atual);
  if (fat?.data_ano_anterior) datasPossiveis.push(fat.data_ano_anterior);
  if (preco?.data) datasPossiveis.push(preco.data);

  const dataInicio = obterPrimeiraDataMes(fat.data_atual, datasPossiveis);
  const dataFim = fat.data_atual;

  /* ========================== SLIDE 1 ============================ */

  document.getElementById("fatQtdAtual").innerText = qtd.atual + " pedidos";
  document.getElementById("fatValorAtual").innerText = formatarMoeda(fat.atual);
  document.getElementById("fatDataAtual").innerText =
    "de " + dataInicio + " até " + dataFim;

  document.getElementById("fatQtdAnterior").innerText =
    qtd.ano_anterior + " pedidos";
  document.getElementById("fatValorAnterior").innerText =
    formatarMoeda(fat.ano_anterior);
  document.getElementById("fatDataAnterior").innerText =
    "de 01/" + fat.data_ano_anterior.substring(3) +
    " até " + fat.data_ano_anterior;

  const elFatVar = document.getElementById("fatVariacao");
  const pfFat = fat.variacao >= 0 ? "▲" : "▼";
  elFatVar.innerText =
    `${pfFat} ${formatarPercentual(Math.abs(fat.variacao))} vs ano anterior`;
  aplicarCorPosNeg(elFatVar, fat.variacao);

  /* META FAT */
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

  const mes = Number(fat.data_atual.substring(3, 5));
  const metaFat = METAS[mes].fat;
  const metaFatPercCalc = (fat.atual / metaFat) * 100;

  document.getElementById("fatMetaValor").innerText =
    "Meta mês: " + formatarMoeda(metaFat);

  const elFatMetaPercText = document.getElementById("fatMetaPerc");
  elFatMetaPercText.innerText =
    "🎯 " + metaFatPercCalc.toFixed(1).replace(".", ",") + "% da meta";

  elFatMetaPercText.classList.remove("meta-ok", "meta-atencao", "meta-ruim");
  if (metaFatPercCalc >= 100) elFatMetaPercText.classList.add("meta-ok");
  else if (metaFatPercCalc >= 80) elFatMetaPercText.classList.add("meta-atencao");
  else elFatMetaPercText.classList.add("meta-ruim");

  /* ======================= SLIDE 2 – KG ======================== */

  const elKgVarHere = document.getElementById("kgVariacao");
  const pfKG = kg.variacao >= 0 ? "▲" : "▼";
  elKgVarHere.innerText =
    `${pfKG} ${formatarPercentual(Math.abs(kg.variacao))} vs ano anterior`;
  aplicarCorPosNeg(elKgVarHere, kg.variacao);

  document.getElementById("kgQtdAtual").innerText = qtd.atual + " pedidos";
  document.getElementById("kgValorAtual").innerText =
    formatarNumero(kg.atual) + " kg";
  document.getElementById("kgDataAtual").innerText =
    "de " + dataInicio + " até " + dataFim;

  document.getElementById("kgQtdAnterior").innerText =
    qtd.ano_anterior + " pedidos";
  document.getElementById("kgValorAnterior").innerText =
    formatarNumero(kg.ano_anterior) + " kg";
  document.getElementById("kgDataAnterior").innerText =
    "de 01/" + fat.data_ano_anterior.substring(3) +
    " até " + fat.data_ano_anterior;

  const metaKG = METAS[mes].kg;
  const metaKGperc = (kg.atual / metaKG) * 100;

  document.getElementById("kgMetaValor").innerText =
    "Meta mês: " + formatarNumero(metaKG) + " kg";

  const elKgMetaPercText = document.getElementById("kgMetaPerc");
  elKgMetaPercText.innerText =
    "🎯 " + metaKGperc.toFixed(1).replace(".", ",") + "% da meta";

  elKgMetaPercText.classList.remove("meta-ok", "meta-atencao", "meta-ruim");
  if (metaKGperc >= 100) elKgMetaPercText.classList.add("meta-ok");
  else if (metaKGperc >= 80) elKgMetaPercText.classList.add("meta-atencao");
  else elKgMetaPercText.classList.add("meta-ruim");

  /* ==================== SLIDE 3 – TICKET ===================== */

  document.getElementById("ticketAtual").innerText =
    formatarMoeda(ticket.atual);
  document.getElementById("ticketAnterior").innerText =
    formatarMoeda(ticket.ano_anterior);

  document.getElementById("ticketQtdAtual").innerText =
    qtd.atual + " pedidos no período";
  document.getElementById("ticketQtdAnterior").innerText =
    qtd.ano_anterior + " pedidos no período";

  const elTicketVar = document.getElementById("ticketVariacao");
  const pfT = ticket.variacao >= 0 ? "▲" : "▼";
  elTicketVar.innerText =
    `${pfT} ${formatarPercentual(Math.abs(ticket.variacao))} vs ano anterior`;
  aplicarCorPosNeg(elTicketVar, ticket.variacao);

  /* ==================== SLIDE 4 – PREÇO MÉDIO ================= */

  if (preco) {
    document.getElementById("precoMedioKG").innerText =
      "R$ " + preco.preco_medio_kg.toLocaleString("pt-BR");

    document.getElementById("precoMedioM2").innerText =
      "R$ " + preco.preco_medio_m2.toLocaleString("pt-BR");

    document.getElementById("precoDataKG").innerText =
      "Atualizado até " + preco.data;

    document.getElementById("precoDataM2").innerText =
      "Atualizado até " + preco.data;
  }
});
