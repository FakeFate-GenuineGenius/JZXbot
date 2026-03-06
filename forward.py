import asyncio
import json
import websockets
import requests

WS_URL = "ws://127.0.0.1:3001"
HTTP_URL = "http://127.0.0.1:3000"

GROUP_ID = 799940831   # 你的QQ群号

# 自动回复内容
AUTO_REPLY = """
你好，我现在不在线。

你的消息已经转发到群里，
管理员看到后会回复你。
"""

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

                    # 私聊消息
                    if data["message_type"] == "private":

                        qq = data["user_id"]
                        text = data["raw_message"]

                        print("收到私聊:", qq, text)

                        # 转发到群
                        forward = f"""
QQ: {qq}
消息内容: {text}
"""

                        requests.post(
                            f"{HTTP_URL}/send_group_msg",
                            json={
                                "group_id": GROUP_ID,
                                "message": forward
                            }
                        )

                        # 自动回复
                        requests.post(
                            f"{HTTP_URL}/send_private_msg",
                            json={
                                "user_id": qq,
                                "message": AUTO_REPLY
                            }
                        )

                    # 群消息
                    if data["message_type"] == "group":

                        if data["group_id"] != GROUP_ID:
                            continue

                        text = data["raw_message"]

                        # 回复格式
                        # 例如：
                        # 回复 123456 hello

                        if text.startswith("回复"):

                            parts = text.split(" ",2)

                            if len(parts) >= 3:

                                target = parts[1]
                                message = parts[2]

                                requests.post(
                                    f"{HTTP_URL}/send_private_msg",
                                    json={
                                        "user_id": target,
                                        "message": message
                                    }
                                )

                                print("已转发回复")

        except Exception as e:
            print("断开连接，5秒重连:", e)
            await asyncio.sleep(5)

asyncio.run(listen())
