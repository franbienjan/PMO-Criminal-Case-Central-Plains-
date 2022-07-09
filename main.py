import discord
import os
import json
import pytz
from replit import db
from datetime import datetime
#from keep_alive import keep_alive

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
witnessFile = json.load(open('witness.json'))
tz_PH = pytz.timezone('Asia/Manila')

###############################################
##     PMO Criminal Case (Central Plains)    ##
##            Friday Bot Codes               ##
###############################################

discordId = {
  "GUILD" : 795152305405689857,
  "ROLE_ADMIN" : 795155371533664266,
  "ROLE_AGENTS" : 897716177994940436,
  "ROLE_FRIENDS" : 816569905502748693,
  "CHANNEL_CS" : 897723726232191016,
  "CHANNEL_MAIN" : 897723172282060801,
  "CHANNEL_LKW" : 918541354274005014,
  "CHANNEL_ME" : 897724780017496085,
  "CHANNEL_LOGS" : 995226634305146880
};

# List of rooms
rooms = [
  "LKW",
  "CS",
  "ME"
]

# Function to check whether user has permissions to execute command
async def checkPermissions(channel, user, isAdmin):
  isAllowed = False

  for role in user.roles:
    roleId = role.id
    if (discordId['ROLE_FRIENDS'] == roleId) or (isAdmin == False and discordId['ROLE_AGENTS'] == roleId) or (discordId['ROLE_ADMIN'] == roleId):
      isAllowed = True
      break
    
  if isAllowed == False:
    await channel.send(user.display_name + ", you are not allowed to do that action.")

  return isAllowed

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content
  user = message.author
  channel = message.channel
  userId = str(user.id)
  userName = user.display_name

  # TEST COMMAND ONLY
  if msg.startswith("$hellofriday"):
    await message.channel.send("Hello!")

  #**************************************
  #*              ROOMS                 *
  #**************************************
  if msg.startswith("?select "):

    # Block non-players from choosing.
    isAllowed = await checkPermissions(channel, user, False)
    if isAllowed == False:
      return

    if db[userId + "-room"] in rooms:
      outputEmoji = '🚫'
      await message.add_reaction(outputEmoji)
      return
    
    room = msg.split("?select ", 1)[1]
    outputMsg = "ok"
    outputEmoji = '✅'

    if user.voice == None:
      outputMsg = userName + ", you need to be in PMOBI HQ Voice Channel before making that decision."
      await message.channel.send(outputMsg)
      outputEmoji = '❌'
    elif room not in rooms:
      outputMsg = userName + ", that is not a valid room."
      await message.channel.send(outputMsg)
      outputEmoji = '❌'
    else:
      db[userId + "-room"] = room
      roomChannel = client.get_channel(discordId["CHANNEL_" + room])
      await user.move_to(roomChannel)

    await message.add_reaction(outputEmoji) 
    return

  #**************************************
  #*           INTERVIEW                *
  #**************************************
  if msg.startswith("?interview "):
    
    # Block non-players from choosing.
    isAllowed = await checkPermissions(channel, user, False)
    if isAllowed == False:
      return
      
    names = msg.split("?interview ", 1)[1]
    names = names.split(" ")
    caseNumber = db["caseNumber"]

    if len(names) != 2:
      await message.add_reaction('❌') 
      return

    for name in names:
      if name not in db["suspects"]:
        await message.add_reaction('❌')
        return

    print(db[userId + "-persons"])
    if len(db[userId + "-persons"]) > 0:
      await message.add_reaction('🚫')
      return

    witness0 = witnessFile[names[0]]
    witness1 = witnessFile[names[1]]
    db[userId + "-persons"] = names

    embedVar = discord.Embed(title="🔎 **INTERROGATION - CASE #" + db["caseNumber"] + "** 🔍",description="",color=0x0F0000)
    embedVar.add_field(name="Notes by", value=userName + "\n" + str(datetime.now(tz_PH).strftime("%d/%m/%Y %H:%M:%S")), inline=False)
    embedVar.add_field(name=names[0], value=witness0[caseNumber], inline=False)
    embedVar.add_field(name=names[1], value=witness1[caseNumber], inline=False)

    await user.send(embed=embedVar)
    await message.add_reaction('✅')

    #Post in logs channel as well
    logsChannel = client.get_channel(discordId["CHANNEL_LOGS"])
    await logsChannel.send(embed=embedVar)
    
    return

  #**************************************
  #*               RECAP                *
  #**************************************
  if msg.startswith("$recap "):

    # Block non-admin from choosing.
    isAllowed = await checkPermissions(channel, user, True)
    if isAllowed == False:
      return
    
    cmd = msg.split("$recap ", 1)[1]
    outputMsg = ""

    agentList = client.get_guild(discordId["GUILD"]).get_role(discordId["ROLE_AGENTS"]).members
    adminList = client.get_guild(discordId["GUILD"]).get_role(discordId["ROLE_ADMIN"]).members
    friendList = client.get_guild(discordId["GUILD"]).get_role(discordId["ROLE_FRIENDS"]).members
    everyone = agentList + adminList + friendList
    
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
      
    elif cmd == "rooms":
      listRooms = {
        "CS" : [],
        "LKW" : [],
        "ME" : [],
        "NONE" : []
      }

      # Sort agents in rooms
      for agent in everyone:
        room = db[str(agent.id) + "-room"]
        if room not in rooms:
          room = "NONE"
        listRoomSpecific = listRooms[room]
        listRoomSpecific.append(agent.display_name)

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
      
      for agent in everyone:
        personList = db[str(agent.id) + "-persons"]
        if len(personList) > 0:
          valueMsg = ", ".join(personList)
        else:
          valueMsg = "None."
        embedVar.add_field(name=agent.display_name, value=valueMsg, inline=False)

      await message.channel.send(embed=embedVar)
      return

  #**************************************
  #*    CLEARING AND INITIALIZATION     *
  #**************************************
        
  if msg.startswith("$clear "):
    
    # Block non-admin from choosing.
    isAllowed = await checkPermissions(channel, user, True)
    if isAllowed == False:
      return
    
    cmd = msg.split("$clear ", 1)[1]
    outputMsg = ""
    agentList = client.get_guild(discordId["GUILD"]).get_role(discordId["ROLE_AGENTS"]).members
    admin = client.get_guild(discordId["GUILD"]).get_role(discordId["ROLE_ADMIN"]).members
    friends = client.get_guild(discordId["GUILD"]).get_role(discordId["ROLE_FRIENDS"]).members
    agents = agentList + admin + friends
    print(agents)

    if cmd == "rooms":
      for agent in agents:
        db[str(agent.id) + "-room"] = ""
      await message.channel.send("Rooms have been cleared.")

    if cmd == "persons":
      for agent in agents:
        db[str(agent.id) + "-persons"] = []
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
    # Block non-admin from choosing.
    isAllowed = await checkPermissions(channel, user, True)
    if isAllowed == False:
      return

    # Main GC Voice Channel
    mainChannel = client.get_channel(discordId["CHANNEL_MAIN"])

    everyone = []
    for role in ["ROLE_AGENTS", "ROLE_FRIENDS", "ROLE_ADMIN"]:
      roleMembers = client.get_guild(discordId["GUILD"]).get_role(discordId[role]).members
      for roleMember in roleMembers:
        if roleMember.voice == None:
          continue
        await roleMember.move_to(mainChannel)

    await message.channel.send("All agents are now back to the HQ.")
    return
  
  #**************************************
  #*           PERSON SETTING           *
  #**************************************
  if msg.startswith("$set-params "):
    # Block non-admin from choosing.
    isAllowed = await checkPermissions(channel, user, True)
    if isAllowed == False:
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