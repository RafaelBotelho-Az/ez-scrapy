import csv
import requests
from bs4 import BeautifulSoup

url = "https://lista.mercadolivre.com.br/coxim-motor-direito-linfan-x60"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = requests.get(url, headers=headers)


if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    produtos = soup.find_all('li', class_='ui-search-layout__item')


    with open('produtos.csv', mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Produto', 'Preço', 'Vendedor'])
        
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

            writer.writerow([nome, preco_completo, seller_name])

    print("Dados salvos com sucesso no arquivo 'produtos.csv'")
else:
    print(f"Erro ao acessar a página: {response.status_code}")