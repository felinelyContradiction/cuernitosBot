
from discord.ext import commands
from discord import app_commands

from random import randint

from utils import *
from economy import *
from config import *
from functions import checkData

from lang.langManager import langMan

class gambling(commands.Cog):
    def __init__(self, client):

        self.client = client
        self.maxDice = 30
        self.maxDiceSides = 1000

    @app_commands.command(name="dice", description="Roll some dice.")
    @app_commands.describe(dice="Amount of dice", sides="Sides per die")
    async def roll(self, interaction: discord.Interaction, dice: int = 2, sides: int = 6):

        author = interaction.user

        textResult: str = ''
        totalResult: int = 0
        for i in range(dice):

            rollResult = randint(1, sides)
            totalResult += rollResult

            if i >= dice - 1:
                textResult = textResult + f'{rollResult}'
            else:
                textResult = textResult + f'{rollResult} + '

        if dice > 1:
            textResult = textResult + f' = {totalResult}'

        embed = discord.Embed(title=f'{textResult}', description='', color=author.color)
        embed.set_author(name=author.display_name, icon_url=author.avatar)

        embed.set_footer(text=f'({dice}d{sides})')

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Let the coins decide the fate.")
    async def coinflip(self, interaction: discord.Interaction):

        guildID = interaction.guild_id

        chance = randint(1, 100)

        if chance <= 50:
            await interaction.response.send_message(f':coin:｜{langMan.getString("coinflipHeads", guildID=guildID)}')
        elif chance > 50:
            await interaction.response.send_message(f':coin:｜{langMan.getString("coinflipTails", guildID=guildID)}')

    @app_commands.command(name="double", description="Let's go gambling!! Gamble the balance you have on this guild.")
    @app_commands.describe(amount="Amount to gamble.")
    async def double(self, interaction: discord.Interaction, amount: int):

        author = interaction.user
        guildID = interaction.guild_id

        checkData(guildID)

        if amount <= 0:
            await interaction.response.send_message(f':grey_question:｜{langMan.getString("gambleZero", guildID=guildID)}')
            return

        if getUserMoney(author) < amount:
            await interaction.response.send_message(f':grey_question:｜{langMan.getString("noMoney", guildID=guildID)}')
            return

        chance: int = randint(1, 100)

        if chance <= getGamblingChance(guildID):
            increaseUserMoney(amount, author)
            embed = discord.Embed(title='', description='', color=8257405)
            embed.add_field(name=f'{langMan.getString("gambleWon", guildID=guildID)}',
                            value=f'> {langMan.getString("newGambleBalance", guildID=guildID, extra1=getUserMoney(author))}', inline=False)
        else:
            decreaseUserMoney(amount, author)
            embed = discord.Embed(title='', description='', color=16743805)
            embed.add_field(name=f'{langMan.getString("gambleLose", guildID=guildID)}',
                            value=f'> {langMan.getString("newGambleBalance", guildID=guildID, extra1=getUserMoney(author))}', inline=False)

        embed.timestamp = datetime.datetime.now()
        embed.set_footer(icon_url="https://files.catbox.moe/lsejxo.png")

        embed.set_author(name=author.display_name, icon_url=author.avatar)

        await interaction.response.send_message(embed=embed)

async def setup(client):
    await client.add_cog(gambling(client))