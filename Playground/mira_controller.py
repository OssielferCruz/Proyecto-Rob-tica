import time
import math
import serial
import serial.tools.list_ports

class MiraController:
    """
    Controlador serial para Mira vía consola MicroPython REPL / RAW REPL en ESP32 (COM6).
    Soporta movimientos suaves, reseteo atómico, ejecución segura RAW REPL e interrupción por Ctrl+C.
    """
    def __init__(self, port="COM6", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.is_connected = False
        self.current_xyz = [0, -163, 212]
        self.suction_state = False
        self.last_cmd_time = 0
        self.connect()

    def connect(self):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(b'\x03\r\n')
                self.ser.reset_input_buffer()
                self.is_connected = True
                return True
            except Exception:
                self.is_connected = False

        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.2
            )
            self.is_connected = True
            print(f"[MiraController] [OK] Conectado exitosamente a {self.port} @ {self.baudrate}")
            
            self.ser.write(b'\x03\r\n')
            time.sleep(0.1)
            init_code = [
                "import __espmax",
                "from espmax import ESPMax",
                "from BusServo import BusServo",
                "from SuctionNozzle import SuctionNozzle",
                "bus_servo = BusServo()",
                "arm = ESPMax(bus_servo)",
                "nozzle = SuctionNozzle()"
            ]
            for line in init_code:
                self.ser.write(line.encode('utf-8') + b'\r\n')
                time.sleep(0.04)
            return True
        except Exception as e:
            self.is_connected = False
            print(f"[MiraController] [ERROR] No se pudo abrir {self.port}: {e}")
            return False

    def close(self):
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except Exception:
                pass
        self.is_connected = False

    def exec_micropython(self, cmd: str, force=False):
        now = time.time()
        if not force and (now - self.last_cmd_time < 0.05):
            return False
        self.last_cmd_time = now

        if not self.is_connected or not self.ser or not self.ser.is_open:
            if not self.connect():
                return False
        try:
            self.ser.reset_input_buffer()
            self.ser.write(cmd.encode('utf-8') + b'\r\n')
            self.ser.flush()
            return True
        except Exception as e:
            print(f"[MiraController] Error enviando comando REPL: {e}")
            self.is_connected = False
            return False

    def exec_raw_repl(self, code_str: str):
        """
        Ejecuta o escribe un script Python completo en el ESP32 en modo RAW REPL (Ctrl+A),
        evitando cualquier error de sintaxis o sangría.
        """
        if not self.is_connected or not self.ser or not self.ser.is_open:
            if not self.connect():
                return False
        try:
            # 1. Entrar a RAW REPL (Ctrl+A = \x01)
            self.ser.write(b'\x01')
            time.sleep(0.2)
            self.ser.read_all()

            # 2. Enviar bloque de código
            self.ser.write(code_str.encode('utf-8'))
            time.sleep(0.1)

            # 3. Ejecutar comando (Ctrl+D = \x04)
            self.ser.write(b'\x04')
            time.sleep(0.5)

            # 4. Salir de RAW REPL (Ctrl+B = \x02)
            self.ser.write(b'\x02')
            time.sleep(0.1)
            return True
        except Exception as e:
            print(f"[MiraController] Error en ejecucion Raw REPL: {e}")
            self.is_connected = False
            return False

    def set_xyz(self, x, y, z, move_time=None):
        dx = int(x) - self.current_xyz[0]
        dy = int(y) - self.current_xyz[1]
        dz = int(z) - self.current_xyz[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)

        if move_time is None:
            move_time = int(max(600, min(2200, 450 + dist * 5)))

        self.current_xyz = [int(x), int(y), int(z)]
        repl_cmd = f"arm.set_position(({int(x)}, {int(y)}, {int(z)}), {int(move_time)})"
        return self.exec_micropython(repl_cmd, force=True)

    def set_pwm_servo(self, angle, move_time=400):
        repl_cmd = f"nozzle.set_angle({int(angle - 90)}, {int(move_time)})"
        return self.exec_micropython(repl_cmd)

    def set_suction_nozzle(self, state: bool):
        self.suction_state = state
        repl_cmd = "nozzle.on()" if state else "nozzle.off()"
        return self.exec_micropython(repl_cmd, force=True)

    def go_home(self, move_time=1800):
        self.suction_state = False
        self.current_xyz = [0, -163, 212]
        home_cmd = f"nozzle.off(); arm.go_home({int(move_time)})"
        return self.exec_micropython(home_cmd, force=True)

    def stop_game(self):
        """
        Envía interrupción Ctrl+C atómica sobre el bus serie para salir de Raw REPL o while True,
        apaga la bomba y retorna a Home.
        """
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(b'\x02\x03\x03\r\n')
                time.sleep(0.15)
                self.ser.reset_input_buffer()
            except Exception:
                pass
        return self.go_home(1500)
