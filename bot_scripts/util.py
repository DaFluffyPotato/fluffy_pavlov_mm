from .config import config

emoji_numbers = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']

def read_f(path):
    f = open(path, 'r')
    dat = f.read()
    f.close()
    return dat

def grammatical_list(strings):
    output = ''
    for i, string in enumerate(strings):
        if i != 0:
            if len(strings) != 2:
                output += ','
            if i == len(strings) - 1:
                output += ' and '
            else:
                output += ' '
        output += string
    return output

def emoji_list(strings):
    output = ''
    for i, string in enumerate(strings):
        output += emoji_numbers[i + 1] + ' - ' + string + '\n'
    return output[:-1]

def calc_rank(mmr):
    for rank in config['ranks']:
        if mmr > rank[1]:
            return rank[0]
    return rank[0]
