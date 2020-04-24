# CloudBot
CloudBot - Um Simples, rápido e versátil, Bot IRC de código aberto em Python!

## Notas

- As versões **gonzobot** e **master** estão com os links direcionados para seus respectivos repositórios proprietários. Nesses dois casos, me detive a apenas traduzir o arquivo de "orientações à instalação" deles, que estão no própio repositório da IRChelp Brasil;
- Este projeto (tucuju) é relacionado apenas à tradução dos plugins do software (CloudBot) e não à programação;
- Para realizar o download correto, escolha a versão desejada no canto superior esquerdo da página, onde esta escrito **Branch**. Irá aparecer os arquivos dessa versão. Logo após, é só seguir as orientações da seçao Download CloudBot;
- Para alguns [comandos](https://wiki.irchelp.com.br/wiki/Portal:Tucujú) como `.weather`, `.gse`, `.spotify` e outros, é necessário adquirir as respectivas APIs. Procure no google sobre como obter esse recurso das empresas que fornecem esses serviços;
- Veja o arquivo [CHANGELOG.md](CHANGELOG.md) para ver as últimas atualizações das traduções.

## Download CloudBot

Há atualmente quatro versões diferentes neste repositório. Cada uma tem um nível de estabilidade e característica:
 - **tucuju** *(estável)*: Esta versão possui tudo que há na versão **master** e na versão **gonzobot** e mais as nossas traduções para o português. Também contém atualizações e correções de vários erros de grafia.
 - **tucuju-dev** *(instável)*: Esta versão é a de desenvolvimento do **tucuju** e inclui algumas traduções que não foram ainda revisionadas.
 - **gonzobot** *(estável)*: Esta versão é a da  Rede Snoonet ou seja, sem as traduções para o português. Contém tudo que há na versão **master** com adição dos plugins adicionados pela Snoonet IRC. Esta versão é atualizada constantemente e contém correções de vários bugs da versão master.
 - **master** *(estável (antiga/original))*: Esta versão é estável, com o código testado mas sem as traduções para o português e sem alguns plugins da Rede Snoonet. Esta versão é baseada diretamente na versão upstream master e atualmente não é mais atualizada.

## Instalação do CloudBot

Primeiramente, o CloudBot executa somente sob **Python 3.5.3 ou superior**

Para instalar o CloudBot no *nix (linux, etc), veja [aqui](docs/installing/nix.md)

Para instalar o CloudBot no Windows, veja [aqui](docs/installing/win.md)


### Execução do CloudBot

Antes de executar o bot, renomeie o arquivo `config.default.json` para `config.json` e edite suas configurações. Você pode testar se o arquivo JSON é válido usando [jsonlint.com](http://jsonlint.com/)!

Depois que você instalou as dependências necessárias e renomeou o arquivo de configuração, você pode executar o bot! Tenha certeza de estar na pasta correta e digite o seguinte comandos:

```
python3 -m cloudbot
```

Você também pode executar o bot usando diretamente o arquivo `cloudbot/__main__.py`, o qual executa em qualquer diretório.
```
python3 CloudBot/cloudbot/__main__.py
```
Especifique o caminho /caminho/para/diretorio/cloudbot/__main__.py, onde o `cloudbot` esta.

## Ajuda do CloudBot

### Documentação

A documentação do CloudBot é atualmente um pouco desatualizada e poderá não estar totalmente correta. Se você precisa de ajuda, visite [#gonzobot - Snoonet](https://webchat.snoonet.org/#gonzobot-dev). Eles, com verteza, vão lhe ajudar.

Para escrever seus plugins, visite [Página Wiki de plugins do CloudBot](https://github.com/CloudBotIRC/CloudBot/wiki/Writing-your-first-command-plugin).

Mais informações poderão ser encontradas na [Página Principal da mesma Wiki](https://github.com/CloudBotIRC/CloudBot/wiki).

Para saber todos os comandos em português, acesse o [Portal Tucujú](https://wiki.irchelp.com.br/wiki/Portal:Tucujú) em nossa [Wirchelp](https://wiki.irchelp.com.br/).

### Suporte

Os desenvolvedores do código podem ser encontrados no [#gonzobot-dev](https://webchat.snoonet.org/#gonzobot-dev) na [Snoonet](https://snoonet.org) e também podem tirar suas dúvidas.

Se você acredita que achou um bug/tem uma ideia/sugestão, por favor **abra uma chamada** no Github dos desenvolvedores [TotallyNotRobots](https://github.com/TotallyNotRobots/CloudBot) e contate-os no IRC!

## Log de mudanças das traduções

Veja [CHANGELOG.md](CHANGELOG.md)

## Licença

O CloudBot é **licenciado** sobe a licença **GPL v3**. Os temos são os seguintes.

![GPL V3](https://www.gnu.org/graphics/gplv3-127x51.png)
    
    CloudBot

    Copyright © 2011-2015 Luke Rogers / CloudBot Project

    CloudBot is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CloudBot is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CloudBot.  If not, see <http://www.gnu.org/licenses/>.
    
O Cloudbot usa dados GeoLite2 criados por MaxMind, disponível em
<a href="http://www.maxmind.com">http://www.maxmind.com</a>. Os dados GeoLite2 são distribuidos sobe a linceça [Creative Commons Attribution-ShareAlike 3.0 Unported License](https://creativecommons.org/licenses/by-sa/3.0/)

![Powered by wordnik](https://www.wordnik.com/img/wordnik_badge_a1.png)

Os Plugins de traduções são um serviço da [Yandex.Translate](https://translate.yandex.com)

O Cloudbot usa dados fornecidos pela <a href="http://wordnik.com">http://wordnik.com</a> de acordo com a wordnik.com API <a href="http://developer.wordnik.com/#!/terms">termos de serviço</a>.
