import sys
import re
import sqlite3
import requests
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QFormLayout,
                               QHBoxLayout, QLineEdit, QPushButton, QMessageBox, QComboBox)

class CadastroApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cadastro de Usuário")
        self.resize(400, 500)
        self.inicializar_banco()
        self.configurar_interface()

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
        layout_principal = QVBoxLayout()
        form_layout = QFormLayout()

        # Campos do Formulário
        self.nome_input = QLineEdit()
        self.cpf_cnpj_input = QLineEdit()
        self.cpf_cnpj_input.setPlaceholderText("Apenas números (11 ou 14 dígitos)")
        self.email_input = QLineEdit()
        self.celular_input = QLineEdit()
        self.celular_input.setPlaceholderText("(XX) 9XXXX-XXXX")
        self.cep_input = QLineEdit()
        self.cep_input.setPlaceholderText("Apenas números (8 dígitos)")
        
        self.logradouro_input = QLineEdit()
        self.numero_input = QLineEdit()
        self.complemento_input = QLineEdit()
        self.bairro_input = QLineEdit()
        self.cidade_input = QLineEdit()
        self.estado_input = QComboBox()
        self.estado_input.addItems(["", "SP", "RJ", "MG", "BA", "PR", "SC", "RS", "PE", "CE", "Outros"])

        # Adicionando ao Form
        form_layout.addRow("Nome Completo:*", self.nome_input)
        form_layout.addRow("CPF ou CNPJ:*", self.cpf_cnpj_input)
        form_layout.addRow("E-mail:*", self.email_input)
        form_layout.addRow("Celular:*", self.celular_input)
        
        # Layout H para CEP e Botão de Busca
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

        layout_principal.addLayout(form_layout)

        # Botões de Ação
        botoes_layout = QHBoxLayout()
        self.btn_salvar = QPushButton("Cadastrar")
        self.btn_salvar.clicked.connect(self.processar_cadastro)
        self.btn_limpar = QPushButton("Limpar")
        self.btn_limpar.clicked.connect(self.limpar_formulario)
        
        botoes_layout.addWidget(self.btn_salvar)
        botoes_layout.addWidget(self.btn_limpar)
        layout_principal.addLayout(botoes_layout)

        self.setLayout(layout_principal)

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

        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Erro de Conexão", "Não foi possível conectar ao serviço de CEP. Verifique sua internet.")
        except requests.exceptions.Timeout:
            QMessageBox.critical(self, "Erro", "O serviço de CEP demorou muito para responder.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro inesperado ao consultar a API: {str(e)}")

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
            return "CPF (11 dígitos) ou CNPJ (14 dígitos) inválido. Digite apenas números."
        
        email = self.email_input.text().strip()
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return "O endereço de e-mail possui um formato inválido."
        
        celular = self.celular_input.text().strip()
        if not re.match(r'^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$', celular):
            return "O número de celular foi informado incorretamente."
        
        if not self.logradouro_input.text().strip() or not self.numero_input.text().strip():
            return "Logradouro e Número são obrigatórios."

        return None 

    def processar_cadastro(self):
        erro = self.validar_dados()
        if erro:
            QMessageBox.warning(self, "Erro de Validação", erro)
            return

        try:
            self.cursor.execute("""
                INSERT INTO pessoas (nome, cpf_cnpj, email, celular, cep, logradouro, numero, complemento, bairro, cidade, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.nome_input.text(), self.cpf_cnpj_input.text(), self.email_input.text(),
                self.celular_input.text(), self.cep_input.text(), self.logradouro_input.text(),
                self.numero_input.text(), self.complemento_input.text(), self.bairro_input.text(),
                self.cidade_input.text(), self.estado_input.currentText()
            ))
            self.conn.commit()
            QMessageBox.information(self, "Sucesso", "Cadastro realizado com sucesso!")
            self.limpar_formulario()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar no banco de dados: {str(e)}")

    def limpar_formulario(self):
        for widget in self.findChildren(QLineEdit):
            widget.clear()
        self.estado_input.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = CadastroApp()
    janela.show()
    sys.exit(app.exec())