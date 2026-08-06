/**
 * @file MaxArm_ctl.h
 * @author Wu TongXing
 * @brief Arduino与MaxArm通讯
 * @version 0.1
 * @date 2024-02-24
 */

#ifndef MAXARM_CTL_H
#define MAXARM_CTL_H

#include <Arduino.h>
#include "SoftwareSerial.h" //软串口库

#define rxPin 7      //Arduino与MaxArm通讯串口
#define txPin 6      

//************* 数据结构定义 begin *************

/*
 * 0xAA 0x55 | func | data_len | data | check
 */

#define CONST_STARTBYTE1 0xAAu
#define CONST_STARTBYTE2 0x55u


//帧功能号枚举
enum PACKET_FUNCTION {
  FUNC_SET_ANGLE = 0x01,
  FUNC_SET_XYZ = 0x03,
  FUNC_SET_PWMSERVO = 0x05,
  FUNC_SET_SUCTIONNOZZLE = 0x07,
  FUNC_READ_ANGLE = 0x11,
  FUNC_READ_XYZ = 0x13
};

//************* 数据结构定义 end ***************

class MaxArm_ctl {
  public:
    //构造函数
    MaxArm_ctl(void);

    //串口开启函数
    void serial_begin(void);

    //设置角度
    void set_angles(uint8_t* angles , uint16_t time);

    //设置xyz
    void set_xyz(int16_t* pos , uint16_t time);

    //设置末端舵机角度
    void set_pwmservo(uint8_t angle , uint16_t time);

    //设置喷嘴功能
    void set_SuctioNnozzle(int func);

    //读取角度
    bool read_angles(int* angles);

    //读取xyz
    bool read_xyz(int* pos);

  private:
    bool rec_handle(uint8_t* res , uint8_t func);
};


#endif //MAXARM_CTL_H
