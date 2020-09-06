import requests
import websockets
import json
import random
from datetime import date, datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands


# =====================GLOBAL DATA=====================
client = commands.Bot(command_prefix='!')
channel_id =  # integer, from specific discord channel
service_id = ''  # DBG API service_id. do not add the 's:'
BotToken = ''  # From your discord appliance 'Bot' page.

websocketurl = 'wss://push.planetside2.com/streaming?environment=ps2&service-id=s:' + service_id

curr_target_id = "5428387121714939329"  # this variable might not actually be used.

sub_deaths_json = {"action": "subscribe", "eventNames": ["Death"], "service": "event"}  # this should stay constant
sub_deaths_json["characters"] = ["5428387121714939329"]  # this will change, and be updated automatically

clear_sub = {"action": "clearSubscribe", "all": "true","service": "event"}

target_list = {}  # list of everyone who opts-in
killboard = {}  # current leaderboard

queue_target_update = 0  # bool, set if we need to update subscriptions due to !choose_target

curr_target = 'splishsplash'

# =====================HELPER FUNCTIONS=====================
def get_player_id(player_name):
    req = requests.get('https://census.daybreakgames.com/s:'+service_id
                       + '/get/ps2:v2/character/?name.first_lower=' + player_name.lower())
    ident = req.json()
    return ident['character_list'][0]['character_id']


def get_player_name_by_id(id):
    req = requests.get('https://census.daybreakgames.com/s:'+service_id
                       + '/get/ps2:v2/character/?character_id=' + id)
    ident = req.json()
    return ident['character_list'][0]['name']['first_lower']


def check_valid_name(player):
    req = requests.get('https://census.daybreakgames.com/s:'+service_id
                       + '/get/ps2:v2/character/?name.first_lower=' + player)
    reqjson = req.json()
    if reqjson['returned'] == 1:
        return True
    else:
        return False

def clear_board():
    global killboard
    for i in list(killboard):
        del killboard[i]

async def declare_winner():
    global killboard
    try:
        MaxValue = max(killboard.values())
        winners_list = [key for key, value in killboard.items() if value == MaxValue]
        winners = ', '.join(winners_list)
        channel = client.get_channel(channel_id)
        await channel.send('Winner is: ' + winners + '! Congrats!!')
    except TypeError:
        channel = client.get_channel(channel_id)
        await channel.send('No winner.')
        pass
    except ValueError:
        channel = client.get_channel(channel_id)
        await channel.send('No winner.')
        pass
    except RuntimeError:
        channel = client.get_channel(channel_id)
        await channel.send('No winner.')
        pass
    clear_board()


async def update_subs(ws):
    global curr_target, curr_target_id, queue_target_update
    if queue_target_update == 1:
        queue_target_update = 0
        await declare_winner()
        await ws.send(json.dumps(clear_sub))
        try:
            curr_target = random.choice(list(target_list))
        except IndexError:
            channel = client.get_channel(channel_id)
            await channel.send('No Players! "!join playername" to join!')
        sub_deaths_json["characters"] = [get_player_id(curr_target)]
        curr_target_id = get_player_id(curr_target)
        channel = client.get_channel(channel_id)
        await channel.send('New target is: ' + curr_target + '! Happy hunting!')
        await ws.send(json.dumps(sub_deaths_json))


# =====================MAIN LOOP=====================
async def kill_tracker():
    global killboard
    async with websockets.connect(websocketurl) as websocket:  # init connection with DBG's websockets
        await websocket.send(json.dumps(sub_deaths_json))  # initial websockets sub for target's kill feed
        channel = client.get_channel(channel_id)
        await channel.send('Current target is: ' + curr_target + '! Get \'em boys!')
        while True:
            await update_subs(websocket)
            message = await websocket.recv()
            msg = json.loads(message)
            try:
                if msg['payload']['character_id'] == curr_target_id:
                    killer = get_player_name_by_id(msg['payload']['attacker_character_id'])
                    if killer in target_list:
                        killboard[killer] = killboard.get(killer, 0) + 1
            except KeyError:
                continue


# ======================DISCORD COMMANDS=====================
@client.event
async def on_ready():
    print("Beep Boop")
    await kill_tracker()

@client.command()
async def joinfun(ctx, player_name):
    if player_name.lower() not in target_list:
        if check_valid_name(player_name.lower()):
            target_list[player_name.lower()] = get_player_id(player_name)
            await ctx.send('Added. Good luck!')
        else:
            await ctx.send('Incorrect Name?')
    else:
        await ctx.send('Already joined!')


@client.command()
async def leavefun(ctx, player_name):
    if player_name.lower() in target_list:
        del target_list[player_name.lower()]
        await ctx.send('Removed')
    else:
        await ctx.send('Already left.')

# !choose_target can take up to 1 min to update the websockets subscription. be patient.
@client.command()
async def choose_target(ctx):
    global queue_target_update
    queue_target_update = 1
    await ctx.send('Acquiring new target!')

@client.command()
async def tk_leaderboard(ctx):
    global killboard
    leaders = ''
    try:
        maxV = max(killboard.values())
        winners_l = [key for key, value in killboard.items() if value == maxV]
        leaders = ', '.join(winners_l)
    except ValueError:
        pass
    if leaders:
        await ctx.send('Current leader is: ' + leaders + ' with ' + str(maxV) + ' kills.')
    else:
        await ctx.send('No leader')

@client.command()
async def tk_help(ctx):
    await ctx.send("""Available commands: \n '!joinfun <character name>' to join the killfest. \n '!leavefun <character name>' to be removed from the killfest.\n '!tk_leaderboard' to show the current leader. \n '!choose_target' to randomly choose a new target. \n '!tk_help' for this message.\n Leaderboard resets daily reset at 4pm EST""")

# ======================SCHEDULED TASKS=====================
sched = AsyncIOScheduler()
sched.start()


@sched.scheduled_job('interval', hours=24, start_date='2020-08-26 16:00:00')
async def period_job():
    global queue_target_update
    channel = client.get_channel(channel_id)
    await channel.send('Resetting TK Tournament')
    queue_target_update = 1

client.run(BotToken)
