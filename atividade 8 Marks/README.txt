Sistema de Cadastro de Pessoas - PySide6
Descrição do Projeto Essa é uma aplicação desktop desenvolvida em Python com a biblioteca PySide6, correspondente à atividade prática de Programação Orientada a Objetos. O sistema consiste em uma tela de cadastro de usuários com validação inteligente de dados, comunicação com serviços externos na web e persistência em banco de dados.
Principais Funcionalidades Implementadas
    • Interface Gráfica (GUI): Construída de forma limpa e organizada com PySide6, utilizando formulários estruturados e componentes adequados (como QLineEdit e QComboBox).
    • Integração com API Externa: Consulta automática de endereço através do preenchimento do CEP, utilizando a API pública do ViaCEP.
    • Validação de Dados: O sistema checa automaticamente se os campos obrigatórios estão vazios e valida os formatos de e-mail, CPF/CNPJ (11 ou 14 dígitos), Celular e CEP.
    • Tratamento de Erros: Respostas visuais em formato pop-up (QMessageBox) orientam o usuário exatamente sobre o que precisa ser corrigido (ex: formato de e-mail inválido, ausência de conexão com a API, CEP inexistente).
    • Banco de Dados Local: Os cadastros válidos são salvos automaticamente utilizando SQLite (gerando o arquivo usuarios.db), garantindo a organização do código e persistência dos dados.
Como Executar a Aplicação
    1. Certifique-se de ter o Python instalado no seu computador.
    2. Abra o terminal (PowerShell, CMD ou terminal do VS Code) na pasta onde os arquivos do projeto estão salvos.
    3. Instale as bibliotecas dependentes (PySide6 para a tela e requests para a API) digitando o seguinte comando no terminal e apertando Enter:
		
		pip install PySide6 requests

Após a instalação ser concluída, execute o arquivo principal da aplicação com o comando:
		
		python app.py 
