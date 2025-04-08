import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog
import os

def carregar_csv():
    root = tk.Tk()
    root.withdraw()
    arquivo = filedialog.askopenfilename(filetypes=[("Arquivos CSV", "*.csv")])
    if not arquivo:
        return None
    try:
        df = pd.read_csv(arquivo)
        return df
    except Exception as e:
        return None

def gerar_graficos(df, colunas_fonte_personalizada=None, colunas_max_categorias=None, colunas_quebra_linha=None):
    pasta_saida = "Graficos2"
    os.makedirs(pasta_saida, exist_ok=True)
    
    #gerar_grafico_disciplinas_por_ano(df)
         
    fontes_padrao = 10
    fontes_personalizadas = colunas_fonte_personalizada if colunas_fonte_personalizada else {}
    
    max_categorias_padrao = 100
    categorias_personalizadas = colunas_max_categorias if colunas_max_categorias else {}
    
    quebra_linha_padrao = 20
    quebras_personalizadas = colunas_quebra_linha if colunas_quebra_linha else {}

    principais_cidades_ac = ["Rio Branco-AC", "Cruzeiro do Sul-AC", "Tarauaca-AC", "Sena Madureira-AC"]
    
    if "ANO_DISCIPLINA" in df.columns:
        df["ANO_DISCIPLINA"] = df["ANO_DISCIPLINA"].apply(lambda x: x if x != df["ANO_DISCIPLINA"].max() else None)
                 
    if "COTAS" in df.columns:
        df["COTAS"] = df["COTAS"].replace({
            "Candidatos de Escola Publica com Baixa Renda PPI": "Baixa Renda PPI",
            "Candidatos de Escola Publica Independente de Renda PPI": "Independente de Renda PPI"})
        
    for coluna in df.select_dtypes(include=['number']).columns:
        plt.figure(figsize=(12, 6))
        catego = df[coluna].value_counts().index.astype(int)
        valor = df[coluna].value_counts().values
        colors = sns.color_palette("viridis", len(catego))
        ax = sns.barplot(x=catego, y=valor, palette=colors)

        
        rotulo_x, rotulo_y = definir_rotulos(pasta_saida, coluna)
        plt.xlabel(rotulo_x, fontsize=11, labelpad=7)
        plt.ylabel(rotulo_y, fontsize=11, labelpad=10)
            
        plt.grid(False)

        for u in ax.patches:
            ax.annotate(f'{int(u.get_height())}', (u.get_x() + u.get_width() / 2, u.get_height()), 
                        xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', 
                        fontsize=10, color='black')

        plt.savefig(os.path.join(pasta_saida, f"{coluna}.png"))
        plt.close()
    
    for coluna in df.select_dtypes(include=['object']).columns:
        if coluna == "NATURALIDADE":
            df_filtrado = df.copy()
            df_filtrado["NATURALIDADE"] = df_filtrado["NATURALIDADE"].apply(lambda x: x if x in principais_cidades_ac else "Outros")

            plt.figure(figsize=(12, 6))
            ax = sns.countplot(x=df_filtrado["NATURALIDADE"], order=df_filtrado["NATURALIDADE"].value_counts().index, palette="viridis")

            rotulo_x, rotulo_y = definir_rotulos(pasta_saida, coluna)
            plt.xlabel(rotulo_x, fontsize=11, labelpad=7)
            plt.ylabel(rotulo_y, fontsize=11, labelpad=10)
            
            for l in ax.patches:
                ax.annotate(f'{int(l.get_height())}', (l.get_x() + l.get_width() / 2, l.get_height()),
                            xytext=(0, 3), textcoords='offset points', ha='center', va='bottom',
                            fontsize=10, color='black')

            plt.savefig(os.path.join(pasta_saida, f"{coluna}.png"))
            plt.close()
            
        else:
            plt.figure(figsize=(12, 6))
            
            df_filtrado = df.copy()  
            if coluna == "DEFICIENCIAS":
                df_filtrado = df[df["DEFICIENCIAS"] != "Sem Deficiencia"]
            
            if coluna == "FORMA_EVASAO":
                df_filtrado = df[df["FORMA_EVASAO"] != "Sem Evasao"]
            
            max_categorias = categorias_personalizadas.get(coluna, max_categorias_padrao)
            top_categorias = df_filtrado[coluna].value_counts().nlargest(max_categorias).index
            df_filtrado[coluna] = df_filtrado[coluna].apply(lambda x: x if x in top_categorias else "Outros")
            
            luck = sns.countplot(x=df_filtrado[coluna], order=df_filtrado[coluna].value_counts().index, palette='viridis')
            rotulo_x, rotulo_y = definir_rotulos(pasta_saida, coluna)
            
            plt.xlabel(rotulo_x, fontsize=11, labelpad=7)
            plt.ylabel(rotulo_y, fontsize=11, labelpad=10)
            
            fonte_tamanho = fontes_personalizadas.get(coluna, fontes_padrao)
            plt.xticks(ha='center', fontsize=fonte_tamanho)
            
            quebra_linha = quebras_personalizadas.get(coluna, quebra_linha_padrao)
            
            def format_label(label):
                text = label.get_text()
                return '\n'.join([text[u:u+quebra_linha] for u in range(0, len(text), quebra_linha)]) if len(text) > quebra_linha else text
            
            luck.set_xticklabels([format_label(label) for label in luck.get_xticklabels()])

            for l in luck.patches:
                luck.annotate(f'{int(l.get_height())}', (l.get_x() + l.get_width() / 2, l.get_height()),
                              xytext=(0, 3), textcoords='offset points', ha='center', va='bottom',
                              fontsize=fonte_tamanho, color='black')
            
            plt.savefig(os.path.join(pasta_saida, f"{coluna}.png"))
            plt.close()

def gerar_grafico_bolsas_por_ano(df):
    pasta_saida = "Graficos2"
    os.makedirs(pasta_saida, exist_ok=True)

    matriculados_por_ano = {
        2008: 214, 2009: 163, 2010: 239, 2011: 285, 2012: 276,
        2013: 191, 2014: 175, 2015: 155, 2016: 187, 2017: 165,
        2018: 165, 2019: 180, 2020: 145, 2021: 170, 2022: 187, 2023: 200
    }

    bolsas_por_ano = {}
    for ano in matriculados_por_ano.keys():
        qtd_bolsas = df[(df["ANO_INGRESSO"] == ano) & (df["BOLSA"] == "Possuia")].shape[0]
        bolsas_por_ano[ano] = qtd_bolsas

    df_plot = pd.DataFrame({
        "Ano": list(matriculados_por_ano.keys()),
        "Matriculados": list(matriculados_por_ano.values()),
        "Com Bolsa": [bolsas_por_ano.get(ano, 0) for ano in matriculados_por_ano.keys()]
    })

    plt.figure(figsize=(12, 6))
    ax = plt.bar(df_plot["Ano"], df_plot["Matriculados"], label="Alunos que não possuíam bolsa", color="steelblue")
    ax2 = plt.bar(df_plot["Ano"], df_plot["Com Bolsa"], label="Alunos que possuíam bolsa", color="orange")

    plt.title("")
    plt.xlabel("Ano de Ingresso")
    plt.ylabel("Quantidade de Alunos")
    plt.legend()
    
    for i in range(len(df_plot["Ano"])):
        plt.text(df_plot["Ano"][i], df_plot["Matriculados"][i] - 10, str(df_plot["Matriculados"][i]), ha='center', va='top', color='white', fontsize=10)
        plt.text(df_plot["Ano"][i], df_plot["Com Bolsa"][i] - 2, str(df_plot["Com Bolsa"][i]), ha='center', va='top', color='black', fontsize=10)

    plt.savefig(os.path.join(pasta_saida, "BOLSAS_POR_ANO.png"))
    plt.close()

def gerar_grafico_disciplinas_por_ano(df):
    pasta_saida = "Graficos"
    os.makedirs(pasta_saida, exist_ok=True)

    df["ANO_DISCIPLINA"] = pd.to_numeric(df["ANO_DISCIPLINA"], errors="coerce")
    df = df.dropna(subset=["ANO_DISCIPLINA"])
    df["ANO_DISCIPLINA"] = df["ANO_DISCIPLINA"].astype(int)

    df = df[df["ANO_DISCIPLINA"] <= 2023]
        
    categorias_validas = ["Aprovado", "Reprovado", "Reprovado por Frequencia"]
    df_filtrado = df[df["SITUACAO_DISCIPLINA"].isin(categorias_validas)]

    df_grouped = df_filtrado.groupby(["ANO_DISCIPLINA", "SITUACAO_DISCIPLINA"]).size().unstack(fill_value=0)

    df_percent = df_grouped.div(df_grouped.sum(axis=1), axis=0) * 100

    df_plot = df_grouped.reset_index()
    df_percent_plot = df_percent.reset_index()

    plt.figure(figsize=(12, 6))

    colors = {
        "Aprovado": "#34a853",  
        "Reprovado": "#e06666",  
        "Reprovado por Frequencia": "#FFD580" 
    }

    ax = plt.bar(df_plot["ANO_DISCIPLINA"], df_plot["Aprovado"], label="Aprovado", color=colors["Aprovado"])
    ax2 = plt.bar(df_plot["ANO_DISCIPLINA"], df_plot["Reprovado"], bottom=df_plot["Aprovado"], label="Reprovado", color=colors["Reprovado"])
    ax3 = plt.bar(df_plot["ANO_DISCIPLINA"], df_plot["Reprovado por Frequencia"], bottom=df_plot["Aprovado"] + df_plot["Reprovado"], label="Reprovado por Freq.", color=colors["Reprovado por Frequencia"])

    for i in range(len(df_plot["ANO_DISCIPLINA"])):
        plt.text(df_plot["ANO_DISCIPLINA"][i], df_plot["Aprovado"][i] / 2, f"{df_percent_plot['Aprovado'][i]:.0f}%", ha='center', va='center', color='black', fontsize=10)
        plt.text(df_plot["ANO_DISCIPLINA"][i], df_plot["Aprovado"][i] + (df_plot["Reprovado"][i] / 2), f"{df_percent_plot['Reprovado'][i]:.0f}%", ha='center', va='center', color='black', fontsize=10)
        plt.text(df_plot["ANO_DISCIPLINA"][i], df_plot["Aprovado"][i] + df_plot["Reprovado"][i] + (df_plot["Reprovado por Frequencia"][i] / 2), f"{df_percent_plot['Reprovado por Frequencia'][i]:.0f}%", ha='center', va='center', color='black', fontsize=10)

    plt.title("")
    plt.xlabel("Ano")
    plt.ylabel("Quantidade de Disciplinas")
    plt.xticks(df_plot["ANO_DISCIPLINA"], rotation=45) 

    plt.legend(loc="upper left")

    plt.savefig(os.path.join(pasta_saida, "DISCIPLINAS_POR_ANO.png"))
    plt.close()

import os
import pandas as pd
import matplotlib.pyplot as plt

def gerar_grafico_evasao_por_ano(df):
    pasta_saida = "Graficos_Evasao2"
    os.makedirs(pasta_saida, exist_ok=True)

    df["ANO_EVASAO"] = pd.to_numeric(df["ANO_EVASAO"], errors="coerce")
    df = df.dropna(subset=["ANO_EVASAO"])
    df["ANO_EVASAO"] = df["ANO_EVASAO"].astype(int)

    df = df[~df["ANO_EVASAO"].isin([2009, 2011])]
    
    df = df[df["ANO_EVASAO"] <= 2023]

    formas_de_evasao = [
        "Cancelamento", 
        "Desistencia", 
        "Desligamento do Programa", 
        "Falecimento", 
        "Formado", 
        "Transferencia Interna", 
        "Jubilamento", 
        "Reopcao de Curso", 
        "Transferido"
    ]

    df_filtrado = df[df["FORMA_EVASAO"].isin(formas_de_evasao)]

    df_grouped = df_filtrado.groupby(["ANO_EVASAO", "FORMA_EVASAO"]).size().unstack(fill_value=0)

    df_plot = df_grouped.reset_index()

    anos_com_dados = sorted(df_filtrado["ANO_EVASAO"].unique())

    positions = range(len(anos_com_dados))

    plt.figure(figsize=(12, 6))

    colors = {
        "Formado": "#34a853",  
        "Jubilamento": "#e06666",  
        "Desistencia": "#FFD580",
        "Cancelamento": "#8EECE4",  
        "Desligamento do Programa": "#FFB6C1",  
        "Falecimento": "#504B43",  
        "Reopcao de Curso": "#90EE90",  
        "Transferencia Interna": "#645DD7",  
        "Transferido": "#ADD8E6"  
    }

    bottom_vals = pd.Series([0] * len(df_plot), index=df_plot.index)
    for categoria in formas_de_evasao:
        if categoria in df_grouped.columns and df_grouped[categoria].sum() > 0:
            ax = plt.bar(positions, df_plot[categoria], 
                         bottom=bottom_vals, 
                         label=categoria, 
                         color=colors.get(categoria, "#808080"))  
            bottom_vals += df_plot[categoria]  

            for i in range(len(df_plot["ANO_EVASAO"])):
                if df_plot[categoria][i] > 0: 
                    plt.text(positions[i], bottom_vals[i] - df_plot[categoria][i] / 2, 
                             f"{df_plot[categoria][i]}", ha='center', va='center', 
                             color='black', fontsize=10)

    plt.xlabel("Ano de Evasão", fontsize=11, labelpad=7)
    plt.ylabel("Quantidade de Alunos", fontsize=11, labelpad=10)
    plt.xticks(positions, anos_com_dados, rotation=0)

    plt.legend(loc="upper left")

    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, "EVASAO_POR_ANO.png"))
    plt.close()

def definir_rotulos(pasta_saida, coluna):
    if pasta_saida == "Graficos2":
        rotulo_y = "Qunatidade de alunos"
    else:
        rotulo_y = "Qunatidade de disciplinas"

    if "ano" in coluna.lower():
        rotulo_x = "Ano"
    elif "bolsa" in coluna.lower():
        rotulo_x = "Bolsa"
    elif "situacao" in coluna.lower():
        rotulo_x = "Situação"
    elif "cotas" in coluna.lower():
        rotulo_x = "Cotas"
    elif "naturalidade" in coluna.lower():
        rotulo_x = "Naturalidade"
    elif "idade" in coluna.lower():
        rotulo_x = "Idade"
    elif "ch" in coluna.lower():
        rotulo_x = "Carga horária"
    elif "credito" in coluna.lower():
        rotulo_x = "Crédito da Disciplina"
    elif "deficiencias" in coluna.lower():
        rotulo_x = "Deficiência"
    elif "estado" in coluna.lower():
        rotulo_x = "Estado civil"
    elif "etnia" in coluna.lower():
        rotulo_x = "Etnia"
    elif "forma_evasao" in coluna.lower():
        rotulo_x = "Formas de evasão"
    elif "forma_ingresso" in coluna.lower():
        rotulo_x = "Formas de ingresso"
    elif "media" in coluna.lower():
        rotulo_x = "Média das notas"
    elif "periodo" in coluna.lower():
        rotulo_x = "Periodos cursados"
    elif "faltas" in coluna.lower():
        rotulo_x = "Média de Faltas"
    else:
        rotulo_x = coluna

    return rotulo_x, rotulo_y

def main():
    df = carregar_csv()
    if df is not None:
        df.columns = df.columns.str.strip()
        
        if "ID_ALUNO" in df.columns:
            df = df.drop(columns=["ID_ALUNO"])
        
        colunas_fonte_personalizada = {
            "FORMA_INGRESSO": 10,
            "NOME_DISCIPLINA": 2,
            "SITUACAO_DISCIPLINA": 9,
        }
        colunas_max_categorias = {
            "NATURALIDADE": 6,
            "COTAS": 4,
            "FORMA_INGRESSO": 4,
            "DEFICIENCIAS":4,
            "SITUACAO_DISCIPLINA": 4,
            "FORMA_EVASAO":3,
        }
        colunas_quebra_linha = {
            "FORMA_EVASAO": 13,
            "FORMA_INGRESSO": 30,
            "COTAS": 28,
            "DEFICIENCIAS": 22,
            "SITUACAO_DISCIPLINA": 25,
        }

        gerar_graficos(df, colunas_fonte_personalizada, colunas_max_categorias, colunas_quebra_linha)
        #gerar_grafico_evasao_por_ano(df)
        #gerar_grafico_bolsas_por_ano(df)

        print(f"Gráficos salvos na pasta: Graficos")

if __name__ == "__main__":
    main()
