"""Holds all commands that are macros for multiple commands."""

import discord
from discord.ext import commands
from discord.ext.commands import CommandError
import common.cfg as cfg
from common.utils import check_emoji, loading_emoji


class VibrantMacros(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        if not ctx.author.guild_permissions.manage_roles:
            raise CommandError(f"You need Manage Roles permission")
        if ctx.guild.id in cfg.heavy_command_active:
            raise CommandError("Please wait for the current command to finish")
        return True

    @commands.command(name="ilso", aliases=["ILSO"])
    async def import_load_splash_overwrite(self, ctx, *, theme):
        """Macro command: Import->Load->Splash->Overwrite."""

        cfg.suppress_output.add(ctx.guild.id)

        def get_embed(*sequence):
            """Generates an embed with emojies and command names"""
            sequence = zip(sequence, ("Import", "Load", "Splash", "Overwrite"))
            return discord.Embed(
                title="ILSO Status",
                description="\n".join(
                    [f"{check_emoji() if e else loading_emoji()} {c}" for e, c in sequence])
            )

        # Import
        await ctx.invoke(self.bot.get_command("import"), name=theme)
        msg = await ctx.send(embed=get_embed(1, 0, 0, 0))

        # Load
        await ctx.invoke(self.bot.get_command("load"), themename=theme)
        await msg.edit(embed=get_embed(1, 1, 0, 0))

        # Splash
        await ctx.invoke(self.bot.get_command("splash"))
        await msg.edit(embed=get_embed(1, 1, 1, 0))

        # Overwrite
        await ctx.invoke(self.bot.get_command("overwrite"), themename=theme)
        finished_embed = discord.Embed(
            title=f"Tasks complete {check_emoji()}")
        await msg.edit(embed=finished_embed)

        cfg.suppress_output.discard(ctx.guild.id)

    @commands.command(name="acm", aliases=["ACM"])
    async def add_colorme(self, ctx, hexcode, *, name=""):
        """Macro command: Add->Colorme"""
        await ctx.invoke(self.bot.get_command("add"), hexcode, name=name)
        await ctx.invoke(self.bot.get_command("colorme"), cstring=name)

    @commands.command(name="resplash")
    async def resplash(self, ctx):
        """Macro command: Unsplash->Splash"""
        await ctx.invoke(self.bot.get_command("unsplash"))
        await ctx.invoke(self.bot.get_command("splash"))

    @commands.command(name="lso", aliases=["LSO"])
    async def load_splash_overwrite(self, ctx, *, theme):
        """Macro command: Import->Load->Splash->Overwrite."""

        cfg.suppress_output.add(ctx.guild.id)

        def get_embed(*sequence):
            """Generates an embed with emojies and command names"""
            sequence = zip(sequence, ("Load", "Splash", "Overwrite"))
            return discord.Embed(
                title="LSO Status",
                description="\n".join(
                    [f"{check_emoji() if e else loading_emoji()} {c}" for e, c in sequence])
            )

        msg = await ctx.send(embed=get_embed(0, 0, 0))

        # Load
        await ctx.invoke(self.bot.get_command("load"), themename=theme)
        await msg.edit(embed=get_embed(1, 0, 0))

        # Splash
        await ctx.invoke(self.bot.get_command("splash"))
        await msg.edit(embed=get_embed(1, 1, 0))

        # Overwrite
        await ctx.invoke(self.bot.get_command("overwrite"), themename=theme)
        finished_embed = discord.Embed(
            title=f"Tasks complete {check_emoji()}")
        await msg.edit(embed=finished_embed)

        cfg.suppress_output.discard(ctx.guild.id)


def setup(bot):
    bot.add_cog(VibrantMacros(bot))
