import requests
import csv

# URL da API
url = "https://sistemas.ufac.br/api/webacademy/dados-alunos/?__pagesize=500&__page=1"

# Cabeçalhos da requisição
headers = {
    "Content-Type": "application/json",
    "Authorization": ""
    #Envie um Email para Manoel Limera (juniorlimeiras@gmail.com), se quiser o codigo de autorização.
}

# Corpo da requisição JSON
payload = {
    "ANO_INGRESSO": 2019,
    "COD_CURSO": "30" # É o de sistemas
}

# Fazer a requisição POST
response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    print("Requisição bem-sucedida!")
    data = response.json()
    
    alunos = data.get("response", [])
    
    if alunos:
        with open("dados_alunos.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=alunos[0].keys())
            writer.writeheader()
            writer.writerows(alunos)
        
        print("Dados salvos em 'dados_alunos.csv' com sucesso!")
    else:
        print("Nenhum dado encontrado na resposta.")
else:
    print(f"Erro na requisição: {response.status_code}")
    print(response.text)
