
from discord.ext import commands
from discord import app_commands
from discord import ui
from discord.utils import get
from random import randint

from utils import *
from economy import *
from config import *
from functions import checkData

from lang.langManager import langMan

class shopDropView(ui.View):
    def __init__(self, guild: discord.guild):
        super().__init__(timeout=30)  # Timeout in seconds


        self.select = ui.Select(
            placeholder="Select an option",
            min_values=1,
            max_values=1
        )

        roles: dict = getServerBuyableRoles(guild.id)

        for role in roles:

            roleObject = guild.get_role(role)
            self.select.add_option(
                label=roleObject.name,
                value=f'{role}|{roles[role]}',
            )

        self.select.callback = self.on_select
        self.add_item(self.select)

    async def on_select(self, interaction: discord.Interaction):
        buyInfo: str = self.select.values[0]

        user = interaction.user
        guild = interaction.guild

        roleID: int = int(buyInfo.split('|')[0])
        rolePrice: int = int(buyInfo.split('|')[1])

        roleObject = guild.get_role(roleID)

        embed = discord.Embed(title=f"", description='', color=user.color)
        embed.set_author(name=user.display_name, icon_url=user.avatar)

        if rolePrice >= getUserMoney(user):
            await interaction.response.send_message(f"{langMan.getString('noMoney', guild.id)}")
            return

        if roleObject in user.roles:
            await interaction.response.send_message(f"{langMan.getString('alreadyHasRole', guild.id)}")
            return

        await user.add_roles(roleObject)
        decreaseUserMoney(rolePrice, user)

        embed.title = f'{langMan.getString("shopAdquired", extra1=roleObject.name, guildID=guild.id)}'

        await interaction.response.send_message(embed=embed)


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

    @app_commands.command(name="balance", description="Returns someone's balance.")
    @app_commands.describe(user="User")
    async def balance(self, interaction: discord.Interaction, user: discord.User):
        guildID = interaction.guild_id

        checkData(guildID)

        userBalance: int = getUserMoney(user)

        await interaction.response.send_message(f":coin:｜{langMan.getString('balanceInfo', member = user, extra1 = userBalance, guildID = guildID)}")

    @app_commands.command(name="transfer", description="Transfer balance to one or more users. (Distribute balance)")
    async def transfer(self, interaction: discord.Interaction,
                       balance: int,
                       user1: discord.User,
                       user2: discord.User = None,
                       user3: discord.User = None,
                       user4: discord.User = None,
                       user5: discord.User = None):

        author = interaction.user
        guildID = interaction.guild_id

        users = [user1, user2, user3, user4, user5]

        if balance <= 0:
            await interaction.response.send_message(f":grey_question:｜{langMan.getString('belowOrEqualToZero', guildID=guildID)}")
            return

        msg: str = ''

        cleanList = []
        for user in users:
            if user is not None:
                cleanList.append(user)

        for index, user in enumerate(cleanList):
            # We divide the balance among the users.
            balanceToBeGiven = int(balance / len(cleanList))
            increaseUserMoney(balanceToBeGiven, user)

            if index >= len(cleanList) - 1:
                msg += f'{user.display_name}'
            else:
                msg += f'{user.display_name}, '

        decreaseUserMoney(balance, author)

        if len(cleanList) > 1:
            await interaction.response.send_message(f":coin:｜{langMan.getString('gaveMoneyMultiple', author, guildID, balance, msg)}")
        else:
            await interaction.response.send_message(f":coin:｜{langMan.getString('gaveMoneySingle', author, guildID, balance, msg)}")

    @app_commands.command(name="daily", description="Claim daily.")
    async def daily(self, interaction: discord.Interaction):

        author = interaction.user
        guildID = interaction.guild_id

        if not canClaimDaily(author):
            await interaction.response.send_message(f":exclamation:｜{langMan.getString('dailyAlreadyClaimed', author, guildID)}")

            if randint(1, 100) < 10:
                await interaction.response.send_message(
                    f'https://cdn.discordapp.com/attachments/545533865809281025/738133197837041704/Screenshot_20200605-185111.png?ex=6651a35c&is=665051dc&hm=4c2d94ee1e68900c93020f8e44b2ec3f0d35f6ce9898e541251b8ff1427b3f58&')
            return

        reward = randint(getDailyRange(guildID)[0], getDailyRange(guildID)[1])

        increaseUserMoney(reward, author)
        setUserLastDailyClaim(datetime.date.today(), author)

        await interaction.response.send_message(f":coin:｜{langMan.getString('dailyClaimed', author, guildID, reward)}")

    @app_commands.command(name="rank", description="Check out the server balance leaderboard.")
    async def rank(self, interaction: discord.Interaction):

        author = interaction.user
        guildID = interaction.guild_id

        users: dict = {}

        embed = discord.Embed(title=f"{langMan.getString('rankingTitle', author, guildID)}", description='', color=interaction.user.color)

        for member in interaction.guild.members:
            if doesUserWalletExists(member):
                users[f'{member.display_name}'] = getUserMoney(member)

                if len(users) > 10:
                    break

        for key, user in enumerate(sorted(users, key=users.get, reverse=True)):
            embed.add_field(name=f'{key + 1} - {user}', value=f'{users[user]}', inline=False)
            embed.add_field(name=f'', value=f'', inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shop", description="Check out the server's role shop.")
    async def shop(self, interaction: discord.Interaction):

        view = shopDropView(interaction.guild)
        await interaction.response.send_message(f"{langMan.getString('pleaseSelectAnOption', guildID=interaction.guild_id)}", view=view, ephemeral=True)

async def setup(client):
    await client.add_cog(economyCommands(client))