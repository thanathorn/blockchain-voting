import datetime


def printLog(program="", message="", messageType="info"):
    now = datetime.datetime.now()
    if messageType == "info":
        symbol = "*"
    else:
        symbol = "!"
    print("{} | [{}] {}: {}".format(now.strftime("%H:%M:%S"), symbol, program, message))