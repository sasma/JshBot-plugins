import asyncio
import sys
import time

from jshbot.commands import Command, SubCommands
from jshbot.exceptions import BotException

__version__ = '0.1.1'
EXCEPTION = 'Diagnostics'

recent_usages = 0
recent_messages = 0
looping = False


def get_size(data):
    """Recursively gets the size of the data.

    Only recurses for lists, tuples, and dicts
    """
    size = 0
    if isinstance(data, (list, tuple)):
        for item in data:
            size += get_size(item)
    elif isinstance(data, dict):
        for item in data.items():
            size += sys.getsizeof(item[0])
            size += get_size(item[1])
    else:
        size += sys.getsizeof(data)
    return size


def get_commands():
    commands = []
    commands.append(Command(
        'diagnose', SubCommands(('', '', ''), ('stop', '', '')),
        elevated_level=3, hidden=True, group='testing'))
    return commands


async def get_response(
        bot, message, base, blueprint_index, options, arguments,
        keywords, cleaned_content):
    response, tts, message_type, extra = ('', False, 0, None)
    global looping

    if blueprint_index == 0:
        if looping:
            raise BotException(EXCEPTION, "Diagnostics in progress.")
        response = "Setting up diagnostics..."
        message_type = 3
        looping = True
    else:
        if not looping:
            raise BotException(EXCEPTION, "No diagnostics running.")
        response = "Stopping diagnostics."
        looping = False

    return (response, tts, message_type, extra)


async def handle_active_message(bot, message_reference, extra):
    global looping, recent_usages, recent_messages
    await asyncio.sleep(1)
    while looping:
        total_servers = len(bot.servers)
        voice_connections = len(bot.voice_clients)
        data_size = get_size(bot.data)
        running_tasks = 0
        for t in asyncio.Task.all_tasks():
            if not t.done():
                running_tasks += 1
        update = (
            "```\nTimestamp: {0}\n"
            "Total servers: {1}\n"
            "Voice connections: {2}\n"
            "Recent usages: {3}\n"
            "Recent messages: {6}\n"
            "Data size: {4} bytes\n"
            "Pending tasks: {5}```").format(
                time.time(), total_servers, voice_connections,
                recent_usages, data_size, running_tasks, recent_messages)
        recent_usages = 0
        recent_messages = 0
        await bot.edit_message(message_reference, update)
        await asyncio.sleep(60)


async def bot_on_command(bot, command, parsed_input, author):
    if looping:
        global recent_usages
        recent_usages += 1


async def on_message(bot, message):
    if looping:
        global recent_messages
        recent_messages += 1
