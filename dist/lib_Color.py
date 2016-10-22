header = '\033'
style = {}
style['none'] = '0'
style['bold'] = '1'
style['underline'] = '2'
style['negative1'] = '3'
style['negative2'] = '5'
text = {}
text['black'] = '30'
text['red'] = '31'
text['green'] = '32'
text['yellow'] = '33'
text['blue'] = '34'
text['purple'] = '35'
text['cyan'] = '36'
text['white'] = '37'
background = {}
background['black'] = '40'
background['red'] = '41'
background['green'] = '42'
background['yellow'] = '43'
background['blue'] = '44'
background['purple'] = '45'
background['cyan'] = '46'
background['white'] = '47'
print('\033[%s;%s;%sm333' % (style['none'], text['white'], background['black']))
print('\033[%s;%s;%sm' % (style['none'], text['white'], background['black']))


def c(t, text='white', style='none', background='black'):
    return '\033[{};{};{}m'.format(text[text], style[style], background[background]) + t + '\033[0;37;40m'
