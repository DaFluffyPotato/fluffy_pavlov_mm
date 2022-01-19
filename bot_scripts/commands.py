import sys

import discord

from .user import User
from .bot_data import bot_data
from .config import config
from .util import calc_rank

commands = {}

def reg_command(command):
    commands[command.__name__] = command

@reg_command
async def ping(message, args):
    await message.channel.send('pong!')

@reg_command
async def stop_bot(message, args):
    if message.channel.name == config['admin_commands_channel']:
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

        ready_dur = 30
        if len(args) > 1:
            try:
                ready_dur = int(args[1])
                ready_dur = max(1, min(120, ready_dur))
            except ValueError:
                pass

        join_success = bot_data.queues.join_queue(User(bot_data, message.author), queue_id, ready_dur)
        if join_success:
            await message.channel.send(message.author.display_name + ' joined the ' + queue.id + ' queue (' + str(ready_dur) + ' mins). ' + str(queue.player_count) + ' players in queue.')
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
async def stats(message, args):
    queue_id = bot_data.queues.find_channel_queue(message.channel.id)
    target_user = message.author
    if len(message.mentions):
        target_user = message.mentions[0]
    elif len(args) >= 2:
        for user in bot_data.guild.members:
            if user.name == args[1]:
                target_user = user
    if queue_id:
        target_user_obj = User(bot_data, target_user)
        target_user_stats = target_user_obj.get_stats(queue_id)

        message_text = '**' + target_user_obj.name + '** (' + queue_id + ')\n'
        message_text += 'Rank: #' + str(target_user_stats['rank']) + ' - ' + calc_rank(target_user_obj.get_mmr(queue_id)) + '\n'
        message_text += 'MMR: ' + str(round(target_user_obj.get_mmr(queue_id), 1)) + '\n'
        message_text += 'Wins: ' + str(target_user_stats['wins']) + '\n'
        message_text += 'Losses: ' + str(target_user_stats['losses']) + '\n'
        message_text += 'Winrate: ' + str(round(target_user_stats['winrate'] * 100, 1)) + '%\n'
        message_text += '\nHistory:\n'
        message_text += ''.join([bot_data.emotes['win'][0] if (match == 1) else bot_data.emotes['loss'][0] for match in target_user_stats['history'][-10:][::-1]])

        await message.channel.send(message_text)

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

@reg_command
async def clear_queue(message, args):
    if message.channel.name == config['admin_commands_channel']:
        queue_id = args[1]
        bot_data.queues.queues[queue_id].clear()
        await message.channel.send('cleared `' + queue_id + '` queue!')

@reg_command
async def nullify(message, args):
    if message.channel.name == config['admin_commands_channel']:
        match_id = int(args[1])
        match = bot_data.get_match(match_id)
        await match.clear()
        await message.channel.send('nullified match `' + str(match_id) + '`.')

#aliases
commands['cm'] = commands['clear_matches']
commands['r'] = commands['ready']
commands['ur'] = commands['unready']
commands['in'] = commands['inqueue']
commands['s'] = commands['stats']
commands['sb'] = commands['stop_bot']
