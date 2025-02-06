from utils import customException
import ast
from typing import Dict

# Getters
def getConfigInfo(guildID=653492428002820096) -> Dict:

    config: Dict = {}

    with open(f'data/servers/{guildID}/config.txt') as f:
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

def getServerLang(guildID=653492428002820096):
    return getConfigInfo(guildID)['lang']

def getCoinName(guildID=653492428002820096):
    return getConfigInfo(guildID)['coinName']

def getCoinSymbol(guildID=653492428002820096):
    return getConfigInfo(guildID)['coinSymbol']

def getDailyRange(guildID=653492428002820096) -> tuple:
    return getConfigInfo(guildID)['dailyRange']

def getGamblingChance(guildID=653492428002820096):
    return getConfigInfo(guildID)['gamblingWinChance']

def getServerBuyableRoles(guildID=653492428002820096):
    return getConfigInfo(guildID)['buyableRoles']


# Setters
def setConfigFile(new, guildID=653492428002820096):
    with open(f'data/servers/{guildID}/config.txt', 'w') as f:
        for entry in new:
            f.write(f'{entry}={new[entry]}\n')

def setServerLang(new, guildID=653492428002820096):

    data = getConfigInfo(guildID)
    data['lang'] = new
    setConfigFile(data, guildID)

def setCoinName(new, guildID=653492428002820096):

    data = getConfigInfo(guildID)
    data['coinName'] = new
    setConfigFile(data, guildID)

def setCoinSymbol(new, guildID=653492428002820096):

    data = getConfigInfo(guildID)
    data['coinSymbol'] = new
    setConfigFile(data)

def setDailyRange(new, guildID=653492428002820096):

    data = getConfigInfo(guildID)
    data['dailyRange'] = new
    setConfigFile(data)

def setGamblingChance(new, guildID=653492428002820096):

    data = getConfigInfo(guildID)
    data['gamblingWinChance'] = new
    setConfigFile(data)

def setServerBuyableRoles(new, guildID=653492428002820096):

    data = getConfigInfo(guildID)
    data['buyableRoles'] = new
    setConfigFile(data)