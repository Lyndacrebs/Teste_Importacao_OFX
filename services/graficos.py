"""
Geração dos gráficos Plotly em Python.
Cada função recebe os dados já processados e retorna uma string HTML
pronta para ser inserida no template com {{ var | safe }}.
"""
import plotly.graph_objects as go

_SEM_DADOS = '<p class="sem-dados">Nenhuma transação importada ainda.</p>'

_LAYOUT_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Arial, Helvetica, sans-serif', size=12, color='#444'),
)

_CFG = dict(responsive=True, displayModeBar=False)


def _to_div(fig):
    """Converte figura Plotly em div HTML sem incluir o JS do Plotly."""
    return fig.to_html(full_html=False, include_plotlyjs=False, config=_CFG)


def grafico_pizza(dados_categorias):
    """Gráfico de rosca com distribuição de gastos por categoria."""
    if not dados_categorias:
        return _SEM_DADOS

    fig = go.Figure(go.Pie(
        labels=[d['categoria'] for d in dados_categorias],
        values=[d['total'] for d in dados_categorias],
        hole=0.42,
        textinfo='percent',
        hovertemplate='<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>',
    ))
    fig.update_layout(
        **_LAYOUT_BASE,
        height=310,
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=True,
        legend=dict(orientation='v', x=1.02, y=0.5),
    )
    return _to_div(fig)


def grafico_barras(dados_mensais):
    """Gráfico de barras agrupadas: receitas x despesas por mês."""
    if not dados_mensais.get('meses'):
        return _SEM_DADOS

    fig = go.Figure([
        go.Bar(
            name='Receitas',
            x=dados_mensais['meses'],
            y=dados_mensais['receitas'],
            marker_color='#22c55e',
            hovertemplate='R$ %{y:,.2f}<extra>Receitas</extra>',
        ),
        go.Bar(
            name='Despesas',
            x=dados_mensais['meses'],
            y=dados_mensais['despesas'],
            marker_color='#ef4444',
            hovertemplate='R$ %{y:,.2f}<extra>Despesas</extra>',
        ),
    ])
    fig.update_layout(
        **_LAYOUT_BASE,
        height=310,
        barmode='group',
        margin=dict(t=10, b=40, l=60, r=20),
        legend=dict(orientation='h', y=-0.25),
        yaxis=dict(tickprefix='R$ ', gridcolor='#f0f0f0'),
        xaxis=dict(showgrid=False),
    )
    return _to_div(fig)


def grafico_linha(dados_saldo):
    """Gráfico de linha com área mostrando evolução do saldo acumulado."""
    if not dados_saldo.get('datas'):
        return _SEM_DADOS

    fig = go.Figure(go.Scatter(
        x=dados_saldo['datas'],
        y=dados_saldo['saldos'],
        mode='lines+markers',
        line=dict(color='#0055ff', width=2),
        marker=dict(size=5, color='#0055ff'),
        fill='tozeroy',
        fillcolor='rgba(0, 85, 255, 0.07)',
        hovertemplate='%{x}<br><b>R$ %{y:,.2f}</b><extra>Saldo</extra>',
    ))
    fig.update_layout(
        **_LAYOUT_BASE,
        height=320,
        margin=dict(t=10, b=40, l=60, r=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(
            tickprefix='R$ ',
            gridcolor='#f0f0f0',
            zeroline=True,
            zerolinecolor='#ddd',
        ),
    )
    return _to_div(fig)


def grafico_gauge(despesa_total, orcamento):
    """Gauge mostrando despesa atual em relação ao orçamento definido."""
    max_gauge = (
        max(orcamento * 1.2, despesa_total * 1.1)
        if orcamento > 0
        else max(despesa_total * 1.2, 1000.0)
    )
    cor_barra = '#ef4444' if (orcamento > 0 and despesa_total > orcamento) else '#0055ff'

    steps = []
    threshold = {}
    if orcamento > 0:
        steps = [
            dict(range=[0, orcamento * 0.8], color='#dcfce7'),
            dict(range=[orcamento * 0.8, orcamento], color='#fef9c3'),
            dict(range=[orcamento, max_gauge], color='#fee2e2'),
        ]
        threshold = dict(line=dict(color='#000', width=3), thickness=0.75, value=orcamento)

    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=despesa_total,
        delta=dict(
            reference=orcamento,
            increasing=dict(color='#ef4444'),
            decreasing=dict(color='#22c55e'),
            valueformat=',.2f',
        ),
        number=dict(prefix='R$ ', valueformat=',.2f'),
        gauge=dict(
            axis=dict(range=[0, max_gauge], tickprefix='R$ ', nticks=5),
            bar=dict(color=cor_barra),
            bgcolor='#f9f9f9',
            borderwidth=0,
            steps=steps,
            threshold=threshold,
        ),
    ))
    fig.update_layout(
        **_LAYOUT_BASE,
        height=250,
        margin=dict(t=30, b=0, l=30, r=30),
    )
    return _to_div(fig)
