import re
import csv
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
MG_URL = "https://www.magazineluiza.com.br/busca/"

def extrair_valor(string):
    resultado = re.search(r'(\d[\d.,]*)', string)
    if resultado:
        return resultado.group(1)
    return "Preço não encontrado"

def extrair_dos_parenteses(string):
    resultado = re.search(r'\((\d+)\)', string)
    if resultado:
        return resultado.group(1)
    return "Não encontrado"

def perform_scraping_mg(product_name, num_pages, site, file_path, progress_signal):
    base_url = MG_URL + product_name.replace(" ", "+")
    desde = 1

    with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Produto', 'Preço', 'Vendedor', 'Nota', 'Avaliações', 'Entrega Full?'])

        for page in range(num_pages):
            url = f"{base_url}?page={desde}" if desde > 1 else base_url
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.content, 'html.parser')
            produtos = soup.find_all('li', class_='sc-iNIeMn')

            print(f"pesquisando na página {url}")
            if not produtos:
                progress_signal.emit("Nenhum produto encontrado.")
                break

            for produto in produtos:
                titulo_tag = produto.find('h2', class_='sc-cvalOF')
                titulo = titulo_tag.text.strip() if titulo_tag else "Título não encontrado"

                preco = produto.find('p', class_='etFOes')
                if preco:
                    preco_raw = extrair_valor(preco.text.strip())
                    preco_completo = f"R$ {preco_raw}"
                else:
                    preco_completo = "Preço não encontrado"

                seller_tag = produto.find('span', class_='poly-component__seller')
                seller_name = seller_tag.text.strip() if seller_tag else "Seller não identificado"

                produto_rate = produto.find('span', class_='sc-fUkmAC')
                if produto_rate:
                    produto_rate_raw = produto_rate.text.strip()
                    produto_rate = produto_rate_raw[:3]
                else:
                    produto_rate = "Sem Nota"

                avaliacao_tag = produto.find('span', class_='sc-fUkmAC')
                if avaliacao_tag:
                    total_avaliacao = extrair_dos_parenteses(avaliacao_tag.text.strip())
                else:
                    total_avaliacao = "Sem Avaliações"

                entrega_full = 'N/A'

                writer.writerow([titulo, preco_completo, seller_name, produto_rate, total_avaliacao, entrega_full])

            desde += 1