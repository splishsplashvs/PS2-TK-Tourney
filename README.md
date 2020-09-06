# PS2-TK-Tourney
This is a Discord bot written in Python 3. 

It exists for the sole purpose of providing Planetside 2 players some entertainment.  

It will track members of a discord community who opt-in to the teamkilling shenanigans, and announce a winner daily. 

To use it, you must make a discord appliance, and get a service_id to access DBG's API. 

Required fields that must be filled in are: 

channel_id: integer, from specific discord channel the bot will live. 

service_id: DBG API service_id. do not add the 's:'

BotToken: Long alphanumeric string from Discord. 

Optional changes (and shamelessly drawing attention to myself): 

client = commands.Bot(command_prefix='!'): you can change the '!' to any prefix your server uses for bot commands. 

curr_target_id = "5428387121714939329": I initialize this to my character_id, and it will change once people opt-in via !choose_target 

sub_deaths_json["characters"] = ["5428387121714939329"]: same as above. Used to initialize the WebSockets connection. 

curr_target = 'splishsplash': more shameless plugging my name. Can change if you want to initialize to someone else. Changes automatically. 

Once the bot is running, the following commands are available: 

 '!joinfun <character name>' to join the killfest. 
 
 '!leavefun <character name>' to be removed from the killfest.
 
 '!tk_leaderboard' to show the current leader. 
 
 '!choose_target' to randomly choose a new target. 
 
 '!tk_help' for this message.
 
 Leaderboard default is to reset daily at 4pm EST. 
 
 
 Please credit me if you do decide to use or modify my script, but, if you don't that's fine too. 
 
 Feel free to hit me up in game (SplishSplash), or on reddit (u/splishsplashvs) with any questions, feedback, or suggestions. 
