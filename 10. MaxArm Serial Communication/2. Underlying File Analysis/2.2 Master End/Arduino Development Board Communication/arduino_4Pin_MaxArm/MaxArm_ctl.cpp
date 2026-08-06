/**
 * @file MaxArm_ctl.cpp
 * @author Wu TongXing
 * @brief Arduino与MaxArm通讯
 * @version 0.1
 * @date 2024-02-24
 */

#include "MaxArm_ctl.h"

static SoftwareSerial SerialM(rxPin, txPin);  //实例化软串口


/* CRC校验 */
static uint16_t checksum_crc8(const uint8_t *buf, uint16_t len)
{
    uint8_t check = 0;
    while (len--) {
        check = check + (*buf++);
    }
    check = ~check;
    return ((uint16_t) check) & 0x00FF;
}

MaxArm_ctl::MaxArm_ctl(void)
{
  
}


void MaxArm_ctl::serial_begin(void)
{
  SerialM.begin(9600);
}




//设置角度 0~240 (0~1000)
void MaxArm_ctl::set_angles(uint8_t* angles , uint16_t time)
{
  uint16_t pul[3];
  uint8_t msg[20] = {CONST_STARTBYTE1 , CONST_STARTBYTE2};
  msg[2] = FUNC_SET_ANGLE;
  msg[3] = 8;
  pul[0] = angles[0] > 240 ? 240 : angles[0];
  pul[1] = angles[1] > 240 ? 240 : angles[1];
  pul[2] = angles[2] > 240 ? 240 : angles[2];
  pul[0] = map(pul[0] , 0 , 240 , 0 , 1000);
  pul[1] = map(pul[1] , 0 , 240 , 0 , 1000);
  pul[2] = map(pul[2] , 0 , 240 , 0 , 1000);
  memcpy(&msg[4] , pul , 6);
  msg[10] = time & 0x00ff;
  msg[11] = (time>>8)&0x00FF;
  msg[12] = checksum_crc8((uint8_t*)&msg[2] , 10);
  SerialM.write((char*)&msg , 13);
}

//设置xyz
void MaxArm_ctl::set_xyz(int16_t* pos , uint16_t time)
{
  uint8_t msg[20] = {CONST_STARTBYTE1 , CONST_STARTBYTE2};
  msg[2] = FUNC_SET_XYZ;
  msg[3] = 8;
  memcpy(&msg[4] , pos , 6);
  msg[10] = time & 0x00ff;
  msg[11] = (time>>8)&0x00FF;
  msg[12] = checksum_crc8((uint8_t*)&msg[2] , 10);
  SerialM.write((char*)&msg , 13);
}

//设置末端舵机角度 0~180度
void MaxArm_ctl::set_pwmservo(uint8_t angle , uint16_t time)
{
  uint16_t pul = angle > 180 ? 180 : angle;
  uint8_t msg[10] = {CONST_STARTBYTE1 , CONST_STARTBYTE2};
  msg[2] = FUNC_SET_PWMSERVO;
  msg[3] = 4;
  pul = map(pul , 0 , 180 , 500, 2500);
  msg[4] = pul & 0x00ff;
  msg[5] = (pul>>8)&0x00FF;
  msg[6] = time & 0x00ff;
  msg[7] = (time>>8)&0x00FF;
  msg[8] = checksum_crc8((uint8_t*)&msg[2] , 6);
  SerialM.write((char*)&msg , 9);
}

//设置喷嘴功能
void MaxArm_ctl::set_SuctioNnozzle(int func)
{
  uint8_t msg[10] = {CONST_STARTBYTE1 , CONST_STARTBYTE2};
  msg[2] = FUNC_SET_SUCTIONNOZZLE;
  msg[3] = 1;
  // memcpy(&msg[4] , pul , 2);
  if(func < 0 && func > 3)
  {
    Serial.println("set_SuctioNnozzle ERROR");
    return;
  }
  msg[4] = func;
  msg[5] = checksum_crc8((uint8_t*)&msg[2] , 3);
  SerialM.write((char*)&msg , 6);
}

bool MaxArm_ctl::rec_handle(uint8_t* res , uint8_t func)
{
  int len = SerialM.available();
  // 限制读取的数据长度
  len = len > 30 ? 30 : len;
  uint8_t step = 0;
  uint8_t data[8] , index = 0;
  while(len--)
  {
    int rd = SerialM.read();
    switch(step)
    {
      case 0:
        if(rd == 0xAA)
        {
          step++;
        }
        break;
      case 1:
        if(rd == 0x55)
        {
          step++;
        }else{
          step = 0;
        }
        break;
      case 2:
        if(rd == func)
        {
          data[index++] = rd;
          step++;
        }else{
          step = 0;
        }
        break;
      case 3: //接收的数据长度必须为6个字节
        if(rd == 6)
        {
          data[index++] = rd;
          step++;
        }else{
          step = 0;
        }
        break;
      case 4:
        data[index++] = rd;
        if(index >= 8)
        {
          step++;
        }
        break;
      case 5:
        if(checksum_crc8(data , 8) == rd)
        {
          memcpy(res , &data[2] , 6);
          return true;
        }else{
          return false;
        }
        break;
      default:
        step = 0;
        break;
    }
  }
  return false;
}


//读取角度
bool MaxArm_ctl::read_angles(int* angles)
{
  uint8_t msg[10] = {CONST_STARTBYTE1 , CONST_STARTBYTE2};
  msg[2] = FUNC_READ_ANGLE;
  msg[3] = 0;
  msg[4] = checksum_crc8((uint8_t*)&msg[2] , 2);
  while(SerialM.available())
  {
    SerialM.read();
  }
  SerialM.write((char*)&msg , 5);
  uint16_t count = 3;
  delay(300);
  int16_t res[3];
  if(rec_handle((uint8_t*)res , 0x11))
  {
    angles[0] = map(res[0] , 0 , 1000 , 0 , 240);
    angles[1] = map(res[1] , 0 , 1000 , 0 , 240);
    angles[2] = map(res[2] , 0 , 1000 , 0 , 240);
    return true;
  }
  return false;
}

//读取xyz
bool MaxArm_ctl::read_xyz(int* pos)
{
  uint8_t msg[10] = {CONST_STARTBYTE1 , CONST_STARTBYTE2};
  msg[2] = FUNC_READ_XYZ;
  msg[3] = 0;
  msg[4] = checksum_crc8((uint8_t*)&msg[2] , 2);
  while(SerialM.available())
  {
    SerialM.read();
  }
  SerialM.write((char*)&msg , 5);
  delay(300);
  int16_t res[3];
  if(rec_handle((uint8_t*)res , 0x13))
  {
    pos[0] = res[0];
    pos[1] = res[1];
    pos[2] = res[2];
    return true;
  }
  return false;
}


