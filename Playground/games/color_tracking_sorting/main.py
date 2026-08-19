import time
from machine import Pin, I2C
from PID import PID
from WonderCam import *
from Buzzer import Buzzer
from espmax import ESPMax
from PWMServo import PWMServo
from BusServo import BusServo
from SuctionNozzle import SuctionNozzle


pwm = PWMServo()
buzzer = Buzzer()
pwm.work_with_time()
bus_servo = BusServo()
arm = ESPMax(bus_servo)
nozzle = SuctionNozzle()
i2c = I2C(0, scl=Pin(16), sda=Pin(17), freq=400000)
cam = WonderCam(i2c)
cam.set_func(WONDERCAM_FUNC_COLOR_DETECT) # Control de ejecución y procesamiento
cam.set_led(False)

if __name__ == '__main__':
  i = 0
  x, y, z = 0, -120, 150
  buzzer.setBuzzer(100)# Alarma de confirmación sonora
  nozzle.set_angle(0,1000)# Módulo de bomba de succión por vacío y boquilla
  arm.set_position((x, y, z), 2000)
  time.sleep_ms(2000)
  x_pid = PID(0.08, 0.003, 0.0003) # Control de ejecución y procesamiento
  y_pid = PID(0.08, 0.003, 0.0003)
  
  while True:
    cam.update_result() # Control de ejecución y procesamiento
    if cam.get_color_blob(1): # Control de ejecución y procesamiento
      color_num = 1
      color_data = cam.get_color_blob(1) # Control de ejecución y procesamiento
    elif cam.get_color_blob(2): # Control de ejecución y procesamiento
      color_num = 2
      color_data = cam.get_color_blob(2) # Control de ejecución y procesamiento
    elif cam.get_color_blob(3): # Control de ejecución y procesamiento
      color_num = 3
      color_data = cam.get_color_blob(3) # Control de ejecución y procesamiento
    else:
      color_num = 0
      color_data = None
      
    if color_data:
      center_x = color_data[0] 
      center_y = color_data[1]
      
      if abs(center_x - 160) < 15: # Control de ejecución y procesamiento
        center_x = 160 
      x_pid.SetPoint = 160
      x_pid.update(center_x)
      dx = x_pid.output
      x -= dx
      x = 100 if x > 100 else x# Controlador cinemático cartesiano del brazo Mira
      x = -100 if x < -100 else x
      
      if abs(center_y - 120) < 5: # Control de ejecución y procesamiento
        center_y = 120
      y_pid.SetPoint = 120
      y_pid.update(center_y)
      dy = y_pid.output
      y -= dy
      y = -60 if y > -60 else y# Controlador cinemático cartesiano del brazo Mira
      y = -200 if y < -200 else y 
      
      arm.set_position((x,y,z),50)# Controlador cinemático cartesiano del brazo Mira
      
      if abs(dx) < 0.1 and abs(dy) < 0.1:
        i += 1
        if i > 10:
          i = 0
          buzzer.setBuzzer(100)# Alarma de confirmación sonora
          if color_num == 1:# Detección de bloque/tarjeta de color
            print('color: red')
            angle = 45 # Control de ejecución y procesamiento
            (place_x, place_y, place_z) = (-120,-140,85) # Control de ejecución y procesamiento
          elif color_num == 2:# Detección de bloque/tarjeta de color
            print('color: green')
            angle = 62
            (place_x, place_y, place_z) = (-120,-80,85)
          elif color_num == 3:# Detección de bloque/tarjeta de color
            print('color: blue')
            angle = 90
            (place_x, place_y, place_z) = (-120,-20,85)
          else:
            pass 
          
          d_x = x/2.3
          d_y = (68-abs(d_x/3))
          arm.set_position((x+d_x,y-d_y,100),1000)# Controlador cinemático cartesiano del brazo Mira
          time.sleep_ms(1000)
          arm.set_position((x+d_x,y-d_y,86),600) # Control de ejecución y procesamiento
          nozzle.on() # Control de ejecución y procesamiento
          time.sleep_ms(1000)
          arm.set_position((x+d_x,y-d_y,150),1000)# Controlador cinemático cartesiano del brazo Mira
          time.sleep_ms(1000)
          arm.set_position((place_x,place_y,150),1500) # Control de ejecución y procesamiento
          nozzle.set_angle(angle,1500) # Control de ejecución y procesamiento
          time.sleep_ms(1500)
          arm.set_position((place_x,place_y,place_z),1000) # Control de ejecución y procesamiento
          time.sleep_ms(1200)
          nozzle.off() # Control de ejecución y procesamiento
          arm.set_position((place_x,place_y,150),1000)# Controlador cinemático cartesiano del brazo Mira
          time.sleep_ms(1000)
          
          x, y, z = 0, -120, 150
          arm.set_position((x, y, z), 2000)# Controlador cinemático cartesiano del brazo Mira
          nozzle.set_angle(0,1800)# Módulo de bomba de succión por vacío y boquilla
          time.sleep_ms(2000)
      
    time.sleep_ms(50) # Control de ejecución y procesamiento





















