import datetime

# 获取当前时间
now = datetime.datetime.now()
# 获取当前日期
today = datetime.date.today()
# 计算偏移量
offset = datetime.timedelta(days = -2)
# 获取想要的日期或时间
re_date = (now + offset).strftime('%Y-%m-%d')
re_date2 = today + offset

print(now)
print(today)
print(offset)
print(re_date)
print(re_date2)