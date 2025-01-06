Projeto de Cobrança Automatizada via WhatsApp
Descrição
Este projeto é uma solução automatizada para envio de mensagens de cobrança via WhatsApp e verificação de pagamentos, utilizando Selenium WebDriver e integrando com o banco de dados SQLite. Também há integração com o Telegram para notificações. Desenvolvido por Matheus Ribeiro.

Funcionalidades
Envio de mensagens de cobrança inicial para usuários via WhatsApp Web.

Verificação periódica de mensagens para identificação de comprovantes de pagamento.

Atualização automática do status dos pagamentos no banco de dados.

Envio de mensagem de agradecimento após confirmação do pagamento.

Envio de notificações para o Telegram com a tabela de status dos pagamentos.

Encerramento do processo automaticamente quando todos os usuários tiverem realizado o pagamento.

Estrutura do Projeto
main.py: Script principal que inicializa e executa o programa.

whatsapp_utils.py: Contém funções para interagir com o WhatsApp Web, enviar mensagens, verificar comprovantes e atualizar o banco de dados.

db_utils.py: Contém funções para interagir com o banco de dados SQLite.

telegram_utils.py: Contém funções para gerar e enviar notificações via Telegram.

config.py: Arquivo de configuração que contém as informações dos usuários, plano, valor e PIX.

Pré-requisitos
Python 3.6+

Selenium WebDriver

Google Chrome

Driver do Chrome (chromedriver) compatível com a versão do seu Chrome

Instalação
Clone este repositório:

bash
git clone https://github.com/MatheusBenvindo/.git
cd seurepositorio
Instale as dependências:

bash
pip install -r requirements.txt
Configure os dados dos usuários e informações de pagamento no arquivo config.py.

Certifique-se de que o Google Chrome e o ChromeDriver estejam instalados e configurados corretamente.

Execução
Execute o script principal:

bash
python main.py
O script abrirá o WhatsApp Web no navegador, enviará as mensagens de cobrança e começará a verificar as mensagens para identificar comprovantes de pagamento.

Você receberá notificações no Telegram conforme os pagamentos forem confirmados.

Observações
Certifique-se de que o perfil do Chrome utilizado esteja corretamente configurado para evitar a necessidade de autenticação manual no WhatsApp Web.

O intervalo de verificação de mensagens é de 1 minuto.

Autor:
Desenvolvido por Matheus Ribeiro.
Linkedin - https://www.linkedin.com/in/matheus-ribeiro-636b25318/
Github - https://github.com/MatheusBenvindo