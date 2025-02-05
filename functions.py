import os
from config import *
from typing import Dict


defaultConfigs: Dict = {
                'lang'              : 'es',
                'dailyRange'        : (16, 64),
                'coinName'          : 'Coins',
                'coinSymbol'        : '$',
                'gamblingWinChance' : 50,
                'buyableRoles'      : {}
                }

def resetDefaultConfig(guildID=653492428002820096) -> None:
    data = defaultConfigs

    with open(f'data/servers/{guildID}/config.txt', 'w') as f:

        for entry in data:
            f.write(f"{entry}={data[entry]}\n")

def doesDataServerFolderExists():
    if os.path.isfile(f'data/servers'):
        return True
    else:
        return False

def createDataServersFolder():
    os.makedirs(f'data/servers')

def doesConfigFileExists(guildID=653492428002820096) -> bool:
    if os.path.isfile(f'data/servers/{guildID}/config.txt'):
        return True
    else:
        return False

def doesServerDataFolderExists(guildID=653492428002820096) -> bool:
    if os.path.isdir(f'data/servers/{guildID}'):
        return True
    else:
        return False

def createServerDataFolder(guildID) -> None:
    os.makedirs(f'data/servers/{guildID}')

def addMissingConfigs(guildID=653492428002820096) -> None:
    with open(f'data/servers/{guildID}/config.txt', 'a') as f:

        for entry in getMissingConfigs(guildID):
            f.write(f'{entry}={getMissingConfigs(guildID)[entry]}\n')

def getMissingConfigs(guildID=653492428002820096) -> Dict:

    missingConfigs: Dict = {}

    configs = getConfigInfo(guildID)

    for entry in defaultConfigs:
        if not entry in configs:
            missingConfigs[entry] = defaultConfigs[entry]

    return missingConfigs

def isConfigFileValid(guildID=653492428002820096) -> bool:
    configs = getConfigInfo(guildID)

    for entry in defaultConfigs:
        if not entry in configs:
            return False

    for entry in configs:
        if not entry in defaultConfigs:
            return False

    return True

def createConfigFile(guildID=653492428002820096) -> None:

    with open(f'data/servers/{guildID}/config.txt', 'w') as f:
        pass

def checkData(guildID=653492428002820096) -> None:

    if not doesServerDataFolderExists(guildID):
        createServerDataFolder(guildID)
        print(f"{guildID} doesn't have a data folder, creating one... ")

    if not doesConfigFileExists(guildID):
        createConfigFile(guildID)
        resetDefaultConfig(guildID)
        print(f"{guildID} doesn't have a config file, creating one... ")

    if not isConfigFileValid(guildID):
        addMissingConfigs()

if not doesDataServerFolderExists():
    createDataServersFolder()