#include "PC_rec.h"
#include "ESPMax.h"
#include "SuctionNozzle.h"
#include "ESP32PWMServo.h"

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

PC_REC::PC_REC(void)
{
  Serial.begin(9600);
}

void PC_REC::begin(uint16_t bount)
{
  Serial.begin(bount);
}

void PC_REC::rec_data(void)
{
  //读取数据
  uint32_t len = Serial.available();
  while(len--)
  {
    int rd = Serial.read();
    pk_ctl.data[pk_ctl.index_tail] = (char)rd;
    pk_ctl.index_tail++;
    if(BUFFER_SIZE <= pk_ctl.index_tail)
    {
      pk_ctl.index_tail = 0;
    }
    if(pk_ctl.index_tail == pk_ctl.index_head)
    {
      pk_ctl.index_head++;
      if(BUFFER_SIZE <= pk_ctl.index_head)
      {
        pk_ctl.index_head = 0;
      }
    }else{
      pk_ctl.len++;
    }
  }

  uint8_t crc = 0;
  //解析数据
  while(pk_ctl.len > 0)
  {
    switch(pk_ctl.state)
    {
      case STATE_STARTBYTE1: /* 处理帧头标记1 */
        pk_ctl.state = CONST_STARTBYTE1 == pk_ctl.data[pk_ctl.index_head] ? STATE_STARTBYTE2 : STATE_STARTBYTE1;
        break;
      case STATE_STARTBYTE2: /* 处理帧头标记2 */
        pk_ctl.state = CONST_STARTBYTE2 == pk_ctl.data[pk_ctl.index_head] ? STATE_FUNCTION : STATE_STARTBYTE1;
        break;
      case STATE_FUNCTION: /* 处理帧功能号 */
        pk_ctl.state = STATE_LENGTH;
        if(FUNC_SET_ANGLE != pk_ctl.data[pk_ctl.index_head])
          if(FUNC_SET_XYZ != pk_ctl.data[pk_ctl.index_head])
            if(FUNC_SET_PWMSERVO != pk_ctl.data[pk_ctl.index_head])
              if(FUNC_SET_SUCTIONNOZZLE != pk_ctl.data[pk_ctl.index_head])
                if(FUNC_READ_ANGLE != pk_ctl.data[pk_ctl.index_head])
                  if(FUNC_READ_XYZ != pk_ctl.data[pk_ctl.index_head])
                  {
                    pk_ctl.state = STATE_STARTBYTE1;
                  }
        if(STATE_LENGTH == pk_ctl.state) {
            pk_ctl.frame.function = pk_ctl.data[pk_ctl.index_head];
        }
        break;
      case STATE_LENGTH: /* 处理帧数据长度 */
        if(pk_ctl.data[pk_ctl.index_head] >= DATA_SIZE) //若（包含具体信息）信息数据长度>DATA_SIZE,则有问题
        {
          pk_ctl.state = STATE_STARTBYTE1;
          continue;
        }else{
          pk_ctl.frame.data_length = pk_ctl.data[pk_ctl.index_head];
          pk_ctl.state = (0 == pk_ctl.frame.data_length) ? STATE_CHECKSUM : STATE_DATA;
          pk_ctl.data_index = 0;
          break;
        }
      case STATE_DATA: /* 处理帧数据 */
        pk_ctl.frame.data[pk_ctl.data_index] = pk_ctl.data[pk_ctl.index_head];
        ++pk_ctl.data_index;
        if(pk_ctl.data_index >= pk_ctl.frame.data_length) {
            pk_ctl.state = STATE_CHECKSUM;
            pk_ctl.frame.data[pk_ctl.data_index] = '\0';
        }
        break;
      case STATE_CHECKSUM: /* 处理校验值 */
        pk_ctl.frame.checksum = pk_ctl.data[pk_ctl.index_head];
        crc = checksum_crc8((uint8_t*)&pk_ctl.frame.function, pk_ctl.frame.data_length + 2);
        // Serial.println(crc);
        if(crc == pk_ctl.frame.checksum) { /* 校验失败, 跳过执行 */
            deal_command(&pk_ctl.frame); //处理数据
        }
        memset(&pk_ctl.frame, 0, sizeof(struct PacketRawFrame)); //清除
        pk_ctl.state = STATE_STARTBYTE1;
        break;
      default:
        pk_ctl.state = STATE_STARTBYTE1;
        break;
    }
    if(pk_ctl.index_head != pk_ctl.index_tail)
        pk_ctl.index_head++;
    if(BUFFER_SIZE <= pk_ctl.index_head)
        pk_ctl.index_head = 0;
    
    pk_ctl.len--;

  }
}

void PC_REC::deal_command(struct PacketRawFrame* ctl_com)
{
  uint16_t len = ctl_com->data_length;
  switch(ctl_com->function)
  {
    case FUNC_SET_ANGLE: //设置角度 0x01
      {
        Angle_Ctl_Data msg;
        if(len == 8)
        {
          memcpy(&msg , ctl_com->data , sizeof(msg));
          set_servo_in_range(1,msg.pul[0],msg.time);
          delay(2);
          set_servo_in_range(2,msg.pul[1],msg.time);
          delay(2);
          set_servo_in_range(3,msg.pul[2],msg.time);
          delay(2);
        }
      }
      break;

    case FUNC_SET_XYZ: //设置xyz轴 0x03
      {
        XYZ_Ctl_Data msg;
        if(len == 8)
        {
          memcpy(&msg , &ctl_com->data , sizeof(msg));
          float p[3] = {msg.pos[0],msg.pos[1],msg.pos[2]};
          set_position(p , msg.time);
        }
      }
      break;

    case FUNC_SET_PWMSERVO: //设置PWM舵机 0x05
      {
        PWM_Ctl_Data msg;
        if(len == 4)
        {
          memcpy(&msg , &ctl_com->data , sizeof(msg));
          SetPWMServo(1, msg.pul, msg.time);
        }
      }
      break;

    case FUNC_SET_SUCTIONNOZZLE: //设置吸嘴 0x07
      {
        SN_Ctl_Data msg;
        if(len == 1)
        {
          memcpy(&msg , &ctl_com->data , sizeof(msg));
          switch(msg.cmd)
          {
            case 1:
              Pump_on();
              break;
            case 2:
              Valve_on();
              break;
            case 3:
              Valve_off();
              break;
          }
        }
      }
      break;

    case FUNC_READ_ANGLE: //读取角度 0x11
      {
        read_Angle_Data msg;
        int16_t angles[3];
        read_angles(angles);
        uint8_t send_data[20] = {0xAA , 0x55 , 0x11 , 0x06};
        memcpy(&send_data[4] , angles , 6);
        send_data[10] = checksum_crc8(&send_data[2] , 8);
        Serial.write(send_data , 11);
      }
      break;

    case FUNC_READ_XYZ: //读取xyz轴 0x13
      {
        float pos_f[3];
        read_position(pos_f);
        int16_t pos[3] = {(int16_t)pos_f[0] , (int16_t)pos_f[1] , (int16_t)pos_f[2]};
        uint8_t send_data[20] = {0xAA , 0x55 , 0x13 , 0x06};
        memcpy(&send_data[4] , pos , 6);
        send_data[10] = checksum_crc8(&send_data[2] , 8);
        Serial.write(send_data , 11);
      }
      break;

    default:
      break;
  }
}



