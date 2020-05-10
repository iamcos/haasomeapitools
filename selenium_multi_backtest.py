import multiprocessing as mp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from configparser import ConfigParser
from selenium.common.exceptions import InvalidSessionIdException
import json
import numpy as np
from botsellector import BotSellector
from botdatabase import BotDB
from MadHatterBotClass import MadHatterBot
from time import sleep
import pandas as pd
from numpy import arange

'''
driver.find_elements_by_xpath("//*[contains(@class,"cursor earn_pages_button profile_view_img_")]").
'''
try:
    with open('selenium.json', "r") as f:
        session_data = json.load(f)
        url, session_id = session_data
        print(session_data)
except:
    pass


def init_session(webdriver,url =None, session_id=None,):
    try:
        driver = webdriver.Remote(command_executor=url, desired_capabilities={})
        driver.close()   # this prevents the dummy browser
        driver.session_id = session_id
        return driver
    except:
        print(F"Session isn't valid")


def headless(webdriver):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        return driver

def open_multiple_haas(webdriver,addrlst, l, p):
    drvrs = []

    try:
        sessions = retrive_sessions()
        for session in sessions:
            driver = init_session(
                webdriver, url=session.command_executor._url, id=session.session_id)
            drvrs.append(driver)

    except:
        sessions = []




    for adr in addrlst:
        driver = webdriver.Chrome()

        driver.get(adr)
        drvrs.append(driver)

    return drvrs

def store_sessions(sessions):
    frozen = []
    for driver in sessions:
        session_data = driver.command_executor._url, driver.session_id
        frozen.append(json.dumps(session_data))
    with open('selenium.json', "w") as f:
        json.dump(frozen, f)
        print('SAVED TO FILE')


def retrive_sessions(file='selenium.json'):
    sessions = []
    with open('selenium.json', "r") as f:
        data = json.load(f)
        for drv in data:
            driver = json.load(drv)
            sessions.append(driver)
    return sessions

def close_notification():
     element = WebDriverWait(driver, 50).until(
         EC.presence_of_element_located((By.XPATH, "//*[@id='updateClose']")))
     close_btn = driver.find_element_by_xpath("//*[@id='updateClose']").click()
     print('Huge notification closed)')


def login_do(driver, WebDriverWait, l, p):
        driver.get("http://127.0.0.1:8090/#/CustomBots")
        login_el = "username"
        element = WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.ID, login_el)))

        type_username = driver.find_element_by_id('username')
        type_username.send_keys(l)
        type_pwd = driver.find_element_by_id('password')
        type_pwd.send_keys(p)
        login = driver.find_element_by_id('sendLogin')
        login.click()

        element = WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='updateClose']")))
        close_btn = driver.find_element_by_xpath("//*[@id='updateClose']")
        try:
            close_notification()
        except:
            pass
        return driver



try:
    close_btn = driver.find_element_by_xpath("//*[@id='updateClose']").click()

except:
        pass

def chunkify(lst, n):
    return [lst[i::n] for i in arange(n)]


# chunk = chunkify(df, len([clone]))

# print('chuuunks',chunks[0])
# print('Chunks len: ',len(chunk), 'Chunk len: ',len(chunks[0]))


def apply_config_to_interface(config):
    sleep(2)
    bbl = driver.find_element_by_xpath(
        "//div[@id='MadHatterBBandsBox']//div[1]//div[2]//input[1]")
    try:
        bbl.click()
    except:
        driver.find_element_by_xpath(
            f"//div[@id='cBotMadHatterAdvanced']").click()
    finally:
        bbl = driver.find_element_by_xpath(
            "//div[@id='MadHatterBBandsBox']//div[1]//div[2]//input[1]")
        bbl.click()

    bbl.clear()
    bbl.send_keys(str(config['bbl']))
    bbl.send_keys(Keys.ENTER)
    devup = driver.find_element_by_xpath(
        "//div[@id='MadHatterBBandsBox']//div[2]//div[2]//input[1]")
    devup.click()
    devup.clear()
    devup.send_keys(str(config['devup']))
    devup.send_keys(Keys.ENTER)
    devdn = driver.find_element_by_xpath(
        "//div[@id='MadHatterBBandsBox']//div[3]//div[2]//input[1]")
    devdn.click()
    devdn.clear()
    devdn.send_keys(str(config['devdn']))
    devdn.send_keys(Keys.ENTER)

    rsil = driver.find_element_by_xpath("//div[@id='MadHatterRsi']//div[1]//div[2]//input[1]")
    rsil.click()
    rsil.clear()
    rsil.send_keys(str(config['rsil']))
    rsis = driver.find_element_by_xpath(
        "//div[@id='MadHatterRsi']//div[2]//div[2]//input[1]")
    rsis.click()
    rsis.clear()
    rsis.send_keys(str(config['rsis']))
    rsib = driver.find_element_by_xpath(
        "//div[@id='MadHatterRsi']//div[3]//div[2]//input[1]")
    rsib.click()
    rsib.clear()
    rsib.send_keys(str(config['rsib']))

    macdfast = driver.find_element_by_xpath(
        "//div[@id='MadHatterMacd']//div[1]//div[2]//input[1]")
    macdfast.click()
    macdfast.clear()
    macdfast.send_keys(str(config['macdfast']))

    macdslow = driver.find_element_by_xpath(
        "//div[@id='MadHatterMacd']//div[2]//div[2]//input[1]")
    macdslow.click()
    macdslow.clear()
    macdslow.send_keys(str(config['macdslow']))

    macdsign = driver.find_element_by_xpath("//div[@id='MadHatterMacd']//div[3]//div[2]//input[1]")
    macdsign.click()
    macdsign.clear()
    macdsign.send_keys(str(config['macdsign']))
    # save = driver.find_element_by_xpath(
    #     "//div[@id='cBotMadHatterSave']")
    #     # sleep(2)
    # # save.click()
    sleep(2)




def config_bt_bot(driver,webdriver, chunk,bot):
        h = MadHatterBot()
        sleep(1)

        chunk.reset_index(drop=True, inplace=True)
        clones = []

        for ii in range(len(chunk)):

            name = F"{bot.priceMarket.primaryCurrency}|{bot.priceMarket.secondaryCurrency},#{ii}"
            clone = h.clone_bot_for_bt2(bot, str(name))
            print(clone.name,'Clonr NAME')
            config = h.apply_config_to_madhatter_bot(clone, chunk, ii)
            clones.append(clone)
            element = WebDriverWait(driver, 120).until(
                EC.presence_of_element_located(driver,By.XPATH("//*[@data-guid=]")))
            try:
                driver.find_element_by_id("botRemoteStartCustom").click()
            except:
                driver.find_element_by_id("botRemoteWindow").click()
            finally:
                driver.find_element_by_id("botRemoteStartCustom").click()
            try:
                driver.find_element_by_link_text('Close').click()
            except:
                pass

            bt_over = f"The backtest of bot {name} has finished"
            element = WebDriverWait(driver, 120).until(
                EC.text_to_be_present_in_element((By.XPATH("//",bt_over))))

            chunk['roi'][ii] = h.return_bot(clone.guid).roi
            h.delete_temp_bot(clone)
        return chunk

try:
    close_btn = driver.find_element_by_xpath("//*[@id='updateClose']").click()

except:
    pass



def main():
    bot = BotSellector().get_mad_hatter_bot()


    df = BotDB().csv_to_dataframe()

    chunk =df
    pages = "http://127.0.0.1:8090/#/NotificationCenter", "http://127.0.0.1:8090/#/CustomBots"
    l = 1
    p = l
    driver = webdriver.Chrome()
    driver2 = webdriver.Remote(command_executor=the_known_url)
    if driver2.session_id != the_known_session_id:   # this is pretty much guaranteed to be the case
        # this closes the session's window - it is currently the only one, thus the session itself will be auto-killed, yet:
        driver2.close()
        driver2.quit()
        login_do(driver, WebDriverWait, 1, 1)
    try:
        done_chunks = config_bt_bot(driver, webdriver, chunk, bot)
    except Exception as e:
        print(e)
        driver.close()



def get_param_input(param):
    try:
        inp = param.find_element_by_xpath(".//following-sibling::input")
    except:
        pass
    try:
        bol = param.find_element_by_xpath(".//following-sibling::td")
    except:
        pass

if __name__ == "__main__":
    main()
