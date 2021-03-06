import discord
from discord.ext import commands

from ags_experiments.algorithmia import algo_client
from ags_experiments.client_tools import ClientTools
from ags_experiments.database.database_tools import DatabaseTools
from ags_experiments.settings.config import strings, config


class Tagger(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.client_extras = ClientTools(client)
        self.database_extras = DatabaseTools(self.client_extras)

    @commands.command(aliases=["t"])
    async def tagger(self, ctx, nsfw: bool = False, selected_channel: discord.TextChannel = None):
        """
        Generates tags for you based on what you talk about
        """
        if (not ctx.message.channel.is_nsfw()) and nsfw:
            return await ctx.send(strings['tagger']['errors']['nsfw'].format(str(ctx.author)))

        output = await ctx.send(strings['tagger']['title'] + strings['emojis']['loading'])

        await output.edit(content=output.content + "\n" + strings['tagger']['status']['messages'])
        async with ctx.channel.typing():
            username = self.database_extras.opted_in(user_id=ctx.author.id)
            if not username:
                return await output.edit(content=output.content + strings['tagger']['errors']['not_opted_in'])
            messages, channels = await self.database_extras.get_messages(ctx.author.id, config['limit'])

            text = []

            text = await self.client_extras.build_messages(ctx, nsfw, messages, channels,
                                                           selected_channel=selected_channel)

            text1 = ""
            for m in text:
                text1 += str(m) + "\n"
            await output.edit(
                content=output.content + strings['emojis']['success'] + "\n" + strings['tagger']['status'][
                    'analytical_data'])
            algo = algo_client.algo('nlp/AutoTag/1.0.1')
            await output.delete()
            response = algo.pipe(text1)
            tags = list(response.result)
            tag_str = ""
            for tag in tags:
                tag_str = "- " + tag + "\n" + tag_str
            em = await self.client_extras.markov_embed("Tags for " + str(ctx.author), tag_str)
            output = await ctx.send(embed=em)
        emoji = await self.client_extras.get_delete_emoji()
        emoji = emoji[1]
        return await self.client_extras.delete_option(self.client, output, ctx, emoji)


def setup(client):
    client.add_cog(Tagger(client))
