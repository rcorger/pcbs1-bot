import csv
from discord.ext import commands
import discord
import json
from time import sleep

# default values
CONST_MAX_RESULTS: int = 24
FETCHABLE_DATA: bool = False
CONST_INVITE_LINK: str = "https://discord.com/api/oauth2/authorize?client_id=1133824362638749707&permissions=8&scope=bot"

# just regular ol' config.json
with open('config.json') as f:
    CONFIG = json.loads(f.read())
    FETCHABLE_DATA = CONFIG['FETCHABLE_DATA']
    CONST_MAX_RESULTS = CONFIG['MAX_RESULTS']

# PRE-DEFINITIONS FOR PERFORMANCE'S SAKE.

# database of all requirements for apps/games.
with open('./data/pcbs_apps.json') as f:
    APPS = json.loads(f.read())

# part rankings csv reader so i don't have to open the file over and over again...
with open('./data/rankings.csv', 'r') as f:
    reader_of_rankings = csv.DictReader(f)
    PART_RANKINGS = [ line for line in reader_of_rankings ]

# line 24 summarized it pretty well...
with open('./data/pcbs1_data.csv', 'r') as f:
    pcbs1_data_csv_reader = csv.DictReader(f)
    ALL_DATA_PCBS = [ line for line in pcbs1_data_csv_reader ]


intents = discord.Intents.all()
client = commands.Bot(command_prefix=CONFIG["PREFIX"], intents=intents)
easter_egg = []

@client.event
async def on_ready():
    # TODO make this look nicer.
    CONFIG['owner_uname'] = client.get_user(CONFIG['SYS_ADMIN']).name

    activity = discord.Game('PC Building Simulator')
    await client.change_presence(activity=activity, status=discord.Status.dnd)

    print(f"\nLogged in as {client.user.name}\n\n----------------Servers----------------")
    for server in client.guilds:
        print(f'{server.name} - {server.id}')
    print("---------------------------------------")


@client.command(aliases=['wir'])
async def willitrun(ctx: commands.Context, *args):
    setting = None
    args = list(args)

    for i, arg in enumerate(args):
        arg = arg.lower()
        if arg == '-m':
            setting = 'min'
            args.pop(i)
        elif arg == '-r':
            setting = 'rec'
            args.pop(i)
        elif arg == '-4k':
            setting = '4k'
            args.pop(i)
    
    if setting is None:
        return await ctx.reply('A `setting` such as `-m` (for minimum), `-r` (for recommended) or `-4k` (for 4k) `MUST` be provided!')

    app_or_game = ' '.join(args).strip().lower()
    if app_or_game == "":
        return await ctx.reply(f"You must provide a `game/app` you'd like to see `the requirements` for!")

    name_app: str = None
    app_requirments = {}

    for name, reqs in APPS.items():
        if app_or_game in name.lower():
            name_app = name
            app_requirments = reqs
            break
    
    if name_app is None:
        return await ctx.reply(f"`No` app by the name of `{app_or_game}` was found in our data base.")

    if setting == 'min':
        minimum = app_requirments['Minimum Spec']
        return await ctx.reply(
            f"The `MINIMUM` specs for `{name_app}` are:```CPU: {minimum['CPU']}\nGPU: {minimum['GPU']}\nVRAM: {minimum['VRAM']}\nRAM: {minimum['RAM']}\nStorage: {minimum['Storage']}```"
        )
    elif setting == 'rec':
        recommended = app_requirments['Recommended Spec']
        return await ctx.reply(
            f"The `RECOMMENDED` specs for `{name_app}` are:```CPU: {recommended['CPU']}\nGPU: {recommended['GPU']}\nVRAM: {recommended['VRAM']}\nRAM: {recommended['RAM']}\nStorage: {recommended['Storage']}```"
        )
    elif setting == '4k':
        if 'Recommended 4K Spec' in app_requirments.keys():
            recommended = app_requirments['Recommended 4K Spec']
            return await ctx.reply(
                f"The `RECOMMENDED 4K` specs for `{name_app}` are:```CPU: {recommended['CPU']}\nGPU: {recommended['GPU']}\nVRAM: {recommended['VRAM']}\nRAM: {recommended['RAM']}\nStorage: {recommended['Storage']}```"
            )

        return await ctx.reply(f"App/game `{app_or_game}` does `NOT` have a `RECOMMENDED` spec for `4K`!")


@client.command(aliases=['pr'])
async def partranking(ctx: commands.Context, *args):
    item = ' '.join(args).strip().lower()

    if item == "":
        return await ctx.reply("You must provide an item to search for!")

    # search all part ranked items
    for i, line in enumerate(PART_RANKINGS):
        if item in line['Part'].lower():
            if line['Part Type'] == 'CPU':
                return await ctx.reply(
                        f"`{line['Part Type']}` `{line['Part']}` has a ranking score of `{line['Score']}` and is ranked `#{i+1}` in the in-game app!"
                    )
            #gpus
            else:
                return await ctx.reply(
                        f"`{line['Part Type']}` `{line['Part']}` has a ranking score of `{line['Score']}` and is ranked `#{i-125}` in the in-game app!"
                    )


    return await ctx.reply("`No` item matching with your desired query was `Found`!")


@client.command()
async def ping(ctx: commands.Context):
    return await ctx.reply(f":ping_pong: PONG | {round(client.latency * 1000)}ms")

# command to fetch all data from my data base | can be disabled in config.json 
# `FETCHABLE_DATA`
@client.command()
async def fetch(ctx: commands.Context, db: str=None):
    if not FETCHABLE_DATA and ctx.author.id != CONFIG['SYS_ADMIN']:
        return await ctx.reply(f"FETCHABLE_DATA=FALSE")

    if db is None:
        if 'owner_uname' in CONFIG:
            return await ctx.reply(
                f"You `must` `provide` a `database` you'd like to fetch from `{CONFIG['owner_uname']}`!"
            )
        return await ctx.reply("`I'm currently initializing... Ask again in a second.`")

    if db == "rankings":
        with open('./data/rankings.csv', 'rb') as f:
            await ctx.author.send(file=discord.File(f, 'rankings.csv'))
    elif db == "wir": # will it run
        with open('./data/pcbs_apps.json', 'rb') as f:
            await ctx.author.send(file=discord.File(f, 'pcbs_apps.json'))
    elif db == "items":
        with open('./data/pcbs1_data.csv', 'rb') as f:
            await ctx.author.send(file=discord.File(f, 'pcbs1_data.csv'))
    elif db == 'all':
        with open('./data/pcbs1_data.csv', 'rb') as f:
            await ctx.author.send(file=discord.File(f, 'pcbs1_data.csv'))
        with open('./data/pcbs_apps.json', 'rb') as f:
            await ctx.author.send(file=discord.File(f, 'pcbs_apps.json'))
        with open('./data/rankings.csv', 'rb') as f:
            await ctx.author.send(file=discord.File(f, 'rankings.csv'))
    else:
        return await ctx.reply("That `doesn't exist` in my database!")


@client.command(aliases=['gi'])
async def getitem(ctx: commands.Context, *args):
    item = ' '.join(args).strip().lower()
    if item == "":
        return await ctx.reply(f"Must provide an `argument` to search for! `Usage:` ```{CONFIG['PREFIX']}{ctx.command.name} <query>```")

    results = []

    for line in ALL_DATA_PCBS:
        f_p_n = line['Full Part Name'].lower()
        if item in f_p_n or item in f_p_n.replace('-', ' '):
            if len(results) > CONST_MAX_RESULTS:
                break
            results.append(line)
    
    if len(results) > CONST_MAX_RESULTS:
        return await ctx.reply("We have too many of those results. Be more sepcific.") # this can be moved to line no. 183

    # empty list
    if results == []:
        return await ctx.reply("No results were found for your query!")

    # sort by level via lambda
    results.sort(key=lambda x:int(x['Level']))

    result_msg: str = '\n'.join([f"`{res['Part Type']}` `{res['Full Part Name']}` unlocks at `level {res['Level']}` and costs `${res['Price']}`" for res in results])
    result_msg += f"\n```Amount returned: {len(results)} (<{CONST_MAX_RESULTS} MAX)```"
    
    msg = await ctx.reply(result_msg)
    sleep(1)
    
    if "$420" in result_msg and len(results) == 1 and ctx.author.id not in easter_egg:
        msg = await msg.reply("420... nice. :joy::joy::joy::joy::joy::joy::joy::joy::joy:")
        easter_egg.append(ctx.author.id)
        sleep(2.5)
        return await msg.delete()



client.run(token=CONFIG["TOKEN"])