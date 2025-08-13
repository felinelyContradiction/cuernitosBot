import contextlib

from random import choice

from discord.ext.commands import Greedy

with contextlib.redirect_stdout(None):
    import discord
    from discord.ext import commands, tasks
    from discord import app_commands


from data.TOKEN import discordBotKey
from utils import *
from functions import checkData

from lang.langManager import langMan

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix='$', intents=intents)

client.remove_command('help')

guildCounter = 0
ready = False

cogs = ['economyCommands', 'e621', 'gambling', 'russianRoulette', 'admin', 'tag']


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

    possibleStatus = [f'On {guildCounter} servers!',
                      f'Now with slash commands!',
                      f'Baaah',
                      f'Making gambling addicts one user at the time.',
                      f'But nobody came.',
                      f'Trans rights are human rights.',
                      f'Meow',
                      f'Hello. :3']


@tasks.loop(seconds=120)
async def statusUpdate():
    await client.change_presence(activity=discord.CustomActivity(name=choice(possibleStatus)))


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

    await client.tree.sync()

    guild = discord.Object(id=653492428002820096)
    client.tree.copy_global_to(guild=guild)
    await client.tree.sync(guild=guild)

    updatePossibleStatus()

    statusUpdate.start()
    await client.change_presence(activity=discord.CustomActivity(name=choice(possibleStatus)))


class Button(discord.ui.View):
    def __init__(self, guildID, message):
        super().__init__()

        self.guildID = guildID
        self.message = message

    @discord.ui.button(label='1', style=discord.ButtonStyle.blurple)
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

    @discord.ui.button(label='2', style=discord.ButtonStyle.blurple)
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

    @discord.ui.button(label='3', style=discord.ButtonStyle.blurple)
    async def NSFW(self, interaction: discord.Interaction, button: discord.ui.button):
        embed = discord.Embed()
        embed.title = f'{langMan.getString("nsfw", guildID=self.guildID)}'

        embed.add_field(name="󠁪",
                        value=f"* $e621 `<{langMan.getString('tags', guildID=self.guildID)}>`\n  * {langMan.getString('e621Command', guildID=self.guildID)}\n\n",
                        inline=False)

        await self.message.edit(embed=embed)

        await interaction.response.defer()

    @discord.ui.button(label='4', style=discord.ButtonStyle.blurple)
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

    @discord.ui.button(label='5', style=discord.ButtonStyle.blurple)
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

    @discord.ui.button(label='6', style=discord.ButtonStyle.blurple)
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

@commands.command(aliases=['help', 'comandos'], brief='Muestra la lista de comandos.',
                  description="Muestra la lista de comandos y si le pasas un comando te habla más a fondo de él.",
                  extras={'admin': False})
async def ayuda(ctx: discord.ext.commands):
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

    btn = Button(guildID, message)

    await message.edit(embed=embed, content='', view=btn)
client.add_command(ayuda)

async def shutdown():
    print('Shutting down...')
    await client.close()


async def main():
    try:
        async with client:
            await client.start(discordBotKey, reconnect=True)

    except (KeyboardInterrupt, BaseException):
        await shutdown()


if __name__ == '__main__':
    client.run(discordBotKey)
