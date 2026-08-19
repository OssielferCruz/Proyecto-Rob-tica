from micropython import const
import time
import struct
import gc

WONDERCAM_FUNC_NONE = const(0x00)
WONDERCAM_FUNC_FACE_DETECT = const(0x01)
WONDERCAM_FUNC_OBJ_DETECT = const(0x02)
WONDERCAM_FUNC_CLASSIFICATION = const(0x03)
WONDERCAM_FUNC_FEATURE_LEARNING = const(0x04)
WONDERCAM_FUNC_COLOR_DETECT = const(0x05)
WONDERCAM_FUNC_LINE_FOLLOWING = const(0x06)
WONDERCAM_FUNC_APRILTAG = const(0x07)
WONDERCAM_FUNC_QRCODE = const(0x08)
WONDERCAM_FUNC_BARCODE = const(0x09)

WONDERCAM_OBJ_AIRPLANE = const(1)
WONDERCAM_OBJ_BICYCLE = const(2)
WONDERCAM_OBJ_BIRD = const(3)
WONDERCAM_OBJ_BOAT = const(4)
WONDERCAM_OBJ_BOTTLE = const(5)
WONDERCAM_OBJ_BUS = const(6)
WONDERCAM_OBJ_CAR = const(7)
WONDERCAM_OBJ_CAT = const(8)
WONDERCAM_OBJ_CHAIR = const(9)
WONDERCAM_OBJ_COW = const(10)
WONDERCAM_OBJ_DINING_TABLE = const(11)
WONDERCAM_OBJ_DOG = const(12)
WONDERCAM_OBJ_HORSE = const(13)
WONDERCAM_OBJ_MOTORBIKE = const(14)
WONDERCAM_OBJ_PERSON = const(15)
WONDERCAM_OBJ_POTTED_PLANT = const(16)
WONDERCAM_OBJ_SHEEP = const(17)
WONDERCAM_OBJ_SOFA = const(18)
WONDERCAM_OBJ_TRAIN = const(19)
WONDERCAM_OBJ_MONITOR = const(20)


def get_addr_bytes(addr):
    lb = addr & 0xFF
    hb = (addr >> 8) & 0xFF
    return bytearray([lb, hb])


class WonderCam:
    def __init__(self, i2c, address=0x32):
        self.address = address# Controlador I2C para módulo de visión artificial WonderCam
        self.bus = i2c # Control de ejecución y procesamiento
        self.summary = b'' # Control de ejecución y procesamiento
        self.result = b'' # Control de ejecución y procesamiento
        self.curFunc = 0 # Control de ejecución y procesamiento

    def read_from_mem(self, addr, length):
        self.bus.writeto(self.address, get_addr_bytes(addr))
        return self.bus.readfrom(self.address, length)

    def firmware_version(self):
        """
            :   # Lectura I2C del sensor de visión WonderCam
            :   # Lectura I2C del sensor de visión WonderCam
            :  , : "v0.6.5" # Lectura I2C del sensor de visión WonderCam
        """
        # WONDERCAM_REG_SYS_FIRMWARE_VERSION = const(0x0000)
        return self.read_from_mem(0x0000, 16).decode('utf-8').replace('\x00', '')

    def set_led(self, new_st):
        """
            :  LED # Lectura I2C del sensor de visión WonderCam
            :  new_st LED, False, True # Lectura I2C del sensor de visión WonderCam
            : None # Lectura I2C del sensor de visión WonderCam
        """
        # WONDERCAM_REG_SYS_LIGHT_STATE = const(0x0030)
        led = get_addr_bytes(0x0030)
        led += bytes([new_st])
        self.bus.writeto(self.address, led)

    def cur_func(self):
        """
            :   # Lectura I2C del sensor de visión WonderCam
            : fun  # Lectura I2C del sensor de visión WonderCam
            : None # Lectura I2C del sensor de visión WonderCam
        """
        # WONDERCAM_REG_SYS_CURRENT_FUNC = const(0x0035)
        return int(self.read_from_mem(0x0035, 1)[0])

    def set_func(self, func, timeout=3000):
        """
            : ,  # Lectura I2C del sensor de visión WonderCam
            : fun ,  timeout # Lectura I2C del sensor de visión WonderCam
            : True, False # Lectura I2C del sensor de visión WonderCam
        """
        # WONDERCAM_REG_SYS_CURRENT_FUNC = const(0x0035)
        data = get_addr_bytes(0x0035)
        data += bytes([func])
        self.bus.writeto(self.address, data)
        timeout += time.ticks_ms()
        while True:
            time.sleep_ms(50)
            if self.cur_func() == func:
                return True
            if time.ticks_ms() > timeout:
                return False

    def update_result(self):
        """
            :  # Lectura I2C del sensor de visión WonderCam
            :  # Lectura I2C del sensor de visión WonderCam
            : None # Lectura I2C del sensor de visión WonderCam
        """
        # WONDERCAM_REG_FACE_DETECT_BASE = const(0x0400)
        # WONDERCAM_REG_OBJ_DETECT_BASE = const(0x0800)
        # WONDERCAM_REG_CLASSIFICATION_BASE = const(0x0C00)
        # WONDERCAM_REG_FEATURE_LEARNING_BASE = const(0x0E00)
        # WONDERCAM_REG_COLOR_DETECT_BASE = const(0x1000)
        # WONDERCAM_REG_LINE_FOLLOWING_BASE = const(0x1400)
        # WONDERCAM_REG_APRILTAG_BASE = const(0x1E00)
        # WONDERCAM_REG_QRCODE_BASE = const(0x1800)
        # WONDERCAM_REG_BARCODE_BASE = const(0x1C00)
        cur_func = self.cur_func()
        self.curFunc = cur_func
        tmp = (None, 0x0400, 0x0800, 0x0C00, 0x0E00, 0x1000, 0x1400, 0x1E00, 0x1800, 0x1C00)
        addr = tmp[cur_func]
        if addr is None:
            return
        self.summary = self.read_from_mem(addr, 48) # Control de ejecución y procesamiento
        if self.summary[1] > 0: # Control de ejecución y procesamiento
            if 0 < cur_func < 3 or 5 <= cur_func < 7:
                self.result = self.read_from_mem(addr + 0x30, 16 * self.summary[1])
            elif cur_func == 7:
                self.result = self.read_from_mem(addr + 0x30, 32 * self.summary[1])
            else: # Control de ejecución y procesamiento
                self.result = b''
        else:
            self.result = b''

    def is_face_detected(self, id_want=None):
        """
            : ID # Lectura I2C del sensor de visión WonderCam
            : id_want1~5id, None, 0 # Lectura I2C del sensor de visión WonderCam
            :  True # Lectura I2C del sensor de visión WonderCam
                   False # Lectura I2C del sensor de visión WonderCam
        """
        if self.curFunc == WONDERCAM_FUNC_FACE_DETECT and self.summary[1] > 0: # Control de ejecución y procesamiento
            if id_want is None: # Control de ejecución y procesamiento
                return True
            if id_want == 0:
                id_want = 0xFF
            for i in range(4, 4 + self.summary[1]): # Control de ejecución y procesamiento
                if self.summary[i] == id_want:
                    return True
        return False

    def get_face(self, id_want, face_type=1): # Control de ejecución y procesamiento
        """
          :  # Lectura I2C del sensor de visión WonderCam
          : id_want ID， face_type=2 # Lectura I2C del sensor de visión WonderCam
                face_type ， face_type = 1， face_type = 2  # Lectura I2C del sensor de visión WonderCam
          : (X Y, , ) # Lectura I2C del sensor de visión WonderCam
                 None # Lectura I2C del sensor de visión WonderCam
        """
        if self.is_face_detected():
            if face_type == 1: # Control de ejecución y procesamiento
                for i in range(4, 4 + self.summary[1]): # Control de ejecución y procesamiento
                    if self.summary[i] == id_want:
                        index = 16 * (i - 4)
                        return struct.unpack("<hhHH", self.result[index: index + 8])
            elif face_type == 2: # Control de ejecución y procesamiento
                for i in range(4, 4 + self.summary[1]):
                    if self.summary[i] == 0xFF:
                        id_want -= 1 # Control de ejecución y procesamiento
                        if id_want == 0:
                            index = 16 * (i - 4)
                            return struct.unpack("<hhHH", self.result[index: index + 8])
            else:
                pass
        return None

    def __is_detected_common(self, func, id_want):
        if self.curFunc == func and self.summary[1] > 0:
            if id_want is None:
                return True
            else:
                for i in range(2, 2 + self.summary[1]):
                    if self.summary[i] == id_want:
                        return True
        return False

    def is_object_detected(self, id_want=None):
        """
            : ID # Lectura I2C del sensor de visión WonderCam
            : id_wantNone, id_wantID # Lectura I2C del sensor de visión WonderCam
            :  True # Lectura I2C del sensor de visión WonderCam
                  False # Lectura I2C del sensor de visión WonderCam
        """
        return self.__is_detected_common(WONDERCAM_FUNC_OBJ_DETECT, id_want)

    def get_object(self, id_want, index):
        """
            :  # Lectura I2C del sensor de visión WonderCam
            : id_wantID， index() # Lectura I2C del sensor de visión WonderCam
            : (X, Y, , ) # Lectura I2C del sensor de visión WonderCam
        """
        if self.is_object_detected():
            for i in range(2, 2 + self.summary[1]):
                if self.summary[i] == id_want:
                    index -= 1
                    if index == 0:
                        index = 16 * (i - 2)
                        return struct.unpack("<hhHH", self.result[index: index + 8])
        return None

    def most_likely_id(self):
        """
          : ID # Lectura I2C del sensor de visión WonderCam
          :  # Lectura I2C del sensor de visión WonderCam
          : , ID # Lectura I2C del sensor de visión WonderCam
        """
        if self.curFunc == WONDERCAM_FUNC_CLASSIFICATION or self.curFunc == WONDERCAM_FUNC_FEATURE_LEARNING:
            return self.summary[1]
        return 0

    def max_conf(self):
        """
          : ID # Lectura I2C del sensor de visión WonderCam
          :  # Lectura I2C del sensor de visión WonderCam
          : ,  # Lectura I2C del sensor de visión WonderCam
        """
        if self.curFunc == WONDERCAM_FUNC_CLASSIFICATION or self.curFunc == WONDERCAM_FUNC_FEATURE_LEARNING:
            conf = int.from_bytes(self.summary[2:4], "little", False)
            conf = conf / 10000.0
            return conf
        return 0

    def conf_of_id(self, id_want):
        """
          : id_want # Lectura I2C del sensor de visión WonderCam
          :  # Lectura I2C del sensor de visión WonderCam
          : ,  # Lectura I2C del sensor de visión WonderCam
        """
        if self.curFunc == WONDERCAM_FUNC_CLASSIFICATION or self.curFunc == WONDERCAM_FUNC_FEATURE_LEARNING:
            addr = 0x10 + ((id_want - 1) * 4)
            conf = int.from_bytes(self.summary[addr: addr + 2], "little", False)
            conf = conf / 10000.0
            return conf
        return 0

    def is_color_blob_detected(self, id_want=None):
        """
          : ID # Lectura I2C del sensor de visión WonderCam
          : id_want=ID, id_wantNoneID， id_want1~7ID # Lectura I2C del sensor de visión WonderCam
          :  True # Lectura I2C del sensor de visión WonderCam
                 False # Lectura I2C del sensor de visión WonderCam
        """
        return self.__is_detected_common(WONDERCAM_FUNC_COLOR_DETECT, id_want)

    def get_color_blob(self, id_want):
        """
          : ID # Lectura I2C del sensor de visión WonderCam
          : id_want=ID # Lectura I2C del sensor de visión WonderCam
          : (X Y, , ) # Lectura I2C del sensor de visión WonderCam
                 None # Lectura I2C del sensor de visión WonderCam
        """
        if self.is_color_blob_detected(id_want):
            for i in range(2, 2 + self.summary[1]):
                if self.summary[i] == id_want:
                    index = 16 * (i - 2)
                    return struct.unpack("<hhHH", self.result[index: index + 8])
        return None

    def is_line_detected(self, id_want=None):
        """
          : ID # Lectura I2C del sensor de visión WonderCam
          : id_want=ID, id_wantNoneID， id_want1~3ID # Lectura I2C del sensor de visión WonderCam
          :  True # Lectura I2C del sensor de visión WonderCam
                 False # Lectura I2C del sensor de visión WonderCam
        """
        return self.__is_detected_common(WONDERCAM_FUNC_LINE_FOLLOWING, id_want)

    def get_line(self, id_want):
        """
          : ID # Lectura I2C del sensor de visión WonderCam
          : id_want=ID # Lectura I2C del sensor de visión WonderCam
          : (X， Y, X, Y, , ) # Lectura I2C del sensor de visión WonderCam
                 None # Lectura I2C del sensor de visión WonderCam
        """
        if self.is_line_detected(id_want):
            for i in range(2, 2 + self.summary[1]):
                if self.summary[i] == id_want:
                    index = 16 * (i - 2)
                    x, y, w, h, angle, offset = struct.unpack("<hhHHhh", self.result[index: index + 12])
                    angle = angle - 180 if angle > 90 else angle
                    offset = abs(offset) - 160
                    return x, y, w, h, angle, offset
        return None

    """
    apriltag, WonderCam Standard v1TAG36H11,apriltag # Lectura I2C del sensor de visión WonderCam
    """

    def is_tag_detected(self, id_want=None):
        """
          : ， ID # Lectura I2C del sensor de visión WonderCam
          : id_want NoneID, IDID # Lectura I2C del sensor de visión WonderCam
          :   True # Lectura I2C del sensor de visión WonderCam
                 False # Lectura I2C del sensor de visión WonderCam
        """
        return self.__is_detected_common(WONDERCAM_FUNC_APRILTAG, id_want)

    def num_of_tag_detected(self, id_want=None):
        """
          :  # Lectura I2C del sensor de visión WonderCam
          : id_want None, IDID # Lectura I2C del sensor de visión WonderCam
          :   # Lectura I2C del sensor de visión WonderCam
                0 # Lectura I2C del sensor de visión WonderCam
        """
        ret = 0
        if self.curFunc == WONDERCAM_FUNC_APRILTAG:
            if id_want is None:
                return int(self.summary[1])
            else:
                if id_want >= 0:
                    for i in range(2, 2 + self.summary[1]):
                        if self.summary[i] == id_want:
                            ret += 1
        return ret

    def get_tag(self, id_want, index):
        """
          : indexidid_want # Lectura I2C del sensor de visión WonderCam
          : id_wantid, indexindexid_want (id, ) # Lectura I2C del sensor de visión WonderCam
          :  (X, Y, , , X, X, Y, Y, Z, Z) # Lectura I2C del sensor de visión WonderCam
        """
        if self.is_tag_detected():
            for i in range(2, 2 + self.summary[1]):
                if self.summary[i] == id_want:
                    index -= 1
                    if index == 0:
                        index = 32 * (i - 2)
                        return struct.unpack("<hhHHffffff", self.result[index: index + 32])
        return None

    def is_qrcode_detected(self):
        """
          :  # Lectura I2C del sensor de visión WonderCam
          :  # Lectura I2C del sensor de visión WonderCam
          :  True # Lectura I2C del sensor de visión WonderCam
                 False # Lectura I2C del sensor de visión WonderCam
        """
        if self.curFunc == WONDERCAM_FUNC_QRCODE and self.summary[1] > 0:
            return True
        return False

    def is_barcode_detected(self):
        """
          :  # Lectura I2C del sensor de visión WonderCam
          :  # Lectura I2C del sensor de visión WonderCam
          :  True # Lectura I2C del sensor de visión WonderCam
                 False # Lectura I2C del sensor de visión WonderCam
        """
        if self.curFunc == WONDERCAM_FUNC_BARCODE and self.summary[1] > 0:
            return True
        return False

    def len_of_code(self):
        """
           : / # Lectura I2C del sensor de visión WonderCam
           :  # Lectura I2C del sensor de visión WonderCam
           : /, /0 # Lectura I2C del sensor de visión WonderCam
         """
        if self.is_qrcode_detected() or self.is_barcode_detected():
            return int.from_bytes(self.summary[0x20: 0x22], "little", False)
        return 0

    def update_code_content(self):
        """
           : /, # Lectura I2C del sensor de visión WonderCam
           :  # Lectura I2C del sensor de visión WonderCam
           : None # Lectura I2C del sensor de visión WonderCam
        """
        # WONDERCAM_REG_QRCODE_BASE = const(0x1800)
        # WONDERCAM_REG_BARCODE_BASE = const(0x1C00)
        if self.result == b'':
            length = self.len_of_code()
            if length > 0:
                if self.curFunc == WONDERCAM_FUNC_QRCODE:
                    self.result = self.read_from_mem(0x1830, length)
                elif self.curFunc == WONDERCAM_FUNC_BARCODE:
                    self.result = self.read_from_mem(0x1C30, length)
                else:
                    pass

    def string_from_code(self):
        """
          : /() # Lectura I2C del sensor de visión WonderCam
          :  # Lectura I2C del sensor de visión WonderCam
          : /, //DecodeNone # Lectura I2C del sensor de visión WonderCam
        """
        code_str = None
        if self.is_qrcode_detected() or self.is_barcode_detected():
            self.update_code_content()
            try:
                code_str = self.result.decode("utf-8")
            except:
                pass
        return code_str

    def bytes_from_code(self):
        """
          : /() # Lectura I2C del sensor de visión WonderCam
          :  # Lectura I2C del sensor de visión WonderCam
          : /, b'' # Lectura I2C del sensor de visión WonderCam
        """
        if self.is_qrcode_detected() or self.is_barcode_detected():
            self.update_code_content()
        return self.result


gc.collect()

if __name__ == "__main__":
    from machine import Pin, I2C
    i2c = I2C(0, scl=Pin(16), sda=Pin(17), freq=400000)
    cam = WonderCam(i2c)
    cam.set_func(WONDERCAM_FUNC_FACE_DETECT) # Control de ejecución y procesamiento
    while True:
        cam.update_result()
        print(cam.get_face(1, 2)) # Control de ejecución y procesamiento
        time.sleep(0.2)

