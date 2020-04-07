import discord

from vars import emoji_dict, bot


class PaginatedMessage:
    def __init__(self, content, pointer=0):
        """Pointer is the current index"""
        self.content = list(content.items())
        self.pointer = pointer


class PaginatedImage(PaginatedMessage):
    # maybe use a jump url for this or something
    pass


class PaginatedEmbed(PaginatedMessage):

    _items = {}  # Channel id: self

    def __init__(self, content, pointer=0):
        super().__init__(content, pointer)
        self.embed = self.generate_embed()
        self.message = None

    @classmethod
    def get(cls, id):
        return cls._items.get(id)

    def generate_embed(self):
        """Generates an embed based on pointer value"""
        content = self.content[self.pointer][1]

        # create embed
        embed = discord.Embed(title=content.get("title"),
                              description=content.get("description"))

        # add content not including title/desc fields
        for k, v in content.items():
            if k in ("title", "description"):
                continue
            embed.add_field(name=k, value=v, inline=False)

        return embed

    async def minimize(self):
        empty_embed = discord.Embed(
            title="minimized",
            description=" ")
        await self.message.edit(embed=empty_embed)

    async def send(self, channel):
        self.message = await channel.send(embed=self.embed)
        await self.message.add_reaction(emoji_dict["left_arrow"])
        await self.message.add_reaction(emoji_dict["right_arrow"])
        await self.message.add_reaction(emoji_dict["home_arrow"])
        await self.message.add_reaction(emoji_dict["up_arrow"])
        await self.message.add_reaction(emoji_dict["down_arrow"])
        PaginatedEmbed._items[channel.id] = self

    async def update(self):
        await self.message.edit(embed=self.generate_embed())


@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    pe = PaginatedEmbed.get(reaction.message.channel.id)

    if not pe or reaction.message.id != pe.message.id:
        return

    if reaction.emoji == emoji_dict["left_arrow"]:
        await pe.message.remove_reaction(emoji_dict["left_arrow"], user)
        if pe.pointer == 0:
            return
        else:
            pe.pointer -= 1
            await pe.update()

    elif reaction.emoji == emoji_dict["right_arrow"]:
        await pe.message.remove_reaction(emoji_dict["right_arrow"], user)
        if pe.pointer == len(pe.content) - 1:
            return
        else:
            pe.pointer += 1
            await pe.update()

    elif reaction.emoji == emoji_dict["home_arrow"]:
        await pe.message.remove_reaction(emoji_dict["home_arrow"], user)
        if pe.pointer == 0:
            return
        else:
            pe.pointer = 0
            await pe.update()

    elif reaction.emoji == emoji_dict["up_arrow"]:
        await pe.message.remove_reaction(emoji_dict["up_arrow"], user)
        await pe.minimize()

    elif reaction.emoji == emoji_dict["down_arrow"]:
        await pe.message.remove_reaction(emoji_dict["down_arrow"], user)
        await pe.update()
