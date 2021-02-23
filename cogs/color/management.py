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

    def cog_check(self, ctx):
        """Ensure user has permissions and heavy command is not active for cog commands."""
        if not ctx.author.guild_permissions.manage_roles:
            raise CommandError(f"You need Manage Roles permission")
        if ctx.guild.id in cfg.heavy_command_active:
            raise CommandError("Please wait for the current command to finish")
        return True

    @commands.command(name="add", aliases=["new"])
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
                "Color names must be shorter than 100 characters and cannot include `|`")

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
            "members": []
        }

        # update database
        db.guilds.update_one(
            {"_id": ctx.guild.id},
            {"$push": {"colors": new_color}}
        )
        await ctx.invoke(bot.get_command("colors"))  # show new set

    @commands.command(name="remove", aliases=["delete"])
    async def remove_color(self, ctx, *, color: utils.ColorConverter):
        """Remove a color from a guild's colors."""

        # remove color from db
        db.guilds.update_one(
            {"_id": ctx.guild.id},
            {"$pull": {"colors": color}}
        )

        # remove role if exists
        if color["role"]:
            role = ctx.guild.get_role(color["role"])
            await role.delete()

        await ctx.invoke(bot.get_command("colors"))  # show updated set

    @commands.command(name="rename", aliases=["rn"])
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
            await role.edit(name=after)
            # else:
            #     # remove false role value in database
            #     db.coll.update_one(
            #         {"_id": ctx.guild.id, "colors": color},
            #         {"$set": {"colors.$.role": None}}
            #     )

        # update database
        db.guilds.update_one(
            {"_id": ctx.guild.id, "colors": color},
            {"$set": {"colors.$.name": after}}
        )

        await ctx.invoke(bot.get_command("colors"))

    @commands.command(name="recolor", aliases=["rc", "recolour"])
    async def recolor(self, ctx, *, query):
        """Change the way a color looks."""
        colors = db.get(ctx.guild.id, "colors")

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
            new_color = utils.to_rgb(after)
            await role.edit(color=new_color)
            # else:
            #     db.coll.update_one(
            #         {"_id": ctx.guild.id, "colors": color},
            #         {"$set": {"colors.$.role": None}}
            #     )

        # update database
        db.guilds.update_one(
            {"_id": ctx.guild.id, "colors": color},
            {"$set": {"colors.$.hexcode": after}}
        )

        await ctx.invoke(bot.get_command("colors"))

    @commands.command(name="clear_colors", aliases=["clear_colours"])
    async def clear_colors(self, ctx):
        """Removes all active colors."""
        colors = db.get(ctx.guild.id, "colors")
        msg = await ctx.send(embed=discord.Embed(title="Clearing colors.."))

        # remove roles
        for color in colors:
            if color["role"]:
                role = ctx.guild.get_role(color["role"])
                await role.delete()

        db.guilds.update_one(
            {"_id": ctx.guild.id},
            {"$set": {"colors": []}}
        )
        await msg.edit(embed=discord.Embed(
            title="Colors Removed!",
            color=discord.Color.green())
        )

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Removes a role from a color if user deletes it"""
        db.guilds.update_one(
            {"_id": role.guild.id, "colors.role": role.id},
            {"$set": {"colors.$.role": None, "colors.$.members": []}}
        )

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        """Updated a color if the associated role is updated"""
        # Name has changed
        if before.name != after.name:
            db.guilds.update_one(
                {"_id": before.guild.id, "colors.role": before.id},
                {"$set": {"colors.$.name": after.name}}
            )
        # Hexcode has changed
        if before.color != after.color:
            db.guilds.update_one(
                {"_id": before.guild.id, "colors.role": before.id},
                {"$set": {"colors.$.hexcode": str(after.color)}}
            )


def setup(bot):
    bot.add_cog(ColorManagement(bot))
