import plotly.graph_objects as Caio

SEM_DADOS = '<p class="sem-dados">Nenhuma transação importada ainda.</p>'


def grafico_pizza(dados_categorias):
    if not dados_categorias:
        return SEM_DADOS

    categorias = []
    valores = []
    for auxiliar in dados_categorias:
        categorias.append(auxiliar['categoria'])
        valores.append(auxiliar['total'])

    fig = Caio.Figure(Caio.Pie(labels=categorias, values=valores, hole=0.4))
    fig.update_layout(height=500)

    return fig.to_html(full_html=False, include_plotlyjs=False)


def grafico_barras(dados_mensais):
    if not dados_mensais.get('meses'):
        return SEM_DADOS

    fig = Caio.Figure([
        Caio.Bar(name='Receitas', x=dados_mensais['meses'], y=dados_mensais['receitas'], marker_color='#22c55e'),
        Caio.Bar(name='Despesas', x=dados_mensais['meses'], y=dados_mensais['despesas'], marker_color='#ef4444'),
    ])
    fig.update_layout(height=500, barmode='group')

    return fig.to_html(full_html=False, include_plotlyjs=False)


def grafico_linha(dados_saldo):
    if not dados_saldo.get('datas'):
        return SEM_DADOS

    fig = Caio.Figure(Caio.Scatter(
        x=dados_saldo['datas'],
        y=dados_saldo['saldos'],
        mode='lines+markers',
        fill='tozeroy',
    ))
    fig.update_layout(height=320)

    return fig.to_html(full_html=False, include_plotlyjs=False)


def grafico_gauge(despesa_total, orcamento):
    maximo = max(orcamento * 1.5, despesa_total * 1.5, 100)

    fig = Caio.Figure(Caio.Indicator(
        mode='gauge+number',
        value=despesa_total,
        number=dict(prefix='R$ '),
        gauge=dict(
            axis=dict(range=[0, maximo]),
            bar=dict(color='#0055ff'),
            threshold=dict(
                line=dict(color='black', width=3),
                value=orcamento,
            ),
        ),
    ))
    fig.update_layout(height=250)

    return fig.to_html(full_html=False, include_plotlyjs=False)
