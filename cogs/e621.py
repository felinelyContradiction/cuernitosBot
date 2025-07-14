import contextlib

with contextlib.redirect_stdout(None):
    import discord
    from discord.ext import commands
    import e621py_wrapper as e621

from random import choice, randint

from utils import *
from lang.langManager import langMan

limit = 100

class Button(discord.ui.View):
    def __init__(self, message, index, posts, guildID, ctx):
        super().__init__()

        self.message = message
        self.index = index
        self.posts = posts
        self.guildID = guildID
        self.context = ctx

    @discord.ui.button(label=f'<<<', style=discord.ButtonStyle.blurple)
    async def goBackTen(self, interaction: discord.Interaction, button: discord.ui.button):

        if interaction.user != self.context.author:
            await interaction.response.defer()
            return

        self.index -= 10

        if self.index < 0:
            self.index = len(self.posts) - abs(self.index)

        await self.message.edit(embed=getEmbed(self.context, self.guildID, self.posts, self.index))

        await interaction.response.defer()

    @discord.ui.button(label=f'<', style=discord.ButtonStyle.blurple)
    async def goBack(self, interaction: discord.Interaction, button: discord.ui.button):

        if interaction.user != self.context.author:
            await interaction.response.defer()
            return

        self.index -= 1

        if self.index < 0:
            self.index = len(self.posts) - 1

        await self.message.edit(embed=getEmbed(self.context, self.guildID, self.posts, self.index))

        await interaction.response.defer()

    @discord.ui.button(label=f'Random', style=discord.ButtonStyle.blurple)
    async def random(self, interaction: discord.Interaction, button: discord.ui.button):

        if interaction.user != self.context.author:
            await interaction.response.defer()
            return

        self.index = randint(0, len(self.posts) - 1)

        await self.message.edit(embed=getEmbed(self.context, self.guildID, self.posts, self.index))

        await interaction.response.defer()

    @discord.ui.button(label=f'>', style=discord.ButtonStyle.blurple)
    async def goNext(self, interaction: discord.Interaction, button: discord.ui.button):

        if interaction.user != self.context.author:
            await interaction.response.defer()
            return

        self.index += 1

        if self.index >= len(self.posts):
            self.index = 0

        await self.message.edit(embed=getEmbed(self.context, self.guildID, self.posts, self.index))

        await interaction.response.defer()

    @discord.ui.button(label=f'>>>', style=discord.ButtonStyle.blurple)
    async def goNextTen(self, interaction: discord.Interaction, button: discord.ui.button):

        if interaction.user != self.context.author:
            await interaction.response.defer()
            return

        self.index += 10

        if self.index >= len(self.posts):
            self.index = len(self.posts) - self.index

        await self.message.edit(embed=getEmbed(self.context, self.guildID, self.posts, self.index))

        await interaction.response.defer()

def getPostInfo(post):

    data = {}

    data['id'] = post['id']
    data['url'] = post['file']['url']
    data['upVotes'] = post['score']['up']
    data['downVotes'] = post['score']['down']
    data['favCount'] = post['fav_count']
    data['artist'] = post['tags']['artist']

    return data

def getEmbed(ctx, guildID, posts, index):

    post = getPostInfo(posts[index])

    embed = discord.Embed()

    embed.title = f"{', '.join(post['artist'])}"
    embed.description = f':thumbsup: ⁣ {post["upVotes"]} ⁣ | ⁣ :thumbsdown: ⁣ {abs(post["downVotes"])} ⁣ | ⁣ :heart: ⁣ {post["favCount"]}'
    embed.add_field(name='', value=f'[__< {langMan.getString("e621GoToPost", guildID=guildID)} >__](https://e621.net/posts/{post["id"]})', inline=True)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)

    embed.set_image(url=post['url'])

    embed.set_footer(text=f"{index + 1} / {len(posts)}")

    return embed

class e621Command(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.lastE621PostFound = None

        self.page = 0
        self.ignorePagination = True

        self.blacklist = 'underage'

        self.e621Client = e621.client()


    @commands.command()
    async def e621(self, ctx: commands.Context, *, tags='score:>100'):

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        curIndex = 0

        if not ctx.channel.is_nsfw():
            await ctx.send(f':no_entry_sign:｜{langMan.getString("NSFWOnlyCommand", guildID=guildID)}')
            return

        message = await ctx.send(f':blue_circle:｜{langMan.getString("e621Searching", guildID=guildID)}')

        if 'pool:' in tags:
            posts = self.e621Client.posts.search(tags=f'order:id {tags} -flash -webm', blacklist=self.blacklist, limit=-1, page=self.page, ignorepage=self.ignorePagination)
        else:
            posts = self.e621Client.posts.search(tags=f'order:random {tags} -flash -webm', blacklist=self.blacklist, limit=limit, page=self.page, ignorepage=self.ignorePagination)

        temp = []

        for entry in posts:
            if entry not in temp:
                temp.append(entry)

        posts = temp
                

        if not posts:
            await message.edit(content=f':blue_circle:｜{langMan.getString("e621NotFound", guildID=guildID)}')
            return

        embed = getEmbed(ctx, guildID, posts, curIndex)
        button = Button(message, curIndex, posts, guildID, ctx)

        await message.edit(embed=embed, content='', view=button)

async def setup(client):
    await client.add_cog(e621Command(client))