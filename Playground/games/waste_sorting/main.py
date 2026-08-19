import time
from machine import Pin, I2C
from PID import PID
from WonderCam import *
from Buzzer import Buzzer
from espmax import ESPMax
from PWMServo import PWMServo
from BusServo import BusServo
from SuctionNozzle import SuctionNozzle

# Clasificación inteligente de residuos con cámara WonderCam

pwm = PWMServo()
buzzer = Buzzer()
pwm.work_with_time()
bus_servo = BusServo()
arm = ESPMax(bus_servo)
nozzle = SuctionNozzle()
i2c = I2C(0, scl=Pin(16), sda=Pin(17), freq=400000)
cam = WonderCam(i2c)
cam.set_func(WONDERCAM_FUNC_CLASSIFICATION) # Control de ejecución y procesamiento
cam.set_led(True)

if __name__ == '__main__':
  x, y, z = 0, -120, 150
  buzzer.setBuzzer(100)# Alarma de confirmación sonora
  nozzle.set_angle(0,1000)# Módulo de bomba de succión por vacío y boquilla
  arm.set_position((x, y, z), 2000)
  time.sleep_ms(2000)
  result_data = []
  result = 0
  
  while True:
    cam.update_result() # Control de ejecución y procesamiento
    result_data.append(cam.most_likely_id()) # Control de ejecución y procesamiento
    if len(result_data) == 30: # Control de ejecución y procesamiento
      result = sum(result_data) / 30.0 # Control de ejecución y procesamiento
      result_data = []
      
      if result != int(result): # Control de ejecución y procesamiento
        result = 0
        continue # Control de ejecución y procesamiento
      
      if 2 <= result and result <= 4: # Control de ejecución y procesamiento
        print('id:',int(result),' Hazardous waste')
        angle = 38 # Control de ejecución y procesamiento
        move_time = 1000
        (place_x, place_y, place_z) = (-120,-170,60) # Control de ejecución y procesamiento
        
      elif 5 <= result and result <= 7: # Control de ejecución y procesamiento
        print('id:',int(result),' Recyclable material')
        angle = 52
        move_time = 1200
        (place_x, place_y, place_z) = (-120,-120,60)
        
      elif 8 <= result and result <= 10: # Control de ejecución y procesamiento
        print('id:',int(result),' Kitchen garbage')
        angle = 68
        move_time = 1400
        (place_x, place_y, place_z) = (-120,-70,60)
        
      elif 11 <= result and result <= 13: # Control de ejecución y procesamiento
        print('id:',int(result),' Other garbage')
        angle = 90
        move_time = 1600
        (place_x, place_y, place_z) = (-120,-20,60)
        
      else: # Control de ejecución y procesamiento
        continue # Control de ejecución y procesamiento

      d_y = 65
      buzzer.setBuzzer(100)# Alarma de confirmación sonora
      arm.set_position((x,y-d_y,100),1000)# Controlador cinemático cartesiano del brazo Mira
      time.sleep_ms(1000)
      arm.set_position((x,y-d_y,50),600) # Control de ejecución y procesamiento
      nozzle.on() # Control de ejecución y procesamiento
      time.sleep_ms(1000)
      arm.set_position((x,y-d_y,150),800)# Controlador cinemático cartesiano del brazo Mira
      time.sleep_ms(1000)
      arm.set_position((place_x,place_y,150),move_time) # Control de ejecución y procesamiento
      nozzle.set_angle(angle,move_time) # Control de ejecución y procesamiento
      time.sleep_ms(move_time)
      arm.set_position((place_x,place_y,place_z),800) # Control de ejecución y procesamiento
      time.sleep_ms(1000)
      nozzle.off() # Control de ejecución y procesamiento
      arm.set_position((place_x,place_y,150),800)# Controlador cinemático cartesiano del brazo Mira
      time.sleep_ms(1000)
      
      x, y, z = 0, -120, 150
      arm.set_position((x, y, z), move_time)# Controlador cinemático cartesiano del brazo Mira
      nozzle.set_angle(0,move_time)# Módulo de bomba de succión por vacío y boquilla
      time.sleep_ms(move_time)
      
    time.sleep_ms(50) # Control de ejecución y procesamiento





















