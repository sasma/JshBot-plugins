import asyncio
import time
import re

from jshbot import data
from jshbot.commands import Command, SubCommands, Shortcuts
from jshbot.exceptions import BotException

__version__ = '0.1.0'
EXCEPTION = 'Selfbot assist plugin'
uses_configuration = False

translation_tables = []


def get_commands():
    new_commands = []
    new_commands.append(Command(
        'selfbot', SubCommands(
            ('language ?channel: &', 'language (channel <channel ID>) '
             '(message ID)', 'Searches for a message where a language '
             'was used. Provide a channel ID if you want to be discreet. '
             'Inspects the last 500 messages.'),
            ('utc', 'utc', 'Gets date and time information for UTC.'),
            ('clean ?regex: ^', 'clean (regex <pattern>) <number>', 'Cleans '
             'the given number of messages that optionally match the given '
             'regex pattern.')),
        shortcuts=Shortcuts(
            ('sb', '{}', '^', '<arguments>', '<arguments>')),
        description='Selfbot mode helper commands.', elevated_level=3,
        group='selfbot'))

    new_commands.append(Command(
        'texttools', SubCommands(
            ('tiny ^', 'tiny <text>', 'Makes text tiny.'),
            ('fancy ^', 'fancy <text>', 'Makes text fancy.'),
            ('invert ^', 'invert <text>', 'Flips text.'),
            ('aesthetic ^', 'aesthetic <text>', 'Vaporwave.'),
            ('cursive ^', 'cursive <text>', 'The other fancy text.'),
            ('zalgo ^', 'zalgo <text>', 'REALLY annoy people.')),
        shortcuts=Shortcuts(
            ('tt', '{}', '^', '<arguments>', '<arguments>'),
            ('tiny', 'tiny {}', '^', 'tiny <text>', '<text>'),
            ('fancy', 'fancy {}', '^', 'fancy <text>', '<text>'),
            ('invert', 'invert {}', '^', 'invert <text>', '<text>'),
            ('aesthetic', 'aesthetic {}', '^', 'aesthetic <text>', '<text>'),
            ('cursive', 'cursive {}', '^', 'cursive <text>', '<text>')),
        description='Annoy People: the Plugin', elevated_level=3,
        group='selfbot'))

    return new_commands


async def get_response(
        bot, message, base, blueprint_index, options, arguments,
        keywords, cleaned_content):
    response, tts, message_type, extra = ('', False, 0, None)

    if base == 'selfbot':

        if blueprint_index == 0:  # Language check
            pattern = re.compile('```\w+(?!.*```)')
            if 'channel' in options:  # Search in a specific channel
                channel = data.get_channel(bot, options['channel'])
            else:
                channel = message.channel
            if arguments[0]:  # Search for a specific message
                sieve = lambda x: x.id == arguments[0]
            else:
                sieve = lambda x: bool(pattern.search(x.content))
            matched_messages = await filter_messages(
                bot, channel, cutoff=1, sieve=sieve)
            if matched_messages:
                match_result = pattern.search(matched_messages[0].content)
                if match_result is None:
                    raise BotException(EXCEPTION, "No language found.")
                language = match_result.group(0)[3:]
                response = 'The language for ID {0.id} is `{1}`.'.format(
                    matched_messages[0], language)
            else:
                raise BotException(EXCEPTION, "No valid message found.")

        elif blueprint_index == 1:  # UTC time stuff
            response = '`UTC: {0} ({1})`\n`Local: {2}`'.format(
                time.strftime('%c', time.gmtime(time.time())),
                time.time(), time.strftime('%c'))

        elif blueprint_index == 2:  # Clean messages
            if 'regex' in options:
                raise BotException(
                    EXCEPTION,
                    "Hah, you think I know REGEX? Think again, bub.")
            try:
                cutoff = int(arguments[0])
                assert cutoff > 0
            except:
                raise BotException(EXCEPTION, "Invalid number.")
            matched_messages = await filter_messages(
                bot, message.channel, cutoff=cutoff + 1,
                sieve=lambda x: x.author == message.author)
            for pending_message in matched_messages:
                await bot.delete_message(pending_message)
                await asyncio.sleep(1)
            message_type, extra = 2, 2
            response = 'Deleted {} message(s)'.format(len(matched_messages))

    elif base == 'texttools':
        message_type = 4  # Replace
        table = translation_tables[blueprint_index]
        response = cleaned_content.split(' ', 1)[1].translate(table)

    return (response, tts, message_type, extra)


async def filter_messages(
        bot, channel, limit=500, before=None, after=None,
        cutoff=0, sieve=None):
    """Returns a list of messages that matches the sieve if given.

    Keyword arguments:
    limit -- limit of the number of message to iterate through.
    before -- passed to logs_from.
    after -- also passed to logs_from.
    cutoff -- stops iteration if the number defined by cutoff is found.
        If the value is 0, this will not cutoff and iterate all the way.
    sieve -- function to be used like a filter. Will be passed a message.
    """
    matched_messages = []
    found = 0
    async for message in bot.logs_from(
            channel, limit=limit, before=before, after=after):
        if sieve:
            if sieve(message):
                matched_messages.append(message)
                found += 1
                if cutoff != 0 and found >= cutoff:
                    break
        else:
            matched_messages.append(message)
    return matched_messages


async def on_ready(bot):
    """Set translation tables."""
    global translation_tables

    if bot.fresh_boot:
        base_table = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                      "1234567890!@#$%^&*()_+-=`~[]\\;',./{}|:\"<>? ")
        changed_tables = [
            "ᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏᶫᵐᶰᵒᵖᑫʳˢᵗᵘᵛʷˣʸᶻᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᑫᴿˢᵀᵁⱽᵂˣʸᶻ"
            "¹²³⁴⁵⁶⁷⁸⁹⁰﹗@#﹩﹪^﹠﹡⁽⁾_+⁻⁼`~[]\\﹔',⋅/{}|﹕\"<>﹖ ",
            "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ"
            "1234567890!@#$%^&*()_+-=`~[]\\;',./{}|:\"<>? ",
            "ɐqɔpǝɟƃɥıɾʞןɯuodbɹsʇnʌʍxʎzɐqɔpǝɟƃɥıɾʞןɯuodbɹsʇn𐌡ʍxʎz"
            "1234567890¡@#$%^⅋*()_+-=`~[]\\;,‘./{}|:\"<>¿ ",
            "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"
            "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
            "１２３４５６７８９０！＠＃＄％^＆＊（）_＋－＝`~[]\\"
            "；＇，．／{}|：\"<>？　",
            "𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝒜𝐵𝒞𝒟𝐸𝐹𝒢𝐻𝐼𝒥𝒦𝐿𝑀𝒩𝒪𝒫𝒬𝑅𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵"
            "𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫𝟢!@#$%^&*()_+-=`~[]\\;',./{}|:\"<>? "]
        translation_tables = [  # WHY
            str.maketrans(base_table, changed_table)
            for changed_table in changed_tables
        ]