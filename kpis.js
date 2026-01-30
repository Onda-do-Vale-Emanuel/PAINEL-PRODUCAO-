async function carregarJSON(caminho) {
    try {
        const r = await fetch(caminho);
        if (!r.ok) return null;
        return await r.json();
    } catch (e) {
        console.error("Erro ao carregar:", caminho, e);
        return null;
    }
}

async function carregarKPIs() {
    const faturamento = await carregarJSON("site/dados/kpi_faturamento.json");
    const kg = await carregarJSON("site/dados/kpi_kg_total.json");
    const ticket = await carregarJSON("site/dados/kpi_ticket_medio.json");
    const preco = await carregarJSON("site/dados/kpi_preco_medio.json");

    return { faturamento, kg, ticket, preco };
}

function atualizarTela(d) {

    /* ================================
       SLIDE 1 - FATURAMENTO
    ================================= */
    if (d.faturamento) {
        document.getElementById("fatQtdAtual").innerText =
            d.faturamento.atual ?? "--";

        document.getElementById("fatValorAtual").innerText =
            d.faturamento.valor_atual
                ? `R$ ${d.faturamento.valor_atual.toLocaleString("pt-BR")}`
                : "--";

        document.getElementById("fatDataAtual").innerText =
            d.faturamento.data ?? "--";

        document.getElementById("fatQtdAnterior").innerText =
            d.faturamento.ano_anterior ?? "--";

        document.getElementById("fatValorAnterior").innerText =
            d.faturamento.valor_ano_anterior
                ? `R$ ${d.faturamento.valor_ano_anterior.toLocaleString("pt-BR")}`
                : "--";

        document.getElementById("fatDataAnterior").innerText =
            d.faturamento.data_ano_anterior ?? "--";

        document.getElementById("fatVariacao").innerText =
            d.faturamento.variacao
                ? `${d.faturamento.variacao}%`
                : "--";

        document.getElementById("fatMetaValor").innerText =
            `Meta mês: R$ ${d.faturamento.meta.toLocaleString("pt-BR")}`;

        document.getElementById("fatMetaPerc").innerText =
            `🎯 ${d.faturamento.meta_perc}% da meta`;
    }

    /* ================================
       SLIDE 2 - KG TOTAL
    ================================= */
    if (d.kg) {
        document.getElementById("kgQtdAtual").innerText =
            d.kg.atual ?? "--";

        document.getElementById("kgValorAtual").innerText =
            d.kg.atual
                ? `${d.kg.atual.toLocaleString("pt-BR")} kg`
                : "--";

        document.getElementById("kgDataAtual").innerText =
            d.kg.data ?? "--";

        document.getElementById("kgQtdAnterior").innerText =
            d.kg.ano_anterior ?? "--";

        document.getElementById("kgValorAnterior").innerText =
            d.kg.ano_anterior
                ? `${d.kg.ano_anterior.toLocaleString("pt-BR")} kg`
                : "--";

        document.getElementById("kgDataAnterior").innerText =
            d.kg.data_ano_anterior ?? "--";

        document.getElementById("kgVariacao").innerText =
            d.kg.variacao ? `${d.kg.variacao}%` : "--";

        document.getElementById("kgMetaValor").innerText =
            `Meta mês: ${d.kg.meta.toLocaleString("pt-BR")} kg`;

        document.getElementById("kgMetaPerc").innerText =
            `🎯 ${d.kg.meta_perc}% da meta`;
    }

    /* ================================
       SLIDE 3 – TICKET MÉDIO
    ================================= */
    if (d.ticket) {
        document.getElementById("ticketAtual").innerText =
            d.ticket.atual
                ? `R$ ${d.ticket.atual.toLocaleString("pt-BR")}`
                : "--";

        document.getElementById("ticketQtdAtual").innerText =
            d.ticket.qtd_atual ?? "--";

        document.getElementById("ticketAnterior").innerText =
            d.ticket.ano_anterior
                ? `R$ ${d.ticket.ano_anterior.toLocaleString("pt-BR")}`
                : "--";

        document.getElementById("ticketQtdAnterior").innerText =
            d.ticket.qtd_ano_anterior ?? "--";

        document.getElementById("ticketVariacao").innerText =
            d.ticket.variacao ? `${d.ticket.variacao}%` : "--";
    }

    /* ================================
       SLIDE EXTRA – PREÇO MÉDIO
    ================================= */
    if (d.preco) {
        document.getElementById("preco-medio-kg").innerText =
            `R$ ${d.preco.preco_medio_kg.toLocaleString("pt-BR")}`;

        document.getElementById("preco-medio-m2").innerText =
            `R$ ${d.preco.preco_medio_m2.toLocaleString("pt-BR")}`;
    }
}

/* INICIAR O SISTEMA */
(async () => {
    const dados = await carregarKPIs();
    atualizarTela(dados);
})();
