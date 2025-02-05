import contextlib


from random import randint, uniform, choice

from discord.ext.commands import Greedy

with contextlib.redirect_stdout(None):
    import discord, asyncio
    from discord.ext import commands, tasks
    from discord.utils import get
    import datetime


from data.TOKEN import token
from utils import *
from economy import *
from config import *
from functions import checkData
from typing import Dict

from lang.langManager import langMan

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix='$', intents=intents)

client.remove_command('help')

guildCounter = 0
ready = False

cogs = ['e621', 'economyCommands', 'admin', 'gambling', 'russianRoulette']
async def loadCogs():
    for cog in cogs:
        try:
            await client.load_extension(f'cogs.{cog.lower()}')
            print(f'{cog} cog loaded.')
        except Exception as e:
            print(f'Failed to load {cog} cog: {e}')


possibleStatus = []

def updatePossibleStatus():
    global possibleStatus

    possibleStatus = [f'{guildCounter} servers!',
                      f'$help',
                      f'baaah',
                      f'people turn into gambling addicts',
                      f', but nobody came']

@tasks.loop(seconds=120)
async def statusChange():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{choice(possibleStatus)}"))

@client.event
async def on_guild_join(guild):
    global guildCounter, possibleStatus
    guildCounter += 1

    updatePossibleStatus()

@client.event
async def on_ready() -> None:

    global guildCounter, possibleStatus, ready

    if ready:
        return

    ready = True

    await loadCogs()

    for guild in client.guilds:
        guildCounter += 1
        checkData(guild.id)

    updatePossibleStatus()

    statusChange.start()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{choice(possibleStatus)}"))

@commands.command(aliases=['help', 'comandos'], brief='Muestra la lista de comandos.', description="Muestra la lista de comandos y si le pasas un comando te habla más a fondo de él.", extras={'admin': False})
async def ayuda(ctx: discord.ext.commands, pagina: int = 1):

    author = getAuthor(ctx)
    guildID = ctx.message.author.guild.id

    embed = discord.Embed(title='', description='', color=ctx.author.color)
    embed.set_footer(icon_url="https://files.catbox.moe/1m1mxx.png")
    #embed.set_author(name=author.display_name, icon_url=author.avatar)

    numberOfPages = 5

    match pagina:
        case 1:

            embed.title = f'{langMan.getString("page", guildID=guildID)} 1/{numberOfPages}  -  {langMan.getString("economy", guildID=guildID)}'

            embed.add_field(name="󠁪",
                            value=f"* $wallet `<{langMan.getString('user', guildID=guildID)}>`\n  * {langMan.getString('walletCommand', guildID=guildID)}\n\n"
                                  f"* $give `<{langMan.getString('amount', guildID=guildID)}>` `<{langMan.getString('users', guildID=guildID)}>`\n  * {langMan.getString('giveCommand', guildID=guildID)}\n\n"
                                  f"* $daily\n  * {langMan.getString('dailyCommand', guildID=guildID)}\n\n"
                                  f"* $rank\n  * {langMan.getString('rankCommand', guildID=guildID)}\n\n"
                                  f"* $shop list\n  * {langMan.getString('shopListCommand', guildID=guildID)}\n\n"
                                  f"* $shop buy `<{langMan.getString('index', guildID=guildID)}>`\n  * {langMan.getString('shopBuyCommand', guildID=guildID)}\n\n",
                            inline=False)

        case 2:
            embed.title = f'{langMan.getString("page", guildID=guildID)} 2/{numberOfPages}  -  {langMan.getString("gambling", guildID=guildID)}'

            embed.add_field(name="󠁪",
                            value=f"* $double `<{langMan.getString('amount', guildID=guildID)}>`\n  * {langMan.getString('doubleCommand', guildID=guildID)}\n\n"
                                  f"* $coinflip\n  * {langMan.getString('coinflipCommand', guildID=guildID)}\n\n"
                                  f"* $roll `<{langMan.getString('dice', guildID=guildID)}>`\n  * {langMan.getString('rollCommand', guildID=guildID)}\n\n",
                            inline=False)

        case 3:
            embed.title = f'{langMan.getString("page", guildID=guildID)} 3/{numberOfPages}  -  {langMan.getString("nsfw", guildID=guildID)}'

            embed.add_field(name="󠁪",
                            value=f"* $e621 `<{langMan.getString('tags', guildID=guildID)}>`\n  * {langMan.getString('e621Command', guildID=guildID)}\n\n",
                            inline=False)

        case 4:

            embed.title = f'{langMan.getString("page", guildID=guildID)} 4/{numberOfPages}  -  {langMan.getString("roulette", guildID=guildID)}'

            embed.add_field(name="󠁪",
                    value=f"* $ru join\n  * {langMan.getString('ruJoinHelp', guildID=guildID)}\n\n"
                          f"* $ru leave\n  * {langMan.getString('ruLeaveHelp', guildID=guildID)}\n\n"
                          f"* $ru start\n  * {langMan.getString('ruStartHelp', guildID=guildID)}\n\n"
                          f"* $ru shoot `<{langMan.getString('user', guildID=guildID)}>`\n  * {langMan.getString('ruShootHelp', guildID=guildID)}\n\n"
                          f"* $ru shootme\n  * {langMan.getString('ruShootmeHelp', guildID=guildID)}\n\n"
                          f"* $ru bet `<{langMan.getString('amount', guildID=guildID)}>`\n  * {langMan.getString('ruBetHelp', guildID=guildID)}\n\n"
                          f"* $ru wins `<{langMan.getString('user', guildID=guildID)}>`\n  * {langMan.getString('ruWinsHelp', guildID=guildID)}\n\n",
                    inline=False)


        case 5:

            embed.title = f'{langMan.getString("page", guildID=guildID)} 5/5  -  {langMan.getString("admin", guildID=guildID)}'

            embed.add_field(name="󠁪",
                            value=f"* $coinName `<{langMan.getString('name', guildID=guildID)}>`\n  * {langMan.getString('coinNameCommand', guildID=guildID)}\n\n"
                                  f"* $coinSymbol `<{langMan.getString('symbol', guildID=guildID)}>`\n  * {langMan.getString('coinSymbolCommand', guildID=guildID)}\n\n"
                                  f"* $dailyRange `<{langMan.getString('firstValue', guildID=guildID)}>` `<{langMan.getString('secondValue', guildID=guildID)}>`\n  * {langMan.getString('dailyRangeCommand', guildID=guildID)}\n\n"
                                  f"* $setLang `<{langMan.getString('lang', guildID=guildID)}>`\n  * {langMan.getString('setLangCommand', guildID=guildID)}\n\n"
                                  f"* $addShopRole `<{langMan.getString('role', guildID=guildID)}>` `<{langMan.getString('price', guildID=guildID)}>`\n  * {langMan.getString('addShopRoleCommand', guildID=guildID)}\n\n"
                                  f"* $removeShopRole `<{langMan.getString('role', guildID=guildID)}>`\n  * {langMan.getString('removeShopRoleCommand', guildID=guildID)}\n\n",
                            inline=False)

    if pagina <= 0 or pagina > numberOfPages:
        await ctx.send(f":grey_question:｜{langMan.getString('invalidPage', guildID=guildID)}")
        return

    await ctx.send(embed=embed)
client.add_command(ayuda)


async def shutdown():
    print('Apagando...')
    await client.close()

async def main():
    try:
        async with client:
            await client.start(token, reconnect=True)

    except (KeyboardInterrupt, BaseException):
        await shutdown()


if __name__ == '__main__':
    client.run(token)
