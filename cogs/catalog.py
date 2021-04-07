import discord
from discord.ext import commands
import common.cfg as cfg
from common.utils import image_to_file


class CatalogListeners(commands.Cog):
    """Handles catalogs."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Responds to reactions."""
        catalog = cfg.catalogs.get(reaction.message.channel.id, None)
        # ignore bot or non-related reaction
        if user == self.bot.user or not catalog or catalog.message.id != reaction.message.id:
            return

        # Only remove reactions on embed because images are resent
        if catalog.type == "Embed":
            await catalog.message.remove_reaction(reaction.emoji, user)

        if reaction.emoji == cfg.emojis["left_arrow"]:
            # Adjust pointer and update message
            if catalog.page != 0:
                catalog.page -= 1
                await catalog.send(reaction.message.channel)  # update image

        elif reaction.emoji == cfg.emojis["right_arrow"]:
            # Adjust pointer and update message
            if catalog.page != len(catalog)-1:
                catalog.page += 1
                await catalog.send(reaction.message.channel)  # update image

        elif reaction.emoji == cfg.emojis["home_arrow"]:
            # Adjust pointer and update message
            catalog.page = 0
            await catalog.send(reaction.message.channel)  # update image

        elif reaction.emoji == cfg.emojis["double_down"]:
            await catalog.sendall()  # send all images

        elif reaction.emoji == cfg.emojis["updown_arrow"]:
            if catalog.minimized:
                await catalog.send(reaction.message.channel)  # maximize
                catalog.minimized = False
            else:
                await catalog.minimize()


def setup(bot):
    bot.add_cog(CatalogListeners(bot))


class Catalog:
    """Base class for any paginated message"""
    image_reactions = ["left_arrow", "right_arrow",
                       "home_arrow", "double_down"]
    embed_reactions = ["left_arrow", "right_arrow",
                       "home_arrow", "updown_arrow"]

    def __init__(self, content, page=0):
        """Creates a paginated message"""
        self.content = content
        self.page = page
        self.message = None
        self.type = "Embed" if isinstance(content[0], dict) else "Image"
        self.minimized = False

    def __len__(self):
        return len(self.content)

    @property
    def channel(self):
        """Get the channel message is sent in."""
        return self.message.channel

    async def send(self, channel):
        """Sends the message containing the catalog."""
        # Send Images
        if self.type == "Image":
            # only one image to send
            if len(self.content) == 1:
                print("only one")
                imagefile = image_to_file(self.content[0])
                return await channel.send(file=imagefile)

            await self.delete_message()  # delete current message

            # Send and add reactions to new image
            imagefile = image_to_file(self.content[self.page])
            self.message = await channel.send(file=imagefile)
            await self.add_reactions(self.image_reactions)

        # Send embeds
        elif self.type == "Embed":
            # Edit or send new message
            if self.message:
                await self.message.edit(embed=self.generate_embed())
            else:
                self.message = await channel.send(embed=self.generate_embed())
                await self.add_reactions(self.embed_reactions)

        # add to catalog instances
        cfg.catalogs[self.channel.id] = self

    async def add_reactions(self, reactions):
        """Add reactions to the contained message."""
        for reaction in reactions:
            await self.message.add_reaction(cfg.emojis[reaction])

    async def delete_message(self):
        """Attempts to delete the message stored."""
        if self.message:
            try:
                await self.message.delete()
            except discord.errors.NotFound:
                pass  # ignore failure if message cant be located

    async def sendall(self):
        """Send all images."""
        # only for images
        if self.type != "Image":
            return

        await self.delete_message()  # Delete current message

        # send all images
        for imfile in [image_to_file(img) for img in self.content]:
            await self.channel.send(file=imfile)

        cfg.catalogs.pop(self.channel.id, None)  # remove from instances

    def generate_embed(self):
        """Forms an embed from content"""
        if self.type != "Embed":
            return

        page = self.content[self.page]

        # create embed
        embed = discord.Embed(
            title=page["title"],
            description=page["description"]
        )

        # add content not including title/desc fields
        for k, v in page.items():
            if k not in ("title", "description"):
                embed.add_field(name=k, value="\n".join(v), inline=False)

        return embed

    async def minimize(self):
        """Minimize the embed"""
        if self.type != "Embed":
            return

        min_embed = discord.Embed(
            title=self.content[self.page]["title"],
            description=""
        )
        await self.message.edit(embed=min_embed)
        self.minimized = True
