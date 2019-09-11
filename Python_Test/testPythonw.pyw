import time
import logging
import logging.handlers
 
# logging初始化工作
logging.basicConfig()
 
# myapp的初始化工作
myapp = logging.getLogger('myapp')
myapp.setLevel(logging.INFO)
 
# 添加TimedRotatingFileHandler
# 定义一个1秒换一次log文件的handler
# 保留3个旧log文件
filehandler = logging.handlers.TimedRotatingFileHandler("test.log", when='S', interval=1, backupCount=3)
# 设置后缀名称，跟strftime的格式一样
filehandler.suffix = "%Y-%m-%d_%H-%M-%S.log"
myapp.addHandler(filehandler)
 
while True:
    time.sleep(0.1)
    myapp.info("test")


# python.exe在运行程序的时候，会弹出一个黑色的控制台窗口（也叫命令行窗口、DOS/CMD窗口）；
# pythonw.exe是无窗口的Python可执行程序，意思是在运行程序的时候，没有窗口，代码在后台执行。
# 跟 python.exe 比较起来，pythonw.exe 有以下的不同：
# 1）执行时不会弹出控制台窗口（也叫 DOS 窗口）
# 2）所有向原有的 stdout 和 stderr 的输出都无效
# 3）所有从原有的 stdin 的读取都只会得到 EOF