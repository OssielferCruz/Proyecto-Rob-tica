#!/usr/bin/env python3
# encoding: utf-8
# MaxArm python sdk

import  MaxArm_ctl
import  time

ma = MaxArm_ctl.MaxArm_ctl(device = "/dev/ttyUSB0", baudrate=9600)

while True:
    print("set suction nnozzle")
    ma.set_SuctioNnozzle(1)
    time.sleep(2)
    ma.set_SuctioNnozzle(2)
    time.sleep(0.2)
    ma.set_SuctioNnozzle(3)
    time.sleep(2)
    
    print("set angles")
    angles = [90,90,90]
    ma.set_angles(angles , 1000)
    time.sleep(2)
    angles = [45,90,90]
    ma.set_angles(angles , 1000)
    time.sleep(2)

    print("set xyz")
    xyz = {120 , -180 , 85}
    ma.set_xyz(xyz , 1000)
    time.sleep(2)
    xyz = {-120,-180,85}
    ma.set_xyz(xyz , 1000)
    time.sleep(2)
    
    print("set pwm servo")
    ma.set_pwmservo(135,1000)
    time.sleep(2)
    ma.set_pwmservo(45,1000)
    time.sleep(2)
    
    print("read xyz")
    angles = ma.read_xyz()
    print(angles)
    time.sleep(2)
