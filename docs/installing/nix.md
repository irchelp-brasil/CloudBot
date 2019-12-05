### Fazendo o Download

#### Arquivo
Faça o download do CloudBot de [https://github.com/TotallyNotRobots/CloudBot/zipball/gonzobot.zip](https://github.com/TotallyNotRobots/CloudBot/archive/gonzobot.zip) and unzip, ou execute os seguintes comandos:
```bash
curl -Ls https://github.com/TotallyNotRobots/CloudBot/archive/gonzobot.zip > CloudBot.zip
unzip CloudBot.zip
cd CloudBot-gonzobot
```

#### Git

Alternativamente, você também pode clonar o CloudBot usando o comando:
```bash
git clone https://github.com/TotallyNotRobots/CloudBot.git
cd CloudBot
```

### Instando Dependências

Todas as dependências python do CloudBot's estão listadas no arquivo `requirements.txt`, e podem ser instalados com o pip.

Mas primeiro, você vai precisar dos pacotes `git`, `python3.5-dev` e `libenchant1c2a`, `libxml2-dev`, `libxslt-dev` and `zlib1g-dev`. Instale esse pacotes com seu Sistema de Gerenciamento de Pacotes preferido.

Por exemeplo, para sistemas baseados em Debian, você pode usar o comando:
```bash
[sudo] apt-get install -y python3.5-dev git libenchant-dev libxml2-dev libxslt-dev zlib1g-dev
```

Você também vai precisar instalar o `pip`, que pode ser feito seguindo [esse guia](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#installing-pip)

Também é recomendado que você crie um ambiente virtual para isolar o bot do sistema de atualização de bibliotecas. Primeiramente, [instale o pacote de ambiente virtual](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#installing-virtualenv) se necessário, e então [crie o ambiente virtual](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)

Vamos nos referir ao amboente virtual como `<VENV_DIR>` da qui em diante.

Uma vez o ambiente vistual criado, [ative-o](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment).

Finalmente, instale as dependência python usando o `pip` executando o seguinte comando no diretório do CloudBot:
```bash
pip install -Ur requirements.txt
```

Agora você esta pronto para executar o bot! Isso pode ser realizando simplismente executando o módulo cloudbot da seguinte forma
```bash
python -m cloudbot
```
ou sem o ativamento do ambiente virtual, use o comando
```bash
<VENV_DIR>/bin/python -m cloudbot
```
