"""Module holds Paginated sending class that allow a neatly functioning UI
to save space with discord and provide easy navigation
NGL this module kinda ugly and needs to be cleaned up
"""

import discord

from vars import emoji_dict, bot
from utils import to_sendable


class PaginatedMessage:
    """Base class for any paginated message"""

    def __init__(self, content, pointer=0):
        """Pointer is the current index

        Args:
            content: either a list of images or a list of dictionaries
            pointer: The page index
        """
        if isinstance(content, dict):
            self.content = list(content.items())
        else:
            self.content = content
        self.pointer = pointer if -1 < pointer < len(content) else 0
        self.message = None

    @property
    def channel(self):
        """get the channel"""
        return self.message.channel

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
    _items = {}
    REACTIONS = {emoji_dict[name] for name in
                 ("left_arrow", "right_arrow", "updown")}

    def __init__(self, content, pointer=0):
        super().__init__(content, pointer)
        self.pointer = pointer if -1 < pointer < len(content) else 0

    @classmethod
    def get(cls, id):
        return cls._items.get(id)

    async def send(self, channel):
        if len(self.content) == 1:
            file = to_sendable(self.content[0])
            return await channel.send(file=file)

        # Clear buttons from old message
        old = PaginatedImage._items.pop(channel.id, None)
        if old:
            try:
                await old.message.clear_reactions()
            except discord.errors.NotFound:
                pass

        file = to_sendable(self.content[self.pointer])
        self.message = await channel.send(file=file)
        await self.add_reactions("left_arrow", "right_arrow", "updown")
        PaginatedImage._items[channel.id] = self

    async def sendall(self):
        """Send all of the image at once"""
        await self.message.delete()  # Delete current message

        # Send all files
        for img in self.content:
            await self.channel.send(file=to_sendable(img))

        PaginatedImage._items.pop(self.channel.id, None)

    async def update(self):
        """Change the currently displayed image."""
        await self.message.delete()  # delete old image

        # send new message
        file = to_sendable(self.content[self.pointer])
        self.message = await self.channel.send(file=file)
        await self.add_reactions("left_arrow", "right_arrow", "updown")


class PaginatedEmbed(PaginatedMessage):

    _items = {}  # Channel id: self
    REACTIONS = {emoji_dict[name] for name in
                 ("left_arrow", "right_arrow", "home_arrow",
                  "up_arrow", "refresh")}

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
        embed = self.generate_embed()
        channel = self.channel
        await self.message.delete()
        self.message = await channel.send(embed=embed)
        await self.add_reactions(default=True)

    async def send(self, channel):
        # Clear buttons from old message
        old = PaginatedEmbed._items.pop(channel.id, None)
        if old:
            try:
                await old.message.clear_reactions()
            except:
                pass

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
        pe = PaginatedImage.get(reaction.message.channel.id)
        if not pe or reaction.message.id != pe.message.id:
            return

    if reaction.emoji not in type(pe).REACTIONS:
        return

    if reaction.emoji == emoji_dict["left_arrow"]:
        # Only remove reactions on embed because images are resent
        if isinstance(pe, PaginatedEmbed):
            await pe.message.remove_reaction(emoji_dict["left_arrow"], user)

        # Adjust pointer and update message
        if pe.pointer == 0:
            return
        else:
            pe.pointer -= 1
            await pe.update()

    elif reaction.emoji == emoji_dict["right_arrow"]:
        # Only remove reactions on embed because images are resent
        if isinstance(pe, PaginatedEmbed):
            await pe.message.remove_reaction(emoji_dict["right_arrow"], user)

        # Adjust pointer and update message
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

    elif reaction.emoji == emoji_dict["updown"]:
        await pe.sendall()
