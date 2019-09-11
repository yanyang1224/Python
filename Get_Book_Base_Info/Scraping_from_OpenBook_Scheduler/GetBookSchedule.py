from datetime import date,datetime
from apscheduler.schedulers.blocking import BlockingScheduler

from GetRecentBook import GetRecentBook

def getRecentBook():
    pp = GetRecentBook()
    pp.run()

def run():
    # BlockingScheduler
    sched = BlockingScheduler()
    # 每天凌晨运行
    sched.add_job(getRecentBook, 'cron', hour=0, misfire_grace_time=60, coalesce=True)
    # # 每间隔2小时执行一次
    # sched.add_job(getRecentBook, 'interval', hour=2)
    sched.start()

if __name__=='__main__':
    run()