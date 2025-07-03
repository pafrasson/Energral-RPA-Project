import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import numpy as np
import pandas as pd
import sqlite3

db_file = 'database.db'
conn = None # Inicializa a variável de conexão

try:
    # Conecta ao banco de dados SQLite
    conn = sqlite3.connect(db_file)
    print(f"Conexão com o banco de dados '{db_file}' estabelecida com sucesso!")

    # Consultas para obter a contagem de equipamentos por status (em minúsculas)
    inativo = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "inativo"')
    falha = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "falha"')
    falha_critica = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "falha crítica"')
    operacional = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "operacional"')
    manutencao = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "em manutenção"')

    # Obter os resultados das consultas
    row_inativo = inativo.fetchone()
    row_falha = falha.fetchone()
    row_falha_critica = falha_critica.fetchone()
    row_operacional = operacional.fetchone()
    row_manutencao = manutencao.fetchone()

    # Extrair as contagens, garantindo que sejam 0 se não houver resultados ou forem None
    contagem_inativo = row_inativo[0] if row_inativo and row_inativo[0] is not None else 0
    contagem_falha = row_falha[0] if row_falha and row_falha[0] is not None else 0
    contagem_falha_critica = row_falha_critica[0] if row_falha_critica and row_falha_critica[0] is not None else 0
    contagem_operacional = row_operacional[0] if row_operacional and row_operacional[0] is not None else 0
    contagem_manutencao = row_manutencao[0] if row_manutencao and row_manutencao[0] is not None else 0

    # Dados para o gráfico de pizza
    x = [contagem_inativo, contagem_falha, contagem_falha_critica, contagem_operacional, contagem_manutencao]
    labels = ['Inativo', 'Falha', 'Falha Crítica', 'Operacional', 'Em Manutenção']

    # Definir cores personalizadas para cada status para melhor visualização
    status_colors = {
        'Inativo': '#FFC300',       # Amarelo (para inativo, um estado neutro)
        'Falha': '#FF5733',         # Laranja-Vermelho (para falha, indicando atenção)
        'Falha Crítica': '#C70039', # Vermelho Escuro (para falha crítica, alto alerta)
        'Operacional': '#28A745',   # Verde (para operacional, indicando bom funcionamento)
        'Em Manutenção': '#007BFF'  # Azul (para em manutenção, indicando trabalho em andamento)
    }
    # Garante que a ordem das cores corresponda à ordem dos dados 'x' e 'labels'
    ordered_colors = [status_colors[label] for label in labels]

    # Configurar 'explode' para destacar a fatia de 'Falha Crítica'
    explode = [0] * len(x)
    # Verifica se 'Falha Crítica' existe nas labels e se há contagem para ela
    if 'Falha Crítica' in labels and contagem_falha_critica > 0:
        idx_falha_critica = labels.index('Falha Crítica')
        explode[idx_falha_critica] = 0.1 # Valor para destacar a fatia

    # Criar a figura e o eixo do gráfico
    fig, ax = plt.subplots(figsize=(10, 10)) # Ajusta o tamanho da figura para melhor clareza

    # Gerar o gráfico de pizza
    # radius=1 para facilitar o cálculo das posições das anotações (centro 0,0)
    # pctdistance=0.75 para posicionar as porcentagens dentro das fatias
    wedges, texts, autotexts = ax.pie(x, colors=ordered_colors, radius=1,
                                      wedgeprops={"linewidth": 1, "edgecolor": "white"},
                                      explode=explode,
                                      autopct='%1.1f%%',
                                      pctdistance=0.75)

    # Adicionar anotações (setas e rótulos) para cada fatia
    center_x, center_y = 0, 0 # O centro do gráfico de pizza é (0,0)
    radius = 1 # O raio do gráfico de pizza
    text_radius_multiplier = 1.67 # Multiplicador para a distância do texto em relação ao centro

    for i, (wedge, label) in enumerate(zip(wedges, labels)):
        # Calcula o ângulo do ponto médio da fatia
        angle = (wedge.theta2 + wedge.theta1) / 2.0

        # Ponto na fatia do gráfico (xy) onde a seta se origina
        x_slice = center_x + (radius * np.cos(np.deg2rad(angle)))
        y_slice = center_y + (radius * np.sin(np.deg2rad(angle)))

        # Posição para o texto (xytext) onde o rótulo será exibido
        x_text = center_x + (radius * text_radius_multiplier) * np.cos(np.deg2rad(angle))
        y_text = center_y + (radius * text_radius_multiplier) * np.sin(np.deg2rad(angle))

        # Ajusta o alinhamento horizontal do texto com base no ângulo para evitar sobreposição
        ha = 'left' if 90 < angle < 270 else 'right'
        if angle == 90 or angle == 270: ha = 'center'

        # Adiciona a anotação com seta e uma caixa de texto
        ax.annotate(label, xy=(x_slice, y_slice), xytext=(x_text, y_text),
                    arrowprops=dict(arrowstyle="-", connectionstyle="arc3,rad=.7", color='gray', lw=0.2),
                    fontsize=12, ha=ha, va='center',
                    # Adiciona uma caixa de fundo ao texto para melhor legibilidade
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", lw=0.5, alpha=0.8))

    # Melhorias visuais gerais
    # Título do gráfico
    ax.set_title('Distribuição do Status das Máquinas', fontsize=20, fontweight='bold', color='#333333', pad=30)
    ax.set_aspect('equal') # Garante que o gráfico de pizza seja um círculo perfeito
    ax.axis('off') # Remove os eixos e rótulos padrão do matplotlib para um visual mais limpo

    # Ajustar propriedades do texto das porcentagens dentro das fatias
    for autotext in autotexts:
        autotext.set_color('white') # Cor do texto
        autotext.set_fontsize(12)   # Tamanho da fonte
        autotext.set_fontweight('bold') # Negrito

    # Remover os rótulos padrão do pie (já que estamos usando anotações personalizadas)
    for text in texts:
        text.set_visible(False)

    # Definir uma cor de fundo suave para a figura para um visual mais agradável
    fig.patch.set_facecolor('#f5f5f5')

    plt.show()

except sqlite3.Error as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
finally:
    # Garante que a conexão com o banco de dados seja fechada, mesmo que ocorra um erro
    if conn:
        conn.close()
        print("Conexão com o banco de dados fechada.")
