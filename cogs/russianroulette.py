import asyncio

from discord.ext import commands, tasks
from random import choice, randint
import discord

from utils import *
from economy import *
from config import *
from functions import checkData

from lang.langManager import langMan


class russianRoulette(commands.Cog):
    def __init__(self, client=None):
        self.client = client

        self.chambersSize: int = 6
        self.bulletAmount: int = 1

        self.matchData: Dict = {}

        self.spinEnabled: bool = False
        self.randomPlayerStart: bool = True

        self.minPlayers = 2

        self.delayBetweenMessages = 1.50

        self.cancelTimeAdvert = 60

        # Cancel Timer
        self.cancelTimer.start()

    @tasks.loop(seconds=1)
    async def cancelTimer(self):

        try:
            for guild in self.matchData:

                if self.matchData[guild]['timeLeftToCancel'] <= 0:
                    return

                self.matchData[guild]['timeLeftToCancel'] -= 1

                if self.matchData[guild]['timeLeftToCancel'] == self.cancelTimeAdvert:
                    await self.matchData[guild]['channel'].send(
                        f'La partida de ruleta rusa se cancelará en {self.matchData[guild]["timeLeftToCancel"]} segundos')

                if self.matchData[guild]['timeLeftToCancel'] <= 1:
                    await self.matchData[guild]['channel'].send(
                        f'La partida de ruleta rusa fue cancelada.')

                    del self.matchData[guild]
        except:
            pass

    def addGuildData(self, guild):

        if self.matchData.get(str(guild.id), False):
            return

        self.matchData[str(guild.id)] = {}

        self.matchData[str(guild.id)]['chambers'] = []
        self.matchData[str(guild.id)]['players'] = []
        self.matchData[str(guild.id)]['curChamber'] = 0
        self.matchData[str(guild.id)]['curPlayer'] = 0
        self.matchData[str(guild.id)]['jackpot'] = 0
        self.matchData[str(guild.id)]['playing'] = False
        self.matchData[str(guild.id)]['channel'] = None
        self.matchData[str(guild.id)]['timeLeftToCancel'] = 0

    def fillChambers(self, guild):
        self.matchData[str(guild.id)]['chambers'] = []

        bulletsLeft = self.bulletAmount

        for slot in range(0, self.chambersSize):
            self.matchData[str(guild.id)]['chambers'].append(False)

        while bulletsLeft > 0:

            choosenIndex = randint(0, len(self.matchData[str(guild.id)]['chambers']) - 1)

            if not self.matchData[str(guild.id)]['chambers'][choosenIndex]:
                self.matchData[str(guild.id)]['chambers'][choosenIndex] = True
                bulletsLeft -= 1

    def clampTurnPosition(self, guild):
        if self.matchData[str(guild.id)]['curPlayer'] > len(self.matchData[str(guild.id)]['players']) - 1:
            self.matchData[str(guild.id)]['curPlayer'] = 0

    def clampChamberPosition(self, guild):
        if self.matchData[str(guild.id)]['curChamber'] > len(self.matchData[str(guild.id)]['chambers']) - 1:
            self.matchData[str(guild.id)]['curChamber'] = 0

    def hasPlayerAlreadyJoined(self, ctx: discord.ext.commands, user: discord.Member):

        guild = ctx.message.author.guild

        if user in self.matchData[str(guild.id)]['players']:
            return True

        return False

    async def join(self, ctx: discord.ext.commands):

        guild = ctx.message.author.guild

        if self.hasPlayerAlreadyJoined(ctx, getAuthor(ctx)):
            return

        if self.matchData[str(guild.id)]['playing']:
            await ctx.send(f":gun:｜{langMan.getString('ruAlreadyStarted', guildID=guild.id)}")
            return

        self.matchData[str(guild.id)]['players'].append(getAuthor(ctx))

        await ctx.send(f":gun:｜{langMan.getString('ruJoin', guildID=guild.id, member=getAuthor(ctx))}")

        self.matchData[str(guild.id)]['channel'] = ctx.channel
        self.matchData[str(guild.id)]['timeLeftToCancel'] = 180

    async def leave(self, ctx: discord.ext.commands):

        guild = ctx.message.author.guild

        if not self.hasPlayerAlreadyJoined(ctx, getAuthor(ctx)):
            return

        self.matchData[str(guild.id)]['players'].remove(getAuthor(ctx))

        if not self.matchData[str(guild.id)]['players']:
            del self.matchData[str(guild.id)]

        await ctx.send(f":gun:｜{langMan.getString('ruLeave', guildID=guild.id, member=getAuthor(ctx))}")

    async def start(self, ctx: discord.ext.commands):

        guild = ctx.message.author.guild

        if self.matchData[str(guild.id)]['playing']:
            await ctx.send(f":grey_question:｜{langMan.getString('ruAlreadyStarted', guildID=guild.id)}")
            return

        if not self.hasPlayerAlreadyJoined(ctx, getAuthor(ctx)):
            await ctx.send(
                f":grey_question:｜{langMan.getString('ruNotInGame', guildID=guild.id, member=getAuthor(ctx))}")
            return

        if not len(self.matchData[str(guild.id)]['players']) >= self.minPlayers:
            await ctx.send(f":grey_question:｜{langMan.getString('ruNotEnoughPlayers', guildID=guild.id)}")
            return

        self.matchData[str(guild.id)]['playing'] = True
        self.fillChambers(guild)
        await ctx.send(f":gun:｜{langMan.getString('ruStart', guildID=guild.id)}")

        await asyncio.sleep(self.delayBetweenMessages)

        if self.randomPlayerStart:
            self.matchData[str(guild.id)]['curPlayer'] = randint(0, len(self.matchData[str(guild.id)]['players']) - 1)

        await ctx.send(
            f":gun:｜{langMan.getString('ruYourTurn', guildID=guild.id, extra1=self.matchData[str(guild.id)]['players'][self.matchData[str(guild.id)]['curPlayer']].display_name)}")

        self.matchData[str(guild.id)]['timeLeftToCancel'] = 600

    async def endGame(self, ctx, guild):

        winner = self.matchData[str(guild.id)]['players'][0]
        setUserRuWins(getUserRuWins(winner) + 1, winner)

        await ctx.send(
            f":gun:｜{langMan.getString('ruGameOver', guildID=guild.id, extra1=winner.display_name, extra2=getUserRuWins(winner))}")

        if self.matchData[str(guild.id)]['jackpot'] > 0:
            increaseUserMoney(self.matchData[str(guild.id)]['jackpot'], winner)
            await ctx.send(
                f":gun:｜{langMan.getString('ruBetWinner', guildID=guild.id, member=winner, extra1=self.matchData[str(guild.id)]['jackpot'])}")

        del self.matchData[str(guild.id)]

    def isGameOver(self, guild):
        if len(self.matchData[str(guild.id)]['players']) <= 1:
            return True

        return False

    def eliminatePlayer(self, guild, player):
        self.matchData[str(guild.id)]['players'].remove(player)
        self.fillChambers(guild)

    def isPlayerTurn(self, ctx, guild):

        if self.matchData[str(guild.id)]['players'][self.matchData[str(guild.id)]['curPlayer']] == getAuthor(ctx):
            return True

        return False

    async def nextTurn(self, ctx, guild):

        self.moveToNextChamber(guild)

        self.matchData[str(guild.id)]['curPlayer'] += 1
        self.clampTurnPosition(guild)

        player = self.matchData[str(guild.id)]['players'][self.matchData[str(guild.id)]['curPlayer']]

        await ctx.send(f":gun:｜{langMan.getString('ruYourTurn', guildID=guild.id, extra1=player.display_name)}")

    def moveToNextChamber(self, guild):

        self.matchData[str(guild.id)]['curChamber'] += 1
        self.clampChamberPosition(guild)

    def isBulletInCurrentChamber(self, guild):

        if self.matchData[str(guild.id)]['chambers'][self.matchData[str(guild.id)]['curChamber']]:
            return True

        return False

    async def checks(self, ctx, guild):

        if not self.matchData[str(guild.id)]['playing']:
            await ctx.send(f":grey_question:｜{langMan.getString('ruNoGame', guildID=guild.id)}")
            return False

        if not self.hasPlayerAlreadyJoined(ctx, getAuthor(ctx)):
            await ctx.send(f":grey_question:｜{langMan.getString('ruNotInGame', guildID=guild.id)}")
            return False

        if not self.isPlayerTurn(ctx, guild):
            await ctx.send(
                f":grey_question:｜{langMan.getString('ruNotYourTurn', guildID=guild.id, extra1=getAuthor(ctx).display_name)}")
            return False

        return True

    async def shoot(self, ctx: discord.ext.commands, user: discord.Member):

        guild = ctx.message.author.guild

        if not await self.checks(ctx, guild):
            return

        if not self.hasPlayerAlreadyJoined(ctx, user):
            await ctx.send(f":grey_question:｜{langMan.getString('ruUserIsNotPlaying', guildID=guild.id, member=user)}")
            return

        if user == getAuthor(ctx):
            await ctx.send(f":grey_question:｜{langMan.getString('notPossible', guildID=guild.id)}")
            return

        if self.isBulletInCurrentChamber(guild):
            await ctx.send(
                f":gun:｜{langMan.getString('ruShootSuccess', guildID=guild.id, extra1=getAuthor(ctx).display_name, extra2=user.display_name)}")
            self.eliminatePlayer(guild, user)
        else:
            await ctx.send(
                f":gun:｜{langMan.getString('ruShootFail', guildID=guild.id, extra1=getAuthor(ctx).display_name, extra2=user.display_name)}")

            await asyncio.sleep(self.delayBetweenMessages)

            self.moveToNextChamber(guild)

            if self.isBulletInCurrentChamber(guild):
                await ctx.send(
                    f":gun:｜{langMan.getString('ruShootYourselfFail', guildID=guild.id, extra1=getAuthor(ctx).display_name)}")
                self.eliminatePlayer(guild, getAuthor(ctx))
            else:
                await ctx.send(
                    f":gun:｜{langMan.getString('ruShootYourselfSuccess', guildID=guild.id, extra1=getAuthor(ctx).display_name)}")

        await asyncio.sleep(self.delayBetweenMessages)

        if self.isGameOver(guild):
            await self.endGame(ctx, guild)
        else:
            await self.nextTurn(ctx, guild)

    async def selfShoot(self, ctx: discord.ext.commands):

        guild = ctx.message.author.guild

        if not await self.checks(ctx, guild):
            return

        if self.isBulletInCurrentChamber(guild):
            await ctx.send(
                f":gun:｜{langMan.getString('ruShootYourselfFail', guildID=guild.id, extra1=getAuthor(ctx).display_name)}")
            self.eliminatePlayer(guild, getAuthor(ctx))
        else:
            await ctx.send(
                f":gun:｜{langMan.getString('ruShootYourselfSuccess', guildID=guild.id, extra1=getAuthor(ctx).display_name)}")

        await asyncio.sleep(self.delayBetweenMessages)

        if self.isGameOver(guild):
            await self.endGame(ctx, guild)
        else:
            await self.nextTurn(ctx, guild)

    async def spin(self, ctx: discord.ext.commands):

        guild = ctx.message.author.guild

        if not self.checks(ctx, guild):
            return

    async def bet(self, ctx: discord.ext.commands, amount: int):

        guild = ctx.message.author.guild

        if self.matchData[str(guild.id)]['playing']:
            await ctx.send(f":grey_question:｜{langMan.getString('ruCantBet', guildID=guild.id, member=getAuthor(ctx))}")
            return False

        if not self.hasPlayerAlreadyJoined(ctx, getAuthor(ctx)):
            await ctx.send(
                f":grey_question:｜{langMan.getString('ruNotInGame', guildID=guild.id, member=getAuthor(ctx))}")
            return False

        if not isinstance(amount, int):
            await ctx.send(f":grey_question:｜{langMan.getString('invalidAmount', guildID=guild.id)}")
            return

        if getUserMoney(getAuthor(ctx)) < amount:
            await ctx.send(f":grey_question:｜{langMan.getString('noMoney', guildID=guild.id)}")
            return

        self.matchData[str(guild.id)]['jackpot'] += amount
        decreaseUserMoney(amount, getAuthor(ctx))

        await ctx.send(
            f":gun:｜{langMan.getString('ruBetPlaced', guildID=guild.id, member=getAuthor(ctx), extra1=amount, extra2=self.matchData[str(guild.id)]['jackpot'])}")

    async def wins(self, ctx: discord.ext.commands, user: discord.Member = None):

        guild = ctx.message.author.guild

        if user is None:
            user = getAuthor(ctx)

        await ctx.send(
            f":gun:｜{langMan.getString('ruWins', guildID=guild.id, member=user, extra1=getUserRuWins(user))}")

    @commands.command(aliases=['ru', 'rr'])
    async def roulette(self, ctx: discord.ext.commands, command: str = 'none', extra=None):

        guild = ctx.message.author.guild

        self.addGuildData(guild)

        user = None
        try:
            user = ctx.guild.get_member(convert_mention_to_id(extra))
        except:
            pass

        if user != None:
            extra = user

        match command.lower():

            case 'none':
                await ctx.send(f":gun:｜{langMan.getString('ruNoAction', guildID=guild.id)}")

            case 'join':
                await self.join(ctx)

            case 'leave':
                await self.leave(ctx)

            case 'shoot':
                await self.shoot(ctx, extra)

            case 'shootme':
                await self.selfShoot(ctx)

            case 'start':
                await self.start(ctx)

            case 'bet':
                await self.bet(ctx, int(extra))

            case 'wins':
                await self.wins(ctx, extra)


async def setup(client):
    await client.add_cog(russianRoulette(client))
