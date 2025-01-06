# Projeto de Cobrança Automatizada via WhatsApp/Telegram

## Descrição
Projeto automatizado para cobrança de planos famílias divididos com diversas pessoas, utilizando o número WhatsApp para envio/cobrança das mensagens e Telegram para atualização e obtenção de dados em tempo real no celular. O código utiliza a verificação de PDF nas últimas 5 mensagens enviadas no WhatsApp para confirmar o pagamento e atualizar o banco de dados em SQLite. Em seguida, envia uma tabela com as informações úteis (usuário e pagamento) para o Telegram. Este modelo pode ser otimizado conforme sua necessidade. É possível utilizar seu WhatsApp pessoal. Após cada pagamento ser atualizado, ele envia uma tabela com os dados atualizados através do seu Telegram. Quando o status de todos os usuários for "pago", o sistema envia uma mensagem relembrando de abater a fatura. O objetivo do código é verificar e enviar conforme o mês atual, utilizando automações para enviar mensalmente no quinto dia útil do mês.

## Funcionalidades
- Envio de mensagens de cobrança inicial para usuários via WhatsApp Web.
- Verificação periódica de mensagens para identificação de comprovantes de pagamento.
- Atualização automática do status dos pagamentos no banco de dados.
- Envio de mensagem de agradecimento após confirmação do pagamento.
- Envio de notificações para o Telegram com a tabela de status dos pagamentos.
- Encerramento do processo automaticamente quando todos os usuários tiverem realizado o pagamento.

## Estrutura do Projeto
- `main.py`: Script principal que inicializa e executa o programa.
- `whatsapp_utils.py`: Contém funções para interagir com o WhatsApp Web, enviar mensagens, verificar comprovantes e atualizar o banco de dados.
- `db_utils.py`: Contém funções para interagir com o banco de dados SQLite.
- `telegram_utils.py`: Contém funções para gerar e enviar notificações via Telegram.
- `config.py`: Arquivo de configuração que contém as informações dos usuários, plano, valor e PIX.

## Pré-requisitos
- Python 3.6+
- Selenium WebDriver
- Google Chrome
- Driver do Chrome (chromedriver) compatível com a versão do seu Chrome

## Instalação
1. Clone este repositório:
    ```bash
    git clone https://github.com/MatheusBenvindo/.git
    cd seurepositorio
    ```
2. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
3. Renomeie `config_example.py` para `config.py` e substitua os valores pelos reais.

4. Configure as variáveis de ambiente criando um arquivo `.env`:
    ```plaintext
    TELEGRAM_TOKEN=seu-token-do-telegram
    PIX=chave-pix-exemplo
    ```

5. Certifique-se de que o Google Chrome e o ChromeDriver estejam instalados e configurados corretamente.

## Execução
1. Execute o script principal:
    ```bash
    python main.py
    ```

2. O script abrirá o WhatsApp Web no navegador, enviará as mensagens de cobrança e começará a verificar as mensagens para identificar comprovantes de pagamento.

3. Você receberá notificações no Telegram conforme os pagamentos forem confirmados.

## Observações
- Certifique-se de que o perfil do Chrome utilizado esteja corretamente configurado para evitar a necessidade de autenticação manual no WhatsApp Web.
- O intervalo de verificação de mensagens é de 1 minuto.
- De tempos em tempos, será necessário autenticar o WhatsApp novamente.

## Como Criar um Bot no Telegram

1. Abra o Telegram e procure por "BotFather".
2. Inicie uma conversa com o BotFather e use o comando `/start`.
3. Use o comando `/newbot` e siga as instruções para criar um novo bot.
4. O BotFather fornecerá um token de API. Adicione este token ao arquivo `.env` como `TELEGRAM_TOKEN`.

## Configuração do Perfil do Chrome

O projeto utiliza um perfil do Chrome para armazenar os cookies do WhatsApp Web e evitar a necessidade de escanear o QR Code a cada execução.

1. **Crie uma pasta**: Crie uma pasta `suapasta` na raiz do projeto.
2. **Abra o Chrome**: Digite `chrome://version` na barra de endereços.
3. **Copie o caminho do perfil**: Copie o caminho da pasta do seu perfil principal do Chrome (ao lado de "Profile Path").
4. **Cole o conteúdo na nova pasta**: Cole o conteúdo da pasta do seu perfil principal na pasta `suapasta` que você criou.
5. **Ajuste o caminho no código**: Ajuste o caminho da pasta `perfil_chrome` no arquivo `whatsapp_utils.py` para o caminho da pasta `suapasta`.

## Como Rodar o Código em Segundo Plano com Selenium Headless

Para rodar o Selenium em segundo plano, você pode usar o modo headless. Aqui está como você pode fazer isso:

1. Abra o arquivo `whatsapp_utils.py` e encontre a função `criar_driver`.
2. Adicione a opção `headless` ao ChromeOptions.

    **Exemplo de código atualizado:**

    ```python
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    def criar_driver():
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Adiciona o modo headless
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--disable-gpu")

        # Adicione aqui o caminho do perfil do Chrome
        chrome_options.add_argument("user-data-dir=/path/to/your/chrome/profile")

        driver = webdriver.Chrome(options=chrome_options)
        return driver
    ```

## Exemplo de `config.py`

```python
# Renomeie o arquivo para config.py na utilização do mesmo

usuarios = [
    {
        "id_usuario": 1,
        "nome": "Usuário Exemplo 1",
        "numero": "5511999999999",
        "valor": 50.0,
    },
    {
        "id_usuario": 2,
        "nome": "Usuário Exemplo 2",
        "numero": "5511999999998",
        "valor": 45.0,
    },
    {
        "id_usuario": 3,
        "nome": "Usuário Exemplo 3",
        "numero": "5511999999997",
        "valor": 60.0,
    },
    {
        "id_usuario": 4,
        "nome": "Usuário Exemplo 4",
        "numero": "5511999999996",
        "valor": 55.0,
    },
]

plano = "Plano Exemplo"
valor = 50.0
pix = "chave-pix-exemplo"
TELEGRAM_TOKEN = "seu-token-do-telegram"


## Autor

Desenvolvido por Matheus Ribeiro.
- [LinkedIn](https://www.linkedin.com/in/matheus-ribeiro-636b25318/)
- [GitHub](https://github.com/MatheusBenvindo)