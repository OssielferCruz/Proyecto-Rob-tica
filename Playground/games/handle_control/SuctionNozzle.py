import time
from machine import Pin, PWM
from PWMServo import PWMServo

pump_io = [21,19] # Control de ejecución y procesamiento
valve_io = [18,5] # Control de ejecución y procesamiento


class SuctionNozzle:
  
  def __init__(self, pump_io=pump_io, valve_io=valve_io, hz=1000):
    self.pump_f = PWM(Pin(pump_io[0]))
    self.pump_b = PWM(Pin(pump_io[1]))
    self.valve_f = PWM(Pin(valve_io[0]))
    self.valve_b = PWM(Pin(valve_io[1]))
    self.pump_f.freq(hz)
    self.pump_b.freq(hz)
    self.valve_f.freq(hz)
    self.valve_b.freq(hz)
    self.hz = hz
    self.pwm_servo = PWMServo()
    self.pwm_servo.work_with_time()
    self.nozzle_st = False
    
  def on(self): # Control de ejecución y procesamiento
    self.pump_f.duty(self.hz)
    self.pump_b.duty(0)
    self.valve_f.duty(0)
    self.valve_b.duty(0)
    self.nozzle_st = True
  
  def off(self): # Apagar bomba de succión y liberar solenoide
    self.valve_f.duty(self.hz)
    self.valve_b.duty(0)
    self.pump_f.duty(0)
    self.pump_b.duty(0) 
    time.sleep_ms(300)
    self.valve_f.duty(0)
    self.valve_b.duty(0)
    self.nozzle_st = False
  
  def set_angle(self, angle=0, duration=1000):
    pulse = map(angle, -90, 90, 500, 2500)
    pulse = 500 if pulse < 500 else pulse
    pulse = 2500 if pulse > 2500 else pulse
    self.pwm_servo.run(1, pulse, duration)

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
