/**
 * @pro  arduino_and_MaxArm
 * @author Wu TongXing
 * @brief  arduino与MaxArm通讯例程
 * @version 0.1
 * @date 2024-02-24
 */

#include "MaxArm_ctl.h"

MaxArm_ctl ma_ctl;

void setup() {
  Serial.begin(115200);
  ma_ctl.serial_begin();
}






void loop() {
  //设置总线舵机角度
  Serial.println("set angles");
  uint8_t angles[3] = {120,100,120};
  //将总线舵机的角度分别设置为120/100/120度,运行时间为1000ms
  ma_ctl.set_angles(angles , 1000); 
  delay(1500);

  //设置xyz坐标
  Serial.println("set xyz");
  int16_t xyz[2][3] = {{120,-180,85},{-120,-180,85}};
  //将xyz坐标设置为120/-180/85,运行时间为1000ms
  ma_ctl.set_xyz(xyz[0] , 1000);  
  delay(1500);
  //将xyz坐标设置为-120/-180/85,运行时间为1000ms
  ma_ctl.set_xyz(xyz[1] , 1000);  
  delay(1500);

  //设置PWM舵机角度
  Serial.println("set pwm servo");
  //将PWM舵机角度设置为90度,运行时间为1000ms
  ma_ctl.set_pwmservo(90,1000); 
  delay(1500);
  //将PWM舵机角度设置为45度,运行时间为1000ms
  ma_ctl.set_pwmservo(45,1000); 
  delay(1500);
  //将PWM舵机角度设置为135度,运行时间为1000ms
  ma_ctl.set_pwmservo(135,1000);  
  delay(1500);

  //设置吸嘴功能
  Serial.println("set suction nnozzle")
  ma_ctl.set_SuctioNnozzle(1);  //打开气泵
  delay(1500);
  ma_ctl.set_SuctioNnozzle(2);  //打开电磁阀并关闭气泵
  delay(200);
  ma_ctl.set_SuctioNnozzle(3);  //关闭电磁阀
  delay(1500);

  //读取并打印出当前状态的总线舵机角度
  Serial.println("read angles");
  int16_t read_a[3] = {0,0,0};
  if(ma_ctl.read_angles(read_a))
  {
    Serial.print("angles: ");
    Serial.print(read_a[0]);
    Serial.print(" ");
    Serial.print(read_a[1]);
    Serial.print(" ");
    Serial.print(read_a[2]);
    Serial.println(" ");
  }
  delay(100);

  //读取并打印出当前状态的xyz坐标
  Serial.println("read xyz");
  int16_t read_x[3] = {0,0,0};
  if(ma_ctl.read_xyz(read_x))
  {
    Serial.print("xyz: ");
    Serial.print(read_x[0]);
    Serial.print(" ");
    Serial.print(read_x[1]);
    Serial.print(" ");
    Serial.print(read_x[2]);
    Serial.println(" ");
  }
  delay(100);
}
