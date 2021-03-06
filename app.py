# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import sys

import markovify
import os
import random
from argparse import ArgumentParser
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)

if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# generate markov models
base_dir = os.path.dirname(os.path.realpath(__file__))

# with open(os.path.join(base_dir, 'alex_jones.txt')) as f:
#     alex = f.read()
#
# with open(os.path.join(base_dir, 'jerkcity.txt')) as f:
#     jerkcity = f.read()
#
# model_alex = markovify.Text(alex)
# model_jerkcity = markovify.Text(jerkcity)
#
# model_qb = markovify.combine([model_alex, model_jerkcity], [1.5, 1])

with open(os.path.join(base_dir, 'lines.txt')) as f:
    model_qb = markovify.NewlineText(f, retain_original=False)


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


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text

    if text.startswith('Qb') or text.startswith('qb'):
        response = model_qb.make_sentence_with_start(beginning=text.split()[1], strict=False)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))

    else:

        if random.random() < 0.5:

            if event.source.user_id != 'nrl8938i' and not text.startswith('http'):

                with open('new_lines.txt', 'a') as f:
                    f.write('{}\n'.format(text.lower()))

        if random.random() < 0.05:
            response = model_qb.make_short_sentence(280)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))


if __name__ == "__main__":

    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
