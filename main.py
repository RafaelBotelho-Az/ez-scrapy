import csv, sys, requests
from PySide6 import QtWidgets
from bs4 import BeautifulSoup

ml_url = "https://lista.mercadolivre.com.br/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML_url, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.btn_extrair = QtWidgets.QPushButton("Extrair")
        self.search_input = QtWidgets.QLineEdit()
        self.combo_pg = QtWidgets.QComboBox()
        self.combo_sites = QtWidgets.QComboBox()

        self.lb_pesquisa = QtWidgets.QLabel("Digite o nome do produto que deseja fazer a extração:")
        self.lb_paginas = QtWidgets.QLabel("Selecione o número de páginas para fazer a extração:")
        self.lb_sites = QtWidgets.QLabel("Selecione o site que será feito a extração::")

        self.layout = QtWidgets.QVBoxLayout(self)

        self.layout.addWidget(self.lb_pesquisa)
        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.lb_paginas)
        self.layout.addWidget(self.combo_pg)
        self.layout.addWidget(self.lb_sites)
        self.layout.addWidget(self.combo_sites)
        self.layout.addWidget(self.btn_extrair)

        self.combo_pg.addItems(['','1','2','3','4','5','6','7','8','9','10'])
        self.combo_sites.addItems(['','Mercado Livre','Shopee','Magazine Luiza'])
        self.search_input.setPlaceholderText('Produto...')

        self.btn_extrair.clicked.connect(self.scrapy)

    def scrapy(self):

        if self.search_input.text() == '':
            QtWidgets.QMessageBox.warning(self, "Aviso", "O campo do produto não pode estar vazio.")
            return

        if self.combo_pg.currentText() == '':
            QtWidgets.QMessageBox.warning(self, "Aviso", "Por favor, selecione o número de páginas.")
            return

        if self.combo_sites.currentText() == '':
            QtWidgets.QMessageBox.warning(self, "Aviso", "Por favor, selecione um site.")
            return

        base_url = ml_url + self.search_input.text().replace(" ", "-")
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Salvar Arquivo CSV", "", "Arquivos CSV (*.csv)")

        if not file_path:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Operação cancelada.")
            return

        desde = 1 
        prod_por_pg = 50
        max_pg = int(self.combo_pg.currentText())
        pg_atual = 0

        with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Produto', 'Preço', 'Vendedor', 'Nota', 'Avaliações'])

            while pg_atual < max_pg:
                if desde == 1:
                    url = base_url
                else:
                    url = f"{base_url}/_Desde_{desde}_NoIndex_True"
                print(f"Buscando dados da página: {url}")

                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                produtos = soup.find_all('li', class_='ui-search-layout__item')

                if response.status_code != 200:
                    print(f"Erro ao acessar a página: {response.status_code}")
                    break

                if not produtos:
                    print("Nenhum produto encontrado. Encerrando busca.")
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
                pg_atual += 1

        QtWidgets.QMessageBox.information(self, "Concluído", f"Busca concluída! Dados salvos em '{file_path}'")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(700, 350)
    widget.show()

    sys.exit(app.exec())