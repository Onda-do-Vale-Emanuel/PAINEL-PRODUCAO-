// ======================================================
// PAINEL INFORMATIVO PRODUÇÃO - KPIs
// ======================================================

function formatarNumeroKg(valor) {
  const numero = Math.round(Number(valor || 0));

  return numero.toLocaleString("pt-BR", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }) + " Kg";
}

function formatarVariacao(valor) {
  const sinal = valor >= 0 ? "▲" : "▼";
  const classe = valor >= 0 ? "positivo" : "negativo";

  return `<span class="${classe}">${sinal} ${Math.abs(valor).toFixed(2)}%</span>`;
}

// =========================
// PESO DO DIA
// =========================

fetch("dados/kpi_peso_dia.json")
  .then(res => res.json())
  .then(data => {

    document.getElementById("diaDataAtual").innerText =
      `Data: ${data.data_atual}`;

    // IMPRESSORAS
    document.getElementById("diaImpAtual").innerText =
      formatarNumeroKg(data.impressoras.atual);

    document.getElementById("diaImpAnterior").innerText =
      formatarNumeroKg(data.impressoras.ano_anterior);

    document.getElementById("diaImpVar").innerHTML =
      formatarVariacao(data.impressoras.variacao);

    // ACABAMENTO
    document.getElementById("diaAcabAtual").innerText =
      formatarNumeroKg(data.acabamento.atual);

    document.getElementById("diaAcabAnterior").innerText =
      formatarNumeroKg(data.acabamento.ano_anterior);

    document.getElementById("diaAcabVar").innerHTML =
      formatarVariacao(data.acabamento.variacao);
  });


// =========================
// ACUMULADO DO MÊS
// =========================

fetch("dados/kpi_acumulado_mes.json")
  .then(res => res.json())
  .then(data => {

    document.getElementById("mesPeriodoAtual").innerText =
      `Período: ${data.periodo_atual}`;

    // IMPRESSORAS
    document.getElementById("mesImpAtual").innerText =
      formatarNumeroKg(data.impressoras.atual);

    document.getElementById("mesImpAnterior").innerText =
      formatarNumeroKg(data.impressoras.ano_anterior);

    document.getElementById("mesImpVar").innerHTML =
      formatarVariacao(data.impressoras.variacao);

    // ACABAMENTO
    document.getElementById("mesAcabAtual").innerText =
      formatarNumeroKg(data.acabamento.atual);

    document.getElementById("mesAcabAnterior").innerText =
      formatarNumeroKg(data.acabamento.ano_anterior);

    document.getElementById("mesAcabVar").innerHTML =
      formatarVariacao(data.acabamento.variacao);
  });