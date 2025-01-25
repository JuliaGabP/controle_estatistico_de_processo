from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import os
import numpy as np
import requests

app = Flask(__name__)

# Criar diretório para salvar gráficos
GRAPH_DIR = "static/graphs"
if not os.path.exists(GRAPH_DIR):
    os.makedirs(GRAPH_DIR)

# Configuração do Bot Telegram
BOT_TOKEN = "7958030003:AAE5Jn7YJf-5WHzR3pLNsl0UiFN56buDsKc"
CHAT_ID = "-4785715708"

def enviar_alerta_telegram(mensagem):
    """
    Função para enviar uma mensagem via Telegram
    """
    url = f"https://api.telegram.org/bot7958030003:AAE5Jn7YJf-5WHzR3pLNsl0UiFN56buDsKc/sendMessage"
    payload = {
        "chat_id": "-4785715708",
        "text": mensagem
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Alerta enviado com sucesso!")
        else:
            print(f"Erro ao enviar alerta: {response.text}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

# Rota para o gráfico X
@app.route("/graficox", methods=["GET", "POST"])
def graficox():
    if request.method == "POST":
        # Etapa 1: Receber número de amostras e valor de A2
        if "num_amostras" in request.form and "A2" in request.form and not any(f"x_{i+1}" in request.form for i in range(int(request.form["num_amostras"]))):
            num_amostras = int(request.form["num_amostras"])
            A2 = float(request.form["A2"])
            dados = {"num_amostras": num_amostras, "A2": A2}
            return render_template("graficox.html", dados=dados, grafico_path=None)

        # Etapa 2: Receber valores de X̄ e R
        elif "x_1" in request.form:
            num_amostras = int(request.form["num_amostras"])
            A2 = float(request.form["A2"])

            # Capturar valores de X̄ e R
            x_values = [float(request.form[f"x_{i+1}"]) for i in range(num_amostras)]
            r_values = [float(request.form[f"r_{i+1}"]) for i in range(num_amostras)]

            # Calcular limites usando fórmulas estatísticas
            media_global = np.mean(x_values)
            r_medio = np.mean(r_values)
            limite_superior = media_global + (A2 * r_medio)
            limite_inferior = media_global - (A2 * r_medio)
            def verificar_regras(amostras_x, media_global, r_medio):
                """
                Verifica as regras da Western Electric e retorna os pontos que violam as regras.
                """
                limite_superior = media_global + A2 * r_medio
                limite_inferior = media_global - A2 * r_medio
                dois_sigma_superior = media_global + (2/3) * (A2 * r_medio)
                dois_sigma_inferior = media_global - (2/3) * (A2 * r_medio)
                um_sigma_superior = media_global + (1/3) * (A2 * r_medio)
                um_sigma_inferior = media_global - (1/3) * (A2 * r_medio)
    
                fora_limites = []
                sinais_amarelos = []

                # Regra 1: Ponto fora dos limites superiores/inferiores
                fora_limites = [i + 1 for i, x in enumerate(amostras_x) if x > limite_superior or x < limite_inferior]

                # Regra 2: Duas de três consecutivas acima de 2σ
                for i in range(len(amostras_x) - 2):
                    subset = amostras_x[i:i+3]
                    acima_2_sigma = sum(1 for x in subset if x > dois_sigma_superior)
                    abaixo_2_sigma = sum(1 for x in subset if x < dois_sigma_inferior)
                    if acima_2_sigma >= 2 or abaixo_2_sigma >= 2:
                        sinais_amarelos.append(f"Amostras {i+1}-{i+3}")

                # Regra 3: Quatro de cinco consecutivas acima de 1σ
                for i in range(len(amostras_x) - 4):
                    subset = amostras_x[i:i+5]
                    acima_1_sigma = sum(1 for x in subset if x > um_sigma_superior)
                    abaixo_1_sigma = sum(1 for x in subset if x < um_sigma_inferior)
                    if acima_1_sigma >= 4 or abaixo_1_sigma >= 4:
                        sinais_amarelos.append(f"Amostras {i+1}-{i+5}")

                # Regra 4: Oito consecutivas no mesmo lado da média
                for i in range(len(amostras_x) - 7):
                    subset = amostras_x[i:i+8]
                    acima_media = all(x > media_global for x in subset)
                    abaixo_media = all(x < media_global for x in subset)
                    if acima_media or abaixo_media:
                        sinais_amarelos.append(f"Amostras {i+1}-{i+8}")

                return fora_limites, sinais_amarelos
            # Verificar regras da Western Electric
            fora_limites, sinais_amarelos = verificar_regras(x_values, media_global, r_medio)
            
            # Enviar alertas
            if fora_limites:
                mensagem_vermelho = f"⚠️ Sinal VERMELHO; Pontos fora dos limites no Gráfico X̄: {fora_limites}"
                enviar_alerta_telegram(mensagem_vermelho)

            if sinais_amarelos:
                mensagem_amarelo = f"⚠️ Sinal AMARELO detectado (Western Electric): {sinais_amarelos}"
                enviar_alerta_telegram(mensagem_amarelo)

            # Gerar gráfico
            plt.figure()
            plt.plot(x_values, marker="o", label="Valores de X̄")
            plt.axhline(y=media_global, color="green", linestyle="--", label="Média Global")
            plt.axhline(y=limite_superior, color="red", linestyle="--", label="Limite Superior")
            plt.axhline(y=limite_inferior, color="red", linestyle="--", label="Limite Inferior")
            plt.title("Gráfico X̄")
            plt.xlabel("Amostra")
            plt.ylabel("X̄")
            plt.legend()
            plt.grid()

            # Salvar gráfico
            filepath = os.path.join(GRAPH_DIR, "grafico_x.png")
            plt.savefig(filepath)
            plt.close()

            return render_template("graficox.html", grafico_path=filepath, dados=None, fora_limites=fora_limites)

    # Primeira vez acessando a página
    return render_template("graficox.html", grafico_path=None, dados=None)



# Rota para o gráfico R
@app.route("/graficor", methods=["GET", "POST"])
def graficor():
    if request.method == "POST":
        # Etapa 1: Receber número de amostras e valores de D3 e D4
        if "num_amostras" in request.form and "D3" in request.form and "D4" in request.form and not any(f"r_{i+1}" in request.form for i in range(int(request.form["num_amostras"]))):
            num_amostras = int(request.form["num_amostras"])
            D3 = float(request.form["D3"])
            D4 = float(request.form["D4"])
            dados = {"num_amostras": num_amostras, "D3": D3, "D4": D4}
            return render_template("graficor.html", dados=dados, grafico_path=None)

        # Etapa 2: Receber valores de X̄ e R
        elif "r_1" in request.form:
            num_amostras = int(request.form["num_amostras"])
            D3 = float(request.form["D3"])
            D4 = float(request.form["D4"])

            # Capturar valores de R
            r_values = [float(request.form[f"r_{i+1}"]) for i in range(num_amostras)]

            # Calcular limites
            r_medio = np.mean(r_values)
            limite_superior = D4 * r_medio
            limite_inferior = D3 * r_medio

            # Identificar pontos fora dos limites
            fora_limites = [i+1 for i, r in enumerate(r_values) if r > limite_superior or r < limite_inferior]
            if fora_limites:
                mensagem = f"⚠️ ALERTA VERMELHO Pontos fora dos limites no Gráfico R: {fora_limites}"
                enviar_alerta_telegram(mensagem)

            # Gerar gráfico
            plt.figure()
            plt.plot(r_values, marker="o", label="Valores de R")
            plt.axhline(y=r_medio, color="green", linestyle="--", label="R Médio")
            plt.axhline(y=limite_superior, color="red", linestyle="--", label="Limite Superior")
            plt.axhline(y=limite_inferior, color="red", linestyle="--", label="Limite Inferior")
            plt.title("Gráfico R")
            plt.xlabel("Amostra")
            plt.ylabel("R")
            plt.legend()
            plt.grid()

            # Salvar gráfico
            filepath = os.path.join(GRAPH_DIR, "grafico_r.png")
            plt.savefig(filepath)
            plt.close()

            return render_template("graficor.html", grafico_path=filepath, dados=None, fora_limites=fora_limites)

    # Primeira vez acessando a página
    return render_template("graficor.html", grafico_path=None, dados=None)


if __name__ == "__main__":
    app.run(debug=True)
