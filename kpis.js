async function carregarKPIs() {
    const pedidos = await fetch("dados/kpi_quantidade_pedidos.json").then(r => r.json());
    const ticket = await fetch("dados/kpi_ticket_medio.json").then(r => r.json());
    const kg = await fetch("dados/kpi_kg_total.json").then(r => r.json());

    document.getElementById("kpi-pedidos").innerText = pedidos.atual;
    document.getElementById("var-pedidos").innerText = pedidos.variacao + "%";

    document.getElementById("kpi-ticket").innerText =
        ticket.atual.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
    document.getElementById("var-ticket").innerText = ticket.variacao + "%";

    document.getElementById("kpi-kg").innerText = kg.atual.toLocaleString("pt-BR");
    document.getElementById("var-kg").innerText = kg.variacao + "%";
}

async function carregarPrecoMedio() {
    const arquivo = await fetch("dados/kpi_preco_medio.json").then(r => r.json());

    const precoKg = arquivo.valor_total / arquivo.atual;
    const precoM2 = arquivo.valor_total / arquivo.total_m2;

    document.getElementById("preco-medio-kg").innerText =
        precoKg.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

    document.getElementById("preco-medio-m2").innerText =
        precoM2.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

carregarKPIs();
carregarPrecoMedio();
