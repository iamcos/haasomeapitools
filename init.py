# Haasonline connect script

import configserver
from haasomeapi.HaasomeClient import HaasomeClient
from haasomeapi.enums.EnumErrorCode import EnumErrorCode


def connect():
    ip, secret = configserver.validateserverdata()
    haasomeClient = HaasomeClient(ip, secret)
    return haasomeClient


def main():
    do = connect().test_credentials()

    print("There are ", len(do.result.values()), "wallets registerd in the system")
    return do.result


if __name__ == "__main__":
    main()
