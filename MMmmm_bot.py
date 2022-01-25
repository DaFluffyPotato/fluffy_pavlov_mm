import os

import discord
from discord.ext import tasks

import bot_scripts.util as util
from bot_scripts.commands import commands
from bot_scripts.bot_data import bot_data

token = util.read_f('token.txt')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

guild_id = 'Fluffy\'s Pavlov Matchmaking'

tick_count = 0

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == guild_id:
            print('found matching guild!')
            bot_data.load(client, guild)
            #bot_data.queues.debug_mode = True

    print('Connected to Discord!')

    regular_tasks.start()

@client.event
async def on_message(message):
    if len(message.content):
        if message.content[0] == '!':
            base_cmd = message.content.split(' ')[0][1:].lower()
            if base_cmd in commands:
                await commands[base_cmd](message, message.content.split(' '))

            for match in bot_data.active_matches:
                await match.process_message(message)

@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.channel.category == bot_data.matches_category:
        for match in bot_data.active_matches:
            await match.process_reaction(reaction, user)
    for duo_invite in bot_data.duo_invites:
        await duo_invite.process_reaction(reaction, user)

@tasks.loop(seconds=1)
async def regular_tasks():
    global tick_count
    tick_count += 1

    if tick_count % 10 == 0:
        biggest_queue = [None, 0]
        for queue in bot_data.queues.queues.values():
            if len(queue.users) > biggest_queue[1]:
                biggest_queue = [queue.id, len(queue.users)]

        if biggest_queue[0] == None:
            activity = discord.Game(name='nobody in queue')
        else:
            activity = discord.Game(name=str(biggest_queue[1]) + ' player in ' + biggest_queue[0])
        await client.change_presence(activity=activity)

    for duo_invite in bot_data.duo_invites[::-1]:
        await duo_invite.tick()
        if duo_invite.resolved:
            bot_data.duo_invites.remove(duo_invite)

    if bot_data.queues:
        await bot_data.queues.tick()
    for match in bot_data.active_matches[::-1]:
        if match.waiting_to_gen:
            await match.full_init()
        elif not match.completed:
            await match.tick()
        else:
            bot_data.active_matches.remove(match)

client.run(token)
