
from discord.ext import commands
from random import choice
import discord

from utils import *
from economy import *
from config import *
from functions import checkData

from lang.langManager import langMan

class admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['nombreMoneda', 'nombremoneda', 'coinname'])
    async def coinName(self, ctx: discord.ext.commands, newName: str = None):

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        checkData(guildID)

        if (not isAdmin(ctx) and not isOwner(ctx)):
            await ctx.send(f":no_entry_sign:｜{langMan.getString('noAdminPrivileges', guildID=guildID)}")
            return

        if not newName:
            await ctx.send(f":grey_question:｜{langMan.getString('noCoinNameSpecified', guildID=guildID)}")
            return

        setCoinName(newName, guildID)
        await ctx.send(f":white_check_mark:｜{langMan.getString('newCoinNameSuccess', guildID=guildID, extra1=newName)}")

    @commands.command(aliases=['simboloMoneda', 'simbolomoneda', 'coinsymbol'])
    async def coinSymbol(self, ctx: discord.ext.commands, newSymbol: str = None):

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        checkData(guildID)

        if (not isAdmin(ctx) and not isOwner(ctx)):
            await ctx.send(f":no_entry_sign:｜{langMan.getString('noAdminPrivileges', guildID=guildID)}")
            return

        if not newSymbol:
            await ctx.send(f":grey_question:｜{langMan.getString('noCoinSymbolSpecified', guildID=guildID)}")
            return

        setCoinSymbol(newSymbol, guildID)
        await ctx.send(f":white_check_mark:｜{langMan.getString('newCoinSymbolSuccess', guildID=guildID, extra1=newSymbol)}")

    @commands.command(aliases=['rangoDiaria', 'rangodiaria', 'dailyrange'])
    async def dailyRange(self, ctx: discord.ext.commands, firstValue: int = None, secondValue: int = None):

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        checkData(guildID)

        if (not isAdmin(ctx) and not isOwner(ctx)):
            await ctx.send(f":no_entry_sign:｜{langMan.getString('noAdminPrivileges', guildID=guildID)}")
            return

        if not isinstance(firstValue, int):
            await ctx.send(f":grey_question:｜{langMan.getString('firstDailyValueInvalid', guildID=guildID)}")
            return

        if not isinstance(secondValue, int):
            await ctx.send(f":grey_question:｜{langMan.getString('secondDailyValueInvalid', guildID=guildID)}")
            return

        if firstValue <= 0 or secondValue <= 0:
            await ctx.send(f":grey_question:｜{langMan.getString('dailyValuesBelowZero', guildID=guildID)}")
            return

        if firstValue >= secondValue:
            await ctx.send(f":grey_question:｜{langMan.getString('firstDailyValueBigger', guildID=guildID)}")
            return

        if secondValue <= firstValue:
            await ctx.send(f":grey_question:｜{langMan.getString('secondDailyValueSmaller', guildID=guildID)}")
            return

        setDailyRange((firstValue, secondValue), guildID)
        await ctx.send(f":white_check_mark:｜{langMan.getString('newDailyRangeSuccess', guildID=guildID, extra1=firstValue, extra2=secondValue)}")

    @commands.command(aliases=['cambiarIdioma', 'cambiaridioma', 'setlang'])
    async def setLang(self, ctx: discord.ext.commands, langIndex = -1):

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        if (not isAdmin(ctx) and not isOwner(ctx)):
            await ctx.send(f":no_entry_sign:｜{langMan.getString('noAdminPrivileges', guildID=guildID)}")
            return

        if langIndex == -1:

            text = f'> {langMan.getString("langList", guildID=guildID)}\n\n'

            for key, lang in enumerate(langMan.availableLanguages):
                text = text + f'* {key} - {langMan.languagesNames[key]}\n'

            await ctx.send(text)
            return

        if langIndex < 0 or langIndex > len(langMan.availableLanguages):
            await ctx.send(f":grey_question:｜{langMan.getString('invalidLang', guildID=guildID)}")
            return

        #if not newLang.lower() in langMan.availableLanguages:

        newLang = langMan.availableLanguages[langIndex]

        setServerLang(newLang, guildID)

        await ctx.send(f":white_check_mark:｜{langMan.getString('langChange', guildID=guildID)}")

    @commands.command(aliases=['addshoprole'])
    async def addShopRole(self, ctx: discord.ext.commands, role: discord.Role = None, price: int = None):

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        if (not isAdmin(ctx) and not isOwner(ctx)):
            await ctx.send(f":no_entry_sign:｜{langMan.getString('noAdminPrivileges', guildID=guildID)}")
            return

        if role is None:
            return

        if price is None:
            return


        newRoleList = getServerBuyableRoles(guildID)

        newRoleList[role.id] = price

        setServerBuyableRoles(new = newRoleList, guildID = guildID)

        await ctx.send(f":white_check_mark:｜{langMan.getString('roleAdded', extra1=role.name, extra2=price, guildID=guildID)}")

    @commands.command(aliases=['removeshoprole'])
    async def removeShopRole(self, ctx: discord.ext.commands, role: discord.Role = None):

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        if (not isAdmin(ctx) and not isOwner(ctx)):
            await ctx.send(f":no_entry_sign:｜{langMan.getString('noAdminPrivileges', guildID=guildID)}")
            return

        if role is None:
            return

        newRoleList = getServerBuyableRoles(guildID)

        if not role.id in newRoleList:
            return

        newRoleList.pop(role.id)

        setServerBuyableRoles(new = newRoleList, guildID = guildID)

        await ctx.send(f":white_check_mark:｜{langMan.getString('roleRemoved', extra1=role.name, guildID=guildID)}")

async def setup(client):
    await client.add_cog(admin(client))