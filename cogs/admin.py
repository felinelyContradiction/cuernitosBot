import discord
from discord.ext import commands
from discord import app_commands
from discord import ui

from random import choice


from utils import *
from config import *
from functions import checkData

from lang.langManager import langMan

class languageDropView(ui.View):
    def __init__(self, guildID):
        super().__init__(timeout=30)  # Timeout in seconds

        self.guildID = guildID

        self.select = ui.Select(
            placeholder="Select an option",
            min_values=1,
            max_values=1
        )

        for lang in langMan.availableLanguages:
            self.select.add_option(
                label=langMan.getLangFullname(lang),
                value=lang.upper(),
            )

        self.select.callback = self.on_select
        self.add_item(self.select)

    async def on_select(self, interaction: discord.Interaction):

        selected_value = self.select.values[0]

        setServerLang(selected_value.lower(), self.guildID)
        await interaction.response.send_message(f":white_check_mark:｜{langMan.getString('langChange', guildID=self.guildID)}")

class admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="set_coin_name", description="Sets a new name to represent the guild's balance.")
    @app_commands.describe(new_name="Name to be used")
    async def set_coin_name(self, interaction: discord.Interaction, new_name: str):

        guildID = interaction.guild_id

        checkData(guildID)

        if (not isAdminFromInteraction(interaction) and not isOwnerFromInteraction(interaction)):
            await interaction.response.send_message(f":no_entry_sign:｜{langMan.getString('noAdminPrivileges', guildID=guildID)}")
            return

        setCoinName(new_name, guildID)
        await interaction.response.send_message(f":white_check_mark:｜{langMan.getString('newCoinNameSuccess', guildID=guildID, extra1=new_name)}")

    @app_commands.command(name="set_coin_symbol", description="Sets a new symbol to represent the guild's balance.")
    @app_commands.describe(new_symbol="Symbol to be used")
    async def set_coin_symbol(self, interaction: discord.Interaction, new_symbol: str):

        guildID = interaction.guild_id

        checkData(guildID)

        if (not isAdminFromInteraction(interaction) and not isOwnerFromInteraction(interaction)):
            await interaction.response.send_message(f":no_entry_sign:｜{langMan.getString('noAdminPrivileges', guildID=guildID)}")
            return

        setCoinName(new_symbol, guildID)
        await interaction.response.send_message(f":white_check_mark:｜{langMan.getString('newCoinNameSuccess', guildID=guildID, extra1=new_symbol)}")

    @app_commands.command(name="set_daily_range", description="Sets a new range for the daily rewards on this guild.")
    @app_commands.describe(first_value="First value", second_value='Second value')
    async def set_daily_range(self, interaction: discord.Interaction, first_value: int, second_value: int):

        guildID = interaction.guild_id

        checkData(guildID)

        if (not isAdminFromInteraction(interaction) and not isOwnerFromInteraction(interaction)):
            await interaction.response.send_message(f":no_entry_sign:｜{langMan.getString('noAdminPrivileges', guildID=guildID)}")
            return

        if first_value <= 0 or second_value <= 0:
            await interaction.response.send_message(f":grey_question:｜{langMan.getString('dailyValuesBelowZero', guildID=guildID)}")
            return

        if first_value >= second_value:
            await interaction.response.send_message(f":grey_question:｜{langMan.getString('firstDailyValueBigger', guildID=guildID)}")
            return

        if second_value <= first_value:
            await interaction.response.send_message(f":grey_question:｜{langMan.getString('secondDailyValueSmaller', guildID=guildID)}")
            return

        setDailyRange((first_value, second_value), guildID)
        await interaction.response.send_message(f":white_check_mark:｜{langMan.getString('newDailyRangeSuccess', guildID=guildID, extra1=first_value, extra2=second_value)}")

    @app_commands.command(name="set_language", description="Sets the language of CuernitosBot on this server.")
    async def set_language(self, interaction: discord.Interaction):

        guildID = interaction.guild_id

        if (not isAdminFromInteraction(interaction) and not isOwnerFromInteraction(interaction)):
            await interaction.response.send_message(f":no_entry_sign:｜{langMan.getString('noAdminPrivileges', guildID=guildID)}")
            return

        view = languageDropView(guildID)
        await interaction.response.send_message(f"{langMan.getString('pleaseSelectAnOption', guildID=guildID)}", view=view, ephemeral=True)

    @app_commands.command(name="add_role_to_shop", description="Adds a role to the server shop.")
    @app_commands.describe(role="Role to be added.", price='Price of the role.')
    async def add_role_to_shop(self, interaction: discord.Interaction, role: discord.Role, price: int):
        guildID = interaction.guild_id

        if (not isAdminFromInteraction(interaction) and not isOwnerFromInteraction(interaction)):
            await interaction.response.send_message(f":no_entry_sign:｜{langMan.getString('noAdminPrivileges', guildID=guildID)}")
            return

        if price <= 0:
            await interaction.response.send_message(f":no_entry_sign:｜{langMan.getString('invalidRolePrice', guildID=guildID)}")
            return

        newRoleList = getServerBuyableRoles(guildID)
        newRoleList[role.id] = price
        setServerBuyableRoles(new = newRoleList, guildID = guildID)

        await interaction.response.send_message(f":white_check_mark:｜{langMan.getString('roleAdded', extra1=role.name, extra2=price, guildID=guildID)}")

    @app_commands.command(name="remove_role_from_shop", description="Removes a role from the server shop.")
    @app_commands.describe(role="Role to be removed.")
    async def remove_role_from_shop(self, interaction: discord.Interaction, role: discord.Role):
        guildID = interaction.guild_id

        if (not isAdminFromInteraction(interaction) and not isOwnerFromInteraction(interaction)):
            await interaction.response.send_message(f":no_entry_sign:｜{langMan.getString('noAdminPrivileges', guildID=guildID)}")
            return

        newRoleList = getServerBuyableRoles(guildID)

        if not role.id in newRoleList:
            await interaction.response.send_message(f":no_entry_sign:｜{langMan.getString('roleNotInShop', guildID=guildID)}")
            return

        newRoleList.remove(role.id)
        setServerBuyableRoles(new = newRoleList, guildID = guildID)

        await interaction.response.send_message(f":white_check_mark:｜{langMan.getString('roleRemoved', extra1=role.name, guildID=guildID)}")

async def setup(client):
    await client.add_cog(admin(client))