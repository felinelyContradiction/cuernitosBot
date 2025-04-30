import contextlib

from main import client

with contextlib.redirect_stdout(None):
    import discord
    from discord.ext import commands
    import e621py_wrapper as e621
    import json
    from discord.utils import get

from collections import defaultdict

from random import choice, randint

from utils import *
from lang.langManager import langMan


# Tag command stuff

maxTagsPerUser = 10
maxTagNameLength = 30
maxTagContentLength = 125

def getTagsData():
    with open('data/tags.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    return data


def setTagsData(newData):
    with open('data/tags.json', 'w', encoding='utf-8') as file:
        json.dump(newData, file, indent=4)


def getRandomGlobal():
    data = getTagsData()

    result = choice(list(data.keys()))

    return (data, result)


def getRandomLocal(guildID):
    data = getTagsData()

    result = choice(list(data.keys()))
    while True:
        if int(data[result]['server']) == int(guildID):
            break

        result = choice(list(data.keys()))

    return (data, result)


def getTagByName(name):
    data = getTagsData()

    for entry in data:
        if data[entry]['name'] == str(name):
            return data[entry]

    return None


def getTagIndexByName(name):
    data = getTagsData()

    for entry in data:
        if data[entry]['name'] == str(name):
            return entry


def getTagAmountNumber():
    data = getTagsData()

    return len(data)


def getUserTags(userID):
    data = getTagsData()

    results = []

    for entry in data:
        if int(data[entry]['authorID']) == int(userID):
            results.append(data[entry])

    return results

def getUserTagAmount(userID):
    data = getUserTags(userID)

    return len(data)


def getServerTags(serverID):
    data = getTagsData()

    results = []

    for entry in data:
        if int(data[entry]['server']) == int(serverID):
            results.append(data[entry])

    return results


def addTag(ctx, name, content):
    data = getTagsData()

    newData = {}

    for key, entry in enumerate(data):
        newData[key] = data[entry]

    tagData = {'name': f'{name}',
               'author': f'{getAuthor(ctx).name}',
               'authorID': f'{getAuthor(ctx).id}',
               'content': f'{content}',
               'server': f'{ctx.guild.id}'}

    newData[f'{getTagAmountNumber()}'] = tagData

    setTagsData(newData)


def isUserTagOwner(id, name):
    tag = getTagByName(name)

    if int(id) == int(tag["authorID"]):
        return True
    return False


def removeTagByID(id):
    data = getTagsData()

    data.pop(id)

    newData = {}
    for key, entry in enumerate(data):
        newData[key] = data[entry]

    setTagsData(newData)

def removeTag(name: str):
    data = getTagsData()

    data.pop(getTagIndexByName(name))

    newData = {}
    for key, entry in enumerate(data):
        newData[key] = data[entry]

    setTagsData(newData)

class funCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['t'])
    async def tag(self, ctx: commands.Context, command: str = 'local', tagName='', *tagContent: str):

        providedTagName = command
        command = command.lower()

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        if command == 'add':

            if tagName == 'add' or tagName == 'remove' or tagName == 'global' or tagName == 'local' or tagName == 'list':
                await ctx.send(f":no_entry_sign:｜{langMan.getString('tagInvalidName', guildID=guildID)}")
                return

            if tagName == '':
                await ctx.send(f":no_entry_sign:｜{langMan.getString('tagNoName', guildID=guildID)}")
                return

            tag = getTagByName(tagName)

            if tag:
                if isUserTagOwner(author.id, tagName):
                    await ctx.send(f":no_entry_sign:｜{langMan.getString('tagAlreadyExists', guildID=guildID)}")
                    return

            if tag:
                if int(tag['server']) == int(ctx.guild.id):
                    await ctx.send(f":no_entry_sign:｜{langMan.getString('tagAlreadyExitsHere', guildID=guildID)}")
                    return

            if getUserTagAmount(author.id) >= maxTagsPerUser:
                await ctx.send(f":no_entry_sign:｜{langMan.getString('tagLimitReached', guildID=guildID)}")
                return

            if not tagContent and not ctx.message.attachments:
                await ctx.send(f":no_entry_sign:｜{langMan.getString('tagNoContent', guildID=guildID)}")
                return

            if len(tagName) > maxTagNameLength:
                await ctx.send(f":no_entry_sign:｜{langMan.getString('tagNameTooLong', guildID=guildID, extra1=maxTagNameLength)}")
                return

            if len(tagContent) > maxTagContentLength:
                await ctx.send(f":no_entry_sign:｜{langMan.getString('tagContentTooLong', guildID=guildID, extra1=maxTagContentLength)}")
                return

            if '@' in tagContent:
                await ctx.send(f":no_entry_sign:｜{langMan.getString('tagFunny', guildID=guildID, extra1=maxTagContentLength)}")
                return

            content = ''
            for character in tagContent:
                content = content + ' ' + character

            if ctx.message.attachments:
                content = content + '\n' + ctx.message.attachments[0].url

            addTag(ctx, tagName, content)

            await ctx.send(f':envelope:｜{langMan.getString("tagAdded", guildID=guildID, extra1=tagName)}')

            return

        if command == 'remove':
            data = getTagsData()

            possibleResults = []

            for entry in data:
                if data[entry]['name'] == tagName:
                    possibleResults.append([entry, data[entry]])

            for entry in possibleResults:
                if not int(entry[1]['authorID']) == author.id:
                    continue

                removeTagByID(entry[0])
                await ctx.send(f':envelope:｜{langMan.getString("tagRemoved", guildID=guildID, extra1=tagName)}')
                return

            else:
                await ctx.send(f':envelope:｜{langMan.getString("tagNotOwner", guildID=guildID, extra1=tagName)}')
                return

        if command == 'global':
            data = getRandomGlobal()[0]
            result = getRandomGlobal()[1]

            await ctx.send(
                f'> {langMan.getString("tagAuthor", guildID=guildID, extra1=tagName)}: **{data[result]["author"]}**\n> {langMan.getString("tagName", guildID=guildID, extra1=tagName)}: **{data[result]["name"]}**\n\n{data[result]["content"]}')
            return

        if command == 'local':
            data = getRandomLocal(ctx.author.guild.id)[0]
            result = getRandomLocal(ctx.author.guild.id)[1]

            await ctx.send(
                f'> {langMan.getString("tagAuthor", guildID=guildID, extra1=tagName)}: **{data[result]["author"]}**\n> {langMan.getString("tagName", guildID=guildID, extra1=tagName)}: **{data[result]["name"]}**\n\n{data[result]["content"]}')
            return

        if command == 'list':

            if tagName == '':
                userID = author.id
            else:
                userID = tagName
                if '<@' in tagName:
                    userID = int(convert_mention_to_id(tagName))

                userID = int(userID)

            #user = get(client.get_all_members(), id=str(userID))
            user = ctx.guild.get_member(userID)
            #user = await client.fetch_user(userID)

            tagList = getUserTags(userID)
            serverTags = getServerTags(ctx.guild.id)

            if not user:
                await ctx.send(f':envelope:｜{langMan.getString("tagNotOnThisServer", guildID=guildID)}')
                return

            if not tagList:
                await ctx.send(f':envelope:｜{langMan.getString("tagNoUserTags", guildID=guildID)}')
                return

            msg = (f'**{user.display_name}**\n'
                   f'**{getUserTagAmount(userID)}/{maxTagsPerUser}**\n\n')
            takenTags = []

            for tag in tagList:

                for serverTag in serverTags:
                    if tag['name'] == serverTag['name'] and tag['authorID'] != serverTag['authorID']:
                        takenTags.append(serverTag['name'])

                if tag['name'] in takenTags:
                    msg = msg + f'\n* ~~{tag["name"]}~~\n  * **{langMan.getString("tagCurrentlyOcuppied", guildID=guildID)}**'
                    continue

                msg = msg + f'\n* {tag["name"]}'

            await ctx.send(msg)
            return

        data = getTagsData()

        possibleResults = []

        for entry in data:
            if data[entry]['name'] == providedTagName:
                possibleResults.append(data[entry])

        if not possibleResults:
            await ctx.send(f':envelope:｜{langMan.getString("tagNotFound", guildID=guildID)}')
            return

        for entry in possibleResults:
            if int(entry['server']) == int(ctx.guild.id):
                await ctx.send(f'> {langMan.getString("tagAuthor", guildID=guildID, extra1=tagName)}: **{entry["author"]}**\n\n{entry["content"]}')
                return
        else:
            await ctx.send(f'> {langMan.getString("tagAuthor", guildID=guildID, extra1=tagName)}: **{possibleResults[0]["author"]}**\n\n{possibleResults[0]["content"]}')
            return


async def setup(client):
    await client.add_cog(funCommands(client))
