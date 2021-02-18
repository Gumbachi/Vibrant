import discord
import common.cfg as cfg
import common.database as db
from common.cfg import bot
import common.utils as utils
from discord.ext import commands
from discord.ext.commands.errors import CommandError, UserInputError


class ColorManagement(commands.Cog):
    """Handles commands and listeners related to modifying the colors connected to a guild."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add", aliases=["new"])
    @commands.has_guild_permissions(manage_roles=True)
    async def add_color(self, ctx, hexcode, *, name=""):
        """Add a color to the database colors."""
        colors = db.get(ctx.guild.id, "colors")

        if len(colors) >= cfg.color_limit:
            raise CommandError(f"Color Limit Reached ({len(colors)}/50)")

        if not utils.validate_hex(hexcode):
            raise UserInputError(
                f"Invalid hexcode. Get help at https://htmlcolorcodes.com/")

        if "|" in name or len(name) > 100:
            raise UserInputError(
                "Color names must be shorter than 100 characters and cannot include '|'")

        # auto name if name not given
        if not name:
            name = f"Color {len(colors) + 1}"

        # change black color because #000000 in discord is transparent
        if hexcode in {"#000000", "#000"}:
            hexcode = "#000001"

        # create and add color
        new_color = {
            "name": name,
            "hexcode": hexcode,
            "role": None,
        }

        # update database
        db.guildcoll.update_one(
            {"_id": ctx.guild.id},
            {"$push": {"colors": new_color}}
        )
        await ctx.invoke(bot.get_command("colors"))  # show new set

    @commands.command(name="remove", aliases=["delete"])
    @commands.has_guild_permissions(manage_roles=True)
    async def remove_color(self, ctx, *, color: utils.ColorConverter):
        """Remove a color from a guilds colors."""

        # remove role if assigned
        if color["role"]:
            role = ctx.guild.get_role(color["role"])
            if role:
                await role.delete()

        # remove color from db
        db.guildcoll.update_one({"_id": ctx.guild.id}, {
                                "$pull": {"colors": color}})
        await ctx.invoke(bot.get_command("colors"))  # show updated set

    @commands.command(name="rename", aliases=["rn"])
    @commands.has_guild_permissions(manage_roles=True)
    async def rename_color(self, ctx, *, query):
        """Rename a color."""

        colors = db.get(ctx.guild.id, "colors")
        try:
            before, after = query.split("|")
        except ValueError:
            raise UserInputError(
                "Command should be formatted as: $rename <color> | <name>")

        # Find the correct color to remove. or dont.
        color = utils.color_lookup(before.strip(), colors)
        if not color:
            raise UserInputError("Couldn't find that color")

        after = after.strip()
        if not after:
            raise UserInputError(
                "Command should be formatted as: $rename <color> | <name>")

        # adjust roles if color is changed
        if color["role"]:
            role = ctx.guild.get_role(color["role"])
            if role:
                await role.edit(name=after)
            # else:
            #     # remove false role value in database
            #     db.coll.update_one(
            #         {"_id": ctx.guild.id, "colors": color},
            #         {"$set": {"colors.$.role": None}}
            #     )

        # update database
        db.guildcoll.update_one(
            {"_id": ctx.guild.id, "colors": color},
            {"$set": {"colors.$.name": after}}
        )

        # Send message
        rn_embed = discord.Embed(
            title=f"Renamed {color['name']} to **{after}**!",
            color=utils.discord_color(color))
        await ctx.send(embed=rn_embed)

    @commands.command(name="recolor", aliases=["rc", "recolour"])
    @commands.has_guild_permissions(manage_roles=True)
    async def recolor(self, ctx, *, query):
        """Change the way a color looks."""

        colors = db.get(ctx.guild.id, "colors")  # query database
        try:
            before, after = query.split("|")
        except ValueError:
            raise UserInputError(
                "Command should be formatted as: $rename <color> | <hexcode>")

        # Find the correct color to remove. or dont.
        color = utils.color_lookup(before.strip(), colors)
        if not color:
            raise UserInputError("Couldn't find that color")

        after = after.strip()
        if not utils.validate_hex(after):
            raise UserInputError(
                "Invalid hexcode. Get help at https://htmlcolorcodes.com/")

        # adjust roles if color is changed
        if color["role"]:
            role = ctx.guild.get_role(color["role"])
            if role:
                new_color = utils.to_rgb(after)
                await role.edit(color=utils.discord_color(new_color))
            # else:
            #     db.coll.update_one(
            #         {"_id": ctx.guild.id, "colors": color},
            #         {"$set": {"colors.$.role": None}}
            #     )

        # update database
        db.guildcoll.update_one(
            {"_id": ctx.guild.id, "colors": color},
            {"$set": {"colors.$.hexcode": after}}
        )

        # Send message
        rc_embed = discord.Embed(
            title=f"Changed {color['name']} to **{after}**!",
            color=utils.discord_color({"hexcode": after}))
        await ctx.send(embed=rc_embed)

    @commands.command(name="clear_all_colors", aliases=["clear_all_colours"])
    @commands.has_guild_permissions(manage_roles=True)
    async def clear_colors(self, ctx):
        """Removes all active colors."""
        colors = db.get(ctx.guild.id, "colors")  # query database
        msg = await ctx.send(embed=discord.Embed(title="Clearing colors.."))

        # remove roles
        for color in colors:
            if color["role"]:
                role = ctx.guild.get_role(color["role"])
                if role:
                    await role.delete()

        db.update_guild(ctx.guild.id, {"colors": []})  # update database
        await msg.edit(embed=discord.Embed(title="Colors Removed!",
                                           color=discord.Color.green()))


def setup(bot):
    bot.add_cog(ColorManagement(bot))
