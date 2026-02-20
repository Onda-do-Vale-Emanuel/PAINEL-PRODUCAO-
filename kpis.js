function formatarKg(valor) {
  return Math.round(Number(valor || 0)).toLocaleString("pt-BR") + " Kg";
}

function formatarPercent(valor) {
  return valor.toFixed(2).replace(".", ",") + " %";
}

function variacaoHTML(valor) {
  const classe = valor >= 0 ? "positivo" : "negativo";
  const seta = valor >= 0 ? "▲" : "▼";
  return `<span class="${classe}">${seta} ${Math.abs(valor).toFixed(2)}%</span>`;
}

/* DIA */
fetch("dados/kpi_peso_dia.json")
.then(r => r.json())
.then(data => {

  document.getElementById("diaImpAtual").innerText = formatarKg(data.impressoras.atual);
  document.getElementById("diaImpAnterior").innerText = formatarKg(data.impressoras.ano_anterior);
  document.getElementById("diaImpVar").innerHTML = variacaoHTML(data.impressoras.variacao);

  document.getElementById("diaAcabAtual").innerText = formatarKg(data.acabamento.atual);
  document.getElementById("diaAcabAnterior").innerText = formatarKg(data.acabamento.ano_anterior);
  document.getElementById("diaAcabVar").innerHTML = variacaoHTML(data.acabamento.variacao);

});

/* ACUMULADO */
fetch("dados/kpi_acumulado_mes.json")
.then(r => r.json())
.then(data => {

  document.getElementById("mesImpAtual").innerText = formatarKg(data.impressoras.atual);
  document.getElementById("mesAcabAtual").innerText = formatarKg(data.acabamento.atual);

});

/* META */
fetch("dados/kpi_meta_mes.json")
.then(r => r.json())
.then(data => {

  document.getElementById("metaImpValor").innerText = formatarKg(data.impressoras.meta);
  document.getElementById("metaImpPercent").innerText = formatarPercent(data.impressoras.percentual);
  document.getElementById("metaImpFalta").innerText =
      data.impressoras.falta > 0 ? "Falta: " + formatarKg(data.impressoras.falta) : "";

  document.getElementById("barraImp").style.width =
      Math.min(data.impressoras.percentual,100) + "%";

  if (data.impressoras.percentual >= 100) {
      document.getElementById("metaImpStatus").innerHTML =
        "🎉 Parabéns! Meta Atingida! 🎆";
  }

  document.getElementById("metaAcabValor").innerText = formatarKg(data.acabamento.meta);
  document.getElementById("metaAcabPercent").innerText = formatarPercent(data.acabamento.percentual);
  document.getElementById("metaAcabFalta").innerText =
      data.acabamento.falta > 0 ? "Falta: " + formatarKg(data.acabamento.falta) : "";

  document.getElementById("barraAcab").style.width =
      Math.min(data.acabamento.percentual,100) + "%";

  if (data.acabamento.percentual >= 100) {
      document.getElementById("metaAcabStatus").innerHTML =
        "🎉 Parabéns! Meta Atingida! 🎆";
  }

});