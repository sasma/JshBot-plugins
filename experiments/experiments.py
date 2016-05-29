# This is where the experiments live. Some continue to become features,
#   others may not have such a *future* ahead of them. Get it? Ha ha.

import discord
import asyncio
import random
import time
import logging

import datetime

from jshbot import data
from jshbot.exceptions import BotException

__version__ = '¯\_(ツ)_/¯'
EXCEPTION = 'Experiments'
uses_configuration = False

def get_commands():

    commands = {}
    shortcuts = {}
    manual = {}

    commands['test'] = (['&'],[()])
    commands['timemasheen'] = (['^'], [()])
    commands['play'] = (['^'], [()])

    return (commands, shortcuts, manual)

async def get_response(bot, message, parsed_command, direct):

    response = ''
    tts = False
    message_type = 0
    extra = None
    base, plan_index, options, arguments = parsed_command

    if base == 'test':
        if arguments: # that's pretty aesthetic mate
            text = arguments.replace(' ', '').lower()
            response = ' '.join([char for char in text])

        else: # asyncio testing
            long_future = bot.loop.run_in_executor(None, long_function)
            await long_future
            #long_function()
            response = "Finished sleeping"

    elif base == 'timemasheen': # carter's time masheen
        for delimiter in ('/', '.', '-'):
            if delimiter in arguments:
                break
        start_date = datetime.datetime.strptime(arguments,
                '%d{0}%m{0}%y'.format(delimiter))
        end_date = start_date + datetime.timedelta(days=1)
        await send_logs_as_file(bot, message.channel, start_date, end_date)
        message_type = 1

    elif base == 'play': # ytdl stuff
        response = "Going to test this later."

    return (response, tts, message_type, extra)

def long_function():
    time.sleep(10)

async def send_logs_as_file(bot, channel, start_date, end_date):
    '''
    Wrapper function for Carter's time machine.
    '''
    messages = []
    large_text = ''
    async for message in bot.logs_from(channel, limit=20000,
            before=end_date, after=start_date):
        messages.append(message)
    for message in reversed(messages):
        if message.edited_timestamp:
            edited = ' (edited {})'.format(message.edited_timestamp)
        else:
            edited = ''
        if message.attachments:
            urls = []
            for attachment in message.attachments:
                urls.append(attachment['url'])
            attached = ' (attached {})'.format(urls)
        else:
            attached = ''
        text = ("{0.author.id} ({0.author.name}) at {0.timestamp}{1}{2}: "
                "\n\t{0.content}\n").format(message, edited, attached)
        large_text += text

    await bot.send_text_as_file(channel, large_text, 'carter')

