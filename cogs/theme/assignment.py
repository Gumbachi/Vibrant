from copy import deepcopy
import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import CommandError, UserInputError
from common.utils import theme_lookup, loading_emoji, check_emoji
import common.cfg as cfg
import common.database as db
from cogs.color.assignment import ColorAssignment


class ThemeAssignment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        if not ctx.author.guild_permissions.manage_roles:
            raise CommandError(f"You need Manage Roles permission")
        if ctx.guild.id in cfg.heavy_command_active:
            raise CommandError("Please wait for the current command to finish")
        return True

    @commands.command(name="load", aliases=["theme.load"])
    async def load_theme(self, ctx, *, themename):
        """Change the active colors to a theme."""

        themes = db.get(ctx.guild.id, "themes")
        theme = theme_lookup(themename, themes)

        output_suppressed = ctx.guild.id in cfg.suppress_output

        if not theme:
            raise UserInputError("Could not find that theme")

        if not output_suppressed:
            embed = discord.Embed(
                title=f"Clearing Colors {loading_emoji()}")
            msg = await ctx.send(embed=embed)

        # Supress output from clear_colors and prevent other commands from modifying colors
        cfg.heavy_command_active.add(ctx.guild.id)
        cfg.suppress_output.add(ctx.guild.id)
        await ctx.invoke(self.bot.get_command("clear_colors"))  # clear colors

        if not output_suppressed:
            cfg.suppress_output.discard(ctx.guild.id)

            # Progress update
            embed = discord.Embed(title=f"Creating Roles {loading_emoji()}")
            await msg.edit(embed=embed)

        # kind of a monster and probably impractical but it works
        # keeps only colors that have members that can be found
        owned_colors = [color for color in theme["colors"]
                        if color["members"]
                        and all([ctx.guild.get_member(member_id) for member_id in color["members"]])]

        # Update colors in db
        colors = deepcopy(theme["colors"])
        for color in colors:
            color["role"] = None
            color["members"] = []

        db.guilds.update_one(
            {"_id": ctx.guild.id},
            {"$set": {"colors": colors}}
        )

        cm_pairs = []  # Color and Member pairs
        for color in owned_colors:
            # create role
            role = await ColorAssignment.create_role(ctx.guild, color)
            color["role"] = role.id

            # add to color member pair
            for member_id in color["members"]:
                cm_pairs.append((color, ctx.guild.get_member(member_id)))

        # Progress update
        if not output_suppressed:
            embed = discord.Embed(title=f"Applying Color {loading_emoji()}")
            await msg.edit(embed=embed)

        # loop and apply colors
        for color, member in cm_pairs:
            await ColorAssignment.color(member, color)
            await asyncio.sleep(1)

        cfg.heavy_command_active.discard(ctx.guild.id)

        # report success
        if ctx.guild.id not in cfg.suppress_output:
            success_embed = discord.Embed(
                title=f"Loaded {theme['name']} {check_emoji()}",
                color=discord.Color.green()
            )
            await msg.edit(embed=success_embed)
            await ctx.invoke(self.bot.get_command("colors"))


def setup(bot):
    bot.add_cog(ThemeAssignment(bot))
