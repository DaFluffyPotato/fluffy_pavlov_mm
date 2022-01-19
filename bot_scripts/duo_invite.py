import time

class DuoInvite:
    def __init__(self, bot_data, queue_id, invite_message, invite_initiator, invite_target):
        self.queue_id = queue_id
        self.queue = bot_data.queues.queues[self.queue_id]
        self.bot_data = bot_data
        self.invite_message = invite_message
        self.invite_initiator = invite_initiator
        self.invite_target = invite_target
        self.creation_date = time.time()
        self.resolved = False

    async def generate(self):
        await self.invite_message.add_reaction('✅')
        await self.invite_message.add_reaction('❌')

    async def process_reaction(self, reaction, user):
        if user.id == self.invite_target.id:
            if reaction.emoji == '✅':
                await self.invite_message.reply(user.name + ' has accepted the duo.')

                # clear existing conflicting duos
                for duo in self.queue.duos[::-1]:
                    if (self.invite_target.id in duo) or (self.invite_initiator.id in duo):
                        self.queue.duos.remove(duo)

                self.queue.duos.append([self.invite_initiator.id, self.invite_target.id])
                print(self.queue.duos)

                self.resolved = True
            if reaction.emoji == '❌':
                await self.invite_message.reply(user.name + ' has declined the duo.')
                self.resolved = True

    async def tick(self):
        if time.time() - self.creation_date > 120:
            await self.invite_message.reply('This invite has expired.')
            self.resolved = True
