import time
import uctypes, gc
from machine import Pin, I2C
import Hiwonder_wifi_ble as HW_wb

from Key import Key
from Led import LED
from USBDevice import *
from Buzzer import Buzzer
from espmax import ESPMax
from Stepper import Stepper
from PWMServo import PWMServo
from micropython import const
from machine import Pin, ADC, Timer
from RobotControl import RobotControl
from SuctionNozzle import SuctionNozzle
from BusServo import BusServo, have_got_servo_pos


print("Please wait...")
key = Key()
led = LED()
buzzer = Buzzer()
pwm = PWMServo()
pwm.work_with_time()
bus_servo = BusServo()
arm = ESPMax(bus_servo)
nozzle = SuctionNozzle()
robot = RobotControl(nozzle)

ble = HW_wb.Hiwonder_wifi_ble(HW_wb.MODE_BLE_SLAVE, name = 'MaxArm')
ble.set_led_key_io(led=26,key=25)

arm.go_home()
print_en = True
nozzle_st = False
nozzle_angle = 0
(x,y,z) = arm.ORIGIN
move_sleep = time.ticks_ms()
nozzle.set_angle(nozzle_angle)

try:
  i2c = I2C(0, scl=Pin(16), sda=Pin(17), freq=100000)
  stepper = Stepper(i2c)
  stepper.set_div(stepper.DIV_1_8)
  stepper.go_home()
  stepper_st = True
  stepper_pul = 0
except:
  stepper_st = False
  
  
def MouseHandle():
  global x,y,z,nozzle_st
  global nozzle_angle,move_sleep
  
  BUTTON_L = 0x01
  BUTTON_R = 0x02
  BUTTON_M = 0x04
  
  msg = USBDevice.get_mouse_msg()
  
  if time.ticks_ms() >= move_sleep: 
    if msg == False:
      return 
    mouse_msg = uctypes.struct(uctypes.addressof(bytes(msg))
              ,{"button": uctypes.UINT8 | 5,'move_X': uctypes.INT8 | 6
              , 'move_Y': uctypes.INT8 | 7,'wheel': uctypes.INT8 | 8})

    if mouse_msg.button & BUTTON_M != 0: # Control de ejecución y procesamiento
      nozzle.off()
      arm.go_home(1500)
      nozzle_angle = 0
      nozzle_st = False
      (x,y,z) = arm.ORIGIN
      buzzer.setBuzzer(80)
      nozzle.set_angle(nozzle_angle)
      move_sleep = time.ticks_ms() + 1500
      
    elif mouse_msg.wheel != 0: # Control de ejecución y procesamiento
      dz = -mouse_msg.wheel*2
      if arm.set_position((x, y, z+dz), 20):
        z += dz
      move_sleep = time.ticks_ms() + 30
    
    else:
      if abs(mouse_msg.move_X) > abs(mouse_msg.move_Y):
        if mouse_msg.button & BUTTON_L != 0: # Control de ejecución y procesamiento
          nozzle_angle += int(mouse_msg.move_X/3)
          if nozzle_angle > 90:nozzle_angle = 90
          if nozzle_angle < -90:nozzle_angle = -90
          nozzle.set_angle(nozzle_angle)
          move_sleep = time.ticks_ms() + 30
          
        else:
          dx = -int(mouse_msg.move_X/8) # Control de ejecución y procesamiento
          if arm.set_position((x+dx, y, z), 20):
            x += dx
          move_sleep = time.ticks_ms() + 30
        
      elif abs(mouse_msg.move_X) < abs(mouse_msg.move_Y):
        if mouse_msg.button & BUTTON_R != 0: # Control de ejecución y procesamiento
          if time.ticks_ms() >= move_sleep:
            nozzle_st = bool(1 - nozzle_st)
            if nozzle_st:nozzle.on()
            else:nozzle.off()
            move_sleep = time.ticks_ms() + 300
          
        else:
          if mouse_msg.button & BUTTON_L == 0: # Control de ejecución y procesamiento
            dy = int(-mouse_msg.move_Y/8)
            if arm.set_position((x, y+dy, z), 20):
              y += dy
            move_sleep = time.ticks_ms() + 30
  
 
 # Modulo de control de gamepad inalámbrico
def Gamepad_Handle():
  time_last = 0
  which_button_press = 0

  def fun():
    global x,y,z,nozzle_angle,move_sleep,stepper_pul
    nonlocal time_last, which_button_press
    
    s = 5
    de = 1
    msg =  USBDevice.get_gamepad_msg()
    
    if msg == PSB_START | PSB_PRESS: # Control de ejecución y procesamiento
      if time.ticks_ms() >= move_sleep:
        robot.stopActionGroup()
        buzzer.setBuzzer(80)
        nozzle.off()
        arm.go_home(1500)
        nozzle_angle = 0
        nozzle.set_angle(0)
        (x,y,z) = arm.ORIGIN
        if stepper_st:
          stepper_pul = 0
          stepper.go_home()
        move_sleep = time.ticks_ms() + 1500
    elif msg == PSB_UP | PSB_PRESS: # Control de ejecución y procesamiento
      if arm.set_position((x, y+de, z),s): # Control de ejecución y procesamiento
        y += de   
        which_button_press = msg
      else: buzzer.setBuzzer(20) # Indicador sonoro del buzzer
      
    elif msg == PSB_DOWN | PSB_PRESS: # Control de ejecución y procesamiento
      if arm.set_position((x, y-de, z),s):
        y -= de
        which_button_press = msg
      else: buzzer.setBuzzer(20)
    
    elif msg == PSB_LEFT | PSB_PRESS: # Control de ejecución y procesamiento
      if arm.set_position((x-de, y, z),s):
        x += de
        which_button_press = msg
      else: buzzer.setBuzzer(20)
      
    elif msg == PSB_RIGHT | PSB_PRESS: # Control de ejecución y procesamiento
      if arm.set_position((x+de, y, z),s):
        x -= de
        which_button_press = msg
      else: buzzer.setBuzzer(20)  
      
    elif msg == PSB_L1 | PSB_PRESS: # Control de ejecución y procesamiento
      if arm.set_position((x, y, z+de),s):
        z += de
        which_button_press = msg
      else: buzzer.setBuzzer(20)
      
    elif msg == PSB_L2 | PSB_PRESS: # Control de ejecución y procesamiento
      if arm.set_position((x, y, z-de),s):
        z -= de
        which_button_press = msg
      else: buzzer.setBuzzer(20)
    
    elif msg == PSB_CIRCLE | PSB_PRESS: # Control de ejecución y procesamiento
      if stepper_st: 
        stepper.goto(300)
      else:
        robot.runActionGroup('1')
      which_button_press = msg
      
    elif msg == PSB_SQUARE | PSB_PRESS: # Control de ejecución y procesamiento
      if stepper_st: 
        stepper.goto(-300)
      else:
        robot.runActionGroup('2')
      which_button_press = msg
      
    elif msg == PSB_TRIANGLE | PSB_PRESS: # Control de ejecución y procesamiento
      nozzle_angle += 3
      nozzle_angle = -90 if nozzle_angle < -90 else nozzle_angle
      nozzle.set_angle(nozzle_angle)
      which_button_press = msg
      
    elif msg == PSB_CROSS | PSB_PRESS: # Control de ejecución y procesamiento
      nozzle_angle -= 3
      nozzle_angle = 90 if nozzle_angle > 90 else nozzle_angle
      nozzle.set_angle(nozzle_angle)
      which_button_press = msg
      
    elif msg == PSB_R2 | PSB_PRESS: # Apagar bomba de succión y liberar solenoide
      nozzle.off()
      which_button_press = msg
      
    elif msg == PSB_R1 | PSB_PRESS: # Encender bomba de succión por vacío
      nozzle.on()
      which_button_press = msg
      
    elif msg & PSB_PRESS_UP == PSB_PRESS_UP: # Control de ejecución y procesamiento
      which_button_press = 0
    
    if time.ticks_ms() - time_last > 10:
      time_last = time.ticks_ms()
      if which_button_press == PSB_UP | PSB_PRESS: # Control de ejecución y procesamiento
        if arm.set_position((x, y+de, z),s):
          y += de
      elif which_button_press == PSB_DOWN | PSB_PRESS:
        if arm.set_position((x, y-de, z),s):
          y -= de
      elif which_button_press == PSB_LEFT | PSB_PRESS: # Control de ejecución y procesamiento
        if arm.set_position((x-de, y, z),s):
          x += de
      elif which_button_press == PSB_RIGHT | PSB_PRESS:
        if arm.set_position((x+de, y, z),s):
          x -= de
      elif which_button_press == PSB_L1 | PSB_PRESS: # Control de ejecución y procesamiento
        if arm.set_position((x, y, z+de),s):
          z += de
      elif which_button_press == PSB_L2 | PSB_PRESS:
        if arm.set_position((x, y, z-de),s):
          z -= de
          
      elif which_button_press == PSB_TRIANGLE | PSB_PRESS: # Control de ejecución y procesamiento
        nozzle_angle += 1
        nozzle_angle = -90 if nozzle_angle < -90 else nozzle_angle
        nozzle.set_angle(nozzle_angle)
        
      elif which_button_press == PSB_CROSS | PSB_PRESS:
        nozzle_angle -= 1
        nozzle_angle = 90 if nozzle_angle > 90 else nozzle_angle
        nozzle.set_angle(nozzle_angle)
        
      elif which_button_press == PSB_CIRCLE | PSB_PRESS: # Control de ejecución y procesamiento
        if stepper_st: 
          stepper.goto(300)
          
      elif which_button_press == PSB_SQUARE | PSB_PRESS:
        if stepper_st: 
          stepper.goto(-300)

  return fun    
GamepadHandle = Gamepad_Handle()


ble_buf = bytearray()
ble_data = bytearray()
def ble_callback():
  global ble_buf
  global ble_data
  
  ble_buf += ble.ble_read() # Control de ejecución y procesamiento
  ble_data = ble_buf
  ble_buf = bytearray()

ble.ble_rx_irq(ble_callback)  

def BleHandle():
  global ble_data,reset_sleep,print_en
  global x,y,z, nozzle_angle, move_sleep
  
  de = 3
  if time.ticks_ms() >= move_sleep:
    if ble.mode == HW_wb.MODE_BLE_SLAVE:
      ble_data_len = len(ble_data)
      if ble_data_len >= 4:
        if ble_data[0] == 0x55 and ble_data[1] == 0x55:
          cmd = ble_data[3]
          if cmd == 0x23: # Control de ejecución y procesamiento
            if ble_data[4] < 0x80: dx = ble_data[4] 
            else: dx = (ble_data[4] - 256)

            if ble_data[5] < 0x80: dy = ble_data[5]
            else: dy = (ble_data[5] - 256)
           
            if ble_data[6] < 0x80: dz = ble_data[6]
            else: dz = (ble_data[6] - 256)
            
            if dx== -1 and dy== -1 and dz== -1: # Control de ejecución y procesamiento
              arm.go_home(1500)
              nozzle.off()
              buzzer.setBuzzer(80)
              nozzle_angle = 0
              nozzle.set_angle(0)
              (x,y,z) = arm.ORIGIN
              move_sleep = time.ticks_ms() + 1500
              
            else: # Control de ejecución y procesamiento
              if arm.set_position((x+dx*de,y+dy*de,z+dz*de), 20): # Control de ejecución y procesamiento
                x += dx*de 
                y += dy*de
                z += dz*de
                print_en = True
              else: # Indicador sonoro del buzzer
                if print_en:
                  buzzer.setBuzzer(20)
                  print_en = False
                
              move_sleep = time.ticks_ms() + 30
            
          if cmd == 0x24: # Control de ejecución y procesamiento
            if ble_data[4] < 0x80: da = ble_data[4] 
            else: da = (ble_data[4] - 256)
            nozzle_angle += da*3
            nozzle_angle = 90 if nozzle_angle > 90 else nozzle_angle
            nozzle_angle = -90 if nozzle_angle < -90 else nozzle_angle
            nozzle.set_angle(nozzle_angle, 80)
            move_sleep = time.ticks_ms() + 30
            
          elif cmd == 0x25: # Control de ejecución y procesamiento
            st = ble_data[4]
            if st == 1: nozzle.on()
            elif st == 0: nozzle.off()
            move_sleep = time.ticks_ms() + 300
            
          elif cmd == 0x06: # Control de ejecución y procesamiento
            name = ble_data[4]
            times = ble_data[5]
            if times == 0:times = 100000
            robot.runActionGroup(str(name), times)
            
          elif cmd == 0x07: # Control de ejecución y procesamiento
            robot.stopActionGroup()
    
  ble_data = bytearray()


def main(t):
  global x,y,z, move_sleep, nozzle_angle
  
  gc.collect()
  key.run_loop()
  USBDevice.run_loop()
  
  BleHandle()
  MouseHandle()
  GamepadHandle()

  if key.down_up(): # Control de ejecución y procesamiento
    if time.ticks_ms() >= move_sleep:
      robot.runActionGroup("100")
      move_sleep = time.ticks_ms() + 1500
    
  if key.down_long(): # Control de ejecución y procesamiento
    if time.ticks_ms() >= move_sleep:
      robot.stopActionGroup()
      move_sleep = time.ticks_ms() + 300


print("Start")
tim = Timer(2)
tim.init(period=15, mode=Timer.PERIODIC, callback=main)

















