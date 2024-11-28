import csv
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
ML_URL = "https://lista.mercadolivre.com.br/"

def perform_scraping(product_name, num_pages, site, file_path, progress_signal):
    base_url = ML_URL + product_name.replace(" ", "-")
    desde = 1
    prod_por_pg = 50


    with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Produto', 'Preço', 'Vendedor', 'Nota', 'Avaliações'])

        for page in range(num_pages):
            url = f"{base_url}/_Desde_{desde}_NoIndex_True" if desde > 1 else base_url
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.content, 'html.parser')

            produtos = soup.find_all('li', class_='ui-search-layout__item')

            if not produtos:
                progress_signal.emit("Nenhum produto encontrado.")
                break

            for produto in produtos:
                titulo_tag = produto.find('h2', class_='poly-box poly-component__title')
                titulo = titulo_tag.text.strip() if titulo_tag else "Título não encontrado"

                preco = produto.find('div', class_='poly-price__current')
                if preco:
                    preco_principal_tag = preco.find('span', class_='andes-money-amount__fraction')
                    preco_principal = preco_principal_tag.text.strip() if preco_principal_tag else "Preço não encontrado"

                    preco_centavos_tag = preco.find('span', class_='andes-money-amount__cents')
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

                writer.writerow([titulo, preco_completo, seller_name, produto_rate, total_avaliacao])

            desde += prod_por_pg
