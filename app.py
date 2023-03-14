import sys
import os
import json
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from datetime import datetime
from urllib import request

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])
channel_id = os.environ["CHANNEL_ID"]
watch_time = int(os.environ.get("WATCH_TIME", 600))

holiday_api_url = 'https://timor.tech/api/holiday/info/'
reply_template = [
    "Great! first volunteer, I will listen carefully. 👂",
    "What awesome topic you bring today? 🦹‍",
    "Wow, look like we have too may topic today, let's keep the length under control, ok? 🙉",
]
topic_count = 0


def is_friday():
    d = datetime.now()

    if d.isoweekday() == 5:
        return True
    else:
        return False


def is_holiday():
    format_current_date = datetime.today().strftime('%Y-%m-%d')
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ' \
                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31'

    req = request.Request(holiday_api_url + format_current_date)
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', user_agent)
    resp = request.urlopen(req).read()

    today_type = json.loads(resp)['type']['type']

    if (today_type == 1) | (today_type == 2):
        return True
    else:
        return False


# Listen button event
@app.action({"action_id": "cr_yes"})
async def click_yes(ack, say, logger, body):
    global topic_count
    logger.info(f"request body: {body}")
    await ack()
    if topic_count >= 2:
        await say(f"<@{body['user']['id']}> {reply_template[2]}")
    else:
        await say(f"<@{body['user']['id']}> {reply_template[topic_count]}")

    topic_count += 1


# Send CR message to channel
async def send_event():
    global topic_count
    global watch_time

    await app.client.chat_postMessage(
        channel=channel_id,
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Hey guys! Anything to say in today's CR? please please tell me~ 😇"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Yes I have"},
                    "action_id": "cr_yes"
                }
            }
        ],
        text="Hey guys! Anything to say in today's CR? please please tell me~ 😇"
    )
    await asyncio.sleep(watch_time)
    if topic_count:
        await app.client.chat_postMessage(
            channel=channel_id,
            text=f"<!here> We have {topic_count} topics today, let's CR tonight! 🚀"
        )
    else:
        await app.client.chat_postMessage(
            channel=channel_id,
            text=f"Look like don't have topic today, bye~ 🥰"
        )

    sys.exit(0)


async def main():
    asyncio.ensure_future(send_event())
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()

if __name__ == "__main__":

    if is_holiday():
        print("Oh, is holiday, bye~")
        sys.exit(0)

    if is_friday():
        app.client.chat_postMessage(
            channel=channel_id,
            text=f"Happy Friday folks, have a nice weekend. 🫣"
        )
        sys.exit(0)

    import asyncio
    asyncio.run(main())
