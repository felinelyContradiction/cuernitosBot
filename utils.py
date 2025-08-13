
import discord

class customException(Exception):
    pass

def convert_mention_to_id(mention):
    return int(mention[1:][:len(mention)-2].replace("@","").replace("!",""))

def getAuthor(ctx):
    return ctx.message.author

def isOwnerFromInteraction(interaction: discord.Interaction):
    if interaction.user == interaction.guild.owner:
        return True
    return False

def isAdminFromInteraction(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        return True
    return False

def isOwner(ctx):
    if getAuthor(ctx) == ctx.guild.owner:
        return True

    return False

def isAdmin(ctx):
    if getAuthor(ctx).guild_permissions.administrator:
        return True
    return False