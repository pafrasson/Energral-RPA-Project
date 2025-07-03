import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import numpy as np
import pandas as pd
import sqlite3

db_file = 'database.db'

try:
    # Conecta ao banco de dados
    conn = sqlite3.connect(db_file)
    # Cria um objeto cursor, que permite executar comandos SQL
    print(f"Conexão com o banco de dados '{db_file}' estabelecida com sucesso!")
    inativo = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "inativo"')
    falha = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "falha"')
    falha_critica = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "falha crítica"')
    operacional = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "operacional"')
    manutencao = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "em manutenção"')

    row_inativo = inativo.fetchone()
    row_falha = falha.fetchone()
    row_falha_critica = falha_critica.fetchone()
    row_operacional = operacional.fetchone()
    row_manutencao = manutencao.fetchone()

    contagem_inativo = row_inativo[0] if row_inativo and row_inativo[0] is not None else 0
    contagem_falha = row_falha[0] if row_falha and row_falha[0] is not None else 0
    contagem_falha_critica = row_falha_critica[0] if row_falha_critica and row_falha_critica[0] is not None else 0
    contagem_operacional = row_operacional[0] if row_operacional and row_operacional[0] is not None else 0
    contagem_manutencao = row_manutencao[0] if row_manutencao and row_manutencao[0] is not None else 0

    x = [contagem_inativo, contagem_falha, contagem_falha_critica, contagem_operacional, contagem_manutencao]
    #x = [contagem_falha,contagem_falha_critica]

    # make data
    colors = plt.get_cmap('PuOr')(np.linspace(0.2, 0.7, len(x)))
    explode = [0.2] * len(x)
    # plot
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.pie(x, colors=colors, radius=3, center=(4, 4),
           wedgeprops={"linewidth": 1, "edgecolor": "white"},
           frame=True,
           explode=explode,
           autopct='%1.1f%%'),

    ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
           ylim=(0, 8), yticks=np.arange(1, 8))

    plt.show()

except sqlite3.Error as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
