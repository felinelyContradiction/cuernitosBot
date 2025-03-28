
from discord.ext import commands
from random import choice, randint, seed
import discord

from utils import *
from economy import *
from config import *
from functions import checkData

from lang.langManager import langMan

class gambling(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['dados'])
    async def roll(self, ctx, diceInfo: str = '2d6'):

        seed()

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        if not 'd' in diceInfo:
            await ctx.send(f':grey_question:｜{langMan.getString("invalidDice", guildID=guildID)}')
            return

        diceInfo: str = diceInfo.split('d')



        dice: int = int(diceInfo[0])
        sides: int = int(diceInfo[1])

        if dice > 100:
            return

        if sides > 100:
            return

        textResult: str = ''

        for i in range(dice):

            rollResult = randint(1, sides)

            if i >= dice - 1:
                textResult = textResult + f'{rollResult}'
            else:
                textResult = textResult + f'{rollResult}, '

        embed = discord.Embed(title=f'> {textResult}', description='', color=ctx.author.color)
        embed.set_author(name=author.display_name, icon_url=author.avatar)

        embed.set_footer(text=f'({dice}d{sides})')

        await ctx.send(embed=embed)

    @commands.command(aliases=['caracruz'])
    async def coinflip(self, ctx):

        seed()

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        chance = randint(1, 100)

        if chance <= 50:
            await ctx.send(f':coin:｜{langMan.getString("coinflipHeads", guildID=guildID)}')
        elif chance > 50:
            await ctx.send(f':coin:｜{langMan.getString("coinflipTails", guildID=guildID)}')

    @commands.command(aliases=['apostar', 'doblar', 'doble', 'gamble'])
    async def double(self, ctx: discord.ext.commands, cantidad=None):

        seed()

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        checkData(guildID)

        if cantidad == None:
            await ctx.send(f':grey_question:｜{langMan.getString("noSpecifiedAmount", guildID=guildID)}')
            return

        try:
            cantidad = int(cantidad)
        except:
            pass

        if not isinstance(cantidad, int):

            if not cantidad.lower() in ['todo', 'all', 'mitad', 'half', 'random', 'aleatorio']:
                await ctx.send(':grey_question:｜La palabra clave ingresada para específicar un monto no existe.')
                return

        if isinstance(cantidad, str):

            if cantidad.lower() == 'todo' or cantidad.lower() == 'all':
                cantidad = getUserMoney(author)
            elif cantidad.lower() == 'mitad' or cantidad.lower() == 'half':
                cantidad = getUserMoney(author) // 2
            elif cantidad.lower() == 'random' or cantidad.lower() == 'aleatorio':
                if getUserMoney(author) > 1:
                    cantidad = randint(1, getUserMoney(author))

        if cantidad <= 0:
            await ctx.send(f':grey_question:｜{langMan.getString("gambleZero", guildID=guildID)}')
            return

        if getUserMoney(author) < cantidad:
            await ctx.send(f':grey_question:｜{langMan.getString("noMoney", guildID=guildID)}')
            return

        chance: int = randint(1, 100)

        if chance <= getGamblingChance(guildID):
            increaseUserMoney(cantidad, author)
            embed = discord.Embed(title='', description='', color=8257405)
            embed.add_field(name=f'{langMan.getString("gambleWon", guildID=guildID)}',
                            value=f'> {langMan.getString("newGambleBalance", guildID=guildID, extra1=getUserMoney(author))}', inline=False)
        else:
            decreaseUserMoney(cantidad, author)
            embed = discord.Embed(title='', description='', color=16743805)
            embed.add_field(name=f'{langMan.getString("gambleLose", guildID=guildID)}',
                            value=f'> {langMan.getString("newGambleBalance", guildID=guildID, extra1=getUserMoney(author))}', inline=False)

        embed.timestamp = datetime.datetime.now()
        embed.set_footer(icon_url="https://files.catbox.moe/lsejxo.png")

        embed.set_author(name=author.display_name, icon_url=author.avatar)

        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(gambling(client))