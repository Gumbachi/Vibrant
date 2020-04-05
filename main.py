import json
import os
import random

import discord
from discord.ext import commands

import database as db
from classes import Guild
from cogs.color.color_assignment import color_user
from utils import check_hex, rgb_to_hex
from authorization import authorize
from vars import bot, extensions, get_prefix, waiting_on_hexcode


@bot.event
async def on_ready():
    """Change presence and collects data from mongo database"""
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.playing,
                                  name="@Vibrant for help"))

    # get preferences from DB
    print("Fetching Preferences...")
    db.get_prefs()

    # collect new guilds and create objects for them
    print("Generating Objects...")
    new_ids = {guild.id for guild in bot.guilds} - set(Guild._guilds.keys())
    new_guilds = [Guild(id) for id in new_ids]

    # update DB with new guilds
    print("Updating Database...")
    db.update_prefs(*new_guilds)
    db.clear_abandoned_guilds()

    print("Ready Player One.")


@bot.event
async def on_message(message):
    """Message listener."""
    # make sure it doesnt run when bot writes message
    if message.author == bot.user:
        return

    # types prefix if bot is mentioned
    if message.mentions and message.mentions[0].id == bot.user.id:
        return await message.channel.send(
            f"Type `{get_prefix(bot, message)}`help for help.")

    # handles message verification if user is adding a color via reaction
    if message.author.id in waiting_on_hexcode.keys():
        id = message.author.id
        hexcode_data = waiting_on_hexcode[id]
        if message.channel.id == hexcode_data["message"].channel.id:
            ctx = await bot.get_context(message)
            if check_hex(message.content):
                await ctx.invoke(bot.get_command("add"), hexcode=message.content, name=hexcode_data["color"])
            else:
                await ctx.send("Invalid Hexcode. Please try again")
                await hexcode_data["message"].edit(
                    content=f"{hexcode_data['message'].content}**Cancelled**")
        del waiting_on_hexcode[id]  # remove user from pool

    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    """Sends a welcome message and attempts to randomly color a user when a
    member joins a server the bot is in"""
    guild = Guild.get(member.guild.id)

    if not guild or not guild.welcome_channel:
        return

    # make sure embed can be sent with or without colors
    if guild.colors:
        color = guild.random_color()  # get random color
        await color_user(guild, member, color)
        accent = discord.Color.from_rgb(*color.rgb)  # discord format
    else:
        color = None
        accent = discord.Color.green()

    # generate and send weclome embed message
    embed = discord.Embed(
        title=f"{member.name} has joined the server!",
        description=f"Please give {member.mention} a warm welcome!",
        color=accent)
    embed.set_thumbnail(url=member.avatar_url)

    await guild.welcome_channel.send(embed=embed)

    if color:
        db.update_prefs(guild)


@bot.event
async def on_member_remove(member):
    """Sends a goodbye message when a member leaves a server the bot is in"""
    guild = Guild.get(member.guild.id)

    # check if welcome channel or guild exists
    if not guild or not guild.welcome_channel:
        return

    # generate and send goodbye message
    embed = discord.Embed(title=f"{member.name} has left the server!",
                          description="They won't be missed",
                          color=discord.Color.red())
    embed.set_thumbnail(url=member.avatar_url)

    await guild.welcome_channel.send(embed=embed)


@bot.event
async def on_member_update(before, after):
    """updates color info if a users color role is manually removed"""
    # check if any roles changed
    if before.roles == after.roles:
        return

    guild = Guild.get(before.guild.id)

    # convert roles to set for comparison
    roles_before = set(before.roles)
    roles_after = set(after.roles)

    # find difference between sets
    removed_roles = roles_before - roles_after
    added_roles = roles_after - roles_before

    # role removed
    if removed_roles:
        for role in removed_roles:
            color = guild.get_color("role_id", role.id)
            if color:
                color.member_ids.discard(before.id)
                if not color.member_ids:
                    try:
                        await role.delete()
                    except discord.errors.NotFound:
                        pass

    # role added
    if added_roles:
        for role in added_roles:
            color = guild.get_color("role_id", role.id)
            if color:
                color.member_ids.add(before.id)


@bot.event
async def on_guild_join(guild):
    """Create new object and update database when the bot joins a guild."""
    print(f"ADDED TO {guild.name}")
    new_guild = Guild(guild.id)
    db.update_prefs(new_guild)


@bot.event
async def on_guild_remove(guild):
    """Delete guild object and db document when bot leaves a guild."""
    print(f"REMOVED FROM {guild.name}")
    Guild._guilds.pop(guild.id)  # remove from internal list
    db.coll.delete_one({"id": guild.id})  # remove from MongoD


@bot.event
async def on_guild_update(before, after):
    """Updates Guild object name if changed"""
    guild = Guild.get(before.id)
    guild.name = after.name  # change name
    db.update_prefs(guild)  # update mongoDB


@bot.event
async def on_guild_channel_delete(channel):
    """Removes a channel from the Guild object if user deletes it"""
    guild = Guild.get(channel.guild.id)

    # remove from disabled channels
    if channel.id in guild.disabled_channel_ids:
        guild.disabled_channel_ids.remove(channel.id)

    # unsets welcome channel if deleted
    if channel.id == guild.welcome_channel_id:
        guild.welcome_channel_id = None

    db.update_prefs(guild)


@bot.event
async def on_guild_role_delete(role):
    """Removes a role from the Guild object if user deletes it"""
    guild = Guild.get(role.guild.id)

    # sets color role id to none if it is deleted
    color = guild.get_color("role_id", role.id)
    if color:
        color.role_id = None
        db.update_prefs(guild)  # update MongoDB


@bot.event
async def on_guild_role_update(before, after):
    """Removes a role from the Guild object if user deletes it"""
    guild = Guild.get(before.guild.id)

    # checks if color has role and change color name and hex to reflect change
    color = guild.get_color('role_id', before.id)
    if color:
        color.name = after.name
        color.hexcode = str(after.color)
        db.update_prefs(guild)  # update MongoDB

# loads extensions(cogs) listed in vars.py
if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"Couldnt load {extension}")
            # print(e)

bot.run(os.environ["TOKEN"])  # runs the bot
