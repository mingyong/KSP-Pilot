# coding=utf-8
import os
import threading
import logging

import colorama
import krpc

intro = """KSP-Pilot v{}
Author: {}
"""

help = """exit/quit: 退出
help: 帮助"""


class Pilot():
    __author__ = 'miswanting'
    __version__ = '0.1.0-alpha'
    
    def __init__(self):
        colorama.init()
        self.isRunning = {}
        self.isRunning['pilot'] = True
        os.system('title KSP-Pilot v{}'.format(self.__version__))
        logging.basicConfig(filename='Pilot.log', level=logging.DEBUG, filemode='w',
                            format='%(relativeCreated)d[%(levelname).4s][%(threadName)-.10s]%(message)s')
        print(intro.format(self.__version__, self.__author__))
        self.startInputStar()
    
    def startInputStar(self):
        def inputStar():
            self.isRunning['inputStar'] = True
            while self.isRunning['inputStar']:
                cmd = input()
                if cmd != '':
                    logging.debug('用户输入：{}'.format(cmd))
                    if cmd == 'exit' or cmd == 'quit':
                        print('用户退出！')
                        logging.info('用户退出！')
                        self.isRunning['inputStar'] = False
                    elif cmd == 'help':
                        print(help)
                    else:
                        self.do(cmd)
                else:
                    logging.debug('用户输入回车！')
        
        self.inputStar = threading.Thread(name='input', target=inputStar)
        self.inputStar.start()
        self.inputStar.join()
    
    def do(self, cmd):
        cmd = cmd.split(' ')
        print(cmd)
        if cmd[0] == '':
            pass


if __name__ == '__main__':
    I = Pilot()
