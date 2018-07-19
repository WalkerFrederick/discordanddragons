import discord, random, firebase_admin
from discord.ext.commands import Bot
from discord.ext import commands
from firebase_admin import credentials
from firebase_admin import firestore

Client = discord.Client()  # initialise Client
client = commands.Bot(command_prefix="//")  # initialise client bot

cred = credentials.Certificate('##################################')
firebase_admin.initialize_app(cred)
db = firestore.client()

users_ref = db.collection(u'users')
docs = users_ref.get()


@client.event
async def on_ready():
    print("d&d running.")  # confirms if the bot is running


class User(object):
    def __init__(self, userID, level, exp, role, armor, weapon, spell, hp):
        self.userID = userID
        self.level = level
        self.exp = exp
        self.role = role
        self.armor = armor
        self.weapon = weapon
        self.spell = spell
        self.hp = hp

    @staticmethod
    def from_dict(source):
        user = User(source[u'userID'], source[u'level'], source[u'exp'], source[u'role'], source[u'armor'], source[u'weapon'], source[u'spell'], source[u'hp'])
        return user

    def to_dict(self):
        dest = {
            u'userID': self.userID,
            u'level': self.level,
            u'exp': self.exp,
            u'role': self.role,
            u'armor': self.armor,
            u'weapon': self.weapon,
            u'spell': self.spell,
            u'hp': self.hp,

        }
        return dest

    def __repr__(self):
        return u'User(userID={}, level={}, exp={},)'.format(
            self.userID, self.level, self.exp, )


@client.event
async def on_message(message):
    charMessage = message.content;
    msgChannel = message.channel
    msgAuthor = message.author.id
    expToLevel = [1, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600, 100000]

    async def levelUp(userId):
        doc = users_ref.document(userID).get()
        userDict = doc.to_dict()
        userDict['level'] = userDict['level'] + 1
        users_ref.document(userId).set(userDict)
        await client.send_message(msgChannel, message.author + ' Leveled Up!!!')

    print(msgAuthor)
    # '//' is unibott's command prefix,
    # this if statement checks if '//' is present the begining of a msg.
    # if '//' is present and a specified command isnt present then an error msg will let the user know.
    if charMessage[0] == '/' and charMessage[1] == '/':
        commandArray = charMessage.replace('/', '').split();
        usrInput = commandArray[0]
        # best practice for a command that takes args,
        # in this case the command '//roll' also needs the max roll value.
        if commandArray[0] == 'ping':
            await client.send_message(msgChannel, 'pong')
        if commandArray[0] == 'level' and commandArray[1] == 'up':
            doc = users_ref.document(msgAuthor).get()
            userDict = doc.to_dict()
            neededExp = expToLevel[userDict['level']]
            if userDict['exp'] >= neededExp:
                userDict['level'] = userDict['level'] + 1
                level = userDict['level']
                newRole = discord.utils.get(message.server.roles, name='level ' + str(level))
                print(userDict['level'])
                oldRole = discord.utils.get(message.server.roles, name='level ' + str(userDict['level'] - 1))
                await client.replace_roles(message.author, newRole)
                users_ref.document(msgAuthor).set(userDict)
                await client.send_message(msgChannel, str(message.author) + ' Leveled Up!!!')

            else:
                expLeft = neededExp - userDict['exp']
                await client.send_message(msgChannel,
                                          str(message.author) + ' still needs ' + str(expLeft) + 'exp to level up')


        elif commandArray[0] == 'stats':
            doc = users_ref.document(msgAuthor).get()
            userDict = doc.to_dict()
            await client.send_message(msgChannel, '```' + 'level: ' + str(userDict['level']) +
                                      '\n' + 'exp: ' + str(userDict['exp']) +
                                      '\n' + 'class: ' + str(userDict['role']) +
                                      '\n' + 'armor-set: ' + str(userDict['armor']) +
                                      '\n' + 'weapon: ' + str(userDict['weapon']) +
                                      '\n' + 'spell-set: ' + str(userDict['spell']) +
                                      '\n' + 'hp: ' + userDict['hp'] + '```',
                                      )
        # ADMIN ONLY COMMANDS -----------------------------------------------------------------------------------------
        elif commandArray[0] == 'add' and discord.utils.get(message.server.roles, name='admin') in message.author.roles:
            print('admin')
            if commandArray[2] == 'exp':
                doc = users_ref.document(message.mentions[0].id).get()
                userDict = doc.to_dict()
                userDict['exp'] = userDict['exp'] + int(commandArray[1])
                users_ref.document(message.mentions[0].id).set(userDict)
                await client.send_message(msgChannel, 'added ' + commandArray[1] + 'exp')
        elif commandArray[0] == 'initDiscordAndDragons' and discord.utils.get(message.server.roles,name='admin') in message.author.roles:
            x = message.server.members
            y = message.server.roles
            colorsArray = [0x535353, 0xffffff, 0xff72c0, 0x9755b9, 0x516cf8, 0x15ffd6, 0x73ff99, 0xffd900, 0xff8800, 0xff0000, 0x640909]
            print(str(len(y)))
            for role in range(len(y),0, -1):
                try:
                    print(len(y))
                    await client.delete_role(message.server, y[role])
                except Exception:
                    print('error')
                    continue
            for i in range (0, 11):
                await client.create_role(message.server, name="level " + str(i), colour=discord.Colour(colorsArray[i]), hoist=True, position=i)
            levelZero = discord.utils.get(message.server.roles, name="level 0")
            for member in x:
                await client.add_roles(member, levelZero)
                users_ref.document(member.id).set(User(member.name, 0, 0, 'traveler', 'like some sandals, maybe', 'spoon', 'none', '1').to_dict())
            await client.create_role(message.server, name="admin")
            admin = discord.utils.get(message.server.roles, name="admin")
            await client.add_roles(message.author, admin)


# this is your unique client token! DO NOT SHARE!!!!!!!!
client.run("###########################")
