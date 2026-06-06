from services.database import conectar_banco


def obter_resumo():
    """Retorna receita total, despesa total e saldo atual."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute(
            "SELECT COALESCE(SUM(valor), 0) as total FROM transacoes WHERE tipo = 'Entrada'"
        )
        receita = float(cursor.fetchone()['total'])

        cursor.execute(
            "SELECT COALESCE(SUM(ABS(valor)), 0) as total FROM transacoes WHERE tipo = 'Saída'"
        )
        despesa = float(cursor.fetchone()['total'])

        return {'receita': receita, 'despesa': despesa, 'saldo': receita - despesa}
    finally:
        cursor.close()
        conexao.close()


def gastos_por_categoria():
    """Retorna lista de {categoria, total} apenas para despesas."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("""
            SELECT c.nome_categoria AS categoria, COALESCE(SUM(ABS(t.valor)), 0) AS total
            FROM transacoes t
            JOIN categorias c ON t.id_categoria = c.id_categoria
            WHERE t.tipo = 'Saída'
            GROUP BY c.nome_categoria
            HAVING total > 0
            ORDER BY total DESC
        """)
        return [{'categoria': r['categoria'], 'total': float(r['total'])} for r in cursor.fetchall()]
    finally:
        cursor.close()
        conexao.close()


def evolucao_saldo():
    """Retorna listas paralelas de datas e saldo acumulado ao longo do tempo."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("""
            SELECT data_transacao, SUM(valor) AS total_dia
            FROM transacoes
            WHERE data_transacao IS NOT NULL
            GROUP BY data_transacao
            ORDER BY data_transacao
        """)
        datas, saldos, acumulado = [], [], 0.0
        for row in cursor.fetchall():
            acumulado += float(row['total_dia'])
            datas.append(row['data_transacao'])
            saldos.append(round(acumulado, 2))
        return {'datas': datas, 'saldos': saldos}
    finally:
        cursor.close()
        conexao.close()


def receitas_vs_despesas_mensal():
    """Retorna dados mensais de receitas e despesas para gráfico de barras."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("""
            SELECT strftime('%Y-%m', data_transacao) AS mes, tipo, SUM(ABS(valor)) AS total
            FROM transacoes
            WHERE data_transacao IS NOT NULL
            GROUP BY mes, tipo
            ORDER BY mes
        """)
        rows = cursor.fetchall()
        meses = sorted({r['mes'] for r in rows if r['mes']})
        receitas, despesas = [], []
        for mes in meses:
            receitas.append(next((float(r['total']) for r in rows if r['mes'] == mes and r['tipo'] == 'Entrada'), 0.0))
            despesas.append(next((float(r['total']) for r in rows if r['mes'] == mes and r['tipo'] == 'Saída'), 0.0))
        return {'meses': meses, 'receitas': receitas, 'despesas': despesas}
    finally:
        cursor.close()
        conexao.close()


def obter_orcamento():
    """Retorna o orçamento mensal definido, ou 0 se não configurado."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'orcamento_mensal'")
        row = cursor.fetchone()
        return float(row['valor']) if row else 0.0
    finally:
        cursor.close()
        conexao.close()


def definir_orcamento(valor):
    """Salva ou atualiza o orçamento mensal no banco."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES ('orcamento_mensal', ?)",
            (str(valor),)
        )
        conexao.commit()
    finally:
        cursor.close()
        conexao.close()
