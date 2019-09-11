from datetime import date,datetime
from apscheduler.schedulers.blocking import BlockingScheduler

class TestSchedule:
    def my_job(self,text):
        print(text)

    def job_function(self):
        print("Hello World")

# BlockingScheduler
sched = BlockingScheduler()

testSchedule = TestSchedule()

# 只会在2009-11-06 00:00:00 执行一次
sched.add_job(testSchedule.my_job, 'date', run_date=date(2009, 11, 6), args=['text'])
# 只会在2009-11-06 16:30:05执行一次
sched.add_job(testSchedule.my_job, 'date', run_date=datetime(2009, 11, 6, 16, 30, 5), args=['text'])
sched.add_job(testSchedule.my_job, 'date', run_date='2019-08-14 11:27:00', args=['text'])

# 6到8月， 11-12月的第三个星期五的00:00, 01:00, 02:00 和 03:00 启动。
sched.add_job(testSchedule.job_function, 'cron', month='6-8,11-12', day='3rd fri', hour='0-3')

# 周一到周五早上5:30运行，直到2020-05-30截止
sched.add_job(testSchedule.job_function, 'cron', day_of_week='mon-fri', hour=5, minute=30, end_date='2020-05-30')
# 周一到周五，早上6:30运行
sched.add_job(testSchedule.job_function, 'cron', day_of_week='1-5', hour=6, minute=30)
# 每天凌晨运行
sched.add_job(testSchedule.job_function, 'cron', hour=0)

# 每间隔2小时执行一次
sched.add_job(testSchedule.job_function, 'interval', hours=2)
# 每间隔2小时执行一次， 从2010-10-10 09:30:00开始到2014-06-15 11:00:00截止。
sched.add_job(testSchedule.job_function, 'interval', hours=2, start_date='2010-10-10 09:30:00', end_date='2014-06-15 11:00:00')
# 每间隔一分钟调度一次
sched.add_job(testSchedule.job_function, 'interval', minutes=1)
# 每间隔一秒调度一次
sched.add_job(testSchedule.job_function, 'interval', seconds=1)

sched.start()

# # corn的使用规则
# year (int|str) – 4-digit year
# month (int|str) – month (1-12)
# day (int|str) – day of the (1-31)
# week (int|str) – ISO week (1-53)
# day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
# hour (int|str) – hour (0-23)
# minute (int|str) – minute (0-59)
# second (int|str) – second (0-59)
# start_date (datetime|str) – earliest possible date/time to trigger on (inclusive)
# end_date (datetime|str) – latest possible date/time to trigger on (inclusive)
# timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone)

# # interval的使用规则
# weeks (int) – number of weeks to wait
# days (int) – number of days to wait
# hours (int) – number of hours to wait
# minutes (int) – number of minutes to wait
# seconds (int) – number of seconds to wait
# start_date (datetime|str) – starting point for the interval calculation
# end_date (datetime|str) – latest possible date/time to trigger on
# timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations


# 在add_job()中添加参数：
# misfire_grace_time: 主要就是为了解决这个was missed by 这个报错，添加允许容错的时间，单位为：s
# coalesce：如果系统因某些原因没有执行任务，导致任务累计，为True则只运行最后一次，为False 则累计的任务全部跑一遍
