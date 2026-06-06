# Este arquivo define as rotas (URLs) do dashboard financeiro.
# Um Blueprint é uma forma de organizar rotas por funcionalidade —
# aqui ficam todas as rotas relacionadas ao dashboard.

from flask import Blueprint, render_template, request, redirect, flash

# Funções que buscam os dados no banco para alimentar o dashboard
from services.dados_dashboard import (
    obter_resumo,                  # receita, despesa e saldo totais
    gastos_por_categoria,          # lista de gastos agrupados por categoria
    evolucao_saldo,                # saldo acumulado ao longo do tempo
    receitas_vs_despesas_mensal,   # comparação mensal de receitas x despesas
    obter_orcamento,               # orçamento mensal salvo pelo usuário
    definir_orcamento,             # salva um novo orçamento mensal
)

# Funções que convertem os dados em gráficos HTML prontos para o template
from services.graficos import (
    grafico_pizza,   # rosca com gastos por categoria
    grafico_barras,  # barras agrupadas de receitas x despesas por mês
    grafico_linha,   # linha de evolução do saldo
    grafico_gauge,   # velocímetro de consumo do orçamento
)

# Cria o Blueprint com o nome 'dashboard' — será registrado no app principal
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
def dashboard():
    """Rota principal do dashboard — monta e exibe todos os dados e gráficos."""

    # Busca os totais financeiros (receita, despesa, saldo)
    resumo    = obter_resumo()

    # Busca o orçamento mensal definido pelo usuário (ou 0 se nunca foi definido)
    orcamento = obter_orcamento()

    # Calcula quantos % do orçamento já foram gastos
    # Evita divisão por zero: se o orçamento for 0, o percentual é 0
    perc_orcamento = round(resumo['despesa'] / orcamento * 100, 1) if orcamento > 0 else 0.0

    # render_template monta o HTML do dashboard.html substituindo as variáveis
    # passadas como parâmetros pelos valores reais
    return render_template(
        'dashboard.html',
        resumo=resumo,                 # dicionário com receita, despesa e saldo
        orcamento=orcamento,           # valor numérico do orçamento (ex: 3000.0)
        perc_orcamento=perc_orcamento, # percentual gasto (ex: 72.5)

        # Cada chart_* é uma string HTML gerada pelo Plotly —
        # o template usa | safe para injetar o HTML sem escapar os caracteres
        chart_pizza=grafico_pizza(gastos_por_categoria()),
        chart_barras=grafico_barras(receitas_vs_despesas_mensal()),
        chart_linha=grafico_linha(evolucao_saldo()),
        chart_gauge=grafico_gauge(resumo['despesa'], orcamento),
    )


@dashboard_bp.route('/dashboard/orcamento', methods=['POST'])
def atualizar_orcamento():
    """Rota que recebe o formulário de orçamento e salva o novo valor no banco."""

    try:
        # Lê o valor enviado pelo formulário HTML; usa 0 como padrão se não vier nada
        valor = float(request.form.get('orcamento', 0))

        # Rejeita valores negativos — orçamento não pode ser negativo
        if valor < 0:
            raise ValueError

        # Salva o novo orçamento no banco de dados
        definir_orcamento(valor)

        # Exibe uma mensagem de sucesso que aparece no topo do dashboard
        flash('Orçamento atualizado com sucesso!', 'sucesso')

    except (ValueError, TypeError):
        # Se o valor não puder ser convertido para número ou for negativo, exibe erro
        flash('Valor de orçamento inválido.', 'erro')

    # Volta para a página do dashboard após salvar (ou após o erro)
    return redirect('/dashboard')
