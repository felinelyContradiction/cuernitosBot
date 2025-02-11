import contextlib

with contextlib.redirect_stdout(None):
    import discord
    from discord.ext import commands
    import e621py_wrapper as e621


from random import choice, randint


from utils import *
from lang.langManager import langMan

class e621Command(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.lastE621PostFound = None

        self.page = 0
        self.ignorePagination = True
        self.limit = 100

        self.blacklist = 'underage'

        self.e621Client = e621.client()



    @commands.command()
    async def e621(self, ctx: commands.Context, *, tags='score:>100'):

        author = getAuthor(ctx)
        guildID = ctx.message.author.guild.id

        if not ctx.channel.is_nsfw():
            await ctx.send(f':no_entry_sign:｜{langMan.getString("NSFWOnlyCommand", guildID=guildID)}')
            return

        message = await ctx.send(f':blue_circle:｜{langMan.getString("e621Searching", guildID=guildID)}')
        posts = self.e621Client.posts.search(tags=f'order:random {tags}', blacklist=self.blacklist, limit=self.limit, page=self.page, ignorepage=self.ignorePagination)

        if not posts:
            await message.edit(content=f':blue_circle:｜{langMan.getString("e621NotFound", guildID=guildID)}')
            #await ctx.send(f':blue_circle:｜{langMan.getString("e621NotFound", guildID=guildID)}')
            return


        post = choice(posts)

        triesBeforeGivingUp = 5

        if self.lastE621PostFound != None:
            while self.lastE621PostFound == post['id']:
                triesBeforeGivingUp -= 1
                post = choice(posts)

                if triesBeforeGivingUp <= 0:
                    break

        id = post['id']
        url = post['file']['url']
        upVotes = post['score']['up']
        downVotes = post['score']['down']
        favCount = post['fav_count']
        artist = post['tags']['artist']

        while '.swf' in url:
            post = choice(posts)

            id = post['id']
            url = post['file']['url']
            upVotes = post['score']['up']
            downVotes = post['score']['down']
            favCount = post['fav_count']
            artist = post['tags']['artist']

        self.lastE621PostFound = post['id']

        if '.webm' in url or '.mp4' in url:
            await message.edit(content=url)
            return

        embed = discord.Embed(title=f"{', '.join(artist)}",
                              description=f':thumbsup: ⁣ {upVotes} ⁣ | ⁣ :thumbsdown: ⁣ {abs(downVotes)} ⁣ | ⁣ :heart: ⁣ {favCount}',
                              )
        embed.add_field(name='', value=f'[__< {langMan.getString("e621GoToPost", guildID=guildID)} >__](https://e621.net/posts/{id})', inline=True)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)

        resultsAmount: str = str(len(posts) // 2)
        if len(posts) >= self.limit:
            resultsAmount = '+' + str(self.limit)

        embed.set_footer(text=f'{langMan.getString("e621ResultsAmountFound", guildID=guildID, extra1=resultsAmount)}')

        embed.set_image(url=url)

        await message.edit(embed=embed, content='')

async def setup(client):
    await client.add_cog(e621Command(client))