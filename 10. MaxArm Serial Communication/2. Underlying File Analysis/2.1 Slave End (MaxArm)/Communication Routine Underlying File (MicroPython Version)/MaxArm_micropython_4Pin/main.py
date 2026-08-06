'''
@file:    main.py
@company: Hiwonder
@author:  CuZn
@date:    2024-02-28
@description: MaxArm接收 其他设备串口信息 并执行
'''

# 载入时间模块
import time
# 载入K210通信类（WonderK210），消息格式类（Find_Box_Msg_st , Find_Box_st , Find_Msg_st）
from MaxArm_ctl  import MaxArm_ctl , SELECT_PORT

# 实例化K210通信类
ma = MaxArm_ctl()

# 开启串口，使用microUSB通讯
ma.begin(SELECT_PORT.PORT_FOR_4Pin)


#loop
while True:
  # 更新接收消息
  ma.rec_data()
  time.sleep_ms(100)









