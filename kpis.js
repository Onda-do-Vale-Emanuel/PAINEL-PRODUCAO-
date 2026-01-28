async function atualizarKPIs() {
  try {
    const fat = await fetch("site/dados/kpi_faturamento.json").then(r => r.json());
    const qtd = await fetch("site/dados/kpi_quantidade_pedidos.json").then(r => r.json());

    // ===== SLIDE 1 =====
    document.getElementById("fatAtual").innerText =
      fat.atual.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

    document.getElementById("qtdAtual").innerText =
      `${qtd.atual} pedidos`;

    document.getElementById("periodoAtual").innerText =
      `até ${fat.data_fim}`;

    document.getElementById("fatAnoAnterior").innerText =
      fat.ano_anterior.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

    document.getElementById("qtdAnoAnterior").innerText =
      `${qtd.ano_anterior} pedidos`;

    document.getElementById("periodoAnterior").innerText =
      `até ${fat.data_ano_anterior || "mesmo período"}`;

    const variacao = document.getElementById("fatVariacao");
    variacao.innerText = `${fat.variacao}% vs ano anterior`;
    variacao.className = "box variacao " + (fat.variacao >= 0 ? "positivo" : "negativo");

    // ===== SLIDE 2 (META FIXA POR ENQUANTO) =====
    const META = 1325000;
    const perc = ((fat.atual / META) * 100).toFixed(1);

    document.getElementById("fatMeta").innerText =
      META.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

    document.getElementById("fatMetaPerc").innerText =
      `${perc}% da meta`;

    // ===== SLIDE 3 =====
    document.getElementById("resumoFat").innerText =
      fat.atual.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

    document.getElementById("resumoQtd").innerText =
      `${qtd.atual} pedidos`;

  } catch (e) {
    console.error("Erro ao atualizar KPIs:", e);
  }
}

atualizarKPIs();
setInterval(atualizarKPIs, 60000);
