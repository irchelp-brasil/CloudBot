### Iniciando

Nós recomendamos o uso de sistemas *unix para a execução do CloudBot, ou Vagrant ao desenvolve-lo. No entanto, é possível instalá-lo no Windows.

Primeiramente, tenha certeza que você tem instalado o Python 3.5. Você pode fazer o download dele no sítio [python.org](https://www.python.org/downloads/release/python-341/).

Próximo passo, você precisa instalar o `pip`.

Você pode instalar o `pip` digitando o seguinte comando no cmd:
```
python3 -m ensurepip
```

Se não der certo, siga [este guia](http://simpledeveloper.com/how-to-install-easy_install/), em inglês, e execute `easy_install pip` no cmd.

### Download

Faça o download do CloudBot no sítio [https://github.com/CloudBotIRC/CloudBot/zipball/master.zip](https://github.com/CloudBotIRC/CloudBot/archive/master.zip).

Desempacote  o arquivo e continue a ler o documento.

### Instalando Dependências

Antes de executar o bot, você precisa instalar algumas dependências Python. Todas as dependências do CloudBot estão relacionadas no arquivo `requirements.txt`.

Essas dependências podem ser intaladas com o `pip` (Gerenciador de Pacotes Python) digitando o seguinte comando no diretório do bot:

    pip install -r requirements.txt

Instalar o `lxml` pode ser um pouco complicado no Windows (você pode ter algumas mensagens de erro com o comando acima) devido à necessidade de compilação, você pode encontrar uma distribuição pre-compilada em [http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml](http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml)
