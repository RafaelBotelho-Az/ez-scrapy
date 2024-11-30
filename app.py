from PySide6 import QtWidgets, QtCore
from scraper_ml import perform_scraping_ml
from scraper_mg import perform_scraping_mg


class ScraperThread(QtCore.QThread):
    progress = QtCore.Signal(str)
    finished = QtCore.Signal(str)

    def __init__(self, product_name, num_pages, site, file_path):
        super().__init__()
        self.product_name = product_name
        self.num_pages = num_pages
        self.site = site
        self.file_path = file_path

    def run(self):
        if self.site == "Mercado Livre":
            perform_scraping_ml(self.product_name, self.num_pages, self.site, self.file_path, self.progress)
            self.finished.emit("Scraping concluído com sucesso!")
        elif self.site == "Magazine Luiza":
            perform_scraping_mg(self.product_name, self.num_pages, self.site, self.file_path, self.progress)
            self.finished.emit("Scraping concluído com sucesso!")


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.btn_extrair = QtWidgets.QPushButton("EXTRAIR")
        self.search_input = QtWidgets.QLineEdit()
        self.combo_pg = QtWidgets.QComboBox()
        self.combo_sites = QtWidgets.QComboBox()
        self.lb_pesquisa = QtWidgets.QLabel("Digite o nome do produto que deseja fazer a extração:")
        self.lb_paginas = QtWidgets.QLabel("Selecione o número de páginas para fazer a extração:")
        self.lb_sites = QtWidgets.QLabel("Selecione o site que será feito a extração:")
        self.spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.layout.addItem(self.spacer)
        self.layout.addWidget(self.lb_pesquisa)
        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.lb_paginas)
        self.layout.addWidget(self.combo_pg)
        self.layout.addWidget(self.lb_sites)
        self.layout.addWidget(self.combo_sites)
        self.layout.addItem(self.spacer)
        self.layout.addWidget(self.btn_extrair)
        self.layout.addItem(self.spacer)

        self.combo_pg.addItems(['', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
        self.combo_sites.addItems(['', 'Mercado Livre', 'Shopee', 'Magazine Luiza'])
        self.search_input.setPlaceholderText('Produto...')

        self.btn_extrair.clicked.connect(self.scrapy)

    def scrapy(self):
        product_name = self.search_input.text()
        num_pages = self.combo_pg.currentText()
        site = self.combo_sites.currentText()

        if not product_name:
            QtWidgets.QMessageBox.warning(self, "Aviso", "O campo do produto não pode estar vazio.")
            return

        if not num_pages:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Por favor, selecione o número de páginas.")
            return

        if not site:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Por favor, selecione um site.")
            return

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Salvar Arquivo CSV", "", "Arquivos CSV (*.csv)")
        if not file_path:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Operação cancelada.")
            return

        self.progress_dialog = QtWidgets.QProgressDialog("Executando scraping...", "", 0, 0, self)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setWindowTitle("Aguarde")
        self.progress_dialog.setModal(True)
        self.progress_dialog.show()

        self.scraper_thread = ScraperThread(product_name, int(num_pages), site, file_path)
        self.scraper_thread.progress.connect(self.update_progress)
        self.scraper_thread.finished.connect(self.on_scraping_finished)
        self.scraper_thread.start()

    def update_progress(self, message):
        self.progress_dialog.setLabelText(message)

    def on_scraping_finished(self, message):
        self.progress_dialog.close()
        QtWidgets.QMessageBox.information(self, "Concluído", message)