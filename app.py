from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot import (
    LineBotApi, WebhookHandler
)
import os
import sys
from flask import Flask, request, abort

import urllib
import requests
import json

app = Flask(__name__)
# app.logger.info(sys.path)

slack_name = {
    "yamate-hachioji": "美濃 佑輝",
}


# 環境変数からchannel_secret・channel_access_tokenを取得
channel_secret = os.environ['LINE_CHANNEL_SECRET']
channel_access_token = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# line_bot_api = LineBotApi(
#     '')
# handler = WebhookHandler('')


@app.route("/")
def hello_world():
    return "hello world!"


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@app.route("/slack", methods=['POST'])
def slack():
    # get X-Line-Signature header value
    # signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    data = {}
    for x in body.split("&"):
        _x = x.split("=")
        data[_x[0]] = _x[1]
    data["link"] = "https://wbawakatetohoku.slack.com/app_redirect?channel=" + \
        data["channel_name"]
    app.logger.info(data.keys())

    flex = FlexSendMessage(
        alt_text=data["text"],
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Channel",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 2,
                                        "wrap": True
                                    },
                                    {
                                        "type": "text",
                                        "text": "#"+data["channel_name"],
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "User",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 2
                                    },
                                    {
                                        "type": "text",
                                        "text": slack_name.get(data["user_name"], data["user_name"]),
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5
                                    }
                                ]
                            },
                            {
                                "type": "spacer"
                            }
                        ]
                    },
                    {
                        "type": "separator"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "spacer"
                            },
                            {
                                "type": "text",
                                "text": urllib.parse.unquote(data["text"]),
                                "wrap": True
                            }
                        ]
                    }
                ]
            },
            "action": {
                "type": "uri",
                "label": "action",
                "uri": data["link"]
            }
        })

    # handle webhook body
    try:
        # handler.handle(body, signature)
        line_bot_api.push_message(
            "C3a45b0b1d853500b3c88f999dc3cc2d7",
            flex
        )
        pass
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=event.message.text))
    app.logger.info(type(event.source))
    d = json.loads(str(event.source))
    requests.post(
        "https://hooks.slack.com/services/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",
        json={
            "text": event.message.text,
            "username": "ID: "+d['userId']
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
