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
    inativo = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE status_maquina = "Inativo"')
    falha = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE status_maquina = "Falha"')
    operacional = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE status_maquina = "Operacional"')

    row_inativo = inativo.fetchone()
    row_falha = falha.fetchone()
    row_operacional = operacional.fetchone()

    contagem_inativo = row_inativo[0] if row_inativo and row_inativo[0] is not None else 0
    contagem_falha = row_falha[0] if row_falha and row_falha[0] is not None else 0
    contagem_operacional = row_operacional[0] if row_operacional and row_operacional[0] is not None else 0

    x = [contagem_inativo, contagem_falha, contagem_operacional]  # 'x' agora tem 2 elementos

    # make data
    colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(x)))
    explode = [0] * len(x)
    # plot
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.pie(x, colors=colors, radius=3, center=(4, 4),
           wedgeprops={"linewidth": 1, "edgecolor": "white"},
           frame=True,
           explode=explode),

    ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
           ylim=(0, 8), yticks=np.arange(1, 8))

    plt.show()

except sqlite3.Error as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
