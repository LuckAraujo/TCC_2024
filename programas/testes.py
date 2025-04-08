import pandas as pd

arquivo_csv = "dados_alunos_disciplinas.csv"
df = pd.read_csv(arquivo_csv, encoding="utf-8")

df["ANO_DISCIPLINA"] = pd.to_numeric(df["ANO_DISCIPLINA"], errors="coerce")
df["MEDIA_FINAL"] = pd.to_numeric(df["MEDIA_FINAL"], errors="coerce")

df_validos = df[df["SITUACAO_DISCIPLINA"].isin(["Aprovado", "Reprovado"])]

disciplina_qtd_alunos = df.groupby("NOME_DISCIPLINA")["ID_ALUNO"].nunique()

disciplina_media_notas = df_validos.groupby("NOME_DISCIPLINA")["MEDIA_FINAL"].mean().round(2)

df_validos["APROVADO"] = df_validos["SITUACAO_DISCIPLINA"].apply(lambda x: 1 if x == "Aprovado" else 0)

disciplina_taxa_aprovacao = (df_validos.groupby("NOME_DISCIPLINA")["APROVADO"].mean() * 100).round(2)

disciplina_media_por_ano = df.groupby(["NOME_DISCIPLINA", "ANO_DISCIPLINA"])["ID_ALUNO"].nunique().groupby("NOME_DISCIPLINA").mean().round().astype(int)

df_resumo = pd.DataFrame({
    "Qtd Alunos": disciplina_qtd_alunos,
    "Média Notas": disciplina_media_notas,
    "Taxa Aprovação (%)": disciplina_taxa_aprovacao,
    "Média Alunos Por Ano": disciplina_media_por_ano
}).reset_index()

# df_resumo.to_csv("tabela_corrigida.csv", index=False)

print(df_resumo)
