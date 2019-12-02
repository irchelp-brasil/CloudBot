# CloudBot
CloudBot tucuju, um bot IRC open-source em Python para canais IRC.

## Download CloudBot

Há atualmente quatro versões diferentes neste repositório, cada uma tem um nível difente de estabilidade e características:
 - **tucuju** *(estável)*: Esta verão possui tudo que há na versão **master** e na versão **gonzobot** e mais as nossas traduções para o português. Essa versão contém atualizações e correção de vários erros de grafia.
 - **tucuju-dev** *(instável)*: Esta versão é a de desenvolvimento do **tucuju** e inclui algumas traduções que não foram ainda revisionadas.
 - **gonzobot** *(estável)*: Esta versão contém tudo que há na versão **master** com adição dos plugins adicionados pela Snoonet IRC. Esta versão é atualizada constantemente e contém correções de vários bugs da versão master.
 - **master** *(estável (antiga/original))*: Esta versão é estável, com o código testado mas sem as traduções para o portugues e sem alguns plugins da Snoonet. Esta versão é baseada diretamente na versão upstream master e atualmente não é mais atualizada.

## Instalação do CloudBot

Primeiramente, o CloudBot "roda" somente sobre **Python 3.5.3 ou superior**

Para instalar o CloudBot no *nix (linux, etc), veja [aqui](docs/installing/nix.md)

Para instalar o CloudBot no Windows, veja [aqui](docs/installing/win.md)


### "Rodando" o CloudBot

Antes de "rodar" o bot, renomeie o arquivo `config.default.json` para `config.json` and edite suas configurações. Você pode testar se o arquivo JSON é válido usando [jsonlint.com](http://jsonlint.com/)!

Depois que você instalou as dependências necessárias e renomeiou o arquivo de configuração, você pode rodar o bot! Tenha certeza de estar na pasta correta e digite o seguinte comandos:

```
python3 -m cloudbot
```

Você também pode "rodar" o bot usando o diretamente o arquivo `cloudbot/__main__.py`, o qual "roda" em qualquer diretório.
```
python3 CloudBot/cloudbot/__main__.py
```
Especifique o caminho /path/to/repository/cloudbot/__main__.py, onde o `cloudbot` esta.

## Ajuda do CloudBot

### Documentação

A documentação do CloudBot é atualmente um pouco desatualizada e poderá não esta totalmente correta. Se você precisa de ajuda, visite [#gonzobot - Snoonet](https://webchat.snoonet.org/#gonzobot-dev). Eles, com verteza, vão lhe ajudar.

Para escrever seus plugins, visite [Página Wiki de plugins](https://github.com/CloudBotIRC/CloudBot/wiki/Writing-your-first-command-plugin).

Mais infirmações poderão ser encontradas na [Página Principal da mesma Wiki](https://github.com/CloudBotIRC/CloudBot/wiki).

### Suporte

Os desenvolvedores do código podee ser encontrador no [#gonzobot-dev](https://webchat.snoonet.org/#gonzobot-dev) na [Snoonet](https://snoonet.org) e também podem tirar suas dúvidas.

Se você acredita que achou um bug/tem uma ideia/sugestão, por favor **abra uma chamada** no Github dos desenvolvedores [TotallyNotRobots (https://github.com/TotallyNotRobots/CloudBot)] e contate-os no IRC!

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

O Cloudbot usa dados fornecidos pela <a href="http://wordnik.com">http://wordnik.com</a> de acordo com a wordnik.com API <a href="http://developer.wordnik.com/#!/terms">terms of service</a>.
