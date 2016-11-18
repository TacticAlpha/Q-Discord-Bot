import discord
from discord.ext import commands
import json

bot = commands.Bot(command_prefix=['Q!', 'q!', '<@247866361064325121> '])
bot.remove_command('help')

token = ''
your_id = ''


def saveJson():
    with open('servers.json', 'w+') as f:
        json.dump(g_list, f)
        print('Updated json file')


def isAuthorized(ctx):

    server, author, message, authorized = ctx.message.server, ctx.message.author, ctx.message, False

    if author.id not in g_list[server.id]['banned']:

        for x in author.roles:

            x = str(x).lower()

            if x in g_list[server.id]['adminRoles']:
                authorized = True

        if author.id == '159023220140277760': authorized = True
        if server.default_channel.permissions_for(message.author).administrator: authorized = True

        print(authorized)

        return authorized


@bot.event
async def on_ready():

    print('Logged in as: {}\nID: {}\n--------------'.format(bot.user.name, bot.user.id))

    with open('servers.json', 'r+') as f:
        global g_list
        g_list = {}
        try:
            g_list = json.load(f)
        except json.decoder.JSONDecodeError:
            pass

    for server in bot.servers:
        print(server.name)
        if server.id not in g_list:
            g_list[server.id] = {}
            g_list[server.id]['queue']  = []
            g_list[server.id]['banned'] = []
            g_list[server.id]['adminRoles'] = ['boss', 'streamer', 'admin', 'moderator']
            saveJson()


@bot.command(pass_context=True)
async def hello():
    await bot.say('Hello world!')


@bot.command(pass_context=True)
async def help():
    await bot.whisper("""
Hello, I am Q, a bot written by Tactic Alpha with the discord.py library.

User Commands:
    `join <ign>` - Joins the queue, assuming you aren't banned or already in it.

Moderator Commands:
    `next <view/take> <number/all>` - Selects the next <number> users in the queue and keeps them in or takes them out.
    `clear` - Clears the queue.
    `controller <add/remove/list> <role> - Adds or removes the given <role> or lists all controller roles.""")


@bot.command(pass_context=True)
async def join(ctx, ign: str=None):
    server, author = ctx.message.server, ctx.message.author

    if author.id not in g_list[server.id]['banned']:

        alreadyInQueue = False

        for x in g_list[server.id]['queue']:

            if author.mention in x[0][0]:
                alreadyInQueue = True

        if alreadyInQueue is False:

            if ign is None:
                await bot.say(':exclamation: Please provide your in game name. `join <ign>`')
                return


            global g_list
            g_list[server.id]['queue'].append([[author.mention, author.display_name], ign])
            saveJson()
            await bot.say(':ok_hand:')

        else:
            await bot.say(":no_entry: You're already in the queue.")

    else:
        if author.id in g_list[server.id]['banned']:
            await bot.say(":no_entry: Banned.")


@bot.command(pass_context=True)
async def next(ctx, mode=None, num=None):

    server, author = ctx.message.server, ctx.message.author

    if num is not None:

        if isAuthorized(ctx):

            if num == 'all':
                num = len(g_list[server.id]['queue'])

            queued = len(g_list[server.id]['queue'])

            num = int(num)

            if num > queued:

                print('Aye')

                if queued == 0:
                    await bot.say(":exclamation: There's no one in the queue!")
                else:
                    await bot.say(':exclamation: `{}` is too many! There are only `{}` people in the queue!'.format(num, len(g_list[server.id]['queue'])))

            else:

                print('Nope')
                atFront = []
                string = ':white_check_mark: {} users have been selected'.format(num)

                if mode == 'take':
                    string += '.\n\n'

                if mode == 'view':
                    string += ' but not removed from the queue.\n\n'

                while num > 0:

                    num -= 1
                    if mode == 'take':
                        atFront.append(g_list[server.id]['queue'][0])
                    if mode == 'view':
                        atFront.append(g_list[server.id]['queue'][num])

                    global g_list
                    if mode == 'take':
                        g_list[server.id]['queue'].remove(g_list[server.id]['queue'][0])

                for y in atFront:

                    if mode == 'take':
                        string += '{}: {}\n'.format(y[0][0], y[1])
                    if mode == 'view':
                        string += '{}: {}\n'.format(y[0][1], y[1])

                saveJson()
                await bot.say(string)

    else:

        await bot.say(':exclamation: The correct usage is `next <view/take> <number/all>')


@bot.command(pass_context=True)
async def clear(ctx):

    server, author = ctx.message.server, ctx.message.author

    if isAuthorized(ctx):

        await bot.say('Are you sure you want to clear the queue? (Y/n)')

        msg = await bot.wait_for_message(author=author)

        if msg.content in ['Y', 'y', 'Yes', 'yes']:

            global g_list
            g_list[server.id]['queue'] = []
            await bot.say(':ok_hand:')

        else:

            await bot.say('Canceled')

    else:

        await bot.say(':no_entry: No access')


@bot.command(pass_context=True)
async def controller(ctx, mode=None, role: str=None):

    server, author, message, authorized = ctx.message.server, ctx.message.author, ctx.message, False

    if isAuthorized(ctx):

        print(role)

        if mode == 'add':

            if role is not None:

                print("Role '{}' is not None")
                print(role)

                if role.lower() not in g_list[server.id]['adminRoles']:

                    global g_list
                    g_list[server.id]['adminRoles'].append(role.lower())
                    await bot.say(':ok_hand:')

                    return

                else:

                    await bot.say(":exclamation: That's already a controller role.")

                    return

        if mode == 'remove':

            if role is not None:

                if role.lower() in g_list[server.id]['adminRoles']:

                    global g_list
                    g_list[server.id]['adminRoles'].remove(role)
                    await bot.say(':ok_hand:')

                    return

                else:

                    await bot.say(":exclamation: That's not a controller role.")

                    return

        if mode == 'list':

            string = ':white_check_mark: The controller roles are:\n\n'

            for x in g_list[server.id]['adminRoles']:

                string += '`{}` '.format(x.capitalize())

            await bot.say(string)

            return

    #    if mode is None or (role is None and mode != 'list'):  This isn't shouldn't be needed because the command should return before it gets to it if there's not an error.

        await bot.say(':exclamation: Correct usage is `controller <add/remove> <role>` or `controller list`')


# @bot.command(pass_context=True)
# async def ban(ctx, *targets):
#     Do stuff

@bot.command(pass_context=True)
async def debug(ctx, mode, *string):

    # This is a command only Tactic Alpha can run.

    if ctx.message.author.id == your_id:

        string = ' '.join(string)

        message = ctx.message
        author, server, channel = message.author, message.server, message.channel

        if mode == 'eval':
            string = eval(string)
            await bot.say('```{}```'.format(string))
        if mode == 'exec':
			# Possibly Broken
            string = exec(string)
			await bot.say('```{}```'.format(string))


bot.run(token)
