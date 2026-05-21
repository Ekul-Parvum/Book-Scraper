
# # -- -- --[  Constants:  ]-- -- --
# lengthOfBar = 30                        # The length of the loading bar
# outputFilePath = "~/WindowsSucks"       # The file path to the outputfiles
# outputFileName = "outPutFile"           # The name of the ouputfiles
# numOfRetries = 3                        # The number of times the program should try getting the soup of a page before giving up.
# # -- -- -- -- -- -- -- -- -- -- --
import json
import logging

def getConfigsFromJson():
    try:
        with open("./config/config.json", "r") as configFile:
            return json.load(configFile)
    except Exception as e:
        logging.error(f"Failed to access config: {e}")
        raise Exception("Failed to access config.")