function formatarKg(v){
  return Math.round(Number(v||0)).toLocaleString("pt-BR")+" Kg";
}

function formatarPercent(v){
  return Number(v||0).toFixed(2).replace(".",",")+" %";
}

function variacaoHTML(v){
  if(isNaN(v)) return "";
  const classe=v>=0?"positivo":"negativo";
  const seta=v>=0?"▲":"▼";
  return `<span class="${classe}">${seta} ${Math.abs(v).toFixed(2)}%</span>`;
}

/* ================= DIA ================= */
fetch("dados/kpi_peso_dia.json")
.then(r=>r.json())
.then(d=>{
  document.getElementById("diaImpAtual").innerText=formatarKg(d.impressoras.atual);
  document.getElementById("diaImpAnterior").innerText=formatarKg(d.impressoras.ano_anterior);
  document.getElementById("diaImpVar").innerHTML=variacaoHTML(d.impressoras.variacao);
  document.getElementById("diaDataAtual").innerText="Data: "+d.data_atual;

  document.getElementById("diaAcabAtual").innerText=formatarKg(d.acabamento.atual);
  document.getElementById("diaAcabAnterior").innerText=formatarKg(d.acabamento.ano_anterior);
  document.getElementById("diaAcabVar").innerHTML=variacaoHTML(d.acabamento.variacao);
  document.getElementById("diaDataAtual2").innerText="Data: "+d.data_atual;
});

/* ================= ACUMULADO ================= */
fetch("dados/kpi_acumulado_mes.json")
.then(r=>r.json())
.then(d=>{
  document.getElementById("mesImpAtual").innerText=formatarKg(d.impressoras.atual);
  document.getElementById("mesImpAnterior").innerText=formatarKg(d.impressoras.ano_anterior);
  document.getElementById("mesImpVar").innerHTML=variacaoHTML(d.impressoras.variacao);
  document.getElementById("mesPeriodoAtual").innerText="Período: "+d.periodo_atual;

  document.getElementById("mesAcabAtual").innerText=formatarKg(d.acabamento.atual);
  document.getElementById("mesAcabAnterior").innerText=formatarKg(d.acabamento.ano_anterior);
  document.getElementById("mesAcabVar").innerHTML=variacaoHTML(d.acabamento.variacao);
  document.getElementById("mesPeriodoAtual2").innerText="Período: "+d.periodo_atual;
});

/* ================= META ================= */
fetch("dados/kpi_meta_mes.json")
.then(r=>r.json())
.then(d=>{
  document.getElementById("metaImpValor").innerText=formatarKg(d.impressoras.meta);
  document.getElementById("metaImpPercent").innerText=formatarPercent(d.impressoras.percentual);
  document.getElementById("metaImpFalta").innerText=d.impressoras.falta>0?"Falta: "+formatarKg(d.impressoras.falta):"";
  document.getElementById("barraImp").style.width=Math.min(d.impressoras.percentual,100)+"%";
  if(d.impressoras.percentual>=100){
    document.getElementById("metaImpStatus").innerHTML="🎉 Parabéns! Meta Atingida! 🎆";
  }

  document.getElementById("metaAcabValor").innerText=formatarKg(d.acabamento.meta);
  document.getElementById("metaAcabPercent").innerText=formatarPercent(d.acabamento.percentual);
  document.getElementById("metaAcabFalta").innerText=d.acabamento.falta>0?"Falta: "+formatarKg(d.acabamento.falta):"";
  document.getElementById("barraAcab").style.width=Math.min(d.acabamento.percentual,100)+"%";
  if(d.acabamento.percentual>=100){
    document.getElementById("metaAcabStatus").innerHTML="🎉 Parabéns! Meta Atingida! 🎆";
  }
});

/* ================= FRASES ================= */
fetch("dados/frases.json")
.then(r=>r.json())
.then(lista=>{
  const hoje = new Date().getDate();
  const frase = lista[(hoje-1) % lista.length];

  document.getElementById("fraseTexto").innerText = `"${frase.frase}"`;
  document.getElementById("fraseAutor").innerText = "- " + frase.autor;
  document.getElementById("fraseSignificado").innerText = "O que significa: " + frase.significado;
});
/* ================= FRASES ================= */
fetch("dados/frases.json")
.then(r=>r.json())
.then(lista=>{
  const hoje = new Date().getDate();
  const frase = lista[(hoje-1) % lista.length];

  document.getElementById("fraseTexto").innerText = `"${frase.frase}"`;
  document.getElementById("fraseAutor").innerText = "- " + frase.autor;
  document.getElementById("fraseSignificado").innerText = "O que significa: " + frase.significado;
});