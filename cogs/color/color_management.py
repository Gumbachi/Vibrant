import discord
from discord.ext import commands

from classes import Guild, Color
import database as db
from authorization import authorize
from vars import bot


class ColorManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add", aliases=["new", "create", "addcolor", "a"])
    async def add_color(self, ctx, hexcode, *, name=""):
        """Add a color to the Guild.

        Args:
            hexcode (str): The hexcode of the new color
            name (str): The name of the new color
        """
        authorize(ctx, "disabled", "roles", "color_limit",
                  name=name, hexcode=hexcode)

        guild = Guild.get(ctx.guild.id)

        # auto name if name not given
        if not name:
            name = f"Color {len(guild.colors) + 1}"

        # change black color because #000000 in discord is transparent
        if hexcode == "#000000":
            hexcode == "#000001"

        # create and add color
        color = Color(name, hexcode, ctx.guild.id)
        guild.colors.append(color)

        # report success
        await ctx.send(
            f"**{color.name}** has been added at index **{color.index}**.")
        await ctx.invoke(bot.get_command("colors"))  # show new set
        db.update_prefs(guild)

    @commands.command(name="remove", aliases=["delete", "r"])
    async def remove_color(self, ctx, *, query=""):
        """Remove a color from the Guild.

        Args:
            color (tuple of str): The search query for color to remove
        """
        authorize(ctx, "disabled", "roles", "colors", color_query=(query, 95))
        guild = Guild.get(ctx.guild.id)

        # get color
        color = guild.find_color(query, 95)

        # remove color and response
        await color.delete()
        await ctx.send(f"**{color.name}** has been deleted!")
        await ctx.invoke(bot.get_command("colors"))  # show updated set
        db.update_prefs(guild)

    @commands.command(name="rename", aliases=["rn"])
    async def rename_color(self, ctx, *, query=""):
        """Rename a color in the Guild's active colors.

        Args:
            color (tuple of str): The color to change the name of
        """
        authorize(ctx, "disabled", "roles", "colors", swap_query=query)

        guild = Guild.get(ctx.guild.id)

        before, after = query.split("|")

        # strip extraneous spaces
        before = before.strip()
        after = after.strip()

        authorize(ctx, color_query=(before, 90))

        color = guild.find_color(before, 90)
        old_name = color.name
        color.name = after

        # adjust roles if color is changed
        if color.role_id:
            role = guild.get_role(color.role_id)
            if role:
                await role.edit(name=color.name)
            else:
                color.role_id = None

        await ctx.send(f"**{old_name}** is now named **{after}**")
        db.update_prefs(guild)

    @commands.command(name="recolor", aliases=["rc", "recolour"])
    async def recolor(self, ctx, *, query=""):
        """Change a color's hexcode.

        Args:
            color (tuple of str): The color to change the name of
        """
        authorize(ctx, "disabled", "roles", "colors", swap_query=query)

        guild = Guild.get(ctx.guild.id)

        before, after = query.split("|")

        # strip extraneous spaces
        before = before.strip()
        after = after.strip()

        # make sure arguments are valid
        authorize(ctx, color_query=(before, 90), hexcode=after)

        color = guild.find_color(before, 90)
        color.hexcode = after

        # adjust roles if color is changed
        if color.role_id:
            role = guild.get_role(color.role_id)
            if role:
                await role.edit(color=discord.Color.from_rgb(*color.rgb))
            else:
                color.role_id = None

        rc_embed = discord.Embed(
            title=f"{color.name} is now colored {after}",
            description=discord.Embed.Empty,
            color=discord.Color.from_rgb(*color.rgb))

        await ctx.send(embed=rc_embed)
        db.update_prefs(guild)

    @commands.command(name="clear_all_colors", aliases=["clear_all_colours"])
    async def clear_colors(self, ctx, backup=True):
        """Remove all colors from the Guild's colors.

        Args:
            backup (bool): Whether or not to send a backup JSON
        """
        authorize(ctx, "disabled", "roles")

        guild = Guild.get(ctx.guild.id)

        await ctx.send("Removing all colors...")
        # remove all colors and clear roles
        async with ctx.channel.typing():
            await guild.clear_colors()

        await ctx.send(f"Success! All colors have been removed.")
        db.update_prefs(guild)


def setup(bot):
    bot.add_cog(ColorManagement(bot))
