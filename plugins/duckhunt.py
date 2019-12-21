import operator
import random
from collections import defaultdict
from threading import Lock
from time import time, sleep

from sqlalchemy import Boolean, Column, Integer, PrimaryKeyConstraint, String, Table, and_, desc
from sqlalchemy.sql import select

from cloudbot import hook
from cloudbot.event import EventType
from cloudbot.util import database
from cloudbot.util.formatting import pluralize_auto, truncate
from cloudbot.util.func_utils import call_with_args

duck_tail = "・゜゜・。。・゜"
duck = ["\\_o< ", "\\_O< ", "\\_0< ", "\\_\u00f6< ", "\\_\u00f8< ", "\\_\u00f3< "]
duck_noise = ["QUACK!", "FLAP FLAP!", "quack!"]

table = Table(
    'duck_hunt',
    database.metadata,
    Column('network', String),
    Column('name', String),
    Column('shot', Integer),
    Column('befriend', Integer),
    Column('chan', String),
    PrimaryKeyConstraint('name', 'chan', 'network')
)

optout = Table(
    'nohunt',
    database.metadata,
    Column('network', String),
    Column('chan', String),
    PrimaryKeyConstraint('chan', 'network')
)

status_table = Table(
    'duck_status',
    database.metadata,
    Column('network', String),
    Column('chan', String),
    Column('active', Boolean, default=False),
    Column('duck_kick', Boolean, default=False),
    PrimaryKeyConstraint('network', 'chan')
)


class ChannelState:
    """
    Represents the state of the hunt in a single channel
    """

    def __init__(self):
        self.masks = []
        self.messages = 0
        self.game_on = False
        self.no_duck_kick = False
        self.duck_status = 0
        self.next_duck_time = 0
        self.duck_time = 0
        self.shoot_time = 0

    def clear_messages(self):
        self.messages = 0
        self.masks.clear()

    def should_deploy(self, conn):
        """Should we deploy a duck?"""
        msg_delay = get_config(conn, 'minimum_messages', 10)
        mask_req = get_config(conn, 'minimum_users', 5)
        return (
            self.game_on and self.duck_status == 0 and
            self.next_duck_time <= time() and
            self.messages >= msg_delay and
            len(self.masks) >= mask_req
        )

    def handle_message(self, event):
        if self.game_on and self.duck_status == 0:
            self.messages += 1
            if event.host not in self.masks:
                self.masks.append(event.host)


scripters = defaultdict(int)
chan_locks = defaultdict(lambda: defaultdict(Lock))
game_status = defaultdict(lambda: defaultdict(ChannelState))
opt_out = defaultdict(list)


def _get_conf_value(conf, field):
    return conf['plugins']['duckhunt'][field]


def get_config(conn, field, default):
    """
    :type conn: cloudbot.client.Client
    :type field: str
    :type default: Any
    """
    try:
        return _get_conf_value(conn.config, field)
    except LookupError:
        try:
            return _get_conf_value(conn.bot.config, field)
        except LookupError:
            return default


@hook.on_start()
def load_optout(db):
    """load a list of channels duckhunt should be off in. Right now I am being lazy and not
    differentiating between networks this should be cleaned up later."""
    new_data = defaultdict(list)
    chans = db.execute(optout.select())
    for row in chans:
        chan = row["chan"]
        new_data[row["network"].casefold()].append(chan.casefold())

    opt_out.clear()
    opt_out.update(new_data)


def is_opt_out(network, chan):
    """
    :type network: str
    :type chan: str
    """
    return chan.casefold() in opt_out[network]


@hook.on_start
def load_status(db):
    """
    :type db: sqlalchemy.orm.Session
    """
    rows = db.execute(status_table.select())
    for row in rows:
        net = row['network']
        chan = row['chan']
        status = get_state_table(net, chan)
        status.game_on = row['active']
        status.no_duck_kick = row['duck_kick']
        if status.game_on:
            set_ducktime(chan, net)


def get_state_table(network, chan):
    """
    :type network: str
    :type chan: str
    """
    return game_status[network.casefold()][chan.casefold()]


def save_channel_state(db, network, chan, status=None):
    """
    :type db: sqlalchemy.orm.Session
    :type network: str
    :type chan: str
    :type status: ChannelState
    """
    if status is None:
        status = get_state_table(network, chan)

    active = status.game_on
    duck_kick = status.no_duck_kick
    res = db.execute(
        status_table.update().where(and_(
            status_table.c.network == network,
            status_table.c.chan == chan
        )).values(active=active, duck_kick=duck_kick)
    )
    if not res.rowcount:
        db.execute(status_table.insert().values(
            network=network, chan=chan, active=active, duck_kick=duck_kick
        ))

    db.commit()


@hook.on_unload
def save_on_exit(db):
    """
    :type db: sqlalchemy.orm.Session
    """
    return save_status(db, False)


# @hook.periodic(8 * 3600, singlethread=True)  # Run every 8 hours
def save_status(db, _sleep=True):
    """
    :type db: sqlalchemy.orm.Session
    :type _sleep: bool
    """
    for network in game_status:
        for chan, status in game_status[network].items():
            save_channel_state(db, network, chan, status)

            if _sleep:
                sleep(5)


def set_game_state(db, conn, chan, active=None, duck_kick=None):
    """
    :type db: sqlalchemy.orm.Session
    :type conn: cloudbot.client.Client
    :type chan: str
    :type active: bool
    :type duck_kick: bool
    """
    status = get_state_table(conn.name, chan)
    if active is not None:
        status.game_on = active

    if duck_kick is not None:
        status.no_duck_kick = duck_kick

    save_channel_state(db, conn.name, chan, status)


@hook.event([EventType.message, EventType.action], singlethread=True)
def increment_msg_counter(event, conn):
    """Increment the number of messages said in an active game channel. Also keep track of the unique masks that are
    speaking.
    :type event: cloudbot.event.Event
    :type conn: cloudbot.client.Client
    """
    if is_opt_out(conn.name, event.chan):
        return

    ignore = event.bot.plugin_manager.find_plugin("core.ignore")
    if ignore and ignore.code.is_ignored(conn.name, event.chan, event.mask):
        return

    get_state_table(conn.name, event.chan).handle_message(event)


@hook.command("starthunt", autohelp=False, permissions=["chanop", "op", "botcontrol"])
def start_hunt(db, chan, message, conn):
    """- Esse comando inica o jogo do pato em seu canal. Para parar o jogo, use o comando .stophunt"""
    if is_opt_out(conn.name, chan):
        return

    if not chan.startswith("#"):
        return "Não casse sozinho, pode não ser seguro."

    check = get_state_table(conn.name, chan).game_on
    if check:
        return "Já esta sendo executado um jogo no {}.".format(chan)

    set_game_state(db, conn, chan, active=True)
    set_ducktime(chan, conn.name)
    message(
        "Patos sorrateiros foram vistos nos arredores deste canal. "
        "Vamos ver quantos voce mata ou faz amizade. "
        "Use .bang para matar os patos ou .befriend para ser amigo deles. "
        "NOTA: Os patos só voam se houver alguma atividade no canal. Do contratio, eles ficam entocados.",
        chan
    )


def set_ducktime(chan, conn):
    """
    :type chan: str
    :type conn: str
    """
    status = get_state_table(conn, chan)  # type: ChannelState
    status.next_duck_time = random.randint(int(time()) + 480, int(time()) + 3600)
    # status.flyaway = status.next_duck_time + 600
    status.duck_status = 0
    # let's also reset the number of messages said and the list of masks that have spoken.
    status.clear_messages()


@hook.command("stophunt", autohelp=False, permissions=["chanop", "op", "botcontrol"])
def stop_hunt(db, chan, conn):
    """- Esse comando para o jogo do pato dentro do canal. O score atual sera preservado.

    :type db: sqlalchemy.orm.Session
    :type chan: str
    :type conn: cloudbot.client.Client
    """
    if is_opt_out(conn.name, chan):
        return

    if get_state_table(conn.name, chan).game_on:
        set_game_state(db, conn, chan, active=False)
        return "O jogo esta parado."

    return "Não há jogo no {}.".format(chan)


@hook.command("duckkick", permissions=["chanop", "op", "botcontrol"])
def no_duck_kick(db, text, chan, conn, notice_doc):
    """<enable|disable> - Se o bot tiver OP ou Hallf-op no canal, você pode digitar .duckkick enable|disable para que
    usuários do canal sejam kickados, caso atirem ou tendem ser amigos de um pato fantasma. O padrão é desligado.

    :type db: sqlalchemy.orm.Session
    :type text: str
    :type chan: str
    :type conn: cloudbot.client.Client
    :type notice_doc: function
    """
    if is_opt_out(conn.name, chan):
        return

    if text.lower() == 'enable':
        set_game_state(db, conn, chan, duck_kick=True)
        return "A partir de agora, os usuários que atirarem ou tentarem ser amigos de um pato fantasma, vão ser kickados." \
               "O pato precisa ter os poderes necessários para fazer esse trabalho."

    if text.lower() == 'disable':
        set_game_state(db, conn, chan, duck_kick=False)
        return "Kick por pato fantasma esta desabilitado."

    notice_doc()
    return None


def generate_duck():
    """Try and randomize the duck message so people can't highlight on it/script against it."""
    rt = random.randint(1, len(duck_tail) - 1)
    dtail = duck_tail[:rt] + u' \u200b ' + duck_tail[rt:]

    dbody = random.choice(duck)
    rb = random.randint(1, len(dbody) - 1)
    dbody = dbody[:rb] + u'\u200b' + dbody[rb:]

    dnoise = random.choice(duck_noise)
    rn = random.randint(1, len(dnoise) - 1)
    dnoise = dnoise[:rn] + u'\u200b' + dnoise[rn:]

    return dtail, dbody, dnoise


@hook.periodic(11, initial_interval=11)
def deploy_duck(bot):
    """
    :type bot: cloudbot.bot.CloudBot
    """
    for network in game_status:
        if network not in bot.connections:
            continue

        conn = bot.connections[network]
        if not conn.ready:
            continue

        for chan in game_status[network]:
            status = get_state_table(network, chan)
            if not status.should_deploy(conn):
                continue

            # deploy a duck to channel
            status.duck_status = 1
            status.duck_time = time()
            dtail, dbody, dnoise = generate_duck()
            conn.message(chan, "{}{}{}".format(dtail, dbody, dnoise))


def hit_or_miss(deploy, shoot):
    """This function calculates if the befriend or bang will be successful.
    :type deploy: float
    :type shoot: float
    """
    if shoot - deploy < 1:
        return .05

    if 1 <= shoot - deploy <= 7:
        out = random.uniform(.60, .75)
        return out

    return 1


def dbadd_entry(nick, chan, db, conn, shoot, friend):
    """Takes care of adding a new row to the database.
    :type nick: str
    :type chan: str
    :type db: sqlalchemy.orm.Session
    :type conn: cloudbot.client.Client
    :type shoot: int
    :type friend: int
    """
    query = table.insert().values(
        network=conn.name,
        chan=chan.lower(),
        name=nick.lower(),
        shot=shoot,
        befriend=friend
    )

    db.execute(query)
    db.commit()


def dbupdate(nick, chan, db, conn, shoot, friend):
    """update a db row
    :type nick: str
    :type chan: str
    :type db: sqlalchemy.orm.Session
    :type conn: cloudbot.client.Client
    :type shoot: int
    :type friend: int
    """
    values = {}
    if shoot:
        values['shot'] = shoot

    if friend:
        values['befriend'] = friend

    if not values:
        raise ValueError("No new values specified for 'friend' or 'shot'")

    query = table.update().where(and_(
        table.c.network == conn.name,
        table.c.chan == chan.lower(),
        table.c.name == nick.lower(),
    )).values(**values)

    db.execute(query)
    db.commit()


def update_score(nick, chan, db, conn, shoot=0, friend=0):
    """
    :type nick: str
    :type chan: str
    :type db: sqlalchemy.orm.Session
    :type conn: cloudbot.client.Client
    :type shoot: int
    :type friend: int
    """
    score = db.execute(select([table.c.shot, table.c.befriend])
                       .where(table.c.network == conn.name)
                       .where(table.c.chan == chan.lower())
                       .where(table.c.name == nick.lower())).fetchone()

    if score:
        dbupdate(nick, chan, db, conn, score[0] + shoot, score[1] + friend)
        return {'shoot': score[0] + shoot, 'friend': score[1] + friend}

    dbadd_entry(nick, chan, db, conn, shoot, friend)
    return {'shoot': shoot, 'friend': friend}


def attack(event, nick, chan, db, conn, attack_type):
    """
    :type event: cloudbot.event.Event
    :type nick: str
    :type chan: str
    :type db: sqlalchemy.orm.Session
    :type conn: cloudbot.client.Client
    :type attack_type: str
    """
    if is_opt_out(conn.name, chan):
        return

    network = conn.name
    status = get_state_table(network, chan)

    out = ""
    if attack_type == "shoot":
        miss = [
            "WHOOSH! Você errou feio o pato!", "Sua arma deu pane!",
            "Mais sorte da proxima vez.",
            "WTF?! Quem é você, Kim Jong Un disparando misseis? você errou."
        ]
        no_duck = "Não há patos voando! Ta atirando no que?"
        msg = "{} Você matou o pato em {:.3f} segundos! Total de {} mortos no {}."
        scripter_msg = "Você puxou o gatinho em {:.3f} segundos, isso é muito rapido Billy The Kid. " \
                       "Tens certeza que isso não é um script? Vai ficar no cantinho da reflexão por 2 horas."
        attack_type = "shoot"
    else:
        miss = [
            "O pato não quer ser seu amigo, mais sorte da proxima vez.",
            "Que estranho! O  pato precisa pensar sobre isso.",
            "O pato disse não, talvez suborna-lo com um oper funcione? Todos adoram o poder não é mesmo?",
            "Quem poderia imaginar que os patos seriam tão ambiciosos?"
        ]
        no_duck = "Você quer ser amigo de um pato fantasma. Isso e assustador."
        msg = "{} Você conquistou a amizade do pato em {:.3f} segundos! Grande Dom Juan! Tem {} amigos no {}."
        scripter_msg = "Você tentou ser amigo do pato em {:.3f} segundos. Isso é muito rápido ativista do Greepeace! " \
                       "Tens certeza que isso não é um script? Vai ficar no cantinho da reflexão por 2 horas."
        attack_type = "friend"

    if not status.game_on:
        return "O jogo caça ao pato não esta sendo executado. Use .starthunt par aniciar o jogo."

    if status.duck_status != 1:
        if status.no_duck_kick == 1:
            conn.cmd("KICK", chan, nick, no_duck)
            return

        return no_duck

    status.shoot_time = time()
    deploy = status.duck_time
    shoot = status.shoot_time
    if nick.lower() in scripters:
        if scripters[nick.lower()] > shoot:
            event.notice(
                "Você esta no cantinho da reflexão. Pode tentar de novo em {:.3f} segundos.".format(
                    scripters[nick.lower()] - shoot
                )
            )
            return

    chance = hit_or_miss(deploy, shoot)
    if not random.random() <= chance and chance > .05:
        out = random.choice(miss) + " Você pode tentar de novo em 7 segundos."
        scripters[nick.lower()] = shoot + 7
        return out

    if chance == .05:
        out += scripter_msg.format(shoot - deploy)
        scripters[nick.lower()] = shoot + 7200
        return random.choice(miss) + " " + out

    status.duck_status = 2
    try:
        args = {
            attack_type: 1
        }

        score = update_score(nick, chan, db, conn, **args)[attack_type]
    except Exception:
        status.duck_status = 1
        event.reply("Ocorreu um erro desconhecido.")
        raise

    event.message(msg.format(
        nick, shoot - deploy,
        pluralize_auto(score, "duck"), chan
    ))
    set_ducktime(chan, conn.name)


@hook.command("bang", autohelp=False)
def bang(nick, chan, db, conn, event):
    """- when there is a duck on the loose use this command to shoot it.

    :type event: cloudbot.event.Event
    :type nick: str
    :type chan: str
    :type db: sqlalchemy.orm.Session
    :type conn: cloudbot.client.Client
    """
    with chan_locks[conn.name][chan.casefold()]:
        return attack(event, nick, chan, db, conn, "shoot")


@hook.command("befriend", autohelp=False)
def befriend(nick, chan, db, conn, event):
    """- when there is a duck on the loose use this command to befriend it before someone else shoots it.

    :type event: cloudbot.event.Event
    :type nick: str
    :type chan: str
    :type db: sqlalchemy.orm.Session
    :type conn: cloudbot.client.Client
    """
    with chan_locks[conn.name][chan.casefold()]:
        return attack(event, nick, chan, db, conn, "befriend")


def top_list(prefix, data, join_char=' • '):
    r"""
    >>> foods = [('Spam', 1), ('Eggs', 4)]
    >>> top_list("Top Foods: ", foods)
    'Top Foods: \x02E\u200bggs\x02: 4 • \x02S\u200bpam\x02: 1'
    """
    sorted_data = sorted(data, key=operator.itemgetter(1), reverse=True)
    return truncate(
        prefix + join_char.join(
            "\x02{}\x02: {:,}".format(k[:1] + '\u200b' + k[1:], v)
            for k, v in sorted_data
        ),
        sep=join_char,
        length=320,
    )


def get_scores(db, score_type, network, chan=None):
    clause = table.c.network == network
    if chan is not None:
        clause = and_(clause, table.c.chan == chan.lower())

    query = select([table.c.name, table.c[score_type]], clause) \
        .order_by(desc(table.c[score_type]))

    scores = db.execute(query).fetchall()
    return scores


class ScoreType:
    def __init__(self, name, column_name, noun, verb):
        self.name = name
        self.column_name = column_name
        self.noun = noun
        self.verb = verb


def get_channel_scores(db, score_type: ScoreType, conn, chan):
    scores_dict = defaultdict(int)
    scores = get_scores(db, score_type.column_name, conn.name, chan)
    if not scores:
        return None

    for row in scores:
        if row[1] == 0:
            continue

        scores_dict[row[0]] += row[1]

    return scores_dict


def _get_global_scores(db, score_type: ScoreType, conn):
    scores_dict = defaultdict(int)
    chancount = defaultdict(int)
    scores = get_scores(db, score_type.column_name, conn.name)
    if not scores:
        return None, None

    for row in scores:
        if row[1] == 0:
            continue

        chancount[row[0]] += 1
        scores_dict[row[0]] += row[1]

    return scores_dict, chancount


def get_global_scores(db, score_type: ScoreType, conn):
    return _get_global_scores(db, score_type, conn)[0]


def get_average_scores(db, score_type: ScoreType, conn):
    scores_dict, chancount = _get_global_scores(db, score_type, conn)
    if not scores_dict:
        return None

    for k, v in scores_dict.items():
        scores_dict[k] = int(v / chancount[k])

    return scores_dict


SCORE_TYPES = {
    'friend': ScoreType('befriend', 'befriend', 'friend', 'friended'),
    'killer': ScoreType('killer', 'shot', 'killer', 'killed'),
}

DISPLAY_FUNCS = {
    'average': get_average_scores,
    'global': get_global_scores,
    None: get_channel_scores,
}


def display_scores(score_type: ScoreType, event, text, chan, conn, db):
    if is_opt_out(conn.name, chan):
        return

    global_pfx = "Duck {noun} pontuação em toda a Rede: ".format(
        noun=score_type.noun
    )
    chan_pfx = "Duck {noun} pontuação no {chan}: ".format(
        noun=score_type.noun, chan=chan
    )
    no_ducks = "Esta parecendo que ninguém {verb} nenhum pato ainda."

    out = global_pfx if text else chan_pfx

    try:
        func = DISPLAY_FUNCS[text.lower() or None]
    except KeyError:
        event.notice_doc()
        return

    scores_dict = call_with_args(func, {
        'db': db,
        'score_type': score_type,
        'conn': conn,
        'chan': chan,
    })

    if not scores_dict:
        return no_ducks

    return top_list(out, scores_dict.items())


@hook.command("friends", autohelp=False)
def friends(text, event, chan, conn, db):
    """[{global|average}] - Mostra a lista dos Top Duck Friends no canal.
    Se o parâmetro 'global' é especificado, todos os canais da base de dados são
    incluídos.

    :type text: str
    :type event: cloudbot.event.CommandEvent
    :type chan: str
    :type conn: cloudbot.client.Client
    :type db: sqlalchemy.orm.Session
    """
    return display_scores(SCORE_TYPES['friend'], event, text, chan, conn, db)


@hook.command("killers", autohelp=False)
def killers(text, event, chan, conn, db):
    """[{global|average}] - Mostra a lista dos Top Duck Killers no canal.
    Se o parâmetro 'global' é especificado, todos os canais da base de dados são
    incluídos.

    :type text: str
    :type event: cloudbot.event.CommandEvent
    :type chan: str
    :type conn: cloudbot.client.Client
    :type db: sqlalchemy.orm.Session
    """
    return display_scores(SCORE_TYPES['killer'], event, text, chan, conn, db)


@hook.command("duckforgive", permissions=["op", "ignore"])
def duckforgive(text):
    """<nick> - Permite que os usuários sejam removidos do período do cantinho da reflexão.

    :type text: str
    """
    if text.lower() in scripters and scripters[text.lower()] > time():
        scripters[text.lower()] = 0
        return "{} has been removed from the mandatory cooldown period.".format(text)

    return "I couldn't find anyone banned from the hunt by that nick"


@hook.command("hunt_opt_out", permissions=["op", "ignore"], autohelp=False)
def hunt_opt_out(text, chan, db, conn):
    """[{add <chan>|remove <chan>|list}] - Executar este comando sem qualquer argumento, mostra o status
    do canal atual. hunt_opt_out add #channel vai desativar todos os comandos de caça do canal especificado.
    hunt_opt_out remove #channel vai reativar o jogo no canal especificado.

    :type text: str
    :type chan: str
    :type db: sqlalchemy.orm.Session
    :type conn: cloudbot.client.Client
    """
    if not text:
        if is_opt_out(conn.name, chan):
            return "A caça ao pato esta desativada no {}. Para reativa-lo, execute o comando .hunt_opt_out remove #channel".format(chan)

        return "A caça ao pato esta ativada no {}. Para desativa-lo, execute o comando .hunt_opt_out add #channel".format(chan)

    if text == "list":
        return ", ".join(opt_out)

    if len(text.split(' ')) < 2:
        return "Por favor, coloque add ou remove a um nome de canal válido."

    command = text.split()[0]
    channel = text.split()[1]
    if not channel.startswith('#'):
        return "Por favor, especifique um canal válido."

    if command.lower() == "add":
        if is_opt_out(conn.name, channel):
            return "A caça ao pato já esta desativada no {}.".format(channel)

        query = optout.insert().values(
            network=conn.name,
            chan=channel.lower()
        )
        db.execute(query)
        db.commit()
        load_optout(db)
        return "A caça ao pato foi desativada com sucesso no {}.".format(channel)

    if command.lower() == "remove":
        if not is_opt_out(conn.name, channel):
            return "A caça ao pato já esta sendo executada no {}.".format(channel)

        delete = optout.delete(optout.c.chan == channel.lower())
        db.execute(delete)
        db.commit()
        load_optout(db)


@hook.command("duckmerge", permissions=["botcontrol"])
def duck_merge(text, conn, db, message):
    """<user1> <user2> - Transfere os pontos de um nick para outro. Os pontos do primeiro nick serão zerados e transferidos para o segundo nick. Essa operação não pode ser desfeita.

    :type text: str
    :type conn: cloudbot.client.Client
    :type db: sqlalchemy.orm.Session
    :type message: function
    """
    oldnick, newnick = text.lower().split()
    if not oldnick or not newnick:
        return "Por favor, informe dois nicks para este comando."

    oldnickscore = db.execute(select([table.c.name, table.c.chan, table.c.shot, table.c.befriend])
                              .where(table.c.network == conn.name)
                              .where(table.c.name == oldnick)).fetchall()

    newnickscore = db.execute(select([table.c.name, table.c.chan, table.c.shot, table.c.befriend])
                              .where(table.c.network == conn.name)
                              .where(table.c.name == newnick)).fetchall()

    duckmerge = defaultdict(lambda: defaultdict(int))
    duckmerge["TKILLS"] = 0
    duckmerge["TFRIENDS"] = 0
    channelkey = {"update": [], "insert": []}
    if oldnickscore:
        if newnickscore:
            for row in newnickscore:
                duckmerge[row["chan"]]["shot"] = row["shot"]
                duckmerge[row["chan"]]["befriend"] = row["befriend"]

            for row in oldnickscore:
                if row["chan"] in duckmerge:
                    duckmerge[row["chan"]]["shot"] = duckmerge[row["chan"]]["shot"] + row["shot"]
                    duckmerge[row["chan"]]["befriend"] = duckmerge[row["chan"]]["befriend"] + row["befriend"]
                    channelkey["update"].append(row["chan"])
                    duckmerge["TKILLS"] = duckmerge["TKILLS"] + row["shot"]
                    duckmerge["TFRIENDS"] = duckmerge["TFRIENDS"] + row["befriend"]
                else:
                    duckmerge[row["chan"]]["shot"] = row["shot"]
                    duckmerge[row["chan"]]["befriend"] = row["befriend"]
                    channelkey["insert"].append(row["chan"])
                    duckmerge["TKILLS"] = duckmerge["TKILLS"] + row["shot"]
                    duckmerge["TFRIENDS"] = duckmerge["TFRIENDS"] + row["befriend"]
        else:
            for row in oldnickscore:
                duckmerge[row["chan"]]["shot"] = row["shot"]
                duckmerge[row["chan"]]["befriend"] = row["befriend"]
                channelkey["insert"].append(row["chan"])
                # TODO: Call dbupdate() and db_add_entry for the items in duckmerge

        for channel in channelkey["insert"]:
            dbadd_entry(newnick, channel, db, conn, duckmerge[channel]["shot"], duckmerge[channel]["befriend"])

        for channel in channelkey["update"]:
            dbupdate(newnick, channel, db, conn, duckmerge[channel]["shot"], duckmerge[channel]["befriend"])

        query = table.delete().where(
            and_(table.c.network == conn.name, table.c.name == oldnick)
        )

        db.execute(query)
        db.commit()
        message("Migrado {} e {} de {} para {}".format(
            pluralize_auto(duckmerge["TKILLS"], "duck kill"), pluralize_auto(duckmerge["TFRIENDS"], "duck friend"),
            oldnick, newnick
        ))
    else:
        return "Não há pontuação a ser transferida para {}".format(oldnick)


@hook.command("ducks", autohelp=False)
def ducks_user(text, nick, chan, conn, db, message):
    """<nick> - Informa o score de pontuação de um nick. Se nenhum nick for apresentado, será informado o score do solicitante.

    :type text: str
    :type nick: str
    :type chan: str
    :type conn: cloudbot.client.Client
    :type db: sqlalchemy.orm.Session
    :type message: function
    """
    name = nick.lower()
    if text:
        name = text.split()[0].lower()

    ducks = defaultdict(int)
    scores = db.execute(select(
        [table.c.name, table.c.chan, table.c.shot, table.c.befriend],
        and_(
            table.c.network == conn.name,
            table.c.name == name,
        )
    )).fetchall()

    if text:
        name = text.split()[0]
    else:
        name = nick

    if scores:
        has_hunted_in_chan = False
        for row in scores:
            if row["chan"].lower() == chan.lower():
                has_hunted_in_chan = True
                ducks["chankilled"] += row["shot"]
                ducks["chanfriends"] += row["befriend"]

            ducks["killed"] += row["shot"]
            ducks["friend"] += row["befriend"]
            ducks["chans"] += 1

        # Check if the user has only participated in the hunt in this channel
        if ducks["chans"] == 1 and has_hunted_in_chan:
            message("{} matou {} e é amigo de {} no {}.".format(
                name, pluralize_auto(ducks["chankilled"], "duck"), pluralize_auto(ducks["chanfriends"], "duck"), chan
            ))
            return

        kill_average = int(ducks["killed"] / ducks["chans"])
        friend_average = int(ducks["friend"] / ducks["chans"])
        message(
            "\x02{}'s\x02 duck stats: \x02{}\x02 mortes e \x02{}\x02 amizades no {}. "
            "Em {}: \x02{}\x02 mortes e  \x02{}\x02 amizades. "
            "Média de \x02{}\x02 e \x02{}\x02 por canal.".format(
                name, pluralize_auto(ducks["chankilled"], "duck"), pluralize_auto(ducks["chanfriends"], "duck"),
                chan, pluralize_auto(ducks["chans"], "channel"),
                pluralize_auto(ducks["killed"], "duck"), pluralize_auto(ducks["friend"], "duck"),
                pluralize_auto(kill_average, "kill"), pluralize_auto(friend_average, "friend")
            )
        )
    else:
        return "Esta parecendo que {} não participa da caça ao pato.".format(name)


@hook.command("duckstats", autohelp=False)
def duck_stats(chan, conn, db, message):
    """- Informa o score do canal e o score da Rede, mostrando o ranking deste ultimo.

    :type chan: str
    :type conn: cloudbot.client.Client
    :type db: sqlalchemy.orm.Session
    :type message: function
    """
    ducks = defaultdict(int)
    scores = db.execute(select(
        [table.c.name, table.c.chan, table.c.shot, table.c.befriend],
        table.c.network == conn.name
    )).fetchall()

    if scores:
        ducks["friendchan"] = defaultdict(int)
        ducks["killchan"] = defaultdict(int)
        for row in scores:
            ducks["friendchan"][row["chan"]] += row["befriend"]
            ducks["killchan"][row["chan"]] += row["shot"]
            # ducks["chans"] += 1
            if row["chan"].lower() == chan.lower():
                ducks["chankilled"] += row["shot"]
                ducks["chanfriends"] += row["befriend"]

            ducks["killed"] += row["shot"]
            ducks["friend"] += row["befriend"]

        ducks["chans"] = int((len(ducks["friendchan"]) + len(ducks["killchan"])) / 2)

        killerchan, killscore = sorted(ducks["killchan"].items(), key=operator.itemgetter(1), reverse=True)[0]
        friendchan, friendscore = sorted(ducks["friendchan"].items(), key=operator.itemgetter(1), reverse=True)[0]
        message(
            "\x02Duck Stats:\x02 {:,} mortes e {:,} amizades no \x02{}\x02. "
            "Em {} \x02{:,}\x02 patos foram mortos e \x02{:,}\x02 foram salvos. "
            "\x02Top Channels:\x02 \x02{}\x02 com {} e \x02{}\x02 com {}".format(
                ducks["chankilled"], ducks["chanfriends"], chan, pluralize_auto(ducks["chans"], "channel"),
                ducks["killed"], ducks["friend"],
                killerchan, pluralize_auto(killscore, "kill"),
                friendchan, pluralize_auto(friendscore, "friend")
            ))
    else:
        return "Ao que parece, não há atividade de patos sorrateiros neste canal ou rede."
