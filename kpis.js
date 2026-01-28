// ======================================================
// CONFIGURAÇÕES
// ======================================================
const META_MES = 1325000;

// ======================================================
// FUNÇÕES AUXILIARES
// ======================================================
function formatarMoeda(valor) {
  return valor.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL"
  });
}

function formatarPercentual(valor) {
  return `${valor.toFixed(1).replace(".", ",")}%`;
}

function aplicarCor(elemento, valor) {
  elemento.classList.remove("positivo", "negativo");
  if (valor > 0) elemento.classList.add("positivo");
  if (valor < 0) elemento.classList.add("negativo");
}

// ======================================================
// KPI FATURAMENTO
// ======================================================
fetch("site/dados/kpi_faturamento.json")
  .then(r => r.json())
  .then(fat => {

    const atual = fat.atual;
    const anterior = fat.ano_anterior;
    const variacao = fat.variacao;

    const dataAtual = `até ${fat.data}`;
    const dataAnterior = `até ${fat.data.replace(fat.data.slice(-4), fat.data.slice(-4) - 1)}`;

    document.getElementById("fatAtual").innerText =
      formatarMoeda(atual);
    document.getElementById("fatDataAtual").innerText =
      `(${dataAtual})`;

    document.getElementById("fatAnoAnterior").innerText =
      formatarMoeda(anterior);
    document.getElementById("fatDataAnoAnterior").innerText =
      `(${dataAnterior})`;

    const elVar = document.getElementById("fatVariacao");
    elVar.innerText =
      `▲ ${formatarPercentual(variacao)} vs ano anterior`;
    aplicarCor(elVar, variacao);

    const percMeta = (atual / META_MES) * 100;
    document.getElementById("fatMeta").innerText =
      `Meta mês: ${formatarMoeda(META_MES)}`;
    document.getElementById("fatMetaPerc").innerText =
      `🎯 ${formatarPercentual(percMeta)} da meta`;
  });

// ======================================================
// KPI QUANTIDADE DE PEDIDOS
// ======================================================
fetch("site/dados/kpi_quantidade_pedidos.json")
  .then(r => r.json())
  .then(qtd => {

    document.getElementById("qtdAtual").innerText =
      qtd.atual;
    document.getElementById("qtdAnoAnterior").innerText =
      qtd.ano_anterior;

    document.getElementById("qtdAtualSlide").innerText =
      qtd.atual;
  });

// ======================================================
// KPI TICKET MÉDIO
// ======================================================
fetch("site/dados/kpi_ticket_medio.json")
  .then(r => r.json())
  .then(ticket => {
    document.getElementById("ticketAtual").innerText =
      formatarMoeda(ticket.valor);
  });
