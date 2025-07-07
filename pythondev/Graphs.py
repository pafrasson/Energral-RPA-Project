import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import numpy as np
import pandas as pd
import sqlite3
import os

def connection():
    db_file = 'database.db'

    # Define custom colors for better readability and a modern feel
    status_colors = {
        'Inativo': '#FFC300',       # Amarelo (neutro, para inativo)
        'Falha': '#FF5733',         # Laranja-Vermelho (alerta, para falha)
        'Falha Crítica': '#C70039', # Vermelho Escuro (alto alerta, para falha crítica)
        'Operacional': '#28A745',   # Verde (positivo, para operacional)
        'Manutenção': '#007BFF'    # Azul (informativo, para em manutenção)
    }

    conn = None # Initialize connection outside try block for finally block access
    allthemachinesstatus(db_file,status_colors,conn)
    alltheerrors(db_file,status_colors,conn)

def allthemachinesstatus(db_file,status_colors,conn):
    try:
        # Check if the database file exists before attempting to connect
        if not os.path.exists(db_file):
            print(f"Erro: O arquivo do banco de dados '{db_file}' não foi encontrado.")
            print("Por favor, verifique o caminho e certifique-se de que o arquivo existe.")
            exit() # Exit if the file doesn't exist

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

        # Ensure counts are non-None
        contagem_inativo = contagem_inativo if contagem_inativo is not None else 0
        contagem_falha = contagem_falha if contagem_falha is not None else 0
        contagem_falha_critica = contagem_falha_critica if contagem_falha_critica is not None else 0
        contagem_operacional = contagem_operacional if contagem_operacional is not None else 0
        contagem_manutencao = contagem_manutencao if contagem_manutencao is not None else 0

        # Data for the pie chart - using a list of tuples to maintain order and associate values with original labels
        data_points = [
            (contagem_inativo, 'Inativo'),
            (contagem_falha, 'Falha'),
            (contagem_falha_critica, 'Falha Crítica'),
            (contagem_operacional, 'Operacional'),
            (contagem_manutencao, 'Manutenção')
        ]

        # Filter out zero values and prepare formatted labels
        filtered_x = []
        filtered_labels = []
        original_status_for_colors = [] # To store original status names for color lookup

        for count, status_name in data_points:
            if count > 0:
                filtered_x.append(count)
                filtered_labels.append(f'{status_name}: {count}') # Formatted label for legend
                original_status_for_colors.append(status_name) # Original name for color mapping

        if not filtered_x: # Check if there's any data to plot after filtering
            print("Não há dados para exibir no gráfico. Todas as contagens são zero.")
            plt.close() # Close any open plot figure
            return # Use return instead of exit() to allow the program to continue if this function is called in a larger script

        # Ensure the order of colors matches the order of data and filtered labels
        ordered_colors = [status_colors[status] for status in original_status_for_colors]

        # Define explode for emphasis (e.g., 'Falha Crítica')
        explode = [0.0] * len(filtered_x) # Start with no explode for all slices
        # Find the index of 'Falha Crítica' in the original_status_for_colors list
        try:
            idx_falha_critica = original_status_for_colors.index('Falha Crítica')
            explode[idx_falha_critica] = 0.05 # Apply significant emphasis to critical failure
        except ValueError:
            # 'Falha Crítica' might not be in the data if its count is zero
            pass

        # Create the figure and axes for the plot
        fig, ax = plt.subplots(figsize=(16, 9)) # Adjust figure size for better clarity

        # Generate the pie chart
        wedges, texts, autotexts = ax.pie(filtered_x,
                                          colors=ordered_colors,
                                          autopct='%1.1f%%',
                                          pctdistance=0.85, # Position percentages closer to the center
                                          wedgeprops={"linewidth": 1, "edgecolor": "white"},
                                          explode=explode, # Use the customized explode list
                                          startangle=90) # Start the first slice at 90 degrees (top)

        # Improve percentage text readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
            # Add a background box for better contrast
            autotext.set_bbox(dict(boxstyle="round,pad=0.2", fc="black", ec="none", lw=0, alpha=0.5))

        # Add a legend with refined positioning and title
        ax.legend(wedges, filtered_labels,
                  title="Status das Máquinas",
                  loc="center left",
                  bbox_to_anchor=(1.05, 0, 0.5, 1), # Adjusted for more space between plot and legend
                  fontsize=12,
                  title_fontsize=14,
                  frameon=False) # No frame around the legend for a cleaner look

        # General visual improvements
        ax.set_title('Distribuição do Status das Máquinas', fontsize=20, fontweight='bold', color='#333333', pad=30)
        ax.set_aspect('equal') # Ensures the pie chart is circular
        ax.axis('off') # Removes the default matplotlib axes for a cleaner look

        # Set a soft background color for the figure
        fig.patch.set_facecolor('#f5f5f5')

        plt.tight_layout() # Adjust layout to prevent labels from overlapping
        plt.savefig('gráfico_visão_geral_maquinas.png', dpi=300, bbox_inches='tight')
        plt.show()

    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    finally:
        # Ensure the database connection is closed, even if an error occurs
        if conn:
            conn.close()
            print("Conexão com o banco de dados fechada.")

def alltheerrors(db_file,status_colors,conn):
    try:
        # Check if the database file exists before attempting to connect
        if not os.path.exists(db_file):
            print(f"Erro: O arquivo do banco de dados '{db_file}' não foi encontrado.")
            print("Por favor, verifique o caminho e certifique-se de que o arquivo existe.")
            exit() # Exit if the file doesn't exist

        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        print(f"Conexão com o banco de dados '{db_file}' estabelecida com sucesso!")

        # Queries to get counts of equipment by status (lowercase for robustness)
        # Fetch results immediately after executing the query
        contagem_falha = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "falha"').fetchone()[0]
        contagem_falha_critica = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "falha crítica"').fetchone()[0]
        contagem_allerrors = conn.execute('SELECT count(id_equipamento) FROM maquinas WHERE LOWER(status_maquina) = "falha crítica" or LOWER(status_maquina) = "falha"').fetchone()[0]

        contagem_fal = contagem_falha if contagem_falha is not None else 0
        contagem_falc = contagem_falha_critica if contagem_falha_critica is not None else 0
        contagem_allerrors = contagem_allerrors if contagem_allerrors is not None else 0

        # Data for the pie chart
        x = [contagem_fal, contagem_falc]
        labels = ['Falha', 'Falha Crítica']

        # Filter out labels and data for zero values to avoid empty slices
        filtered_data = []
        if contagem_fal > 0:
            filtered_data.append((contagem_fal, f'Falha: {contagem_fal}'))
        if contagem_falc > 0:
            filtered_data.append((contagem_falc, f'Falha Crítica: {contagem_falc}'))

        # Unzip the filtered data back into separate lists
        if filtered_data:  # Check if filtered_data is not empty
            filtered_x, filtered_labels = zip(*filtered_data)
            filtered_x = list(filtered_x)  # Convert tuple back to list if needed for further processing
            filtered_labels = list(filtered_labels)
        else:
            # Handle the case where all counts are zero (no data to plot)
            print("Não há dados para exibir no gráfico. Todas as contagens são zero.")
            plt.close()  # Close any open plot figure
            exit()  # Exit the script if no data

        # Ensure the order of colors matches the order of data 'x' and 'labels'
        ordered_colors = []
        for label in filtered_labels:
            # For labels like 'Falha: 24', split by ':' and take the first part, then strip any whitespace
            original_status = label.split(':')[0].strip()
            ordered_colors.append(status_colors[original_status])

        # Define explode for emphasis (e.g., 'Falha Crítica')
        explode = [0.05] * len(filtered_x) # A subtle explode for all slices
        if 'falha crítica' in filtered_labels:
            idx_falha_critica = filtered_labels.index('Falha Crítica')
            explode[idx_falha_critica] = 0.1  # Slightly more emphasis on critical failure

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
                  title=f"Status das Máquinas\nMáquinas com falhas: {contagem_allerrors}",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1), # Position the legend outside the pie
                  fontsize=12,
                  title_fontsize=14,
                  frameon=False) # No frame around the legend

        # General visual improvements
        ax.set_title(f'Distribuição do Status das Máquinas', fontsize=20, fontweight='bold', color='#333333', pad=30)
        ax.set_aspect('equal') # Ensures the pie chart is circular
        ax.axis('off') # Removes the default matplotlib axes for a cleaner look

        # Set a soft background color for the figure
        fig.patch.set_facecolor('#f5f5f5')

        plt.tight_layout() # Adjust layout to prevent labels from overlapping
        plt.savefig('gráfico_falhas.png', dpi=300, bbox_inches='tight')
        plt.show()

    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    finally:
        # Ensure the database connection is closed, even if an error occurs
        if conn:
            conn.close()
            print("Conexão com o banco de dados fechada.")

def main():
    connection()
    print('Programa finalizado!')

if __name__ == '__main__':
    main()