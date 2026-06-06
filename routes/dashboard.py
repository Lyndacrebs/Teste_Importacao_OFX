from flask import Blueprint, render_template, request, redirect, flash
from services.dados_dashboard import (
    obter_resumo,
    gastos_por_categoria,
    evolucao_saldo,
    receitas_vs_despesas_mensal,
    obter_orcamento,
    definir_orcamento,
)
from services.graficos import (
    grafico_pizza,
    grafico_barras,
    grafico_linha,
    grafico_gauge,
)

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
def dashboard():
    resumo   = obter_resumo()
    orcamento = obter_orcamento()
    perc_orcamento = round(resumo['despesa'] / orcamento * 100, 1) if orcamento > 0 else 0.0

    return render_template(
        'dashboard.html',
        resumo=resumo,
        orcamento=orcamento,
        perc_orcamento=perc_orcamento,
        # HTML dos gráficos gerado pelo Python/Plotly
        chart_pizza=grafico_pizza(gastos_por_categoria()),
        chart_barras=grafico_barras(receitas_vs_despesas_mensal()),
        chart_linha=grafico_linha(evolucao_saldo()),
        chart_gauge=grafico_gauge(resumo['despesa'], orcamento),
    )


@dashboard_bp.route('/dashboard/orcamento', methods=['POST'])
def atualizar_orcamento():
    try:
        valor = float(request.form.get('orcamento', 0))
        if valor < 0:
            raise ValueError
        definir_orcamento(valor)
        flash('Orçamento atualizado com sucesso!', 'sucesso')
    except (ValueError, TypeError):
        flash('Valor de orçamento inválido.', 'erro')
    return redirect('/dashboard')
