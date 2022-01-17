import os

import discord
from discord.ext import tasks

import bot_scripts.util as util
from bot_scripts.commands import commands
from bot_scripts.bot_data import bot_data

token = util.read_f('token.txt')

client = discord.Client()

guild_id = 'Fluffy\'s Pavlov Matchmaking'

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == guild_id:
            print('found matching guild!')
            bot_data.load(guild)
            bot_data.queues.debug_mode = True

    print(f'{client.user} has connected to Discord!')

    regular_tasks.start()

@client.event
async def on_message(message):
    if message.content[0] == '!':
        base_cmd = message.content.split(' ')[0][1:]
        if base_cmd in commands:
            await commands[base_cmd](message, message.content.split(' '))

@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.channel.category == bot_data.matches_category:
        for match in bot_data.active_matches:
            await match.process_reaction(reaction, user)

@tasks.loop(seconds=1)
async def regular_tasks():
    for match in bot_data.active_matches:
        if match.waiting_to_gen:
            await match.full_init()

client.run(token)
