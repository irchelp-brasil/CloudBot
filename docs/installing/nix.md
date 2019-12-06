### Fazendo o Download

#### Arquivo
Faça o download do CloudBot de [https://github.com/CloudBotIRC/CloudBot/zipball/master.zip](https://github.com/CloudBotIRC/CloudBot/archive/master.zip) e desenpacote-o, ou execute os seguintes comandos:
```bash
curl -Ls https://github.com/CloudBotIRC/CloudBot/archive/master.zip > CloudBot.zip
unzip CloudBot.zip
cd CloudBot-master
```

#### Git

Alternativamente, você também pode clonar o CloudBot usando o comando:
```bash
git clone https://github.com/CloudBotIRC/CloudBot.git
cd CloudBot
```

### Instalando Dependências

Todas as dependências python do CloudBot estão listadas no arquivo `requirements.txt`, e podem ser instalados com o pip.

Mas primeiro, você vai precisar dos pacotes `git`, `python3.5-dev` e `libenchant1c2a`, `libxml2-dev`, `libxslt-dev` and `zlib1g-dev`. Instale esse pacotes com seu Sistema de Gerenciamento de Pacotes preferido.

Por exemeplo, para sistemas baseados em Debian, você pode usar o comando:
```bash
[sudo] apt-get install -y python3.5-dev git libenchant-dev libxml2-dev libxslt-dev zlib1g-dev
```

Agora, nós precisamos instalar o pip para Python 3.5. Use o seguinte comando:
```
curl -Ls https://bootstrap.pypa.io/get-pip.py | [sudo] python3.5
```

Note que você precisa da versão do pip para **python 3.5**, é por isso que nós recomendamos usar get-pip.py em vez de instalar python-pip ou python3-pip em seu sistema de gerenciamento de pacotes.

Finalmente, instale as dependências Python usando `pip` digitando o seguinte comando no diretório do CloudBot:
```
pip install -r requirements.txt
```
