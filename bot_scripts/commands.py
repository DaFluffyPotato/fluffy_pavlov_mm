import time
import sys

import discord

from .user import User
from .duo_invite import DuoInvite
from .bot_data import bot_data
from .config import config
from .util import calc_rank
from .pings import ready_pings

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

        target_user = User(bot_data, message.author)
        if target_user.banned:
            await message.channel.send('Failed to join queue. Your account has been banned from readying up for the next ' + str(int((target_user.ban_until - time.time()) / 60) + 1) + ' minutes.')
            return None

        duo_msg = ''
        for duo in queue.duos:
            if message.author.id in duo:
                matching_partners = await message.guild.query_members(user_ids=duo[abs(duo.index(message.author.id) - 1)])
                if len(matching_partners):
                    duo_partner = matching_partners[0].name
                    duo_msg = ' Attempting duo with ' + duo_partner + '.'

        join_success = bot_data.queues.join_queue(target_user, queue_id, ready_dur)
        if join_success:
            await ready_pings(bot_data.queues.queues[queue_id])
            await message.channel.send(message.author.display_name + ' joined the ' + queue.id + ' queue (' + str(ready_dur) + ' mins). ' + str(queue.player_count) + ' players in queue.' + duo_msg)
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
async def aroundme(message, args):
    queue_id = bot_data.queues.find_channel_queue(message.channel.id)

    user = User(bot_data, message.author)
    nearby_users = user.get_nearby_users(queue_id)

    message_text = '```'
    for user in nearby_users:
        message_text += '#' + str(user['rank'])  + ': ' + user['name'] + ' - ' + str(round(user['queue_stats'][queue_id]['mmr'] if queue_id in user['queue_stats'] else 0.0, 1)) + '\n'
    if message_text[-1] == '\n':
        message_text = message_text[:-1]
    message_text += '```'

    await message.channel.send(message_text)

@reg_command
async def pingme(message, args):
    queue_id = bot_data.queues.find_channel_queue(message.channel.id)

    try:
        threshold = int(args[1])
    except:
        await message.channel.send('Please specify a player count threshold. Set 0 to disable.')
        return

    bot_data.db.db['ping_rules'].update_one({'_id': message.author.id}, {'$set': {'player_threshold.' + queue_id: threshold}}, upsert=True)
    bot_data.refresh_ping_rules()
    if threshold == 0:
        await message.channel.send('Removed your ping threshold for the `' + queue_id + '` queue.')
    else:
        await message.channel.send('Set your ping threshold for the `' + queue_id + '` queue to `' + str(threshold) + '`.')

@reg_command
async def duoinvite(message, args):
    queue_id = bot_data.queues.find_channel_queue(message.channel.id)
    if queue_id:
        if len(message.mentions):
            invite_initiator = User(bot_data, message.author)
            invite_target = User(bot_data, message.mentions[0])

            if (invite_initiator.get_mmr(queue_id) > config['duo_limit']) or (invite_target.get_mmr(queue_id) > config['duo_limit']):
                await message.channel.send('Both players must be below the duo mmr limit of ' + str(config['duo_limit']) + ' to duo.')
                return None

            new_invite = DuoInvite(bot_data, queue_id, message, invite_initiator, invite_target)
            await new_invite.generate()
            bot_data.duo_invites.append(new_invite)
        else:
            await message.channel.send('Please mention the user you would like to invite.')

@reg_command
async def duoleave(message, args):
    queue_id = bot_data.queues.find_channel_queue(message.channel.id)
    if queue_id:
        queue = bot_data.queues.queues[queue_id]
        print(queue.duos)
        for duo in queue.duos[::-1]:
            if message.author.id in duo:
                queue.duos.remove(duo)
        print(queue.duos)

        await message.channel.send(message.author.name + ' left all duos in this queue.')

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
        match.completed = True
        await message.channel.send('nullified match `' + str(match_id) + '`.')

@reg_command
async def temp_ban(message, args):
    if message.channel.name == config['admin_commands_channel']:
        ban_duration = int(args[1])
        if len(message.mentions):
            target_user = User(bot_data, message.mentions[0])
            target_user.ban(ban_duration)
            await message.channel.send('temp banned ' + target_user.name + ' for ' + str(ban_duration) + ' minutes.')

@reg_command
async def unban(message, args):
    if message.channel.name == config['admin_commands_channel']:
        if len(message.mentions):
            target_user = User(bot_data, message.mentions[0])
            target_user.ban(-1)
            await message.channel.send('unbanned ' + target_user.name + '.')

#aliases
commands['cm'] = commands['clear_matches']
commands['r'] = commands['ready']
commands['ur'] = commands['unready']
commands['in'] = commands['inqueue']
commands['s'] = commands['stats']
commands['sb'] = commands['stop_bot']
commands['am'] = commands['aroundme']
