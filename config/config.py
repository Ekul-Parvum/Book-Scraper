
# # -- -- --[  Constants:  ]-- -- --
# lengthOfBar = 30                        # The length of the loading bar
# outputFilePath = "~/WindowsSucks"       # The file path to the outputfiles
# outputFileName = "outPutFile"           # The name of the ouputfiles
# numOfRetries = 3                        # The number of times the program should try getting the soup of a page before giving up.
# # -- -- -- -- -- -- -- -- -- -- --
import json

def getConfigsFromJson():
    with open("./config/config.json", "r") as configFile:
        return json.load(configFile)