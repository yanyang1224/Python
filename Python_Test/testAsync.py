import asyncio
import time

async def say_after(delay,what):
    await asyncio.sleep(delay)
    print(what)

# # 测试第一种调用方式，耗时3S
# async def main():
#     print(f"started at {time.strftime('%X')}")

#     await say_after(1,'hello')
#     await say_after(2,'world')

#     print(f"finished at {time.strftime('%X')}")

# # 测试第二种使用asyncio.create_task()函数并发调用，耗时2s
# async def main():
#     task1 = asyncio.create_task(say_after(1,'hello'))
#     task2 = asyncio.create_task(say_after(2,'world'))
#     print(f"started at {time.strftime('%X')}")
#     await task1
#     await task2
#     print(f"finished at {time.strftime('%X')}")

# # 创建一个tasks列表，并用await asyncio.wait(tasks)方法并行调用，调用时间为9s
# async def main():
#     print(f"started at {time.strftime('%X')}")
#     tasks = [asyncio.ensure_future(say_after(mill,'hello')) for mill in range(1,10)]
#     print(f"prepared at {time.strftime('%X')}")
#     await asyncio.wait(tasks)
#     print(f"finished at {time.strftime('%X')}")

# 当协程并未开启时可采用该方法并行调用tasks列表，调用时间为9s
def main():
    print(f"started at {time.strftime('%X')}")
    tasks = [asyncio.ensure_future(say_after(mill,'hello')) for mill in range(1,10)]
    print(f"prepared at {time.strftime('%X')}")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    print(f"finished at {time.strftime('%X')}")

# asyncio.run(main())
main()