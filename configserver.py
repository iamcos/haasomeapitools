from __future__ import print_function, unicode_literals
from haasomeapi.HaasomeClient import HaasomeClient
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from datetime import datetime, date, time, timezone
from pathlib import Path


import configparser
import os
import re
import sys

import time


import init


def serverdata():
    print(
        "\n Rotator script collection of over 400 bot configurations that were designed across multiple market conditions and so apply to many at present. \n Setup LOCAL API in Haas Settings section by providing it with IP, Port and Secret. IP can be set to 127.0.0.1 if the server and Rotator are run on one machine. Port usually is 8095, so set that. Secret should not have any special characters, and can be as easy as 123 if run on same machine as rotator. \nMake sure that every field in Haas Local APi settings has data in after your first setup. If Secret is empty - type it again and hit save again, restart Haas. \n \n"
    )
    ip = input("Type Server IP address: ")
    port = input("Type server port number: ")
    secret = input("Type api key: ")

    ipport = "http://" + ip + ":" + port

    config = configparser.ConfigParser()
    config["SERVER DATA"] = {"server_address": ipport, "secret": secret}
    with open("config.ini", "w") as configfile:
        config.write(configfile)
    return ipport, secret


def validateserverdata():
    ipport = ""
    secret = ""

    config = configparser.ConfigParser()
    config.sections()

    try:
        config.read("config.ini")
        logindata = config["SERVER DATA"]
        ipport = logindata.get("server_address")
        secret = logindata.get("secret")
        # print(ipport, secret)
        haasomeClient = HaasomeClient(ipport, secret)
     
        if haasomeClient.test_credentials().errorCode == EnumErrorCode.SUCCESS:
            return ipport, secret
            print(haasomeClient.test_credentials().errorCode)
           
        elif haasomeClient.test_credentials().errorCode == EnumErrorCode.CONNECTION_FAILED:
             serverdata()
    except Exception as e:
        serverdata()
    except FileNotFoundError:
        currentfile = Path("config.ini")
        currentfile.touch(exist_ok=True)
        print("Config has been created!")

        config.read("config.ini")
        logindata = config["SERVER DATA"]
        ipport = logindata.get("server_address")
        secret = logindata.get("secret")
    return ipport, secret


def set_bt2():
    #older version of the code below
    response = input('Would you like to set BT starting date? Y/N: ' )
    if response =='Y' or response == 'y':
        year = input("Write year in 4 digits format: ")
        month = input("write month as 1 to 9, 10 to 12: ")
        day = input("write day as 1-9, 10-31: ")
        hour = input('write hours as: 1-24')
        minute = input('write minutes as 1-60')

        config = configparser.ConfigParser()
        config["BT"] = {"year": year, "month": month, "day": day, 'hour':hour, 'minute':minute}
        with open("bt.ini", "w") as configfile:
            config.write(configfile)
    else:
        pass

def set_bt():

    response = input(
        f'Type date and time in the following format to set as the begining of backtesting: {datetime.today().strftime("%d/%m/%y %H:%M")} ')
    dt = datetime.strptime(response, "%d/%m/%y %H:%M")
    # tt = dt.timetuple()
    print('Backtesting will now start from ',dt)
    config = configparser.ConfigParser()
    config ['TS'] = {'bt_starting_date': dt}
    config["BT"] = {"year": dt.year, "month": dt.month, "day": dt.day, 'hour': dt.hour, 'minute': dt.minute}
    with open("bt.ini", "w") as configfile:
        config.write(configfile)
    return dt







# def main():
#     dt = set_bt()
#     print(dt)


# if __name__ == "__main__":
#     main()
