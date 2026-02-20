function formatarNumero(valor) {
  return Math.round(Number(valor || 0)).toLocaleString("pt-BR") + " Kg";
}

function formatarPercentual(valor) {
  return valor.toFixed(2).replace(".", ",") + " %";
}

/* ================= META ================= */

fetch("dados/kpi_meta_mes.json")
  .then(res => res.json())
  .then(data => {

    // IMPRESSORAS
    document.getElementById("metaImpValor").innerText = formatarNumero(data.impressoras.meta);
    document.getElementById("metaImpPercent").innerText = formatarPercentual(data.impressoras.percentual);
    document.getElementById("metaImpFalta").innerText =
        data.impressoras.falta > 0
            ? "Falta: " + formatarNumero(data.impressoras.falta)
            : "";

    document.getElementById("barraImp").style.width =
        Math.min(data.impressoras.percentual, 100) + "%";

    if (data.impressoras.percentual >= 100) {
        document.getElementById("metaImpStatus").innerHTML =
            "🎉 Parabéns! Meta Atingida! 🎆";
    }

    // ACABAMENTO
    document.getElementById("metaAcabValor").innerText = formatarNumero(data.acabamento.meta);
    document.getElementById("metaAcabPercent").innerText = formatarPercentual(data.acabamento.percentual);
    document.getElementById("metaAcabFalta").innerText =
        data.acabamento.falta > 0
            ? "Falta: " + formatarNumero(data.acabamento.falta)
            : "";

    document.getElementById("barraAcab").style.width =
        Math.min(data.acabamento.percentual, 100) + "%";

    if (data.acabamento.percentual >= 100) {
        document.getElementById("metaAcabStatus").innerHTML =
            "🎉 Parabéns! Meta Atingida! 🎆";
    }
});