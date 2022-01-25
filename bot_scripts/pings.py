import time

from .config import config

ping_cache = {}

async def ready_pings(queue):
    for ping_rule in queue.bot_data.ping_rules:
        if (ping_rule['_id'] not in ping_cache) or (time.time() - ping_cache[ping_rule['_id']] > 60 * config['ping_cooldown']):
            if (queue.id in ping_rule['player_threshold']) and (queue.player_count >= ping_rule['player_threshold'][queue.id]) and (ping_rule['player_threshold'][queue.id] != 0):
                matching_member = queue.bot_data.guild.get_member(ping_rule['_id'])
                if matching_member:
                    ping_cache[ping_rule['_id']] = time.time()
                    await matching_member.send('There are now ' + str(queue.player_count) + ' players in the ' + queue.id + ' queue.')
