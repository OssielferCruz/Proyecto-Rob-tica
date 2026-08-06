#!/usr/bin/env python3
# encoding: utf-8
# MaxArm python sdk

import  MaxArm_ctl
import  time
ma = MaxArm_ctl.MaxArm_ctl(device = "/dev/ttyUSB0", baudrate=9600)

while True:
    #设置吸嘴功能
    print("set suction nnozzle")
    ma.set_SuctioNnozzle(1) #打开气泵
    time.sleep(2)
    ma.set_SuctioNnozzle(2) #打开电磁阀并关闭气泵
    time.sleep(0.2)
    ma.set_SuctioNnozzle(3) #关闭电磁阀
    time.sleep(2)
    
    #设置总线舵机角度
    print("set angles")
    angles = [90,90,90]
    #将总线舵机的角度分别设置为90/90/90度,运行时间为1000ms
    ma.set_angles(angles , 1000) 
    time.sleep(2)
    angles = [45,90,90]
    #将总线舵机的角度分别设置为45/90/90度,运行时间为1000ms
    ma.set_angles(angles , 1000) 
    time.sleep(2)
    
    #设置xyz坐标
    print("set xyz")
    xyz = {120 , -180 , 85} #将xyz坐标设置为120/-180/85,运行时间为1000ms
    ma.set_xyz(xyz , 1000)
    time.sleep(2)
    xyz = {-120,-180,85} #将xyz坐标设置为-120/-180/85,运行时间为1000ms
    ma.set_xyz(xyz , 1000)
    time.sleep(2)
    
    #设置PWM舵机角度
    print("set pwm servo")
    ma.set_pwmservo(135,1000) #将PWM舵机角度设置为135度,运行时间为1000ms
    time.sleep(2)
    ma.set_pwmservo(45,1000) #将PWM舵机角度设置为45度,运行时间为1000ms
    time.sleep(2)
    
    #读取并打印出当前状态的xyz坐标
    print("read xyz")
    xyz = ma.read_xyz()
    print(xyz)
    time.sleep(2)
    
    #读取打印出当前状态的总线舵机角度
    print("read angles")
    angles = ma.read_angles()
    print(angles)
    time.sleep(2)
