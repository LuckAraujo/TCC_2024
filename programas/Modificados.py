from collections import Counter
import time
import requests
import csv
import unicodedata
from datetime import datetime, timedelta

def remover_traco(texto):
    if texto:
        return ''.join(l for l in unicodedata.normalize('NFD', texto) if unicodedata.category(l) != 'Mn')
    return texto

def remover_acentos(aluno):
    for l, u in aluno.items():
        if isinstance(u, str):
            aluno[l] = remover_traco(u)
    return aluno

# def calcular_idade(data_nascimento):
#     if data_nascimento:
#         nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d")
#         hoje = datetime.now()
#         return hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
#     return None

def calcular_idade(data_nascimento, ano,metodo="academico"):
    if data_nascimento:
        nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d")
        hoje = ano
        idade = hoje - nascimento.year
        
        if metodo == "academico":
            if idade < 19:
                return "Menos de 19 anos"
            elif 20 <= idade <= 25:
                return "19-25 anos"
            elif 26 <= idade <= 35:
                return "26-35 anos"
            else:
                return "Acima de 35 anos"
                
    return "Não informado"

def ajustar_ch_total(ch_total):
    try:
        return int(float(ch_total)) if ch_total else "Nao informado"
    except ValueError:
        return "Invalido"

def ajustar_media_final(media_final):
    try:
        media_final = float(media_final)
        if media_final < 5:
            return "0-5"
        elif 5 <= media_final <= 8:
            return "5-8"
        else:
            return "8-10"
    except (ValueError, TypeError):
        return "Nao informado"

def determinar_periodo_academico(mes_ano):
    if not mes_ano or mes_ano == "Nao informado":
        return "Nao informado", "Nao informado"

    mes, ano = map(int, mes_ano.split('/'))

    if ano == 2023:
        if 1 <= mes <= 6:
            return ano, "1 Periodo"
        elif 7 <= mes <= 12:
            return ano, "2 Periodo"
        
    elif ano == 2024:
        if 1 <= mes <= 6:
            return ano, " Periodo"
        elif 7 <= mes <= 12:
            return ano, " Periodo"

    return ano, "Periodo Desconhecido"

def verificar_bolsa_no_periodo(bolsas, ano_disciplina, periodo_disciplina):
    if not bolsas or not ano_disciplina or not periodo_disciplina:
        return "Nao Possuia"
    
    bolsas_separadas = bolsas.split(';')
    for bolsa in bolsas_separadas:
        partes = bolsa.split(" - PERÍODO: ")
        if len(partes) < 2:
            continue  
        
        periodo = partes[1].split(" A ")
        
        try:
            inicio = datetime.strptime(periodo[0].strip(), "%d/%m/%Y")
            fim = datetime.strptime(periodo[1].strip(), "%d/%m/%Y")
        except (ValueError, IndexError):
            continue  
        
        if periodo_disciplina == "1 Periodo":
            inicio_periodo = datetime(ano_disciplina, 1, 1)
            fim_periodo = datetime(ano_disciplina, 6, 30)
        else:
            inicio_periodo = datetime(ano_disciplina, 7, 1)
            fim_periodo = datetime(ano_disciplina, 12, 31)
        
        if not (fim < inicio_periodo or inicio > fim_periodo):
            return "Possuia"
    
    return "Nao Possuia"

def processar_bolsas(bolsas):
    if not bolsas:
        return {}, {}

    bolsas_separadas = bolsas.split(';')
    bolsas_processadas = {}
    datas_bolsas = {}

    for i, bolsa in enumerate(bolsas_separadas, start=1):
        partes = bolsa.split(" - PERÍODO: ")
        nome_bolsa = remover_traco(partes[0].strip())
        bolsas_processadas[f"BOLSA_{i}"] = nome_bolsa

        if len(partes) > 1:
            periodo = partes[1].split(" A ")
            inicio = periodo[0].strip() if len(periodo) > 0 else "Nao informado"
            fim = periodo[1].strip() if len(periodo) > 1 else "Nao informado"

            inicio_formatado = '/'.join(inicio.split('/')[-2:]) if inicio != "Nao informado" else "Nao informado"
            fim_formatado = '/'.join(fim.split('/')[-2:]) if fim != "Nao informado" else "Nao informado"

            datas_bolsas[f"BOLSA_{i}_INICIO"] = inicio_formatado
            datas_bolsas[f"BOLSA_{i}_TERMINO"] = fim_formatado

            ano_inicio, periodo_inicio = determinar_periodo_academico(inicio_formatado)
            ano_fim, periodo_fim = determinar_periodo_academico(fim_formatado)

            datas_bolsas[f"BOLSA_{i}_ANO_INICIO"] = ano_inicio
            datas_bolsas[f"BOLSA_{i}_PERIODO_INICIO"] = periodo_inicio
            datas_bolsas[f"BOLSA_{i}_ANO_TERMINO"] = ano_fim
            datas_bolsas[f"BOLSA_{i}_PERIODO_TERMINO"] = periodo_fim

    return bolsas_processadas, datas_bolsas

def ajustar_credito_disciplina(nome_disciplina, credito):
    creditos_especificos = {
        "Lógica para Computação": "2-1-0",
        "Algoritmos e Linguagem de Programação": "4-1-0",
        "Linguagem de Programação II": "2-1-0",
        "Estrutura de Dados": "2-1-0",
        "Banco de Dados I": "2-1-0",
        "Projetos de Sistemas de Informação": "1-1-0",
        "Pesquisa Operacional": "2-1-0",
        "Redes de Computadores I": "2-1-0",
        "Banco de Dados II": "2-1-0",
        "Gerência de Projetos": "2-1-0",
        "Engenharia Software I": "2-1-0",
        "Empreendedorismo": "2-1-0",
        "Trabalho de Conclusao de Curso II": "1-1-1"
    }
    
    if nome_disciplina in creditos_especificos:
        return creditos_especificos[nome_disciplina]
    else:
        return f"{credito}-0-0"

def categorizar_faltas(num_faltas, ch_total):
    num_faltas = int(float(num_faltas)) if num_faltas not in (None, "", "Não informado") else None
    ch_total = int(float(ch_total)) if ch_total not in (None, "", "Não informado") else None

    if num_faltas == 0 or num_faltas is None:
        return "0-5%"  
    
    percentual_faltas = (num_faltas / ch_total) * 100  
    
    if percentual_faltas < 5:
        return "0-5%"
    elif percentual_faltas < 10:
        return "5-10%"
    elif percentual_faltas < 15:
        return "10-15%"
    elif percentual_faltas < 20:
        return "15-20%"
    elif percentual_faltas < 25:
        return "20-25%"
    else:
        return "Acima de 25%"
    
base_url = "https://sistemas.ufac.br/api/webacademy/dados-alunos/?__pagesize=500&__page="

headers = {
    "Content-Type": "application/json",
    "Authorization": ""
}

alunos_filtrados = []
campos = set()
tempo_total = timedelta()

#escolhe de que ano começa a pegar e que ano termina+1
for ano in range(2008, 2024):
    pagina = 1
    
    print(f"Obtendo dados para o ano {ano}...")
    inicio_ano = time.time()
    
    while True:
        payload = {
            "ANO_INGRESSO": ano,
            "COD_CURSO": "30"  # É o de sistemas    
        }
        
        inicio_pagina = time.time()
        response = requests.post(base_url + str(pagina), json=payload, headers=headers)
        fim_pagina = time.time()

        if response.status_code == 200:
            data = response.json()
            alunos = data.get("response", [])

            if not alunos:  
                break

            for aluno in alunos:
                
                idade = calcular_idade(aluno.get("DT_NASCIMENTO"), ano)
                
                if aluno.get("SITUACAO_DISCIPLINA") in ("Matrícula",) or aluno.get("CREDITOS") in ("0", "", None):
                    continue

                if not aluno.get("NOME_DISCIPLINA"):
                    continue

                if aluno.get("CH_TOTAL") in ("0.00", "36.00","45.00","72.00", "108.00","120.00", "318.00"):
                    continue
                
                if aluno.get("ANO_DISCIPLINA") in (2024,):
                    continue
                
                if aluno["ANO_EVASAO"] == 2024:
                    aluno["ANO_EVASAO"] = ""  
                    aluno["FORMA_EVASAO"] = "Sem Evasao"
                
                etnia = aluno.get("ETNIA", "")
                if etnia != "Nao Declarada" and "." in etnia:
                    etnia = etnia.split(".")[1]
                
                aluno_processado = {
                    "ID_ALUNO": aluno.get("ID"),
                    #"NOME_CURSO": aluno.get("NOME_CURSO") or "Nao informado",
                    #"MODALIDADE_CURSO": aluno.get("MODALIDADE_CURSO") or "Nao informado",
                    #"TURNO_CURSO": aluno.get("TURNO_CURSO") or "Nao informado",
                    "ESTADO_CIVIL": aluno.get("ESTADO_CIVIL") or "Nao informado",
                    "IDADE": idade,
                    "ANO_INGRESSO": aluno.get("ANO_INGRESSO") or "Nao informado",
                    "FORMA_INGRESSO": aluno.get("FORMA_INGRESSO") or "Nao informado",
                    #"ANO_EVASAO": aluno.get("ANO_EVASAO") or "Nao informado",
                    "ANO_EVASAO": aluno.get("ANO_EVASAO") or "",
                    "FORMA_EVASAO": remover_traco(aluno.get("FORMA_EVASAO")) or "Nao informado",
                    "NATURALIDADE": aluno.get("NATURALIDADE") or "Nao informado",
                    "ETNIA": etnia,
                    "DEFICIENCIAS": aluno.get("DEFICIENCIAS") or "Sem Deficiencia",
                    "COTAS": remover_traco(aluno.get("INFO_COTAS", "Ampla Concorrencia")).split(" - ")[-1] if aluno.get("INFO_COTAS") else "Ampla Concorrencia",
                    "NOME_DISCIPLINA": remover_traco(aluno.get("NOME_DISCIPLINA")) or "Nao informado",
                    "ANO_DISCIPLINA": aluno.get("ANO_DISCIPLINA"),
                    "PERIODO_DISCIPLINA": aluno.get("PERIODO_DISCIPLINA") or "Nao informado",
                    "SITUACAO_DISCIPLINA": aluno.get("SITUACAO_DISCIPLINA") or "Nao informado",
                    "CH_TOTAL": ajustar_ch_total(aluno.get("CH_TOTAL")),
                    "CREDITO_DISCIPLINA": ajustar_credito_disciplina(aluno.get("NOME_DISCIPLINA"), aluno.get("CREDITOS", 0)),
                    "MEDIA_FINAL": ajustar_media_final(aluno.get("MEDIA_FINAL")),
                    #"MEDIA_FINAL": aluno.get("MEDIA_FINAL")
                    "FALTAS": categorizar_faltas(aluno.get("NUM_FALTAS"), aluno.get("CH_TOTAL")),
                }

                # bolsas, datas_bolsas = processar_bolsas(aluno.get("BOLSAS"))
                # aluno_processado.update(datas_bolsas)
                # aluno_processado.update(bolsas)
                
                aluno_processado["BOLSA"] = verificar_bolsa_no_periodo(aluno.get("BOLSAS"), aluno.get("ANO_DISCIPLINA"), aluno.get("PERIODO_DISCIPLINA"))

                campos.update(aluno_processado.keys())
                alunos_filtrados.append(aluno_processado)

            pagina += 1  
        else:
            break
        
    fim_ano = time.time()
    tempo_ano = timedelta(seconds=(fim_ano - inicio_ano))
    tempo_total += tempo_ano
    print(f"Tempo para obter dados do ano {ano}: {tempo_ano.total_seconds():.0f} segundo(s)")

minutos, segundos = divmod(tempo_total.total_seconds(), 60)
print(f"Tempo total para obter todos os anos: {int(minutos)} minuto(s) e {int(segundos)} segundo(s)")   


contagem_disciplinas = Counter(aluno["NOME_DISCIPLINA"] for aluno in alunos_filtrados)
alunos_filtrados = [remover_acentos(aluno) for aluno in alunos_filtrados if contagem_disciplinas[aluno["NOME_DISCIPLINA"]] >= 70]

# ids_unicos = len(set(aluno["ID_ALUNO"] for aluno in alunos_filtrados))
# print(f"IDs únicos: {ids_unicos}")

if alunos_filtrados:
    campos = list(aluno_processado.keys())  
    bolsas = [key for aluno in alunos_filtrados for key in aluno.keys() if key.startswith("BOLSA_")]
    campos.extend(sorted(set(bolsas))) 

    with open("dados_alunos_disciplinas.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=campos)
        writer.writeheader()
        writer.writerows(alunos_filtrados)

    print(f"Dados de {len(alunos_filtrados)} alunos salvos em 'dados_alunos_disciplinas.csv' com sucesso!")
else:
    print("Nenhum dado encontrado na resposta.")
