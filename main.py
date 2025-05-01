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

cogs = ['economyCommands', 'e621', 'gambling', 'russianRoulette', 'admin', 'fun']
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
async def statusUpdate():
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

    statusUpdate.start()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{choice(possibleStatus)}"))

class Button(discord.ui.View):
    def __init__(self, guildID, message):
        super().__init__()

        self.guildID = guildID
        self.message = message


    @discord.ui.button(emoji='🪙', style=discord.ButtonStyle.blurple)
    async def economy(self, interaction: discord.Interaction, button: discord.ui.button):

        embed = discord.Embed()
        embed.title = f'{langMan.getString("economy", guildID=self.guildID)}'

        embed.add_field(name="󠁪",
                        value=f"* $wallet `<{langMan.getString('user', guildID=self.guildID)}>`\n  * {langMan.getString('walletCommand', guildID=self.guildID)}\n\n"
                              f"* $give `<{langMan.getString('amount', guildID=self.guildID)}>` `<{langMan.getString('users', guildID=self.guildID)}>`\n  * {langMan.getString('giveCommand', guildID=self.guildID)}\n\n"
                              f"* $daily\n  * {langMan.getString('dailyCommand', guildID=self.guildID)}\n\n"
                              f"* $rank\n  * {langMan.getString('rankCommand', guildID=self.guildID)}\n\n"
                              f"* $shop list\n  * {langMan.getString('shopListCommand', guildID=self.guildID)}\n\n"
                              f"* $shop buy `<{langMan.getString('index', guildID=self.guildID)}>`\n  * {langMan.getString('shopBuyCommand', guildID=self.guildID)}\n\n",
                        inline=False)

        await self.message.edit(embed=embed)

        await interaction.response.defer()

    @discord.ui.button(emoji='🎰', style=discord.ButtonStyle.blurple)
    async def gambling(self, interaction: discord.Interaction, button: discord.ui.button):

        embed = discord.Embed()
        embed.title = f'{langMan.getString("gambling", guildID=self.guildID)}'

        embed.add_field(name="󠁪",
                        value=f"* $double `<{langMan.getString('amount', guildID=self.guildID)}>`\n  * {langMan.getString('doubleCommand', guildID=self.guildID)}\n\n"
                              f"* $coinflip\n  * {langMan.getString('coinflipCommand', guildID=self.guildID)}\n\n"
                              f"* $roll `<{langMan.getString('dice', guildID=self.guildID)}>`\n  * {langMan.getString('rollCommand', guildID=self.guildID)}\n\n",
                        inline=False)

        await self.message.edit(embed=embed)

        await interaction.response.defer()

    @discord.ui.button(emoji='🔞', style=discord.ButtonStyle.blurple)
    async def NSFW(self, interaction: discord.Interaction, button: discord.ui.button):

        embed = discord.Embed()
        embed.title = f'{langMan.getString("nsfw", guildID=self.guildID)}'

        embed.add_field(name="󠁪",
                        value=f"* $e621 `<{langMan.getString('tags', guildID=self.guildID)}>`\n  * {langMan.getString('e621Command', guildID=self.guildID)}\n\n",
                        inline=False)

        await self.message.edit(embed=embed)

        await interaction.response.defer()

    @discord.ui.button(emoji='🔫', style=discord.ButtonStyle.blurple)
    async def roulette(self, interaction: discord.Interaction, button: discord.ui.button):

        embed = discord.Embed()
        embed.title = f'{langMan.getString("roulette", guildID=self.guildID)}'

        embed.add_field(name="󠁪",
                        value=f"* $ru join\n  * {langMan.getString('ruJoinHelp', guildID=self.guildID)}\n\n"
                              f"* $ru leave\n  * {langMan.getString('ruLeaveHelp', guildID=self.guildID)}\n\n"
                              f"* $ru start\n  * {langMan.getString('ruStartHelp', guildID=self.guildID)}\n\n"
                              f"* $ru shoot `<{langMan.getString('user', guildID=self.guildID)}>`\n  * {langMan.getString('ruShootHelp', guildID=self.guildID)}\n\n"
                              f"* $ru shootme\n  * {langMan.getString('ruShootmeHelp', guildID=self.guildID)}\n\n"
                              f"* $ru bet `<{langMan.getString('amount', guildID=self.guildID)}>`\n  * {langMan.getString('ruBetHelp', guildID=self.guildID)}\n\n"
                              f"* $ru wins `<{langMan.getString('user', guildID=self.guildID)}>`\n  * {langMan.getString('ruWinsHelp', guildID=self.guildID)}\n\n",
                        inline=False)


        await self.message.edit(embed=embed)

        await interaction.response.defer()

    @discord.ui.button(emoji='✉️', style=discord.ButtonStyle.blurple)
    async def tag(self, interaction: discord.Interaction, button: discord.ui.button):

        embed = discord.Embed()
        embed.title = f'{langMan.getString("tagBig", guildID=self.guildID)}'

        embed.add_field(name="󠁪",
                        value=
                        f"* $tag add `<{langMan.getString('name', guildID=self.guildID)}>` `<{langMan.getString('content', guildID=self.guildID)}>`\n  * {langMan.getString('tagAddHelp', guildID=self.guildID)}\n\n"
                        f"* $tag remove `<{langMan.getString('tag', guildID=self.guildID)}>`\n  * {langMan.getString('tagRemoveHelp', guildID=self.guildID)}\n\n"
                        f"* $tag local\n  * {langMan.getString('tagLocalHelp', guildID=self.guildID)}\n\n"
                        f"* $tag global\n  * {langMan.getString('tagGlobalHelp', guildID=self.guildID)}\n\n"
                        f"* $tag list `<{langMan.getString('user', guildID=self.guildID)}>`\n  * {langMan.getString('tagListHelp', guildID=self.guildID)}\n\n",
                        inline=False)

        await self.message.edit(embed=embed)

        await interaction.response.defer()

    @discord.ui.button(emoji='🖥️', style=discord.ButtonStyle.blurple)
    async def admin(self, interaction: discord.Interaction, button: discord.ui.button):

        embed = discord.Embed()
        embed.title = f'{langMan.getString("admin", guildID=self.guildID)}'

        embed.add_field(name="󠁪",
                        value=f"* $coinName `<{langMan.getString('name', guildID=self.guildID)}>`\n  * {langMan.getString('coinNameCommand', guildID=self.guildID)}\n\n"
                              f"* $coinSymbol `<{langMan.getString('symbol', guildID=self.guildID)}>`\n  * {langMan.getString('coinSymbolCommand', guildID=self.guildID)}\n\n"
                              f"* $dailyRange `<{langMan.getString('firstValue', guildID=self.guildID)}>` `<{langMan.getString('secondValue', guildID=self.guildID)}>`\n  * {langMan.getString('dailyRangeCommand', guildID=self.guildID)}\n\n"
                              f"* $setLang `<{langMan.getString('lang', guildID=self.guildID)}>`\n  * {langMan.getString('setLangCommand', guildID=self.guildID)}\n\n"
                              f"* $addShopRole `<{langMan.getString('role', guildID=self.guildID)}>` `<{langMan.getString('price', guildID=self.guildID)}>`\n  * {langMan.getString('addShopRoleCommand', guildID=self.guildID)}\n\n"
                              f"* $removeShopRole `<{langMan.getString('role', guildID=self.guildID)}>`\n  * {langMan.getString('removeShopRoleCommand', guildID=self.guildID)}\n\n",
                        inline=False)

        await self.message.edit(embed=embed)

        await interaction.response.defer()

@commands.command(aliases=['help', 'comandos'], brief='Muestra la lista de comandos.', description="Muestra la lista de comandos y si le pasas un comando te habla más a fondo de él.", extras={'admin': False})
async def ayuda(ctx: discord.ext.commands, pagina: int = 1):

    author = getAuthor(ctx)
    guildID = ctx.message.author.guild.id

    embed = discord.Embed()
    embed.title = f'{langMan.getString("economy", guildID=guildID)}'

    embed.add_field(name="󠁪",
                    value=f"* $wallet `<{langMan.getString('user', guildID=guildID)}>`\n  * {langMan.getString('walletCommand', guildID=guildID)}\n\n"
                          f"* $give `<{langMan.getString('amount', guildID=guildID)}>` `<{langMan.getString('users', guildID=guildID)}>`\n  * {langMan.getString('giveCommand', guildID=guildID)}\n\n"
                          f"* $daily\n  * {langMan.getString('dailyCommand', guildID=guildID)}\n\n"
                          f"* $rank\n  * {langMan.getString('rankCommand', guildID=guildID)}\n\n"
                          f"* $shop list\n  * {langMan.getString('shopListCommand', guildID=guildID)}\n\n"
                          f"* $shop buy `<{langMan.getString('index', guildID=guildID)}>`\n  * {langMan.getString('shopBuyCommand', guildID=guildID)}\n\n",
                    inline=False)

    message = await ctx.send(embed=embed)

    '''
    numberOfPages = 6

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

            embed.title = f'{langMan.getString("page", guildID=guildID)} 5/{numberOfPages}  -  {langMan.getString("tag", guildID=guildID)}'

            embed.add_field(name="󠁪",
                    value=
                          f"* $tag add `<{langMan.getString('name', guildID=guildID)}>` `<{langMan.getString('content', guildID=guildID)}>`\n  * {langMan.getString('tagAddHelp', guildID=guildID)}\n\n"
                          f"* $tag remove `<{langMan.getString('tag', guildID=guildID)}>`\n  * {langMan.getString('tagRemoveHelp', guildID=guildID)}\n\n"
                          f"* $tag local\n  * {langMan.getString('tagLocalHelp', guildID=guildID)}\n\n"
                          f"* $tag global\n  * {langMan.getString('tagGlobalHelp', guildID=guildID)}\n\n"
                          f"* $tag list `<{langMan.getString('user', guildID=guildID)}>`\n  * {langMan.getString('tagListHelp', guildID=guildID)}\n\n",

                    inline = False)


        case 6:

            embed.title = f'{langMan.getString("page", guildID=guildID)} 6/{numberOfPages}  -  {langMan.getString("admin", guildID=guildID)}'

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
    '''

    btn = Button(guildID, message)

    await message.edit(embed = embed, content='', view = btn)
client.add_command(ayuda)


async def shutdown():
    print('Shutting down...')
    await client.close()

async def main():
    try:
        async with client:
            await client.start(token, reconnect=True)

    except (KeyboardInterrupt, BaseException):
        await shutdown()


if __name__ == '__main__':
    client.run(token)
