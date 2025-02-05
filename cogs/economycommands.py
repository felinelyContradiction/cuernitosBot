
from discord.ext import commands
from random import choice, randint
import discord, sys

from utils import *
from economy import *
from config import *
from functions import checkData

from lang.langManager import langMan

class economyCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def migrate(self, ctx: discord.ext.commands):

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        try:
            migrateWalletStructure(author)
        except:
            pass
        print(getWalletInfo(author))

    @commands.command(aliases=['cartera', 'balance', 'billetera'])
    async def wallet(self, ctx: discord.ext.commands, user: discord.Member = None):

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        checkData(guildID)

        member = author
        if user != None:
            member = user

        await ctx.send(f":coin:｜{langMan.getString('balanceInfo', member, guildID)}")

    @commands.command(aliases=['dar'])
    async def give(self, ctx: discord.ext.commands, cantidad=None, members: commands.Greedy[discord.Member] = None):

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        if cantidad == None:
            await ctx.send(f":grey_question:｜{langMan.getString('noSpecifiedAmount', guildID=guildID)}")
            return

        try:
            cantidad = int(cantidad)
        except:
            pass

        if not isinstance(cantidad, int):

            if not cantidad.lower() in ['todo', 'all', 'mitad', 'half']:
                await ctx.send(f":grey_question:｜{langMan.getString('unknownKeyword', guildID=guildID)}")
                return

        if members == None:
            await ctx.send(f":grey_question:｜{langMan.getString('noUserSpecified', guildID=guildID)}")
            return

        if isinstance(cantidad, str):

            if cantidad.lower() == 'todo' or cantidad.lower() == 'all':
                cantidad = getUserMoney(author)
            elif cantidad.lower() == 'mitad' or cantidad.lower() == 'half':
                cantidad = getUserMoney(author) // 2

        users = ''

        if cantidad > getUserMoney(author) or getUserMoney(author) <= 0:
            await ctx.send(f":grey_question:｜{langMan.getString('noMoney', guildID=guildID)}")
            return

        if cantidad <= 0:
            await ctx.send(f":grey_question:｜{langMan.getString('belowOrEqualToZero', guildID=guildID)}")
            return

        for key, user in enumerate(members):
            increaseUserMoney(int(cantidad / len(members)), user)

            if key >= len(members) - 1:
                users = users + f'{user.display_name}'
            else:
                users = users + f'{user.display_name}, '

        decreaseUserMoney(cantidad, author)

        if len(members) > 1:
            await ctx.send(f":coin:｜{langMan.getString('gaveMoneyMultiple', author, guildID, cantidad, users)}")
        else:
            await ctx.send(f":coin:｜{langMan.getString('gaveMoneySingle', author, guildID, cantidad, users)}")

    @commands.command(aliases=['diaria', 'dailies'])
    async def daily(self, ctx: discord.ext.commands):

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        checkData(guildID)

        if not canClaimDaily(author):
            await ctx.send(f":exclamation:｜{langMan.getString('dailyAlreadyClaimed', author, guildID)}")

            if randint(1, 100) < 10:
                await ctx.send(
                    f'https://cdn.discordapp.com/attachments/545533865809281025/738133197837041704/Screenshot_20200605-185111.png?ex=6651a35c&is=665051dc&hm=4c2d94ee1e68900c93020f8e44b2ec3f0d35f6ce9898e541251b8ff1427b3f58&')
            return

        reward = randint(getDailyRange(guildID)[0], getDailyRange(guildID)[1])

        increaseUserMoney(reward, author)
        setUserLastDailyClaim(datetime.date.today(), author)

        await ctx.send(f":coin:｜{langMan.getString('dailyClaimed', author, guildID, reward)}")

    @commands.command()
    async def rank(self, ctx: discord.ext.commands):

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        users: dict = {}

        embed = discord.Embed(title=f"{langMan.getString('rankingTitle', author, guildID)}", description='', color=ctx.author.color)

        for member in ctx.guild.members:
            if doesUserWalletExists(member):
                users[f'{member.display_name}'] = getUserMoney(member)

                if len(users) > 10:
                    break

        for key, user in enumerate(sorted(users, key=users.get, reverse=True)):
            embed.add_field(name=f'{key + 1} - {user}', value=f'{users[user]}', inline=False)

            embed.add_field(name=f'', value=f'', inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def shop(self, ctx: discord.ext.commands, command: str = 'list', selection: int = None):

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        embed = discord.Embed(title=f"", description='', color=ctx.author.color)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)

        match command:
            case 'list':

                embed.title = f'{langMan.getString("roleShop", guildID=guildID)}'

                for key, role in enumerate(getServerBuyableRoles(guildID)):

                    curRole = ctx.guild.get_role(role)

                    if curRole.icon:
                        embed.add_field(name=f'> {key + 1}. {curRole.icon} {curRole.name}', value=f'*{getCoinSymbol(guildID)}{getServerBuyableRoles(guildID)[role]}*', inline=False)
                    else:
                        embed.add_field(name=f'> {key + 1}. {curRole.name}', value=f'*{getCoinSymbol(guildID)}{getServerBuyableRoles(guildID)[role]}*', inline=False)

            case 'buy':

                for key, role in enumerate(getServerBuyableRoles(guildID)):
                    if selection - 1 == key:
                        curRole = ctx.guild.get_role(role)
                        price = getServerBuyableRoles(guildID)[role]
                        break
                else:
                    await ctx.send(f"{langMan.getString('invalidIndex', guildID)}")
                    return

                if price >= getUserMoney(author):
                    await ctx.send(f"{langMan.getString('noMoney', guildID)}")
                    return

                if curRole in author.roles:
                    await ctx.send(f"{langMan.getString('alreadyHasRole', guildID)}")
                    return

                try:
                    await author.add_roles(curRole)
                    decreaseUserMoney(price, author)

                    embed.title = f'{langMan.getString("shopAdquired", extra1=curRole.name, guildID=guildID)}'
                except:
                    pass

        await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(economyCommands(client))