import io
import json
import os
from random import randint
import re

import asyncio
import discord
from discord.ext import commands, tasks
from fuzzywuzzy import fuzz, process

import functions as functions
from functions import is_disabled, update_prefs, check_hex
from functions import pfp_analysis, draw_presets, hex_to_rgb
import vars
from vars import bot, get_prefix, waiting_on_reaction, waiting_on_pfp, waiting_on_hexcode
from classes import Color, Guild
from cfg import coll

class Colors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Draws an image of colors and names to display and sends to channel or user
    @commands.command(name="colors", aliases=["colorset", "colourset", "colours"])
    async def show_colors(self, ctx):
        guild = Guild.get_guild(ctx.guild.id)
        fp = io.BytesIO(guild.draw_colors())#get a bytearray and convert to sendable
        if is_disabled(ctx.channel):
            await ctx.message.delete() #delete message if channel is disabled
            await ctx.author.send(f"**{ctx.guild.name}**:", file=discord.File(fp, filename="colors.png"))#to user
        else:
            await ctx.send(file=discord.File(fp, filename="colors.png"))#to channel

    #color a specific user : restricted to manage_roles
    @commands.command(name="color", aliases=["colour"])
    async def color_specific_person(self, ctx, user, *color):
        if is_disabled(ctx.channel):
            await ctx.message.delete()#delete command if disabled
            return await ctx.author.send(f"#{ctx.channel.name} is disabled")

        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.send("You need the `manage roles` permission to use this command")

        await color_user(ctx, user, color, trace=True)#color user

    #color author : anyone can use
    @commands.command(name="colorme", aliases=['me', "colourme"])
    async def colorme(self, ctx, *color):
        if is_disabled(ctx.channel):
            try: await ctx.message.delete()#delete command if disabled
            except: pass
            return await ctx.author.send(f"#{ctx.channel.name} is disabled")

        await color_user(ctx, ctx.author.name, color, trace=True)#color user

    @commands.command(name="uncolorme", aliases=["uncolourme"])
    async def uncolor_me(self, ctx):
        #check channel status
        if is_disabled(ctx.channel):
            await ctx.message.delete()#delete command if disabled
            return await ctx.author.send(f"#{ctx.channel.name} is disabled")

        guild = Guild.get_guild(ctx.guild.id)
        role = guild.get_color_role(ctx.author)
        if not role:
            return await ctx.send("You don't have a color to remove")

        await ctx.author.remove_roles(role)#remove the role
        await ctx.send(f"{ctx.author.name} no longer has the **{role.name}** color role")
        await update_prefs([guild])

    @commands.command(name="splash", aliases=["colorall", "colourall"])
    async def color_server(self, ctx, qcolor=None, trace=True):
        """
        Gathers all of the uncolored people and assigns them a color

        Args:
            qcolor (str): An optional arg for coloring everyone a single color
            trace (bool): Whether or not the function should print anything
        """
        # check if channel status
        if is_disabled(ctx.channel):
            await ctx.message.delete()
            return await ctx.author.send(f"#{ctx.channel.name} is disabled")

        # check permissions
        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.send(
                "You need the `manage roles` permission to use this command")

        guild = Guild.get_guild(ctx.guild.id)

        # check if there are colors
        if not guild.colors and trace:
            return await ctx.send(embed=vars.none_embed)

        #get specific color
        color = None
        if qcolor:
            color = guild.find_color(qcolor)
            if not color:
                return await ctx.send("Couldn't find that color")

        # get uncolored members
        uncolored = [member.name for member in ctx.guild.members
                     if not guild.get_color_role(member)]

        # estimate time to complete command
        if trace:
            await ctx.send(("Coloring everyone will take around "
                f"{len(uncolored)/2 + (5 * (len(uncolored)//8))} seconds"))

        # loop through and color members
        async with ctx.channel.typing():
            index = randint(1, len(guild.colors)) if not color else color.index
            for counter, name in enumerate(uncolored, 1):
                # pause every 8 colors
                if counter%8 == 0 and counter != len(guild.colors):
                    await asyncio.sleep(5)

                # keep index in range
                if index > len(guild.colors):
                    index = 1

                await color_user(ctx, name, (str(index),), trace=False)

                # increment index
                if not color:
                    index += 1

        # report success
        if trace:
            await ctx.send("Success! Everyone visible has been colored")
        await update_prefs([guild])


    @commands.command(name="set", aliases=["preset", "load"])
    async def set_colors(self, ctx, set_name=None):
        if is_disabled(ctx.channel):
            try: await ctx.message.delete()#delete command if disabled
            except: pass
            return await ctx.author.send(f"#{ctx.channel.name} is disabled")

        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.send("You need `manage roles` permission to use this command")

        if set_name not in vars.preset_names:
            raise commands.UserInputError(f"Couldn't find **{set_name}**")

        #read the file into dict
        sep = os.path.sep
        try:
            with open(f"presets{sep}{set_name}.json") as data_file:
                color_data = json.load(data_file)
        except:
            raise Exception("Couldn't open preset")

        guild = Guild.get_guild(ctx.guild.id)
        colors = guild.colors
        roles_to_remove = guild.get_color_role_ids()

        #send backup just incase
        if colors:
            await ctx.invoke(bot.get_command("export"), trace=False)#show new set

        #delete roles
        async with ctx.channel.typing():
            for role_id in roles_to_remove:
                await ctx.guild.get_role(role_id).delete()
            colors.clear() #empty the colors

            #create new color objects for new set
            for color in color_data:
                guild.colors.append(Color(color['name'], color['hexcode'], ctx.guild.id))

        await update_prefs([guild]) #update MongoDB
        await ctx.invoke(bot.get_command("colors"))

    #add a color
    @commands.command(name="add", aliases=["new", "create"])
    async def add_color(self, ctx, hexcode, *name):
        if is_disabled(ctx.channel):
            try: await ctx.message.delete()#delete command if disabled
            except: pass
            return await ctx.author.send(f"#{ctx.channel.name} is disabled")

        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.send("You need `manage roles` permission to use this command")

        name = " ".join(name)
        if len(name) > 99:
            raise commands.UserInputError(f"**{name}** is too long of a name")

        guild = Guild.get_guild(ctx.guild.id)

        if len(guild.colors) >= guild.color_limit:
            return await ctx.send("You've reached the max amount of colors")

        #use regex to verify proper input
        if re.search(r"[\S]+", name) is None:
            name = f"Color {len(guild.colors) + 1}"
        if re.search(r"[|]+", name):
            raise commands.UserInputError("You cannot use the `|` symbol in color names")

        async with ctx.channel.typing():
            if check_hex(hexcode):
                if hexcode == "#000000":
                    hexcode == "#000001"
                color = Color(name, hexcode, ctx.guild.id)
                guild.colors.append(color)
            else:
                raise commands.UserInputError(f"**{hexcode}** is an invalid hex value. Proper format is: #123abc")

        await ctx.send(f"**{color.name}** has been added in position **{color.index}**.")
        await ctx.invoke(bot.get_command("colors"))#show new set
        await update_prefs([guild])

    @commands.command(name="remove", aliases=["delete"])
    async def remove_color(self, ctx, *name):
        if is_disabled(ctx.channel):
            await ctx.message.delete()#delete command if disabled
            return await ctx.author.send(f"#{ctx.channel.name} is disabled")

        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.send("You need `manage roles` permission to use this command")

        guild = Guild.get_guild(ctx.guild.id)
        colors = guild.colors
        name = " ".join(name)

        #verify input and prep
        if not colors:
            return await ctx.send(embed=vars.none_embed)

        color = guild.find_color(name, 95)
        if not color:
            raise commands.UserInputError(f"Couldn't find **{name}**. Try using an index or type `{get_prefix(bot, ctx.message)}help remove` for more help")
        await color.delete()

        await ctx.send(f"**{color.name}** has been deleted!")
        await ctx.invoke(bot.get_command("colors"))#show new set
        await update_prefs([guild])

    #rename a color
    @commands.command("rename")
    async def rename_color(self, ctx, *name):
        if is_disabled(ctx.channel):
            await ctx.message.delete()#delete command if disabled
            return await ctx.author.send(f"#{ctx.channel.name} is disabled")

        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.send("You need `manage roles` permission to use this command")

        name = " ".join(name)
        await swap(ctx, name, "rename")

    #change hexcode of a color
    @commands.command(name="recolor", aliases=["recolour"])
    async def recolor(self, ctx, *name):
        if is_disabled(ctx.channel):
            try: await ctx.message.delete()#delete command if disabled
            except: pass
            return await ctx.author.send(f"#{ctx.channel.name} is disabled")

        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.send("You need `manage roles` permission to use this command")

        name = " ".join(name)
        await swap(ctx, name, "recolor")

    #remove all colors
    @commands.command(name="clear_all_colors", aliases=["clear_all_colours"])
    async def clear_colors(self, ctx, trace=True):
        if is_disabled(ctx.channel):
            await ctx.message.delete()
            return await ctx.author.send(f"#{ctx.channel.name} is disabled")

        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.send("You need `manage roles` permission to use this command")

        guild = Guild.get_guild(ctx.guild.id)
        if trace:
            await ctx.invoke(bot.get_command("export"), trace=False)#show new set

        async with ctx.channel.typing():
            #loop through all colors and delete
            while guild.colors:
                #delete colors
                for color in guild.colors:
                    await color.delete()
            if trace:
                await ctx.send(f"Success! All colors have been removed.")
        await update_prefs([guild])

    #attempts to find most prevalent color in a users profile picutre
    @commands.command("pfp")
    async def get_pfp_color(self, ctx, *name):

        #find the right user
        user = " ".join(name)
        if user == "":
            user = ctx.author

        #check mentions
        elif ctx.message.mentions:
            user = ctx.message.mentions[0]

        #try fuzzy matching
        else:
            member_names = [member.name for member in ctx.guild.members]
            best_user, _ = process.extractOne(user, member_names)
            for member in ctx.guild.members:
                if member.name == best_user:
                    user = member
                    break

        hexcode = pfp_analysis(user.avatar_url)#try to get the best color
        await ctx.send(f"**{hexcode}** matches {user.name}'s profile picture.")
        if ctx.author.guild_permissions.manage_roles:
            prompt =  await ctx.send(f"Would you like to add {hexcode} to your colors?")
            return await add_color_UX(prompt, ctx.author, user.name, hexcode=hexcode)

    #export colors data in json format
    @commands.command("export")
    async def export_colors(self, ctx, trace=True):
        #check for colors
        if not Guild.get_guild(ctx.guild.id).colors:
            return await ctx.send(embed=vars.none_embed)

        #find guild in database and convert to bytes
        if coll.find_one({"id": ctx.guild.id}) is not None:
            colors = coll.find_one({"id": ctx.guild.id})["colors"]
            data = json.dumps(colors, indent=2).encode("utf-8")
            bytes_data = io.BytesIO(data)

            #send data in JSON format
            if trace:
                return await ctx.send(f"JSON file for **{ctx.guild.name}**'s colors:", file = discord.File(bytes_data, filename = f"{ctx.guild.name}_colors.json"))
            else:
                return await ctx.send(file=discord.File(bytes_data, filename=f"{ctx.guild.name}_backup.json"))
        else:
            return Exception("Couldn't find guild. Must be a database error")

    #import data from JSON file
    @commands.command("import")
    async def import_colors(self, ctx):
        if is_disabled(ctx.channel):
            await ctx.message.delete()#delete command if disabled
            return await ctx.author.send(f"#{ctx.channel.name} is disabled")

        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.send("You need `manage roles` permission to use this command")

        #check for attachments
        if not ctx.message.attachments or not ctx.message.attachments[0].filename.endswith(".json"):
            raise commands.UserInputError("Please include a formatted JSON file")

        json_data = json.loads(await ctx.message.attachments[0].read())#load data into a dictionary

        #check file formatting for colors as a list
        if not isinstance(json_data, list):
            raise commands.UserInputError('File is formatted improperly: The file is not structured as a list')

        #check for dictionary type for colors in the list
        for item in json_data:
            if not isinstance(item, dict):
                raise commands.UserInputError('File is formatted improperly: An item in the list is not a python dictionary type')

        #create dictionary of colors
        for color in json_data:
            color["role_id"] = None
            color["guild_id"] = ctx.guild.id

            #check for proper attrs
            if "hexcode" not in color.keys() or "name" not in color.keys():
                raise commands.UserInputError('File is formatted improperly: A color missing "name" or "hexcode" attribute in file')

        guild = Guild.get_guild(ctx.guild.id)
        #send a backup json just in case :)
        if guild.colors:
            await ctx.send("**Backup:**")

        await ctx.invoke(bot.get_command("clear_all_colors"), trace=False)#remove all current colors

        for color in json_data:
            guild.colors.append(Color.from_json(color))#create new color
        await ctx.invoke(bot.get_command("colors"))#display new set
        await update_prefs([guild])#update MongoDB

    @commands.command(name="presets", aliases=["show", "preview"])
    async def preview_colors(self, ctx, set_name=None):
        if not set_name:
            fp = io.BytesIO(draw_presets())#get a bytearray and convert to sendable
            if is_disabled(ctx.channel):
                try:
                    await ctx.message.delete()
                    return await ctx.author.send(f"Presets:", file=discord.File(fp, filename="presets.png"))
                except: pass
            else:
                return await ctx.send(f"Presets:", file=discord.File(fp, filename="presets.png"))

        if set_name not in vars.preset_names:
            raise commands.UserInputError(f"Couldn't find **{set_name}**")

        #read the file into dict
        #sep = os.path.sep
        # try:
        #     with open(f"presets{sep}{set_name}.json") as data_file:
        #         json_data = json.load(data_file)
        # except:
        #     raise Exception(f"Couldn't open preset")


                #need to rework this
        #draw and send colors
        # fp = io.BytesIO(draw_colors(json_data, obj_form=False))#get a bytearray and convert to sendable
        # if is_disabled(ctx.channel):
        #     try:await ctx.message.delete() #delete message if channel is disabled
        #     except:pass
        #     await ctx.author.send(f"**{ctx.guild.name}**:", file=discord.File(fp, filename="colors.png"))#to user
        # else:
        #     await ctx.send(file=discord.File(fp, filename="colors.png"))#to channel

    @commands.command(name="info", aliases=["about"])
    async def show_color_info(self, ctx, color_name):
        guild = Guild.get_guild(ctx.guild.id)

        color = guild.find_color(color_name, threshold=0)
        print(color)
        if not color:
            raise commands.UserInputError(
                f"Couldn't find {color_name}. Try using an index for more accurate results")

        rgb = color.rgb
        member_names = [bot.get_user(id).name for id in color.members]
        color_embed = discord.Embed(
            title=color.name,
            description=(f"Hexcode: {color.hexcode}\n"
                         f"RGB: {rgb}\n"
                         f"Members: {', '.join(member_names)}\n"
                         f"Index: {color.index}\n"
                         f"Role ID: {color.role_id}"),
            color=discord.Color.from_rgb(*color.rgb))

        # manage recipient and cleanup if needed
        if is_disabled(ctx.channel):
            await ctx.message.delete()
            await ctx.author.send(embed=color_embed)# to user
        else:
            await ctx.send(embed=color_embed)

def setup(bot):
    bot.add_cog(Colors(bot))

async def color_user(ctx, quser, qcolor, trace=True):
    """Colors a specific user"""

    guild = Guild.get_guild(ctx.guild.id)
    colors = guild.colors
    qcolor = " ".join(qcolor)

    #check for empty colors
    if not colors and trace:
        return await ctx.send(embed=vars.none_embed)

    user = functions.find_user(ctx.message, quser, ctx.guild)
    if not user:
        raise commands.UserInputError(f"Couldn't find **{quser}**. You should mention a user for a 100% success rate")

    color = guild.find_color(qcolor)
    print(color)
    if not color:
        if ctx.author.guild_permissions.manage_roles:
            prompt = await ctx.send(f"Couldn't find that color. Would you like to add **{qcolor}**?")
            return await add_color_UX(prompt, ctx.author, qcolor)
        else:
            raise commands.UserInputError(f"Couldn't find **{qcolor}**. Try again with an index or more precise name")

    #remove user's current color roles
    role = guild.get_color_role(user)
    if role:
        await user.remove_roles(role)

    #check if role already exists and assigns then ends process if true
    if color.role_id:
        color_role = guild.get_role(color.role_id)
        if color_role:
            await user.add_roles(color_role)
        else:
            color.role_id = None # fix role assignment
    if not color.role_id:
        color_role = await ctx.guild.create_role(name=color.name, color=discord.Color.from_rgb(*color.rgb))
        color.role_id = color_role.id
        await user.add_roles(color_role)

    print(f"COLORING {user} -> {color.name}")
    if trace:
        await ctx.send(f"Gave **{user.name}** the **{color_role.name}** role")
    await update_prefs([guild])

async def swap(ctx, user_input, action):
    """
    Swaps the color or name of a Color object

    Args:
        user_input (str): The input string containing before and after
        action (str): The action to perform
    """
    guild = Guild.get_guild(ctx.guild.id)

    # check if there are colors
    if not guild.colors:
        return await ctx.send(embed=vars.none_embed)

    # verify input
    if not re.search(r"[\d\w\s]+[|]{1}[\d\w\s]+", user_input):
        raise commands.UserInputError(f"**{user_input}** is not a valid input")
    try:
        before, after = user_input.split("|")
    except:
        raise commands.UserInputError("There are too many separators in your input")

    # strip extraneous spaces
    before = before.strip()
    after = after.strip()

    # find color to change
    color = guild.find_color(before, threshold=90)
    if not color:
        raise commands.UserInputError(f"Couldn't find **{before}**. Try using a color's index for better results")

    #rename the color
    if action == "rename":
        await ctx.send(f"**{color.name}** is now named **{after}**")
        color.name = after

    # change the hexcode of the color
    if action == "recolor":
        if check_hex(after):
            await ctx.send(f"Recolored **{color.name}**'s color to **{after}**")
            color.hexcode = after
            color.rgb = hex_to_rgb(after)
        else:
            raise commands.UserInputError(f"**{after}** is an invalid hex code.Proper Format: #123abc")

    # adjust roles if color is changed
    if color.role_id:
        role = guild.get_role(color.role_id)
        await role.edit(name=color.name, color=discord.Color.from_rgb(*color.rgb))

    await update_prefs([guild])#update mongoDB

async def add_color_UX(message, author, color, hexcode=None):
    await message.add_reaction(vars.emoji_dict["checkmark"])
    await message.add_reaction(vars.emoji_dict["crossmark"])
    if not hexcode:
        waiting_on_reaction[author.id] = {"message": message, "color": color}
        try:
            del vars.waiting_on_hexcode[author.id]
        except:
            pass
    else:
        waiting_on_pfp[author.id] = {"message": message, "color": color, "hexcode": hexcode}

@bot.event
async def on_reaction_add(reaction, user):
    if user.id == bot.user.id:
        return

    #check reaction for adding color
    if user.id in waiting_on_reaction.keys():
        waiting_data = waiting_on_reaction[user.id]
        if reaction.message.id == waiting_data["message"].id:
            if reaction.emoji == vars.emoji_dict["checkmark"]:
                await reaction.message.clear_reactions()
                prompt = await reaction.message.channel.send(f"{user.mention}, What will be the hexcode for **{waiting_data['color']}**")
                waiting_on_hexcode[user.id] = {"message": prompt, "color": waiting_data['color']}
            elif reaction.emoji == vars.emoji_dict["crossmark"]:
                await reaction.message.clear_reactions()
                await reaction.message.edit(content=f"{reaction.message.content} **Cancelled**")
        else:
            await waiting_data["message"].clear_reactions()
            await waiting_data["message"].edit(content=f"{reaction.message.content} **Cancelled**")
        del waiting_on_reaction[user.id] 

    #check reaction for adding pfp color
    if user.id in waiting_on_pfp.keys():
        pfp_data = waiting_on_pfp[user.id]
        ctx = await bot.get_context(pfp_data["message"])
        if reaction.message.id == pfp_data["message"].id:
            if reaction.emoji == vars.emoji_dict["checkmark"]:
                await reaction.message.clear_reactions()
                await ctx.invoke(bot.get_command("add"), pfp_data["hexcode"], pfp_data["color"])
            elif reaction.emoji == vars.emoji_dict["crossmark"]:
                await reaction.message.delete()
        else:
            await pfp_data["message"].delete()
        del waiting_on_pfp[user.id]
