import csv
import requests
from bs4 import BeautifulSoup

base_url = "https://lista.mercadolivre.com.br/geladeira"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

with open('produtos_multiplas_paginas.csv', mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['Produto', 'Preço', 'Vendedor', 'Nota', 'Avaliações',])
    
    desde = 1 
    produtos_por_pagina = 50
    max_paginas = 4
    pagina_atual = 0

    while pagina_atual < max_paginas:
        if desde == 1:
            url = base_url
        else:
            url = f"{base_url}/_Desde_{desde}_NoIndex_True"
        print(f"Buscando dados da página: {url}")

        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Erro ao acessar a página: {response.status_code}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        produtos = soup.find_all('li', class_='ui-search-layout__item')

        if not produtos:
            print("Nenhum produto encontrado. Encerrando busca.")
            break

        for produto in produtos:
            nome_tag = produto.find('h2', class_='poly-box poly-component__title')
            nome = nome_tag.text.strip() if nome_tag else "Nome não encontrado"

            preco_atual = produto.find('div', class_='poly-price__current')
            if preco_atual:
                preco_principal_tag = preco_atual.find('span', class_='andes-money-amount__fraction')
                preco_principal = preco_principal_tag.text.strip() if preco_principal_tag else "Preço não encontrado"

                preco_centavos_tag = preco_atual.find('span', class_='andes-money-amount__cents')
                preco_centavos = preco_centavos_tag.text.strip() if preco_centavos_tag else "00"

                preco_completo = f"R$ {preco_principal},{preco_centavos}"
            else:
                preco_completo = "Preço não encontrado"

            seller_tag = produto.find('span', class_='poly-component__seller')
            seller_name = seller_tag.text.strip() if seller_tag else "Seller não identificado"


            produto_rate_tag = produto.find('span', class_='poly-reviews__rating')
            produto_rate = produto_rate_tag.text.strip() if produto_rate_tag else "Sem Avaliações"

            avaliacao_tag = produto.find('span', class_='poly-reviews__total')
            if avaliacao_tag:
                total_avaliacao = avaliacao_tag.text.strip()
                total_avaliacao = total_avaliacao.replace("(", "").replace(")", "")
            else:
                total_avaliacao = "Sem Avaliações"

            writer.writerow([nome, preco_completo, seller_name, produto_rate, total_avaliacao])

        desde += produtos_por_pagina
        pagina_atual += 1

print("Busca concluída e dados salvos em 'produtos_multiplas_paginas.csv'")