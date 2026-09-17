import sys
import re
import sqlite3
import requests
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QFormLayout,
                               QHBoxLayout, QLineEdit, QPushButton, QMessageBox, 
                               QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QLabel)
from PySide6.QtGui import QTextDocument, QPdfWriter, QPageSize
from PySide6.QtCore import Qt

class CadastroApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Cadastro e Gerenciamento")
        self.resize(1100, 600)  
        self.id_selecionado = None 
        
        self.inicializar_banco()
        self.configurar_interface()
        self.carregar_dados()

    def inicializar_banco(self):
        self.conn = sqlite3.connect("usuarios.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT, cpf_cnpj TEXT, email TEXT, celular TEXT,
                cep TEXT, logradouro TEXT, numero TEXT, complemento TEXT,
                bairro TEXT, cidade TEXT, estado TEXT
            )
        """)
        self.conn.commit()

    def configurar_interface(self):
        layout_principal = QHBoxLayout()

        layout_esquerda = QVBoxLayout()
        form_layout = QFormLayout()

        self.nome_input = QLineEdit()
        self.cpf_cnpj_input = QLineEdit()
        self.cpf_cnpj_input.setPlaceholderText("Apenas números")
        self.email_input = QLineEdit()
        self.celular_input = QLineEdit()
        self.celular_input.setPlaceholderText("(XX) 9XXXX-XXXX")
        self.cep_input = QLineEdit()
        self.cep_input.setPlaceholderText("8 dígitos")
        
        self.logradouro_input = QLineEdit()
        self.numero_input = QLineEdit()
        self.complemento_input = QLineEdit()
        self.bairro_input = QLineEdit()
        self.cidade_input = QLineEdit()
        self.estado_input = QComboBox()
        self.estado_input.addItems(["", "SP", "RJ", "MG", "BA", "PR", "SC", "RS", "PE", "CE", "Outros"])

        form_layout.addRow("Nome Completo:*", self.nome_input)
        form_layout.addRow("CPF ou CNPJ:*", self.cpf_cnpj_input)
        form_layout.addRow("E-mail:*", self.email_input)
        form_layout.addRow("Celular:*", self.celular_input)
        
        cep_layout = QHBoxLayout()
        cep_layout.addWidget(self.cep_input)
        self.btn_buscar_cep = QPushButton("Buscar CEP")
        self.btn_buscar_cep.clicked.connect(self.consultar_cep)
        cep_layout.addWidget(self.btn_buscar_cep)
        form_layout.addRow("CEP:*", cep_layout)

        form_layout.addRow("Logradouro:*", self.logradouro_input)
        form_layout.addRow("Número:*", self.numero_input)
        form_layout.addRow("Complemento:", self.complemento_input)
        form_layout.addRow("Bairro:*", self.bairro_input)
        form_layout.addRow("Cidade:*", self.cidade_input)
        form_layout.addRow("Estado:*", self.estado_input)

        layout_esquerda.addLayout(form_layout)

        botoes_layout = QHBoxLayout()
        self.btn_salvar = QPushButton("Salvar (Criar/Atualizar)")
        self.btn_salvar.clicked.connect(self.processar_cadastro)
        self.btn_limpar = QPushButton("Limpar Seleção")
        self.btn_limpar.clicked.connect(self.limpar_formulario)
        botoes_layout.addWidget(self.btn_salvar)
        botoes_layout.addWidget(self.btn_limpar)
        
        layout_esquerda.addLayout(botoes_layout)
        layout_esquerda.addStretch()

        layout_direita = QVBoxLayout()

        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Pesquisar (Nome/CPF):"))
        self.filtro_input = QLineEdit()
        self.filtro_input.textChanged.connect(self.carregar_dados)
        filtro_layout.addWidget(self.filtro_input)
        layout_direita.addLayout(filtro_layout)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "CPF/CNPJ", "E-mail", "Celular"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.itemSelectionChanged.connect(self.selecionar_registro)
        layout_direita.addWidget(self.tabela)

        botoes_tabela_layout = QHBoxLayout()
        self.btn_excluir = QPushButton("Excluir Selecionado")
        self.btn_excluir.clicked.connect(self.excluir_registro)
        self.btn_excluir.setStyleSheet("background-color: #d9534f; color: white;")
        
        self.btn_pdf = QPushButton("Exportar para PDF")
        self.btn_pdf.clicked.connect(self.exportar_pdf)
        self.btn_pdf.setStyleSheet("background-color: #5bc0de; color: white;")
        
        botoes_tabela_layout.addWidget(self.btn_excluir)
        botoes_tabela_layout.addWidget(self.btn_pdf)
        layout_direita.addLayout(botoes_tabela_layout)

        layout_principal.addLayout(layout_esquerda, 1)
        layout_principal.addLayout(layout_direita, 2)  

        self.setLayout(layout_principal)


    def carregar_dados(self):
        """Lê os dados do banco e exibe na tabela (Read com Filtro)."""
        termo_busca = f"%{self.filtro_input.text().strip()}%"
        self.cursor.execute("SELECT id, nome, cpf_cnpj, email, celular FROM pessoas WHERE nome LIKE ? OR cpf_cnpj LIKE ?", (termo_busca, termo_busca))
        resultados = self.cursor.fetchall()

        self.tabela.setRowCount(0)
        for linha, dados_linha in enumerate(resultados):
            self.tabela.insertRow(linha)
            for coluna, dado in enumerate(dados_linha):
                self.tabela.setItem(linha, coluna, QTableWidgetItem(str(dado)))

    def selecionar_registro(self):
        """Ao clicar na tabela, preenche o formulário para Edição."""
        linhas_selecionadas = self.tabela.selectedItems()
        if not linhas_selecionadas:
            return

        self.id_selecionado = int(linhas_selecionadas[0].text())
        
        self.cursor.execute("SELECT * FROM pessoas WHERE id = ?", (self.id_selecionado,))
        registro = self.cursor.fetchone()

        if registro:
            self.nome_input.setText(registro[1])
            self.cpf_cnpj_input.setText(registro[2])
            self.email_input.setText(registro[3])
            self.celular_input.setText(registro[4])
            self.cep_input.setText(registro[5])
            self.logradouro_input.setText(registro[6])
            self.numero_input.setText(registro[7])
            self.complemento_input.setText(registro[8])
            self.bairro_input.setText(registro[9])
            self.cidade_input.setText(registro[10])
            
            estado = registro[11]
            index = self.estado_input.findText(estado)
            if index >= 0:
                self.estado_input.setCurrentIndex(index)

    def excluir_registro(self):
        """Deleta o registro selecionado (Delete)."""
        if not self.id_selecionado:
            QMessageBox.warning(self, "Aviso", "Selecione um registro na tabela para excluir.")
            return

        resposta = QMessageBox.question(self, "Confirmação", "Tem certeza que deseja excluir este registro?", QMessageBox.Yes | QMessageBox.No)
        if resposta == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM pessoas WHERE id = ?", (self.id_selecionado,))
                self.conn.commit()
                QMessageBox.information(self, "Sucesso", "Registro excluído com sucesso.")
                self.limpar_formulario()
                self.carregar_dados()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir: {str(e)}")

    def exportar_pdf(self):
        """Exporta os dados atuais da tabela para um arquivo PDF."""
        caminho_arquivo, _ = QFileDialog.getSaveFileName(self, "Salvar PDF", "relatorio_usuarios.pdf", "Arquivos PDF (*.pdf)")
        
        if not caminho_arquivo:
            return

        html = "<h1>Relatório de Usuários</h1>"
        html += "<table border='1' cellspacing='0' cellpadding='5' width='100%'>"
        html += "<tr><th>ID</th><th>Nome</th><th>CPF/CNPJ</th><th>E-mail</th><th>Celular</th></tr>"

        for linha in range(self.tabela.rowCount()):
            html += "<tr>"
            for coluna in range(self.tabela.columnCount()):
                item = self.tabela.item(linha, coluna)
                texto = item.text() if item else ""
                html += f"<td>{texto}</td>"
            html += "</tr>"
        html += "</table>"

        documento = QTextDocument()
        documento.setHtml(html)

        pdf_writer = QPdfWriter(caminho_arquivo)
        pdf_writer.setPageSize(QPageSize(QPageSize.A4)) 
        
        documento.print_(pdf_writer)
        QMessageBox.information(self, "Sucesso", "PDF exportado com sucesso!")

    def consultar_cep(self):
        cep = self.cep_input.text().strip().replace("-", "")
        if not re.match(r'^\d{8}$', cep):
            QMessageBox.warning(self, "Erro", "Formato de CEP inválido. Digite 8 números.")
            return

        try:
            response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
            response.raise_for_status()
            dados = response.json()

            if "erro" in dados:
                QMessageBox.warning(self, "Erro", "CEP não encontrado na base de dados.")
                return

            self.preencher_endereco(dados)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao consultar API: {str(e)}")

    def preencher_endereco(self, dados):
        self.logradouro_input.setText(dados.get("logradouro", ""))
        self.bairro_input.setText(dados.get("bairro", ""))
        self.cidade_input.setText(dados.get("localidade", ""))
        estado = dados.get("uf", "")
        index = self.estado_input.findText(estado)
        if index >= 0:
            self.estado_input.setCurrentIndex(index)

    def validar_dados(self):
        if not self.nome_input.text().strip():
            return "O campo 'Nome Completo' é obrigatório."
        cpf_cnpj = self.cpf_cnpj_input.text().strip()
        if len(cpf_cnpj) not in [11, 14] or not cpf_cnpj.isdigit():
            return "CPF (11) ou CNPJ (14) inválido. Digite apenas números."
        email = self.email_input.text().strip()
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return "Formato de e-mail inválido."
        if not self.logradouro_input.text().strip() or not self.numero_input.text().strip():
            return "Logradouro e Número são obrigatórios."
        return None

    def processar_cadastro(self):
        """Salva um novo registro (Create) ou atualiza um existente (Update)."""
        erro = self.validar_dados()
        if erro:
            QMessageBox.warning(self, "Erro de Validação", erro)
            return

        dados = (
            self.nome_input.text(), self.cpf_cnpj_input.text(), self.email_input.text(),
            self.celular_input.text(), self.cep_input.text(), self.logradouro_input.text(),
            self.numero_input.text(), self.complemento_input.text(), self.bairro_input.text(),
            self.cidade_input.text(), self.estado_input.currentText()
        )

        try:
            if self.id_selecionado:
                query = """
                    UPDATE pessoas SET 
                    nome=?, cpf_cnpj=?, email=?, celular=?, cep=?, logradouro=?, 
                    numero=?, complemento=?, bairro=?, cidade=?, estado=?
                    WHERE id=?
                """
                self.cursor.execute(query, (*dados, self.id_selecionado))
                mensagem = "Cadastro atualizado com sucesso!"
            else:
                query = """
                    INSERT INTO pessoas (nome, cpf_cnpj, email, celular, cep, logradouro, numero, complemento, bairro, cidade, estado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                self.cursor.execute(query, dados)
                mensagem = "Cadastro realizado com sucesso!"
            
            self.conn.commit()
            QMessageBox.information(self, "Sucesso", mensagem)
            self.limpar_formulario()
            self.carregar_dados()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar no banco de dados: {str(e)}")

    def limpar_formulario(self):
        """Limpa os inputs e desmarca a seleção da tabela."""
        self.id_selecionado = None
        for widget in self.findChildren(QLineEdit):
            widget.clear()
        self.estado_input.setCurrentIndex(0)
        self.tabela.clearSelection()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = CadastroApp()
    janela.show()
    sys.exit(app.exec())