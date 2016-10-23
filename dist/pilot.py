# coding=utf-8
import os
import threading
import logging
import time
import hashlib
import random

import colorama
import krpc

from collections import deque

intro = """KSP-Pilot v{}
kRPC: {}
Author: {}
"""

help = """exit/quit: 退出
help: 帮助
connect: 连接游戏
disconnect: 断开连接
go: 发射火箭
fly: 飞机"""


class Pilot():
    __author__ = 'miswanting'
    __version__ = '0.1.0-alpha'
    
    def __init__(self):
        colorama.init()
        self.taskList = deque([])
        self.isRunning = {}
        self.isRunning['pilot'] = True
        os.system('title KSP-Pilot v{}'.format(self.__version__))
        logging.basicConfig(filename='Pilot.log', level=logging.DEBUG, filemode='w',
                            format='%(relativeCreated)d[%(levelname).4s][%(threadName)-.10s]%(message)s')
        print(intro.format(self.__version__, krpc.__version__, self.__author__))
        self.startInputStar()
        self.taskList.append('connect')
        self.do()
    
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
                        self.taskList.append(cmd)
                        task = threading.Thread(name=self.getHash(), target=self.do)
                        task.start()
                else:
                    logging.debug('用户输入回车！')
        
        self.inputStar = threading.Thread(name='input', target=inputStar)
        self.inputStar.start()
    
    def do(self):
        cmd = self.taskList.popleft()
        cmd = cmd.split(' ')
        if cmd[0] == 'connect':
            try:
                print('正在连接…')
                logging.info('正在连接…')
                self.conn = krpc.connect(name='KSP-Pilot')
                print('连接成功！kRPC 版本：{}'.format(self.conn.krpc.get_status().version))
                logging.info('连接成功！kRPC 版本：{}'.format(self.conn.krpc.get_status().version))
            except:
                pass
        elif cmd[0] == 'disconnect':
            try:
                print('正在断开连接…')
                logging.info('正在断开连接…')
                self.conn.close()
                print('断开连接！')
                logging.info('断开连接！')
            except:
                pass
        elif cmd[0] == 'go':
            print('正在准备发射…')
            logging.info('正在准备发射…')
            
            print('倒计时：3秒')
            logging.info('倒计时：3秒')
            vessel = self.conn.space_center.active_vessel
            print('火箭名称：{}'.format(vessel.name))
            logging.info('火箭名称：{}'.format(vessel.name))
            time.sleep(1)
            
            print('倒计时：2秒')
            logging.info('倒计时：2秒')
            vessel.auto_pilot.target_pitch_and_heading(90, 90)
            vessel.auto_pilot.engage()
            time.sleep(1)
            
            print('倒计时：1秒')
            logging.info('倒计时：1秒')
            vessel.control.throttle = 1
            time.sleep(1)
            
            print('发射！')
            logging.info('发射！')
            vessel.control.activate_next_stage()
            
            while vessel.resources.amount('LiquidFuel') > 0.1:
                isNoFuel = False
                for part in vessel.parts.all:
                    if part.resources.has_resource('LiquidFuel'):
                        if part.resources.amount('LiquidFuel') < 0.1:
                            isNoFuel = True
                if isNoFuel:
                    print('助推火箭分离！')
                    logging.info('助推火箭分离！')
                    vessel.control.activate_next_stage()
                    text = '助推火箭分离成功！高度：{:.2f}m 速度：{:.2f}m/s'
                    print(vessel.flight().speed)
                    print(text.format(vessel.flight().mean_altitude, vessel.flight().speed))
                    logging.info(text.format(vessel.flight().mean_altitude, vessel.flight().speed))
                
                time.sleep(1)
        
        elif cmd[0] == 'fly':
            print('正在准备起飞…')
            logging.info('正在准备起飞…')
            
            print('倒计时：3秒')
            logging.info('倒计时：3秒')
            vessel = self.conn.space_center.active_vessel
            print('飞行器名称：{}'.format(vessel.name))
            logging.info('飞行器名称：{}'.format(vessel.name))
            time.sleep(1)
            
            print('倒计时：2秒')
            logging.info('倒计时：2秒')
            # vessel.auto_pilot.reference_frame = self.conn.space_center.node.reference_frame
            # vessel.auto_pilot.target_pitch_and_heading(10, 90)
            vessel.auto_pilot.target_pitch = 10
            vessel.auto_pilot.target_heading = 90
            vessel.auto_pilot.target_roll = 0
            vessel.auto_pilot.engage()
            time.sleep(1)
            
            print('倒计时：1秒')
            logging.info('倒计时：1秒')
            vessel.control.throttle = 1
            time.sleep(1)
            
            print('起飞！')
            logging.info('起飞！')
            vessel.control.activate_next_stage()
            
            while True:
                if vessel.situation.name == 'flying':
                    break
                time.sleep(0.1)
            
            print('起飞成功！')
            logging.info('起飞成功！')
            vessel.control.gear = False
            
            while True:
                pass
    
    def getHash(self):
        m = hashlib.md5()
        m.update(str(random.random()).encode("utf-8"))
        return m.hexdigest()


if __name__ == '__main__':
    I = Pilot()
