from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import os
import numpy as np

app = Flask(__name__)

# Criar diretório para salvar gráficos
GRAPH_DIR = "static/graphs"
if not os.path.exists(GRAPH_DIR):
    os.makedirs(GRAPH_DIR)

# Rota para a página inicial
@app.route("/")
def index():
    return render_template("index.html")

# Rota para o gráfico X
@app.route("/graficox", methods=["GET", "POST"])
def graficox():
    if request.method == "POST":
        # Etapa 1: Receber número de amostras e tamanho da amostra
        if "num_amostras" in request.form and "tamanho_amostra" in request.form and "amostra_1" not in request.form:
            num_amostras = int(request.form["num_amostras"])
            tamanho_amostra = int(request.form["tamanho_amostra"])

            # Preparar a página para inserir os valores das amostras
            dados = {"num_amostras": num_amostras, "tamanho_amostra": tamanho_amostra}
            return render_template("graficox.html", dados=dados, grafico_path=None)

        # Etapa 2: Receber os valores das amostras
        elif "amostra_1" in request.form:
            num_amostras = int(request.form["num_amostras"])
            tamanho_amostra = int(request.form["tamanho_amostra"])

            # Recolher os dados fornecidos pelo usuário
            amostras = []
            for i in range(num_amostras):
                valores = request.form[f"amostra_{i+1}"].split(",")
                valores = [float(v) for v in valores]
                amostras.append(valores)

            # Calcular médias das amostras
            medias = [np.mean(amostra) for amostra in amostras]
            media_global = np.mean(medias)
            desvio_padrao = np.std(medias)
            limite_superior = media_global + (2 * desvio_padrao)
            limite_inferior = media_global - (2 * desvio_padrao)

            # Gerar gráfico
            plt.figure()
            plt.plot(medias, marker="o", label="Médias das Amostras")
            plt.axhline(y=media_global, color="green", linestyle="--", label="Média Global")
            plt.axhline(y=limite_superior, color="red", linestyle="--", label="Limite Superior")
            plt.axhline(y=limite_inferior, color="red", linestyle="--", label="Limite Inferior")
            plt.title("Gráfico X")
            plt.xlabel("Amostra")
            plt.ylabel("Média")
            plt.legend()
            plt.grid()

            # Salvar gráfico
            filepath = os.path.join(GRAPH_DIR, "grafico_x.png")
            plt.savefig(filepath)
            plt.close()

            return render_template("graficox.html", grafico_path=filepath, dados=None)

    # Primeira vez acessando a página
    return render_template("graficox.html", grafico_path=None, dados=None)


# Rota para o gráfico R
@app.route("/graficor", methods=["GET", "POST"])
def graficor():
    if request.method == "POST":
        # Verifica se estamos recebendo o número de amostras e tamanho da amostra (Etapa 1)
        if "num_amostras" in request.form and "tamanho_amostra" in request.form and "amostra_1" not in request.form:
            num_amostras = int(request.form["num_amostras"])
            tamanho_amostra = int(request.form["tamanho_amostra"])
            
            # Preparar a página para inserir os valores das amostras
            dados = {"num_amostras": num_amostras, "tamanho_amostra": tamanho_amostra}
            return render_template("graficor.html", dados=dados, grafico_path=None)
        
        # Segunda Etapa: Recebemos os valores das amostras
        elif "amostra_1" in request.form:
            num_amostras = int(request.form["num_amostras"])
            tamanho_amostra = int(request.form["tamanho_amostra"])

            # Recolher os dados fornecidos pelo usuário
            amostras = []
            for i in range(num_amostras):
                valores = request.form[f"amostra_{i+1}"].split(",")
                valores = [float(v) for v in valores]
                amostras.append(valores)

            # Calcular alcances das amostras
            alcances = [np.ptp(amostra) for amostra in amostras]
            alcance_medio = np.mean(alcances)
            limite_superior = alcance_medio + 1.5
            limite_inferior = max(alcance_medio - 1.5, 0)

            # Gerar gráfico
            plt.figure()
            plt.plot(alcances, marker="o", label="Alcance das Amostras")
            plt.axhline(y=alcance_medio, color="green", linestyle="--", label="Alcance Médio")
            plt.axhline(y=limite_superior, color="red", linestyle="--", label="Limite Superior")
            plt.axhline(y=limite_inferior, color="red", linestyle="--", label="Limite Inferior")
            plt.title("Gráfico R")
            plt.xlabel("Amostra")
            plt.ylabel("Alcance")
            plt.legend()
            plt.grid()

            # Salvar gráfico
            filepath = os.path.join(GRAPH_DIR, "grafico_r.png")
            plt.savefig(filepath)
            plt.close()

            return render_template("graficor.html", grafico_path=filepath, dados=None)

    # Primeira vez acessando a página
    return render_template("graficor.html", grafico_path=None, dados=None)

if __name__ == "__main__":
    app.run(debug=True)