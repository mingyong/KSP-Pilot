# coding=utf-8
import os
import threading
import logging
import time
import hashlib
import random
import math
import pygame
import pyglet

import colorama
import krpc

from collections import deque
from gtts import gTTS
from tempfile import TemporaryFile

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
        self.player = pyglet.media.Player()
        self.player.play()
        self.taskList = deque([])
        self.soundList = deque([])
        self.startPlayer()
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
            
            text = self.play('倒计时：3秒')
            print(text)
            logging.info(text)
            vessel = self.conn.space_center.active_vessel
            print('火箭名称：{}'.format(vessel.name))
            logging.info('火箭名称：{}'.format(vessel.name))
            time.sleep(1)
            
            text = '倒计时：2秒'
            print(text)
            logging.info(text)
            turn_start_altitude = 250
            turn_end_altitude = 45000
            target_altitude = 1
            print('目标高度：{}'.format(target_altitude))
            logging.info('目标高度：{}'.format(target_altitude))
            time.sleep(1)
            
            text = '倒计时：1秒'
            print(text)
            logging.info(text)
            vessel.control.sas = False
            vessel.control.rcs = False
            vessel.control.throttle = 1
            time.sleep(1)
            
            text = self.play('发射！')
            print(text)
            logging.info(text)
            vessel.control.activate_next_stage()
            vessel.auto_pilot.target_pitch = 90
            vessel.auto_pilot.target_heading = 90
            # vessel.auto_pilot.target_roll = 0
            vessel.auto_pilot.engage()
            
            altitude1 = 7500
            altitude2 = 20000
            altitude3 = 40000
            
            while True:
                isNoFuel = False
                for part in vessel.parts.all:
                    if part.resources.has_resource('LiquidFuel'):
                        if part.resources.amount('LiquidFuel') < 0.1:
                            isNoFuel = True
                if isNoFuel:
                    text = self.play('{}级助推火箭分离！'.format(vessel.control.current_stage))
                    print(text)
                    logging.info(text)
                    vessel.control.activate_next_stage()
                    text = self.play(
                        '助推火箭分离成功！高度：{:.0f}m，速度：{:.2f}m/s。'.format(vessel.flight().mean_altitude,
                                                                   vessel.flight().speed))
                    print(text)
                    logging.info(text)
                if vessel.flight().atmosphere_density < 0.5:
                    break
                time.sleep(0.5)
            
            text = self.play('离开高密度大气！')
            print(text)
            logging.info(text)
            text = self.play('开始重力转弯！')
            print(text)
            logging.info(text)
            vessel.auto_pilot.target_pitch = 80
            
            while True:
                isNoFuel = False
                for part in vessel.parts.all:
                    if part.resources.has_resource('LiquidFuel'):
                        if part.resources.amount('LiquidFuel') < 0.1:
                            isNoFuel = True
                if isNoFuel:
                    text = self.play('{}级助推火箭分离！'.format(vessel.control.current_stage))
                    print(text)
                    logging.info(text)
                    vessel.control.activate_next_stage()
                    text = self.play(
                        '助推火箭分离成功！高度：{:.0f}m，速度：{:.2f}m/s。'.format(vessel.flight().mean_altitude,
                                                                   vessel.flight().speed))
                    print(text)
                    logging.info(text)
                if vessel.flight().atmosphere_density < 0.05:
                    break
                ratio = (0.5 - vessel.flight().atmosphere_density) / (0.5 - 0.05)
                vessel.auto_pilot.target_pitch = 90 - ratio * 30
                time.sleep(1)
            
            text = self.play('离开中密度大气！')
            print(text)
            logging.info(text)
            vessel.auto_pilot.target_pitch = 45
            
            while True:
                isNoFuel = False
                for part in vessel.parts.all:
                    if part.resources.has_resource('LiquidFuel'):
                        if part.resources.amount('LiquidFuel') < 0.1:
                            isNoFuel = True
                if isNoFuel:
                    text = self.play('{}级助推火箭分离！'.format(vessel.control.current_stage))
                    print(text)
                    logging.info(text)
                    vessel.control.activate_next_stage()
                    text = self.play(
                        '助推火箭分离成功！高度：{:.0f}m，速度：{:.2f}m/s。'.format(vessel.flight().mean_altitude,
                                                                   vessel.flight().speed))
                    print(text)
                    logging.info(text)
                if vessel.flight().atmosphere_density < 0.0001:
                    break
                ratio = (0.05 - vessel.flight().atmosphere_density) / (0.05 - 0.0001)
                vessel.auto_pilot.target_pitch = 90 - 30 - ratio * 30
                time.sleep(1)
            
            text = self.play('离开低密度大气！')
            print(text)
            logging.info(text)
            text = self.play('关闭火箭引擎！')
            print(text)
            logging.info(text)
            vessel.control.throttle = 0
            vessel.auto_pilot.disengage()
            vessel.control.sas = True
            time.sleep(1)
            vessel.control.sas_mode = self.conn.space_center.SASMode.prograde
            
            while True:
                if vessel.flight().atmosphere_density == 0:
                    break
                time.sleep(1)
            
            text = self.play('离开大气！')
            print(text)
            logging.info(text)
            text = self.play('开始路径规划！AP={:.0f}m。'.format(vessel.orbit.apoapsis))
            print(text)
            logging.info(text)
            node = vessel.control.add_node(self.conn.space_center.ut + vessel.orbit.time_to_apoapsis)
            while node.orbit.periapsis < vessel.orbit.apoapsis - 1:
                node.prograde += 1
            node.prograde += 1
            text = self.play('路径规划完成！Δv={:.2f}m/s，AP={:.0f}m，PE={:.0f}m。'.format(node.delta_v, node.orbit.apoapsis,
                                                                                 node.orbit.periapsis))
            print(text)
            logging.info(text)
            
            F = vessel.available_thrust
            Isp = vessel.specific_impulse * 9.82
            m0 = vessel.mass
            m1 = m0 / math.exp(node.remaining_delta_v / Isp)
            flow_rate = F / Isp
            burn_time = (m0 - m1) / flow_rate
            text = self.play('变轨时间：{:.2f}s。'.format(burn_time))
            print(text)
            logging.info(text)
            
            text = self.play('调整飞行姿态！')
            print(text)
            logging.info(text)
            vessel.control.sas_mode = self.conn.space_center.SASMode.maneuver
            # while True:
            #     if vessel.orbit.time_to_apoapsis < burn_time / 2:
            #         break
            #     time.sleep(1)
            
            while True:
                if vessel.orbit.time_to_apoapsis < burn_time / 2:
                    break
                time.sleep(1)
            
            text = self.play('开始变轨！')
            print(text)
            logging.info(text)
            vessel.control.throttle = 1
            
            while True:
                isNoFuel = False
                for part in vessel.parts.all:
                    if part.resources.has_resource('LiquidFuel'):
                        if part.resources.amount('LiquidFuel') < 0.1:
                            isNoFuel = True
                if isNoFuel:
                    text = self.play('{}级助推火箭分离！'.format(vessel.control.current_stage))
                    print(text)
                    logging.info(text)
                    vessel.control.throttle = 0
                    time.sleep(1)
                    vessel.control.activate_next_stage()
                    time.sleep(1)
                    vessel.control.throttle = 1
                    text = self.play(
                        '助推火箭分离成功！高度：{:.0f}m，速度：{:.2f}m/s。'.format(vessel.flight().mean_altitude,
                                                                   vessel.flight().speed))
                    print(text)
                    logging.info(text)
                if node.remaining_delta_v < 100:
                    ratio = (100 - node.remaining_delta_v) / 100
                    vessel.control.throttle = 1 - ratio * 0.9
                if node.remaining_delta_v < 1:
                    break
                time.sleep(0.1)
            
            text = self.play('变轨结束！AP={:.0f}m，PE={:.0f}m。'.format(vessel.orbit.apoapsis, vessel.orbit.periapsis))
            print(text)
            logging.info(text)
            vessel.control.throttle = 0
            node.remove()
        
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
    
    def play(self, text):
        def tmp():
            tts = gTTS(text=text, lang='zh')
            hash = self.getHash()
            tts.save('{}.mp3'.format(hash))
            source = pyglet.media.load('{}.mp3'.format(hash))
            source2 = pyglet.media.load('data/Silence01s.mp3')
            self.soundList.append(source)
            # self.player.queue(source1)
            # self.player.queue(source2)
            # tmp1()
        
        def tmp1():
            def tmp11():
                source = pyglet.media.load('Silence01s')
                self.player.queue(source)
                self.player.play()
            
            tt = threading.Thread(target=tmp11)
            tt.start()
        
        t = threading.Thread(target=tmp)
        t.start()
        return text
    
    def startPlayer(self):
        def add():
            print('!')
            pop = self.soundList.popleft()
            self.player.queue(pop)
        def player():
            while True:
                if not self.player.source and len(self.soundList) > 0:
                    pop = self.soundList.popleft()
                    self.player.queue(pop)
                    print(self.player.source)
                
                time.sleep(0.1)
        
        self.player.set_handler(self.player.on_player_eos(), add)
        # p = threading.Thread(target=player)
        # p.start()
    
    def getHash(self):
        m = hashlib.md5()
        m.update(str(random.random()).encode("utf-8"))
        return m.hexdigest()


if __name__ == '__main__':
    I = Pilot()
