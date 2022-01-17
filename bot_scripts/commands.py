import sys

import discord

from .user import User
from .bot_data import bot_data
from .config import config

commands = {}

def reg_command(command):
    commands[command.__name__] = command

@reg_command
async def ping(message, args):
    await message.channel.send('pong!')

@reg_command
async def stop_bot(message, args):
    await message.channel.send('stopping!')
    await sys.exit()

@reg_command
async def inqueue(message, args):
    queue_id = bot_data.queues.find_channel_queue(message.channel.id)
    if queue_id:
        queue = bot_data.queues.queues[queue_id]
        queue_str = str(queue.player_count) + ' players in the ' + queue.id + ' queue: ' + queue.user_list_str
        await message.channel.send(queue_str)

@reg_command
async def ready(message, args):
    queue_id = bot_data.queues.find_channel_queue(message.channel.id)
    if queue_id:
        queue = bot_data.queues.queues[queue_id]
        join_success = bot_data.queues.join_queue(User(bot_data, message.author), queue_id)
        if join_success:
            await message.channel.send(message.author.display_name + ' joined the ' + queue.id + ' queue. ' + str(queue.player_count) + ' players in queue.')
        else:
            await message.channel.send('Failed to join queue. Please finish any existing games and leave all other queues.')

@reg_command
async def unready(message, args):
    queue_id = bot_data.queues.find_channel_queue(message.channel.id)
    if queue_id:
        queue = bot_data.queues.queues[queue_id]
        bot_data.queues.leave_queue(User(bot_data, message.author), queue_id)
        await message.channel.send(message.author.display_name + ' left the ' + queue.id + ' queue. ' + str(queue.player_count) + ' players in queue.')

@reg_command
async def clear_matches(message, args):
    if message.channel.name == config['admin_commands_channel']:
        for channel in bot_data.matches_category.channels:
            await channel.delete()
        roles = await bot_data.guild.fetch_roles()
        for role in roles:
            if role.name.split('-')[0] == 'match':
                await role.delete()
        bot_data.active_matches = []
        await message.channel.send('cleared matches!')
