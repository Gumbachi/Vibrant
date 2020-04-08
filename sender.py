import discord

from vars import emoji_dict, bot


class PaginatedMessage:
    def __init__(self, content, pointer=0):
        """Pointer is the current index"""
        self.content = list(content.items())
        self.pointer = pointer
        self.message = None

    @property
    def channel(self):
        """get the channel"""
        return self.message.channel

    @property
    def reactions(self):
        """get the channel"""
        return self.message.reactions

    async def add_reactions(self, *reactions, **kwargs):
        """Add reactions to the contained message"""

        # default reactions
        if kwargs.get("default"):
            reactions = ("left_arrow", "right_arrow", "home_arrow",
                         "up_arrow", "refresh")

        # add reactions
        for reaction in reactions:
            if isinstance(reaction, discord.Reaction):
                await self.message.add_reaction(reaction)
            elif emoji_dict.get(reaction):
                await self.message.add_reaction(emoji_dict.get(reaction))


class PaginatedImage(PaginatedMessage):
    # maybe use a jump url for this or something
    pass


class PaginatedEmbed(PaginatedMessage):

    _items = {}  # Channel id: self

    def __init__(self, content, pointer=0):
        super().__init__(content, pointer)
        self.embed = self.generate_embed()
        self.minimized = False

    @classmethod
    def get(cls, id):
        return cls._items.get(id)

    def generate_embed(self):
        """Generates an embed based on pointer value"""
        content = self.content[self.pointer][1]

        # create embed
        embed = discord.Embed(title=content.get("title"),
                              description=content.get("description"))

        inline = content.get("inline", False)

        # add content not including title/desc fields
        for k, v in content.items():
            if k in ("title", "description", "inline"):
                continue
            embed.add_field(name=k, value=v, inline=inline)

        return embed

    async def minimize(self):
        """Replace embed with small embed"""
        empty_embed = discord.Embed(
            title="minimized",
            description=" ")
        await self.message.edit(embed=empty_embed)
        self.minimized = True

    async def resend(self):
        """Resend the message."""
        embed = self.message.embeds[0]
        channel = self.channel
        await self.message.delete()
        self.message = await channel.send(embed=embed)
        await self.add_reactions(default=True)

    async def send(self, channel):
        # Clear buttons from old message
        old = PaginatedEmbed._items.pop(channel.id, None)
        if old:
            await old.message.clear_reactions()

        self.message = await channel.send(embed=self.embed)
        await self.add_reactions(default=True)
        PaginatedEmbed._items[channel.id] = self

    async def update(self):
        await self.message.edit(embed=self.generate_embed())
        self.minimized = False


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
        if pe.minimized:
            await pe.update()
        else:
            await pe.minimize()

    elif reaction.emoji == emoji_dict["refresh"]:
        await pe.message.remove_reaction(emoji_dict["refresh"], user)
        await pe.resend()
