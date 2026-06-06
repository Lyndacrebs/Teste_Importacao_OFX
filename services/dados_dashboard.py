# Este arquivo contém todas as funções que buscam dados do banco de dados
# para alimentar os gráficos e cards do dashboard financeiro.

from services.database import conectar_banco  # função que abre a conexão com o SQLite


def obter_resumo():
    """Retorna receita total, despesa total e saldo atual."""

    # Abre a conexão com o banco de dados
    conexao = conectar_banco()
    # O cursor é o objeto que executa as queries SQL
    cursor = conexao.cursor()

    try:
        # Soma todos os valores das transações do tipo 'Entrada' (receitas)
        # COALESCE retorna 0 quando não há transações (SUM de conjunto vazio é NULL no SQLite)
        cursor.execute(
            "SELECT COALESCE(SUM(valor), 0) as total FROM transacoes WHERE tipo = 'Entrada'"
        )
        # fetchone() pega a única linha retornada; ['total'] acessa a coluna pelo nome
        receita = float(cursor.fetchone()['total'])

        # Soma os valores das transações do tipo 'Saída' (despesas)
        # ABS porque saídas são armazenadas com valor negativo no banco
        cursor.execute(
            "SELECT COALESCE(SUM(ABS(valor)), 0) as total FROM transacoes WHERE tipo = 'Saída'"
        )
        despesa = float(cursor.fetchone()['total'])

        # Retorna um dicionário com os três valores calculados
        return {'receita': receita, 'despesa': despesa, 'saldo': receita - despesa}

    finally:
        # O bloco finally sempre executa, mesmo se der erro — garante que a conexão é fechada
        cursor.close()
        conexao.close()


def gastos_por_categoria():
    """Retorna lista de {categoria, total} apenas para despesas."""

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        # Junta a tabela de transações com a de categorias para obter o nome da categoria
        # Filtra só as saídas, agrupa por categoria e ordena da maior para a menor despesa
        # HAVING total > 0 remove categorias com saldo zero (não aparecem no gráfico)
        cursor.execute("""
            SELECT c.nome_categoria AS categoria, COALESCE(SUM(ABS(t.valor)), 0) AS total
            FROM transacoes t
            JOIN categorias c ON t.id_categoria = c.id_categoria
            WHERE t.tipo = 'Saída'
            GROUP BY c.nome_categoria
            HAVING total > 0
            ORDER BY total DESC
        """)

        # Transforma cada linha do resultado em um dicionário e retorna a lista
        return [{'categoria': r['categoria'], 'total': float(r['total'])} for r in cursor.fetchall()]

    finally:
        cursor.close()
        conexao.close()


def evolucao_saldo():
    """Retorna listas paralelas de datas e saldo acumulado ao longo do tempo."""

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        # Agrupa as transações por dia somando os valores (positivos e negativos)
        # e ordena do mais antigo para o mais recente
        cursor.execute("""
            SELECT data_transacao, SUM(valor) AS total_dia
            FROM transacoes
            WHERE data_transacao IS NOT NULL
            GROUP BY data_transacao
            ORDER BY data_transacao
        """)

        # Três listas que crescem juntas: datas, saldos e o acumulador temporário
        datas, saldos, acumulado = [], [], 0.0

        for row in cursor.fetchall():
            # soma progressiva dia a dia para gerar a curva de evolução do saldo
            # Ex: dia 1 = +100, dia 2 = -30 → saldos = [100, 70]
            acumulado += float(row['total_dia'])
            datas.append(row['data_transacao'])
            saldos.append(round(acumulado, 2))  # arredonda para 2 casas decimais (centavos)

        # O Plotly precisa de duas listas paralelas: eixo X (datas) e eixo Y (saldos)
        return {'datas': datas, 'saldos': saldos}

    finally:
        cursor.close()
        conexao.close()


def receitas_vs_despesas_mensal():
    """Retorna dados mensais de receitas e despesas para gráfico de barras."""

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        # strftime('%Y-%m', ...) formata a data como 'YYYY-MM' (ex: '2024-03')
        # Agrupa por mês e tipo, somando os valores absolutos
        cursor.execute("""
            SELECT strftime('%Y-%m', data_transacao) AS mes, tipo, SUM(ABS(valor)) AS total
            FROM transacoes
            WHERE data_transacao IS NOT NULL
            GROUP BY mes, tipo
            ORDER BY mes
        """)
        rows = cursor.fetchall()  # todos os resultados de uma vez

        # Extrai a lista de meses únicos e ordena cronologicamente
        meses = sorted({r['mes'] for r in rows if r['mes']})

        receitas, despesas = [], []

        for mes in meses:
            # Para cada mês, procura o total de receitas naquele mês
            # next(..., 0.0): se o mês não tiver receitas, usa 0 como padrão
            receitas.append(next(
                (float(r['total']) for r in rows if r['mes'] == mes and r['tipo'] == 'Entrada'),
                0.0
            ))
            # Mesma lógica para despesas
            despesas.append(next(
                (float(r['total']) for r in rows if r['mes'] == mes and r['tipo'] == 'Saída'),
                0.0
            ))

        # Retorna três listas paralelas: meses, receitas e despesas (mesma posição = mesmo mês)
        return {'meses': meses, 'receitas': receitas, 'despesas': despesas}

    finally:
        cursor.close()
        conexao.close()


def obter_orcamento():
    """Retorna o orçamento mensal definido, ou 0 se não configurado."""

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        # Busca o valor salvo na tabela de configurações usando a chave 'orcamento_mensal'
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'orcamento_mensal'")
        row = cursor.fetchone()

        # Se a linha existir, converte para float; caso contrário retorna 0
        return float(row['valor']) if row else 0.0

    finally:
        cursor.close()
        conexao.close()


def definir_orcamento(valor):
    """Salva ou atualiza o orçamento mensal no banco."""

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        # INSERT OR REPLACE atualiza o registro se a chave já existir (UPSERT do SQLite)
        # O valor é salvo como texto porque a tabela configuracoes armazena strings genéricas
        cursor.execute(
            "INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES ('orcamento_mensal', ?)",
            (str(valor),)
        )
        # commit() confirma a gravação no banco — sem ele, a alteração é descartada
        conexao.commit()

    finally:
        cursor.close()
        conexao.close()
