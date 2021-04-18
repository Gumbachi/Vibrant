import copy
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

        already_suppressed = ctx.guild.id in cfg.suppress_output

        try:
            embed = discord.Embed(
                title=f"Loading **{theme['name']}** {loading_emoji()}")
            if ctx.guild.id not in cfg.suppress_output:
                msg = await ctx.send(embed=embed)
        except TypeError:
            raise UserInputError("Could not find that theme")

        # Supress output from clear_colors and prevent other commands from modifying colors
        cfg.heavy_command_active.add(ctx.guild.id)
        cfg.suppress_output.add(ctx.guild.id)
        await ctx.invoke(self.bot.get_command("clear_colors"))  # clear colors
        if not already_suppressed:
            cfg.suppress_output.discard(ctx.guild.id)

        # Update colors in db
        theme_ref = copy.deepcopy(theme)
        for color in theme["colors"]:
            color["role"] = None
            color["members"] = []
        db.guilds.update_one(
            {"_id": ctx.guild.id},
            {"$set": {"colors": theme["colors"]}}
        )

        color_memory = {}
        for color in theme_ref["colors"]:
            if not color["members"]:
                continue

            # Color members of a color
            for mid in color["members"]:
                member = ctx.guild.get_member(mid)  # ignore missing members
                if member:

                    # avoids role duplication by ColorAssignment.color
                    color["role"] = color_memory.get(color["name"], None)
                    if not color["role"]:
                        role = await ColorAssignment.create_role(ctx.guild, color)
                        color_memory[color["name"]] = role.id
                        color["role"] = role.id

                    await ColorAssignment.color(member, color)

        # report success
        success_embed = discord.Embed(
            title=f"Loaded **{theme['name']}** {check_emoji()}",
            color=discord.Color.green()
        )
        if ctx.guild.id not in cfg.suppress_output:
            await msg.edit(embed=success_embed)
            await ctx.invoke(self.bot.get_command("colors"))
        cfg.heavy_command_active.discard(ctx.guild.id)


def setup(bot):
    bot.add_cog(ThemeAssignment(bot))
