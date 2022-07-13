import discord

from discord import ApplicationContext, slash_command, Option

from common.database import db
from common.constants import MAX_COLORS, MAX_COLORS_EMBED
from model.color import Color


class ColorManagement(discord.Cog):
    """Handles commands and listeners related to modifying the colors connected to a guild."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    # def cog_check(self, ctx):
    #     """Ensure user has permissions and heavy command is not active for cog commands."""
    #     if not ctx.author.guild_permissions.manage_roles:
    #         raise CommandError(f"You need Manage Roles permission")
    #     if ctx.guild.id in cfg.heavy_command_active:
    #         raise CommandError("Please wait for the current command to finish")
    #     return True

    ################ COMMANDS #################

    @slash_command(name="add")
    async def add_color(
        self, ctx: ApplicationContext,
        name: Option(str, "The name of the color"),
        value: Option(discord.Colour, "The value of the color"),
    ):
        """Add a color to the active set of colors"""
        colors = db.get_colors(ctx.guild.id)

        if len(colors) >= MAX_COLORS:
            return await ctx.respond(embed=MAX_COLORS_EMBED)

        # create and add color
        color = Color(name=name[:30], hexcode=str(value))

        update_successful = db.add_color(ctx.guild.id, color)

        if update_successful:
            await ctx.invoke(self.bot.get_command("colors"))
        else:
            await ctx.respond(embed=discord.Embed(
                title=f"Could not add {color.name}",
                color=color.to_discord_color()
            ))

    # @commands.command(name="remove", aliases=["delete"])
    # async def remove_color(self, ctx, *, color: utils.ColorConverter):
    #     """Remove a color from a guild's colors."""

    #     # remove color from db
    #     db.guilds.update_one(
    #         {"_id": ctx.guild.id},
    #         {"$pull": {"colors": color}}
    #     )

    #     # remove role if exists
    #     if color["role"]:
    #         role = ctx.guild.get_role(color["role"])
    #         await role.delete()

    #     await ctx.invoke(bot.get_command("colors"))  # show updated set

    # @commands.command(name="rename", aliases=["rn"])
    # async def rename_color(self, ctx, *, query):
    #     """Rename a color."""
    #     colors = db.get(ctx.guild.id, "colors")

    #     try:
    #         before, after = query.split("|")
    #     except ValueError:
    #         raise UserInputError(
    #             "Command should be formatted as: $rename <color> | <name>")

    #     # Find the correct color to remove. or dont.
    #     color = utils.color_lookup(before.strip(), colors)
    #     if not color:
    #         raise UserInputError("Couldn't find that color")

    #     after = after.strip()
    #     if not after:
    #         raise UserInputError(
    #             "Command should be formatted as: $rename <color> | <name>")

    #     # adjust roles if color is changed
    #     if color["role"]:
    #         role = ctx.guild.get_role(color["role"])
    #         await role.edit(name=after)

    #     # update database
    #     db.guilds.update_one(
    #         {"_id": ctx.guild.id, "colors": color},
    #         {"$set": {"colors.$.name": after}}
    #     )

    #     await ctx.invoke(bot.get_command("colors"))

    # @commands.command(name="recolor", aliases=["rc", "recolour"])
    # async def recolor(self, ctx, *, query):
    #     """Change the way a color looks."""
    #     colors = db.get(ctx.guild.id, "colors")

    #     try:
    #         before, after = query.split("|")
    #     except ValueError:
    #         raise UserInputError(
    #             "Command should be formatted as: $rename <color> | <hexcode>")

    #     # Find the correct color to remove. or dont.
    #     color = utils.color_lookup(before.strip(), colors)
    #     if not color:
    #         raise UserInputError("Couldn't find that color")

    #     after = after.strip()
    #     if not utils.validate_hex(after):
    #         raise UserInputError(
    #             "Invalid hexcode. Get help at https://htmlcolorcodes.com/")

    #     # adjust roles if color is changed
    #     if color["role"]:
    #         role = ctx.guild.get_role(color["role"])
    #         new_color = utils.to_rgb(after)
    #         await role.edit(color=discord.Color.from_rgb(*new_color))

    #     # update database
    #     db.guilds.update_one(
    #         {"_id": ctx.guild.id, "colors": color},
    #         {"$set": {"colors.$.hexcode": after}}
    #     )

    #     await ctx.invoke(bot.get_command("colors"))

    # @commands.command(name="clear_colors", aliases=["clear_colours"])
    # async def clear_colors(self, ctx):
    #     """Removes all active colors."""
    #     colors = db.get(ctx.guild.id, "colors")

    #     if ctx.guild.id not in cfg.suppress_output:
    #         msg = await ctx.send(embed=discord.Embed(title=f"Clearing colors {loading_emoji()}"))

    #     # remove roles
    #     for color in colors:
    #         if color["role"]:
    #             role = ctx.guild.get_role(color["role"])
    #             await role.delete()
    #             await asyncio.sleep(0.25)

    #     db.guilds.update_one(
    #         {"_id": ctx.guild.id},
    #         {"$set": {"colors": []}}
    #     )
    #     if ctx.guild.id not in cfg.suppress_output:
    #         await msg.edit(embed=discord.Embed(
    #             title=f"Colors Removed {check_emoji()}",
    #             color=discord.Color.green())
    #         )

    # ############# EVENT LISTENERS #############

    # @commands.Cog.listener()
    # async def on_guild_role_delete(self, role):
    #     """Removes a role from a color if user deletes it"""
    #     db.guilds.update_one(
    #         {"_id": role.guild.id, "colors.role": role.id},
    #         {"$set": {"colors.$.role": None, "colors.$.members": []}}
    #     )

    # @commands.Cog.listener()
    # async def on_guild_role_update(self, before, after):
    #     """Updated a color if the associated role is updated"""
    #     # Name has changed
    #     if before.name != after.name:
    #         db.guilds.update_one(
    #             {"_id": before.guild.id, "colors.role": before.id},
    #             {"$set": {"colors.$.name": after.name}}
    #         )
    #     # Hexcode has changed
    #     if before.color != after.color:
    #         db.guilds.update_one(
    #             {"_id": before.guild.id, "colors.role": before.id},
    #             {"$set": {"colors.$.hexcode": str(after.color)}}
    #         )


def setup(bot):
    bot.add_cog(ColorManagement(bot))
