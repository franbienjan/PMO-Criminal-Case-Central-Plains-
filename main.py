import discord
import os
import json
from replit import db
#from keep_alive import keep_alive

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
witnessFile = json.load(open('witness.json'))

###############################################
##     PMO Criminal Case (Central Plains)    ##
##            Friday Bot Codes               ##
###############################################

# List of Players
players = [
  "JANSEN",
  "AJ",
  "CURT",
  "JHON",
  "DIRK",
  "BIMBY",
  "DEXTER",
  "JM",
  "CARLY",
  "CY",
  "JACOB",
  "VHON",
  "Dr. Tricia Robredo",
  "Onee Rose Gaida"
];

discordId = {
  "GUILD" : 795152305405689857,
  "ROLE_AGENTS" : 897716177994940436,
  "ROLE_FRIENDS" : 816569905502748693,
  "CHANNEL_CS" : 897723726232191016,
  "CHANNEL_MAIN" : 897723172282060801,
  "CHANNEL_LKW" : 918541354274005014,
  "CHANNEL_ME" : 897724780017496085
};

#dextermonterey
#Janlapatha
#dirkdaryl
#Carlyvia
#vhooon
#Curt
#jakepicar
#relatemenot
#johnxpao
#JansenKang
#JMHerald
#Ajjustin

hosts = [
  "franbienjan",
  "Ellis",
  "jannabean10"
];

# List of rooms
rooms = [
  "LKW",
  "CS",
  "ME"
]

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content
  user = message.author
  author = message.author.display_name
  username = message.author.name

  # TEST COMMAND ONLY
  if msg.startswith("$hellofriday"):
    await message.channel.send("Hello!")

  #*************************
  # $select room
  #*************************
  if msg.startswith("$select "):

    # Block non-players from choosing.
    if author not in players:
      await message.channel.send(author + ", you are not allowed to do that action.")
      return

    if db[author + "-room"] in rooms:
      outputEmoji = '🚫'
      await message.add_reaction(outputEmoji)
      return
    
    room = msg.split("$select ", 1)[1]
    outputMsg = "ok"
    outputEmoji = '\U0001F44D'

    if message.author.voice == None:
      outputMsg = author + ", you need to be in PMOBI HQ Voice Channel before making that decision."
      await message.channel.send(outputMsg)
      outputEmoji = '❌'
    elif room not in rooms:
      outputMsg = author + ", that is not a valid room."
      await message.channel.send(outputMsg)
      outputEmoji = '❌'
    else:
      db[author + "-room"] = room
      roomChannel = client.get_channel(discordId["CHANNEL_" + room])
      await message.author.move_to(roomChannel)

    await message.add_reaction(outputEmoji) 

    return

  #**************************************
  #*           INTERVIEW                *
  #*
  #**************************************
  if msg.startswith("$interview "):
    
    # Block non-players from choosing.
    if author not in players:
      await message.channel.send(author + ", you are not allowed to do that action.")
      return
      
    names = msg.split("$interview ", 1)[1]
    names = names.split(" ")
    caseNumber = db["caseNumber"]

    if len(names) != 2:
      await message.add_reaction('❌') 
      return

    for name in names:
      if name not in db["suspects"]:
        await message.add_reaction('❌')
        return

    if len(db[author + "-persons"]) > 0:
      await message.add_reaction('🚫')
      return

    witness0 = witnessFile[names[0]]
    witness1 = witnessFile[names[1]]
    db[author + "-persons"] = names

    embedVar = discord.Embed(title="🔎 **INTERROGATION** 🔍",description="",color=0x0F0000)
    embedVar.add_field(name=names[0], value=witness0[caseNumber], inline=False)
    embedVar.add_field(name=names[1], value=witness1[caseNumber], inline=False)

    await message.author.send(embed=embedVar)
    await message.add_reaction('\U0001F44D')  
    return

  #**************************************
  #*               RECAP                *
  #*
  #**************************************
  if msg.startswith("$recap "):

    # Block non-admin from executing this command.
    if username not in hosts:
      await message.channel.send(author + ", you are not allowed to do that action.")
      return
    
    cmd = msg.split("$recap ", 1)[1]
    outputMsg = ""
    print(cmd)

    # Command for listing all players currently in a room.
    if cmd == "params":
      embedVar = discord.Embed(title="🗡 **ROUND DETAILS** 🗡",description="",color=0x0F0000)

      caseNumber = db["caseNumber"]
      if caseNumber == 0:
        embedVar.add_field(name="Note", value="Please set parameters for this round.", inline=True)
      else:
        embedVar.add_field(name="Case #", value=db["caseNumber"], inline=True)
        suspectList = "\n".join(db["suspects"])
        embedVar.add_field(name="Suspects", value=suspectList, inline=False)

      await message.channel.send(embed=embedVar)
      return
      
    elif cmd == "room":
      listRooms = {
        "CS" : [],
        "LKW" : [],
        "ME" : [],
        "NONE" : []
      }

      # Sort players in rooms
      for player in players:
        room = db[player + "-room"]
        if room not in rooms:
          room = "NONE"
        listRoomSpecific = listRooms[room]
        listRoomSpecific.append(player)
        #listRooms[room] = listRoomSpecific

      # Print rooms:
      embedVar = discord.Embed(title=":homes: **ROOM LIST** :homes:",description="",color=0x0F0000)

      roomWithNone = rooms.copy()
      roomWithNone.append("NONE")
      for room in roomWithNone:
        entryList = ""
        if room == "CS":
          roomName = "Crime Scene"
        elif room == "LKW":
          roomName = "Last Known Whereabouts"
        elif room == "ME":
          roomName = "Medical Examiner's Office"
        else:
          roomName = "Not in any rooms"

        specList = listRooms[room]
        if len(specList) == 0:
          entryList = "None."
        else:
          entryList = "\n".join(listRooms[room])

        embedVar.add_field(name=roomName, value=entryList, inline=False)

      await message.channel.send(embed=embedVar)
      return

    elif cmd == "persons":
      embedVar = discord.Embed(title="🕵️ **INTERVIEW LIST** 🕵️",description="",color=0x0F0000)
      for player in players:
        personList = db[player + "-persons"]
        if len(personList) > 0:
          valueMsg = ", ".join(personList)
        else:
          valueMsg = "None."
        embedVar.add_field(name=player, value=valueMsg, inline=False)

      await message.channel.send(embed=embedVar)
      return

  #**************************************
  #*    CLEARING AND INITIALIZATION     *
  #**************************************
        
  if msg.startswith("$clear "):
    
    # Block non-admin from executing this command.
    if username not in hosts:
      await message.channel.send(author + ", you are not allowed to do that action.")
      return
    
    cmd = msg.split("$clear ", 1)[1]
    outputMsg = ""

    if cmd == "rooms":
      for player in players:
        db[player + "-room"] = ""
      await message.channel.send("Rooms have been cleared.")

    if cmd == "persons":
      for player in players:
        db[player + "-persons"] = []
      await message.channel.send("Interrogations have been cleared.")

    if cmd == "params":
      db["caseNumber"] = 0
      db["suspects"] = []
      await message.channel.send("Round parameters have been cleared.")

    return

  #**************************************
  #*          BACK TO MAIN GC           *
  #**************************************
  if msg.startswith("$call-to-main"):
    # Block non-admin from executing this command.
    if  not in hosts:
      await message.channel.send(author + ", you are not allowed to do that action.")
      return

    # Main GC Voice Channel
    mainChannel = client.get_channel(discordId["CHANNEL_MAIN"])
    agents = client.get_guild(discordId["GUILD"]).get_role(discordId["ROLE_AGENTS"]).members

    for agent in agents:
      await agent.move_to(mainChannel)

    await message.channel.send("All agents are now back to the HQ.")
    return
  
  #**************************************
  #*           PERSON SETTING           *
  #**************************************
  if msg.startswith("$set-params "):
    # Block non-admin from executing this command.
    if username not in hosts:
      await message.channel.send(author + ", you are not allowed to do that action.")
      return
      
    inputValues = msg.split("$set-params ", 1)[1]
    inputValues = inputValues.split(" ", 1)

    #[0] = Case Number 
    caseNumber = inputValues[0]
    db["caseNumber"] = caseNumber
    #[1] = Suspect 1... and so on
    suspectList = inputValues[1].split(" ")
    db["suspects"] = suspectList
    
    await message.channel.send("Parameters have been set.")
    return

#keep_alive()
client.run(os.getenv("TOKEN"))