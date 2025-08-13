import contextlib

with contextlib.redirect_stdout(None):
    import json
    import discord
    from discord.ext import commands
    from discord import app_commands
    from discord import ui

from random import choice
import requests
from utils import *
from lang.langManager import langMan


def checkForProfanity(message: str) -> dict:
    response = requests.post(
        'https://vector.profanity.dev',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({'message': message})
    )
    result = response.json()
    return result


# Tag command stuff
maxTagsPerUser = 10
maxTagNameLength = 30
maxTagContentLength = 125
profanityScoreThreshold = .5

reportChannelID = 1398285911279665233  # Devs only

def getReorderedTagList(tagList: dict) -> dict:

    newData: dict = {}
    for index, tagID in enumerate(tagList):
        newData[index] = tagList[tagID]

    return newData

def getTagsData() -> dict:
    with open('data/tags.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    return data


def setTagsData(newData: dict) -> None:
    with open('data/tags.json', 'w', encoding='utf-8') as file:
        json.dump(newData, file, indent=4)


def getRandomGlobalTagID() -> int:
    tagList: dict = getTagsData()

    randGlobalID: int = choice(list(tagList.keys()))

    return randGlobalID


def getRandomLocalTagID(guildID: int) -> int:
    tagList: dict = getTagsData()

    tags = []
    for tagID in tagList:
        tagID: int

        if int(tagList[tagID]['server']) == int(guildID):
            tags.append(tagID)

    if not tags:
        return -1

    randLocalID: int = choice(tags)

    return randLocalID


def getTagByName(name: str):
    tagList: dict = getTagsData()

    for tagID in tagList:
        tagID: int

        if tagList[tagID]['name'] == str(name):
            return tagList[tagID]

    return None


def getTagIndexByName(name: str) -> int:
    tagList: dict = getTagsData()

    for tagID in tagList:
        tagID: int

        if tagList[tagID]['name'] == str(name):
            return tagID


def getTaglistLength() -> int:
    tagList: dict = getTagsData()
    return len(tagList)


def getUserTags(userID: int) -> list:
    tagList: dict = getTagsData()

    userTagsIDList = []

    for tagID in tagList:
        tagID: int

        if int(tagList[tagID]['authorID']) == int(userID):
            userTagsIDList.append(tagList[tagID])

    return userTagsIDList


def getUserTagAmount(userID: int) -> int:
    userTagList: list = getUserTags(userID)

    return len(userTagList)


def getServerTags(serverID: int) -> list:
    tagList: dict = getTagsData()

    serverTagsIDList = []

    for tagID in tagList:
        tagID: int

        if int(tagList[tagID]['server']) == int(serverID):
            serverTagsIDList.append(tagList[tagID])

    return serverTagsIDList


def addTag(user: discord.User, guild: discord.Guild, name: str, content: str) -> None:

    tagList: dict = getTagsData()
    reorderedTagList: dict = getReorderedTagList(tagList)

    tagData = {'name': name,
               'author': user.name,
               'authorID': user.id,
               'content': content,
               'server': guild.id}

    reorderedTagList[getTaglistLength()] = tagData
    setTagsData(reorderedTagList)


def isUserTagOwner(tagID: int, name: str) -> bool:
    tag = getTagByName(name)

    if tagID == int(tag["authorID"]):
        return True
    return False


def deleteTagByID(tagID: int) -> None:
    tagList: dict = getTagsData()

    del tagList[tagID]
    reorderedTagList: dict = getReorderedTagList(tagList)

    setTagsData(reorderedTagList)


def removeTagByName(name: str) -> None:
    tagList: dict = getTagsData()

    del tagList[getTagIndexByName(name)]
    reorderedTagList: dict = getReorderedTagList(tagList)
    setTagsData(reorderedTagList)


def getTagMessage(tagID: int, guildID: int) -> str:
    tagList: dict = getTagsData()

    msg = f'''
    > {langMan.getString("tagAuthor", guildID=guildID)}: **{tagList[tagID]["author"]}**
    > {langMan.getString("tagName", guildID=guildID)}: **{tagList[tagID]["name"]}**
    > Tag ID: **{tagID}**

    {tagList[tagID]["content"]}
    '''

    return msg


def isTagNameTakenLocally(tag: dict, guildID: int) -> bool:
    localTags: list = getServerTags(guildID)

    for localTag in localTags:

        if not tag['name'] == localTag['name']:
            continue

        if not tag['authorID'] != localTag['authorID']:
            continue

        return True

    return False


class Tag(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.reportsChannel = client.get_channel(1398285911279665233)

    @app_commands.command(name="tag_list", description="Returns someone's tag list")
    @app_commands.describe(user="User to retrieve list.")
    async def tag_list(self, interaction: discord.Interaction, user: discord.User):

        guildID = interaction.guild_id

        userTagList: list = getUserTags(user.id)

        if not user:
            await interaction.response.send_message(f':envelope:｜{langMan.getString("tagNotOnThisServer", guildID=guildID)}')
            return

        if not userTagList:
            await interaction.response.send_message(f':envelope:｜{langMan.getString("tagNoUserTags", guildID=guildID)}')
            return

        msg = ''
        takenTags = []
        for tag in userTagList:
            if isTagNameTakenLocally(tag, guildID):
                takenTags.append(tag['name'])

            if tag['name'] in takenTags:
                msg += (f'\n* ~~{tag["name"]}~~'
                        f'\n  * **{langMan.getString("tagCurrentlyOcuppied", guildID=guildID)}**')
                continue

            msg += f'\n* {tag["name"]}'

        embed = discord.Embed(color=user.color)
        embed.add_field(name='', value=msg)
        embed.set_author(name=user.display_name, icon_url=user.avatar)

        embed.set_footer(text=f'{getUserTagAmount(user.id)}/{maxTagsPerUser}')

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tag_random_local", description="Returns a random local tag.")
    async def tag_random_local(self, interaction: discord.Interaction):

        guildID = interaction.guild_id
        tagID = getRandomLocalTagID(guildID)

        if tagID == -1:
            await interaction.response.send_message(f':envelope:｜{langMan.getString("tagNoLocal", guildID=guildID)}')
            return

        await interaction.response.send_message(getTagMessage(tagID=tagID, guildID=guildID))

    @app_commands.command(name="tag_random_global", description="Returns a random global tag.")
    async def tag_random_global(self, interaction: discord.Interaction):

        guildID = interaction.guild_id
        tagID = getRandomGlobalTagID()

        await interaction.response.send_message(getTagMessage(tagID=tagID, guildID=guildID))

    @app_commands.command(name="tag_add", description="Adds a new tag to the server.")
    @app_commands.describe(name="Tag name", content='Tag content')
    async def tag_add(self, interaction: discord.Interaction, name: str, content: str):

        author = interaction.user
        guildID = interaction.guild_id

        tag = getTagByName(name)

        if tag:
            if isUserTagOwner(author.id, name):
                await interaction.response.send_message(
                    f":no_entry_sign:｜{langMan.getString('tagAlreadyExists', guildID=guildID)}")
                return

        if tag:
            if int(tag['server']) == int(guildID):
                await interaction.response.send_message(
                    f":no_entry_sign:｜{langMan.getString('tagAlreadyExitsHere', guildID=guildID)}")
                return

        if getUserTagAmount(author.id) >= maxTagsPerUser:
            await interaction.response.send_message(
                f":no_entry_sign:｜{langMan.getString('tagLimitReached', guildID=guildID)}")
            return

        if len(name) > maxTagNameLength:
            await interaction.response.send_message(
                f":no_entry_sign:｜{langMan.getString('tagNameTooLong', guildID=guildID, extra1=maxTagNameLength)}")
            return

        if len(content) > maxTagContentLength:
            await interaction.response.send_message(
                f":no_entry_sign:｜{langMan.getString('tagContentTooLong', guildID=guildID, extra1=maxTagContentLength)}")
            return

        if '@' in content:
            await interaction.response.send_message(
                f":no_entry_sign:｜{langMan.getString('tagFunny', guildID=guildID, extra1=maxTagContentLength)}")
            return

        nameProfanityValue = checkForProfanity(name)
        contentProfanityValue = checkForProfanity(content)

        if nameProfanityValue['score'] >= profanityScoreThreshold or contentProfanityValue[
            'score'] >= profanityScoreThreshold:
            await interaction.response.send_message(
                f":no_entry_sign:｜{langMan.getString('tagFilter', guildID=guildID, extra1=maxTagContentLength)}")
            return

        addTag(user=interaction.user, guild=interaction.guild, name=name, content=content)

        await interaction.response.send_message(
            f':envelope:｜{langMan.getString("tagAdded", guildID=guildID, extra1=name)}')

    @app_commands.command(name="tag_remove", description="Removes a tag you made on this server.")
    @app_commands.describe(name="Tag name")
    async def tag_remove(self, interaction: discord.Interaction, name: str):

        author = interaction.user
        guildID = interaction.guild_id

        data = getTagsData()
        possibleResults = []

        for entry in data:
            if data[entry]['name'] == name:
                possibleResults.append([entry, data[entry]])

        for entry in possibleResults:
            if not isUserTagOwner(author.id, name):
                continue

            deleteTagByID(entry[0])
            await interaction.response.send_message(
                f':envelope:｜{langMan.getString("tagRemoved", guildID=guildID, extra1=name)}')
            return

        await interaction.response.send_message(
            f':envelope:｜{langMan.getString("tagNotOwner", guildID=guildID, extra1=name)}')

    @app_commands.command(name="tag_report", description="Reports a tag.")
    @app_commands.describe(id="Tag ID")
    async def tag_report(self, interaction: discord.Interaction, id: str):
        data = getTagsData()

        author = interaction.user
        guildID = interaction.guild_id

        if id not in data:
            await interaction.response.send_message(f'{langMan.getString("tagReportInvalid", guildID=guildID)}')
            return

        reportMsg = f'''
**REPORT**

* Reporter
  * {interaction.user.display_name}
  
* Reporter ID
  * {interaction.user.id}

* Reported User
  * {data[id]['author']}
  
* Reported User ID 
  * {data[id]['authorID']}
  
* Server Origin ID 
  * {data[id]['server']}
  
* Tag Name 
  * {data[id]['name']}
  
* Tag ID 
  * {id}
  
* Tag Content
  * `{data[id]['content']}`

'''

        await interaction.response.send_message(f'{langMan.getString("tagReported", guildID=guildID)}')
        await self.reportsChannel.send(reportMsg)

    @app_commands.command(name="tag", description="Search for a tag.")
    @app_commands.describe(name="Tag name")
    async def tag(self, interaction: discord.Interaction, name: str):

        data = getTagsData()
        guildID = interaction.guild_id
        possibleResults = []

        for entry in data:
            if data[entry]['name'] == name:
                possibleResults.append([entry, data[entry]])

        if not possibleResults:
            await interaction.response.send_message(f':envelope:｜{langMan.getString("tagNotFound", guildID=guildID)}')
            return

        for entry in possibleResults:
            if int(entry[1]['server']) == int(guildID):
                await interaction.response.send_message(
                    f'> {langMan.getString("tagAuthor", guildID=guildID, extra1=name)}: **{entry[1]["author"]}**\n> {langMan.getString("tagName", guildID=guildID)}: **{entry[1]["name"]}**\n> Tag ID: **{entry[0]}**\n\n{entry[1]["content"]}')
                return
        else:
            await interaction.response.send_message(
                f'> {langMan.getString("tagAuthor", guildID=guildID, extra1=name)}: **{possibleResults[0][1]["author"]}**\n> {langMan.getString("tagName", guildID=guildID)}: **{possibleResults[0][1]["name"]}**\n> Tag ID: **{possibleResults[0][0]}**\n\n{possibleResults[0][1]["content"]}')


async def setup(client):
    await client.add_cog(Tag(client))
