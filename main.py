import csv, sys, requests
from PySide6 import QtCore, QtWidgets
from bs4 import BeautifulSoup

ml_url = "https://lista.mercadolivre.com.br/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML_url, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.button = QtWidgets.QPushButton("Extrair")
        self.input_1 = QtWidgets.QLineEdit()
        self.paginas = QtWidgets.QComboBox()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.input_1)
        self.layout.addWidget(self.paginas)
        self.layout.addWidget(self.button)

        self.paginas.addItem('Defina o número de páginas para extrair')
        self.paginas.addItems(['1','2','3','4','5','6','7','8','9','10'])
        self.input_1.setPlaceholderText('Digite o nome do produto que deseja fazer a extração')

        self.button.clicked.connect(self.scrapy)

    def scrapy(self):
        paginas = self.paginas.currentText()
        if paginas == 'Defina o número de páginas para extrair':
            QtWidgets.QMessageBox.warning(self, "Aviso", "Por favor, selecione o número de páginas.")
            return

        base_url = ml_url + self.input_1.text().replace(" ", "-")
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Salvar Arquivo CSV", "", "Arquivos CSV (*.csv)")

        if not file_path:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Operação cancelada.")
            return

        desde = 1 
        prod_por_pg = 50
        max_pg = int(paginas)
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
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())