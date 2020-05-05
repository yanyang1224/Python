import sys
import os
from apscheduler.schedulers.blocking import BlockingScheduler

rootPath = os.path.abspath('../')
sys.path.append(rootPath)

from BookGetter.GetBook import GetBook
from Util import LogHandler

def runSchedule():
    getBook = GetBook()
    # getBook.getCip()
    # getBook.getDoubanBook()

    scheduler_log = LogHandler("scheduler_log")
    scheduler = BlockingScheduler(logger=scheduler_log)

    # scheduler.add_job(getBook.DownCover, 'interval', minutes=1)
    # scheduler.add_job(getBook.getCip, 'interval', minutes=1)
    scheduler.add_job(getBook.getDoubanBook, 'interval', minutes=1)

    scheduler.start()

if __name__=='__main__':
    runSchedule()