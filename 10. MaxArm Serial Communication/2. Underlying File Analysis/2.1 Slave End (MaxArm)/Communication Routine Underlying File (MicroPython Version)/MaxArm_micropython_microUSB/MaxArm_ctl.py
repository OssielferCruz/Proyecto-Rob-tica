'''
@file:    MaxArm_ctl.py
@company: Hiwonder
@author:  CuZn
@date:    2024-02-28
@description: MaxArm  
'''

from machine import UART
from micropython import const
from Buzzer import Buzzer
from espmax import ESPMax
import struct

from BusServo import BusServo
import time
from SuctionNozzle import SuctionNozzle

CONST_STARTBYTE1 = const(0xAA)
CONST_STARTBYTE2 = const(0x55)

class SELECT_PORT:
  PORT_FOR_USB = const(0x01)
  PORT_FOR_4Pin = const(0x03)

# CRC


def checksum_crc8(func , len , data):
    check = func + len
    for b in data:
        check = check + b
    check = ~check
    return check & 0xFF


# 
class PacketControllerState:
  # 0xAA 0x55 Length Function Data Checksum
  STARTBYTE1 = const(0)
  STARTBYTE2 = const(1)
  FUNCTION = const(2)
  LENGTH = const(3)
  DATA = const(4)
  CHECKSUM = const(5)

# 
class PACKET_FUNCTION: 
  FUNC_SET_ANGLE = const(0x01)
  FUNC_SET_XYZ = const(0x03)
  FUNC_SET_PWMSERVO = const(0x05)
  FUNC_SET_SUCTIONNOZZLE = const(0x07)
  FUNC_READ_ANGLE = const(0x11)
  FUNC_READ_XYZ = const(0x13)

# 
class PacketRawFrame:
  def __init__(self):
    self.start_byte1 = 0x00
    self.start_byte2 = 0x00
    self.function = 0x00
    self.data_length = 0x00
    # self.data = [0x00] * 256
    self.data = []
    self.checksum = 0x00

# 


class PacketController:
  def __init__(self):
    # 
    self.state = PacketControllerState()
    self.frame = PacketRawFrame()
    self.data_index = 0
    self.index = 0
    # 
    self.len = 0
    # data = [0x00] * 256
    self.data = []

'''
MaxArm
'''
class MaxArm_ctl:
  
  # 
  def __init__(self):
    self.__pk_ctl = PacketController()
    self.data = []
    self.bus_servo = BusServo()
    self.arm = ESPMax(self.bus_servo)
    self.__pk_ctl.state = PacketControllerState.STARTBYTE1

  # ，
  # USB，SELECT_PORT.PORT_FOR_USB；4pin，SELECT_PORT.PORT_FOR_4Pin
  def begin(self , port):
    if port == SELECT_PORT.PORT_FOR_USB:
      print("begin in USB")
      self.__uart = UART(1 , 9600 , tx=1, rx=3 ) # , 9600 , tx=10, rx=9
    else:
      print("begin in 4Pin")
      self.__uart = UART(1, 9600, tx=33, rx=32)
    self.nozzle = SuctionNozzle()
    self.arm.go_home(1500)
    time.sleep_ms(2000)


    # 
  def rec_data(self):
    readbuffer = self.__uart.read()
    if readbuffer is not None:
      data_len = len(readbuffer)
      index = 0
      data_index = 0
      while (data_len > 0):
        # 1
        if PacketControllerState.STARTBYTE1 == self.__pk_ctl.state:
          if CONST_STARTBYTE1 == readbuffer[index]:
            self.__pk_ctl.state = PacketControllerState.STARTBYTE2
          else:
            self.__pk_ctl.state = PacketControllerState.STARTBYTE1
        
        # 2
        elif PacketControllerState.STARTBYTE2 == self.__pk_ctl.state:
          if CONST_STARTBYTE2 == readbuffer[index]:
            self.__pk_ctl.state = PacketControllerState.FUNCTION
          else:
            self.__pk_ctl.state = PacketControllerState.STARTBYTE1
        
        # 
        elif PacketControllerState.FUNCTION == self.__pk_ctl.state:
          self.__pk_ctl.state = PacketControllerState.LENGTH
          if PACKET_FUNCTION.FUNC_READ_ANGLE != readbuffer[index]:
            if PACKET_FUNCTION.FUNC_READ_XYZ != readbuffer[index]:
              if PACKET_FUNCTION.FUNC_SET_ANGLE != readbuffer[index]:
                if PACKET_FUNCTION.FUNC_SET_PWMSERVO != readbuffer[index]:
                  if PACKET_FUNCTION.FUNC_SET_XYZ != readbuffer[index]:
                    if PACKET_FUNCTION.FUNC_SET_SUCTIONNOZZLE != readbuffer[index]:
                      self.__pk_ctl.state = PacketControllerState.STARTBYTE1
          if self.__pk_ctl.state == PacketControllerState.LENGTH:
            self.__pk_ctl.frame.function = readbuffer[index]

        # 
        elif PacketControllerState.LENGTH == self.__pk_ctl.state:
          self.__pk_ctl.frame.data_length = readbuffer[index]
          if 0 == self.__pk_ctl.frame.data_length:
            self.__pk_ctl.state = PacketControllerState.CHECKSUM
          else:
            self.__pk_ctl.state = PacketControllerState.DATA
          data_index = 0
          
        # 
        elif PacketControllerState.DATA == self.__pk_ctl.state:
          self.__pk_ctl.frame.data.append(readbuffer[index])
          data_index += 1
          if data_index >= self.__pk_ctl.frame.data_length:
            self.__pk_ctl.state = PacketControllerState.CHECKSUM
        
        # 
        elif PacketControllerState.CHECKSUM == self.__pk_ctl.state:
          self.__pk_ctl.frame.checksum = readbuffer[index]
          crc = checksum_crc8(self.__pk_ctl.frame.function , 
                              self.__pk_ctl.frame.data_length , 
                              self.__pk_ctl.frame.data)
          # 
          if self.__pk_ctl.frame.checksum == crc:
            self.deal_command(self.__pk_ctl.frame)
          self.__pk_ctl.state = PacketControllerState.STARTBYTE1
          # 
          self.__pk_ctl.frame.data.clear()
  
        # 
        else:
          self.__pk_ctl.state = PacketControllerState.STARTBYTE1
          
        # 
        data_len -= 1
        index += 1


  ''' 
   
  '''
  def deal_command(self , ctl_com):
    len = ctl_com.data_length
    if ctl_com.function == PACKET_FUNCTION.FUNC_SET_ANGLE:
      # print("FUNC_SET_ANGLE")
      if len == 8:
        angles = []
        angles.append((ctl_com.data[0] & 0x00FF) | ((ctl_com.data[1] << 8 ) & 0xFF00))
        angles.append((ctl_com.data[2] & 0x00FF) | ((ctl_com.data[3] << 8 ) & 0xFF00))
        angles.append((ctl_com.data[4] & 0x00FF) | ((ctl_com.data[5] << 8 ) & 0xFF00))
        time_count = (ctl_com.data[6] & 0x00FF) | ((ctl_com.data[7] << 8 ) & 0xFF00)
        self.arm.set_servo_in_range(1 , angles[0] , time_count)
        time.sleep_ms(10)
        self.arm.set_servo_in_range(2 , angles[1] , time_count)
        time.sleep_ms(10)
        self.arm.set_servo_in_range(3 , angles[2] , time_count)
        time.sleep_ms(10)

    elif ctl_com.function == PACKET_FUNCTION.FUNC_SET_XYZ:
      # print("FUNC_SET_XYZ")
      if len == 8:
        xyz = bytes(ctl_com.data[:7])
        time_count = (ctl_com.data[6] & 0x00FF) | ((ctl_com.data[7] << 8 ) & 0xFF00)
        unpacked_data = struct.unpack('<hhh', xyz) 
        self.arm.set_position(unpacked_data , time_count)

    elif ctl_com.function == PACKET_FUNCTION.FUNC_SET_PWMSERVO:
      # print("FUNC_SET_PWMSERVO")
      if len == 4:
        pul = (ctl_com.data[0] & 0x00FF) | ((ctl_com.data[1] << 8 ) & 0xFF00)
        time_count = (ctl_com.data[2] & 0x00FF) | ((ctl_com.data[3] << 8 ) & 0xFF00)
        self.nozzle.set_pwmservo_pul(pul , time_count)

    elif ctl_com.function == PACKET_FUNCTION.FUNC_SET_SUCTIONNOZZLE:
      # print("FUNC_SET_SUCTIONNOZZLE")

      if len == 1:
        if ctl_com.data[0] == 1:
          self.nozzle.on_uart()
        elif ctl_com.data[0] == 2:


          self.nozzle.off_uart_1()
        elif ctl_com.data[0] == 3:
          self.nozzle.off_uart_2()
          
    elif ctl_com.function == PACKET_FUNCTION.FUNC_READ_ANGLE:
      #print("FUNC_READ_ANGLE")
      angles = self.arm.read_angles()
      send_data = bytearray([0xAA,0x55,0x11,0x06])
      send_data += struct.pack('<hhh', angles[0] , angles[1] , angles[2])
      check_num = checksum_crc8(0,0,send_data[2:])
      send_data.append(check_num)
      self.__uart.write(send_data)

    elif ctl_com.function == PACKET_FUNCTION.FUNC_READ_XYZ:
      # print("FUNC_READ_ANGLE")
      (x, y, z) = self.arm.read_position()
      send_data = bytearray([0xAA,0x55,0x13,0x06])
      send_data += struct.pack('<hhh', x, y, z)
      check_num = checksum_crc8(0,0,send_data[2:])
      send_data.append(check_num)
      self.__uart.write(send_data)

    else:
      # print("ERROR")
      pass














