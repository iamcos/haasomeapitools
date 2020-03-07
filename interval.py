from datetime import datetime, date, time, timedelta
import configserver



def total_ticks():
    year, month, day, hour, minute = configserver.read_bt()
    """ Get backtestin ticks in resolution defined in main bot config
	:param year: int: year number
	:param month: int: month number
	:param day: int: day number
	:param interval
	:returns:
	:int: numbers of ticks in configured bot time interval from defined dat
	"""
    ticks = inticks(year, month, day, hour, minute, 1)
    return ticks


def inticks(year, month, day,hour, minute, interval):
    """ Get backtestin ticks in resolution defined in main bot config
	:param year: int: year number
	:param month: int: month number
	:param day: int: day number
	:param interval
	:returns:
	:int: numbers of ticks in configured bot time interval from defined dat
	"""
    t1 = datetime.today()

    t2 = date(year=int(year), month=int(month), day=int(day))
    t3 = time(hour=int(hour), minute=int(minute))

    t4 = datetime.combine(t2, t3)

    t5 = t1-t4

    return t5.total_seconds()/60


def readinterval(bot):

    year, month, day, hour, minute = configserver.read_bt()
    ticks = inticks(int(year), int(month), int(day), int(hour), int(minute) ,bot.interval)
    return ticks



def main():
    year, month, day, hour, minute = configserver.read_bt()
    ticks = inticks(year, month, day, hour, minute, 1)
    print(ticks)


if __name__ == "__main__":
    main()
