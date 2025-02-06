
from datetime import date, timedelta
import os, datetime
import ast
from typing import Dict

defaultWallet: Dict = {
                'money'             : 0,
                'lastDailyClaim'    : '2000-01-01',
                'ruGamesWon'        : 0,
                }


# Getters
def getWalletInfo(caller) -> Dict:

    callerID = caller.id
    guildID = caller.guild.id

    config: Dict = {}

    with open(f'data/servers/{guildID}/economy/{callerID}.txt') as f:
        data = f.readlines()

        for entry in data:
            if not entry or entry == '' or entry == '\n':
                continue

            value = entry.split('=')[1].replace('\n', '')

            try:
                value = ast.literal_eval(value)
            except:
                pass

            config[entry.split('=')[0]] = value

        return config

def getUserMoney(caller):

    checks(caller, caller.guild)

    return getWalletInfo(caller)['money']

def getUserLastDailyClaim(caller):

    checks(caller, caller.guild)

    return getWalletInfo(caller)['lastDailyClaim']

def getUserRuWins(caller):

    checks(caller, caller.guild)

    return getWalletInfo(caller)['ruGamesWon']

# Setters
def setWalletData(new, caller):

    checks(caller, caller.guild)

    with open(f'data/servers/{caller.guild.id}/economy/{caller.id}.txt', 'w') as f:
        for entry in new:
            f.write(f'{entry}={new[entry]}\n')

def setUserMoney(new, caller):

    checks(caller, caller.guild)

    data = getWalletInfo(caller)
    data['money'] = new
    setWalletData(data, caller)

def setUserLastDailyClaim(new, caller):

    checks(caller, caller.guild)

    data = getWalletInfo(caller)
    data['lastDailyClaim'] = new
    setWalletData(data, caller)

def setUserRuWins(new, caller):

    checks(caller, caller.guild)

    data = getWalletInfo(caller)
    data['ruGamesWon'] = new
    setWalletData(data, caller)

def increaseUserMoney(value, caller):

    checks(caller, caller.guild)

    setUserMoney(getUserMoney(caller) + value, caller)

def decreaseUserMoney(value, caller):

    checks(caller, caller.guild)

    setUserMoney(getUserMoney(caller) - value, caller)

def doesGuildWalletFolderExist(guildID):
    if os.path.exists(f'data/servers/{guildID}/economy'):
        return True
    else:
        return False

def createGuildWalletFolder(guildID):
    os.makedirs(f'data/servers/{guildID}/economy')

def addMissingEntries(caller) -> None:
    with open(f'data/servers/{caller.guild.id}/economy/{caller.id}.txt', 'a') as f:

        for entry in getMissingEntries(caller):
            f.write(f'{entry}={getMissingEntries(caller)[entry]}\n')

def getMissingEntries(caller) -> Dict:

    missingConfigs: Dict = {}

    configs = getWalletInfo(caller)

    for entry in defaultWallet:
        if not entry in configs:
            missingConfigs[entry] = defaultWallet[entry]

    return missingConfigs

def isConfigFileValid(caller) -> bool:
    configs = getWalletInfo(caller)

    for entry in defaultWallet:
        if not entry in configs:
            return False

    for entry in configs:
        if not entry in defaultWallet:
            return False

    return True

def createUserWallet(caller):

    callerID = caller.id
    guild = caller.guild

    with open(f'data/servers/{guild.id}/economy/{callerID}.txt', 'x+') as file:
        print(f'Creating wallet file for {caller.name} (User ID: {callerID}) in {guild.name} (Server ID: {guild.id}).')

    setWalletData(defaultWallet, caller)

def doesUserWalletExists(caller):

    callerID = caller.id
    guild = caller.guild

    if not doesGuildWalletFolderExist(guild.id):
        return False

    if not os.path.isfile(f'data/servers/{guild.id}/economy/{callerID}.txt'):
        return False

    return True


def isWalletFileEmpty(caller):

    callerID = caller.id
    guildID = caller.guild.id

    if not doesGuildWalletFolderExist(guildID):
        createGuildWalletFolder(guildID)

    with open(f'data/servers/{guildID}/economy/{callerID}.txt', 'r') as file:
        lines = file.readlines()

        if lines:
            return True
        else:
            return False

def canClaimDaily(caller):

    callerID = caller.id
    guildID = caller.guild.id

    if not doesGuildWalletFolderExist(guildID):
        createGuildWalletFolder(guildID)

    if not doesUserWalletExists(caller):
        createUserWallet(caller)

    date = getUserLastDailyClaim(caller)

    if date != str(datetime.date.today()):
        return True
    else:
        return False

def checks(caller, guild):

    if not doesGuildWalletFolderExist(guild.id):
        createGuildWalletFolder(guild.id)

    if not doesUserWalletExists(caller):
        createUserWallet(caller)

    try:
        migrateWalletStructure(caller)
    except:
        pass

    if not isConfigFileValid(caller):
        addMissingEntries(caller)

def migrateWalletStructure(caller):

    callerID = caller.id
    guildID = caller.guild.id

    newFormat = defaultWallet.copy()

    with open(f'data/servers/{guildID}/economy/{callerID}.txt', 'r') as file:
        lines = file.readlines()

        money = int(lines[0].replace('\n', ''))
        lastDailyClaim = lines[1]

    newFormat['money'] = int(money)
    newFormat['lastDailyClaim'] = lastDailyClaim

    with open(f'data/servers/{guildID}/economy/{callerID}.txt', 'w') as f:
        for entry in newFormat:
            f.write(f'{entry}={newFormat[entry]}\n')