import pandas as pd

def carregar_dados(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo)
    return df

def analisar_bolsa_vs_formacao(df):
    df_filtrado = df[df["FORMA_EVASAO"] != "Sem Evasao"]
    
    formados = df_filtrado.groupby("BOLSA")["FORMA_EVASAO"].apply(lambda x: (x == "Formado").mean() * 100)

    print("\nTaxa de formação entre alunos com e sem bolsa (%):\n")
    for bolsa, taxa in formados.items():
        print(f"{bolsa}: {taxa:.2f}")

def analisar_bolsa_vs_evasao(df):
    df_filtrado = df[df["FORMA_EVASAO"] != "Sem Evasao"]
    
    evasao = df_filtrado.groupby("BOLSA")["FORMA_EVASAO"].apply(lambda x: (x != "Formado").mean() * 100)
    
    print("\nTaxa de evasão entre alunos com e sem bolsa (%):\n")
    for bolsa, taxa in evasao.items():
        print(f"{bolsa}: {taxa:.2f}")

def analisar_bolsa_vs_ingresso(df):
    ingresso = df.groupby("BOLSA")["FORMA_INGRESSO"].value_counts(normalize=True) * 100
    
    print("\nDistribuição de formas de ingresso entre alunos com e sem bolsa (%):\n")
    for (bolsa, forma), taxa in ingresso.items():
        print(f"{bolsa} - {forma}: {taxa:.2f}")

def analisar_bolsa_vs_etnia(df):
    etnia = df.groupby("BOLSA")["ETNIA"].value_counts(normalize=True) * 100
    
    print("\nDistribuição de etnias entre alunos com e sem bolsa (%):\n")
    for (bolsa, grupo_etnico), taxa in etnia.items():
        print(f"{bolsa} - {grupo_etnico}: {taxa:.2f}")

def analisar_bolsa_vs_cotas(df):
    cotas = df.groupby("BOLSA")["COTAS"].value_counts(normalize=True) * 100
    
    print("\nDistribuição de cotas entre alunos com e sem bolsa (%):\n")
    for (bolsa, tipo_cota), taxa in cotas.items():
        print(f"{bolsa} - {tipo_cota}: {taxa:.2f}")

def analisar_bolsa_vs_deficiencia(df):
    df_deficiencia = df[df["DEFICIENCIAS"] != "Sem Deficiencia"]
    deficiencia = df_deficiencia.groupby("BOLSA")["DEFICIENCIAS"].value_counts(normalize=True) * 100
    
    print("\nDistribuição de deficiências entre alunos com e sem bolsa (%):\n")
    for (bolsa, tipo_deficiencia), taxa in deficiencia.items():
        print(f"{bolsa} - {tipo_deficiencia}: {taxa:.2f}")

def analisar_bolsa_vs_idade(df):
    idade = df.groupby("BOLSA")["IDADE"].value_counts(normalize=True) * 100
    
    print("\nDistribuição de faixas etárias entre alunos com e sem bolsa (%):\n")
    for (bolsa, faixa_etaria), taxa in idade.items():
        print(f"{bolsa} - {faixa_etaria}: {taxa:.2f}")

def calcular_percentual_formados(df):
    total_alunos = len(df)
    formados = (df["FORMA_EVASAO"] == "Formado").sum()
    percentual_formados = (formados / total_alunos) * 100
    
    print(f"Total de alunos: {total_alunos}")
    print(f"Alunos formados: {formados}")
    print(f"Porcentagem de alunos formados: {percentual_formados:.2f}%")
    
def main():
    caminho_arquivo = "dados_alunos_unicos.csv"
    df = carregar_dados(caminho_arquivo)
    
    analisar_bolsa_vs_formacao(df)
    analisar_bolsa_vs_evasao(df)
    #analisar_bolsa_vs_ingresso(df)
    #analisar_bolsa_vs_etnia(df)
    #analisar_bolsa_vs_cotas(df)
    #analisar_bolsa_vs_deficiencia(df)
    #analisar_bolsa_vs_idade(df)
    
    calcular_percentual_formados(df)
    
if __name__ == "__main__":
    main()
