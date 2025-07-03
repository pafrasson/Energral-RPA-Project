import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import numpy as np
import pandas as pd
import sqlite3

db_file = '../database.db'

# Define custom colors for better readability and a modern feel
status_colors = {
    'Inativo': '#FFC300',       # Amarelo (neutro, para inativo)
    'Falha': '#FF5733',         # Laranja-Vermelho (alerta, para falha)
    'Falha Crítica': '#C70039', # Vermelho Escuro (alto alerta, para falha crítica)
    'Operacional': '#28A745',   # Verde (positivo, para operacional)
    'Manutenção': '#007BFF'    # Azul (informativo, para em manutenção)
}

conn = None # Initialize connection outside try block for finally block access

try:
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    print(f"Conexão com o banco de dados '{db_file}' estabelecida com sucesso!")

    # Queries to get counts of equipment by status (lowercase for robustness)
    # Fetch results immediately after executing the query
    contagem_inativo = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "inativo"').fetchone()[0]
    contagem_falha = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "falha"').fetchone()[0]
    contagem_falha_critica = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "falha crítica"').fetchone()[0]
    contagem_operacional = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "operacional"').fetchone()[0]
    contagem_manutencao = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "em manutenção"').fetchone()[0]

    # Handle cases where counts might be None if the table is empty or status doesn't exist
    # This ensures we always have an integer for calculations
    contagem_inativo = contagem_inativo if contagem_inativo is not None else 0
    contagem_falha = contagem_falha if contagem_falha is not None else 0
    contagem_falha_critica = contagem_falha_critica if contagem_falha_critica is not None else 0
    contagem_operacional = contagem_operacional if contagem_operacional is not None else 0
    contagem_manutencao = contagem_manutencao if contagem_manutencao is not None else 0

    # Data for the pie chart
    x = [contagem_inativo, contagem_falha, contagem_falha_critica, contagem_operacional, contagem_manutencao]
    labels = ['Inativo', 'Falha', 'Falha Crítica', 'Operacional', 'Manutenção']

    # Filter out labels and data for zero values to avoid empty slices
    # The correct way to filter is to check 'val' (the count) not 'count' (the label)
    filtered_data = [(val, label) for val, label in zip(x, labels) if val > 0]

    # Unzip the filtered data back into separate lists
    if filtered_data: # Check if filtered_data is not empty
        filtered_x, filtered_labels = zip(*filtered_data)
        filtered_x = list(filtered_x) # Convert tuple back to list if needed for further processing
        filtered_labels = list(filtered_labels)
    else:
        # Handle the case where all counts are zero (no data to plot)
        print("Não há dados para exibir no gráfico. Todas as contagens são zero.")
        plt.close() # Close any open plot figure
        exit() # Exit the script if no data

    # Ensure the order of colors matches the order of data 'x' and 'labels'
    ordered_colors = [status_colors[label] for label in filtered_labels]

    # Define explode for emphasis (e.g., 'Falha Crítica')
    explode = [0.05] * len(filtered_x) # A subtle explode for all slices
    if 'Falha Crítica' in filtered_labels:
        idx_falha_critica = filtered_labels.index('Falha Crítica')
        explode[idx_falha_critica] = 0.15  # Slightly more emphasis on critical failure

    # Create the figure and axes for the plot
    fig, ax = plt.subplots(figsize=(10, 10)) # Adjust figure size for better clarity

    # Generate the pie chart
    wedges, texts, autotexts = ax.pie(filtered_x,
                                      colors=ordered_colors,
                                      autopct='%1.1f%%',
                                      pctdistance=0.85, # Position percentages closer to the center
                                      wedgeprops={"linewidth": 1, "edgecolor": "white"},
                                      explode=explode,
                                      startangle=90) # Start the first slice at 90 degrees (top)

    # Improve percentage text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
        autotext.set_bbox(dict(boxstyle="round,pad=0.2", fc="black", ec="none", lw=0, alpha=0.5)) # Background for visibility

    # Add a legend instead of direct annotations for a cleaner look
    ax.legend(wedges, filtered_labels,
              title="Status das Máquinas",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1), # Position the legend outside the pie
              fontsize=12,
              title_fontsize=14,
              frameon=False) # No frame around the legend

    # General visual improvements
    ax.set_title('Distribuição do Status das Máquinas', fontsize=20, fontweight='bold', color='#333333', pad=30)
    ax.set_aspect('equal') # Ensures the pie chart is circular
    ax.axis('off') # Removes the default matplotlib axes for a cleaner look

    # Set a soft background color for the figure
    fig.patch.set_facecolor('#f5f5f5')

    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    plt.show()

except sqlite3.Error as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
finally:
    # Ensure the database connection is closed, even if an error occurs
    if conn:
        conn.close()
        print("Conexão com o banco de dados fechada.")