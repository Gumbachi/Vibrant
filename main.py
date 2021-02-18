import os

import discord
import common.cfg as cfg
from common.cfg import bot


@bot.event
async def on_ready():
    """Change presence and report ready."""
    activity = discord.Game(name=f"@Vibrant for help ({len(bot.guilds)})")
    await bot.change_presence(activity=activity)
    print("Ready Player One.")


@bot.event
async def on_message(message):
    """Message listener."""
    # make sure it doesnt run when bot writes message
    if message.author == bot.user:
        return

    # shows prefix if bot is mentioned
    if message.mentions and message.mentions[0].id == bot.user.id:
        return await message.channel.send(
            f"Type `{cfg.get_prefix(bot, message)}`help for help.")

    await bot.process_commands(message)

# @bot.event
# async def on_member_update(before, after):
#     """updates color info if a users color role is manually removed"""
#     # check if any roles changed
#     if before.roles == after.roles:
#         return

#     guild = Guild.get(before.guild.id)

#     # convert roles to set for comparison
#     roles_before = set(before.roles)
#     roles_after = set(after.roles)

#     # find difference between sets
#     removed_roles = roles_before - roles_after
#     added_roles = roles_after - roles_before

#     # role removed
#     if removed_roles:
#         for role in removed_roles:
#             color = guild.get_color("role_id", role.id)
#             if color:
#                 color.member_ids.discard(before.id)
#                 if not color.member_ids:
#                     try:
#                         await role.delete()
#                     except discord.errors.NotFound:
#                         pass

#     # role added
#     if added_roles:
#         for role in added_roles:
#             color = guild.get_color("role_id", role.id)
#             if color:
#                 color.member_ids.add(before.id)


# @bot.event
# async def on_guild_role_delete(role):
#     """Removes a role from the Guild object if user deletes it"""
#     guild = Guild.get(role.guild.id)

#     # sets color role id to none if it is deleted
#     color = guild.get_color("role_id", role.id)
#     if color:
#         color.role_id = None
#         if not guild.heavy_command_active:
#             db.update_prefs(guild)  # update MongoDB


# @bot.event
# async def on_guild_role_update(before, after):
#     """Removes a role from the Guild object if user deletes it"""
#     guild = Guild.get(before.guild.id)

#     # checks if color has role and change color name and hex to reflect change
#     color = guild.get_color('role_id', before.id)
#     if color:
#         color.name = after.name
#         color.hexcode = str(after.color)
#         if not guild.heavy_command_active:
#             db.update_prefs(guild)  # update MongoDB

# loads extensions(cogs) listed in vars.py
if __name__ == '__main__':
    for extension in cfg.extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"Couldnt load {extension}")
            print(e)

bot.run(os.getenv("TOKEN"))  # runs the bot
