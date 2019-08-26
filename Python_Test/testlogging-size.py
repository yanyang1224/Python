
#!/usr/bin/env python3
 
import time
import logging
import logging.handlers
 
# logging初始化工作
logging.basicConfig()
 
# myapp的初始化工作
myapp = logging.getLogger('myapp')
myapp.setLevel(logging.INFO)
 
# 写入文件，如果文件超过100个Bytes，仅保留5个文件。
handler = logging.handlers.RotatingFileHandler(
              'test.log', maxBytes=100, backupCount=5)
 
# 设置后缀名称，跟strftime的格式一样
myapp.addHandler(handler)
 
while True:
    time.sleep(0.01)
    myapp.info("file test")