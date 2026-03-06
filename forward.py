import asyncio
import json
import websockets
import requests

WS_URL = "ws://127.0.0.1:3001"
HTTP_URL = "http://127.0.0.1:3000"
GROUP_ID = 799940831

# 缓存消息
message_buffer = {}

# 记录是否已经启动计时
timer_tasks = {}


async def send_after_delay(qq):

    await asyncio.sleep(30)

    if qq in message_buffer:

        msgs = message_buffer[qq]

        content = f"陌生人QQ: {qq}\n\n"

        for m in msgs:
            content += m + "\n"

        # 1️⃣ 转发到群
        requests.post(
            f"{HTTP_URL}/send_group_msg",
            json={
                "group_id": GROUP_ID,
                "message": content
            }
        )

        # 2️⃣ 自动回复用户
        requests.post(
            f"{HTTP_URL}/send_private_msg",
            json={
                "user_id": qq,
                "message": "你好，我们已经收到你的消息，请稍等工作人员回复。(这是自动回复，小饺子们无须回复呀)"
            }
        )

        print("已转发并自动回复:", qq)

        del message_buffer[qq]
        del timer_tasks[qq]


async def listen():

    while True:

        try:

            async with websockets.connect(WS_URL) as ws:

                print("机器人已连接")

                while True:

                    msg = await ws.recv()
                    data = json.loads(msg)

                    if data.get("post_type") != "message":
                        continue

                    if data["message_type"] == "private":

                        qq = data["user_id"]
                        text = data["raw_message"]

                        print("收到:", qq, text)

                        # 初始化缓存
                        if qq not in message_buffer:
                            message_buffer[qq] = []

                        message_buffer[qq].append(text)

                        # 如果没有启动计时器
                        if qq not in timer_tasks:

                            timer_tasks[qq] = asyncio.create_task(
                                send_after_delay(qq)
                            )

        except Exception as e:

            print("连接断开，5秒重连:", e)
            await asyncio.sleep(5)


asyncio.run(listen())
