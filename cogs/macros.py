"""Holds all commands that are macros for multiple commands."""

import discord
from discord.ext import commands
from discord.ext.commands import CommandError
import common.cfg as cfg


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
                description="\n".join([f"{e} {c}" for e, c in sequence])
            )

        # Import
        await ctx.invoke(self.bot.get_command("import"), name=theme)
        msg = await ctx.send(embed=get_embed("✅", "⌛", "⌛", "⌛"))

        # Load
        await ctx.invoke(self.bot.get_command("load"), themename=theme)
        await msg.edit(embed=get_embed("✅", "✅", "⌛", "⌛"))

        # Splash
        await ctx.invoke(self.bot.get_command("splash"))
        await msg.edit(embed=get_embed("✅", "✅", "✅", "⌛"))

        # Overwrite
        await ctx.invoke(self.bot.get_command("overwrite"), themename=theme)
        await msg.edit(embed=get_embed("✅", "✅", "✅", "✅"))

        cfg.suppress_output.discard(ctx.guild.id)

    @commands.command(name="acm", aliases=["ACM"])
    async def add_colorme(self, ctx, hexcode, *, name=""):
        """Macro command: Add->Colorme"""
        await ctx.invoke(self.bot.get_command("add"), hexcode, name=name)
        await ctx.invoke(self.bot.get_command("colorme"), cstring=name)


def setup(bot):
    bot.add_cog(VibrantMacros(bot))
