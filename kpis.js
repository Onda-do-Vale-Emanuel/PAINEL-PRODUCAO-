// ======================================================
// PAINEL INFORMATIVO PRODUÇÃO - KPIs
// ======================================================

function formatarKg(valor) {
  return valor.toLocaleString("pt-BR", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }) + " kg";
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

    // Data
    document.getElementById("diaDataAtual").innerText =
      `Data: ${data.data_atual}`;

    // Impressoras
    document.getElementById("diaImpAtual").innerText =
      formatarKg(data.impressoras.atual);

    document.getElementById("diaImpAnterior").innerText =
      formatarKg(data.impressoras.ano_anterior);

    document.getElementById("diaImpVar").innerHTML =
      formatarVariacao(data.impressoras.variacao);

    // Acabamento
    document.getElementById("diaAcabAtual").innerText =
      formatarKg(data.acabamento.atual);

    document.getElementById("diaAcabAnterior").innerText =
      formatarKg(data.acabamento.ano_anterior);

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
      data.periodo_atual;

    // Impressoras
    document.getElementById("mesImpAtual").innerText =
      formatarKg(data.impressoras.atual);

    document.getElementById("mesImpAnterior").innerText =
      formatarKg(data.impressoras.ano_anterior);

    document.getElementById("mesImpVar").innerHTML =
      formatarVariacao(data.impressoras.variacao);

    // Acabamento
    document.getElementById("mesAcabAtual").innerText =
      formatarKg(data.acabamento.atual);

    document.getElementById("mesAcabAnterior").innerText =
      formatarKg(data.acabamento.ano_anterior);

    document.getElementById("mesAcabVar").innerHTML =
      formatarVariacao(data.acabamento.variacao);
  });