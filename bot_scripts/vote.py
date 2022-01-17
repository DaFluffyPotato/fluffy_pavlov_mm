import time

from .util import emoji_numbers as numbers

class Vote:
    def __init__(self, message, option_count, max_choices=1, duration=30):
        self.message = message
        self.option_count = option_count
        self.max_choices = max_choices
        self.start_time = time.time()
        self.duration = duration

        self.user_votes = {}

        self.result = None

    async def finish_init(self):
        for i in range(self.option_count):
            await self.message.add_reaction(numbers[i + 1])

    def process_reaction(self, reaction, user):
        if not self.result:
            if (reaction.message == self.message) and (reaction.message.author.id != user.id):
                if reaction.emoji in numbers:
                    if user.id not in self.user_votes:
                        self.user_votes[user.id] = {}
                    if sum(self.user_votes[user.id].values()) < self.max_choices:
                        if reaction.emoji not in self.user_votes[user.id]:
                            self.user_votes[user.id][reaction.emoji] = 0
                        self.user_votes[user.id][reaction.emoji] += 1

    def tick(self):
        if not self.result:
            time_passed = time.time() - self.start_time
            if time_passed >= self.duration:
                votes = {}
                for user in self.user_votes:
                    for option in self.user_votes[user]:
                        option_str = str(numbers.index(option)) # convert emoji into number
                        if option_str not in votes:
                            votes[option_str] = self.user_votes[user][option]
                        else:
                            votes[option_str] += self.user_votes[user][option]
                self.result = [(int(vote_id), votes[vote_id]) for vote_id in votes]
