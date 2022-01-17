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
