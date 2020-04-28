# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest
import time
import re


class GeneralBruteforcer(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def test_general_bruteforcer(self):
        driver = self.driver
        # ERROR: Caught exception [unknown command [#]]
        # ERROR: Caught exception [unknown command [#]]
        goodroi = "3"
        # ERROR: Caught exception [unknown command [#]]
        bot setting file = "all_up_settings.csv"
        configlineinfile = "0"
        # ERROR: Caught exception [ERROR: Unsupported command [loadVars | ${bot setting file} | ]]
        # ERROR: Caught exception [ERROR: Unsupported command [getEval | ${configlineinfile}+1 | ]]
        # ERROR: Caught exception [unknown command [#]]
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Length'])[1]/following::input[1]").clear()
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Length'])[1]/following::input[1]").send_keys("${bbl}")
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Dev.Up'])[1]/following::input[1]").clear()
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Dev.Up'])[1]/following::input[1]").send_keys("${bbup}")
        driver.find_element_by_xpath(
            "//div[@id='cBotMadHatterBBandsBox']/div[2]/div[2]/i[2]").click()
        driver.find_element_by_xpath(
            "//div[@id='cBotMadHatterBBandsBox']/div[2]/div[2]/i").click()
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Dev.Down'])[1]/following::input[1]").clear()
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Dev.Down'])[1]/following::input[1]").send_keys("${bbdown}")
        driver.find_element_by_xpath(
            "//div[@id='cBotMadHatterBBandsBox']/div[3]/div[2]/i[2]").click()
        driver.find_element_by_xpath(
            "//div[@id='cBotMadHatterBBandsBox']/div[3]/div[2]/i").click()
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Length'])[2]/following::input[1]").clear()
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Length'])[2]/following::input[1]").send_keys("${rsil}")
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Buy level'])[1]/following::input[1]").clear()
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Buy level'])[1]/following::input[1]").send_keys("${rsibuy}")
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Sell level'])[1]/following::input[1]").clear()
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Sell level'])[1]/following::input[1]").send_keys("${rsisell}")
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='MACD Settings'])[1]/following::input[1]").clear()
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='MACD Settings'])[1]/following::input[1]").send_keys("${macdfast}")
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='MACD Fast'])[1]/following::input[2]").clear()
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='MACD Fast'])[1]/following::input[2]").send_keys("${macdslow}")
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='MACD Slow'])[1]/following::input[2]").clear()
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='MACD Slow'])[1]/following::input[2]").send_keys("${macdsign}")
        # ERROR: Caught exception [unknown command [#]]
        driver.find_element_by_xpath(
            "//div[@id='cBotMadHatterBBandsBox']/div[4]/div[2]/div").click()
        driver.find_element_by_xpath(
            "//div[@id='cBotMadHatterBBandsBox']//div[contains(text(),'${matype}')]").click()
        # ERROR: Caught exception [unknown command [#]]
        # ERROR: Caught exception [ERROR: Unsupported command [if | ${consensus}==1 | ]]
        if not driver.find_element_by_xpath("//input[@id='cBotMadHatterUseThreeSignals']").is_selected():
            driver.find_element_by_xpath(
                "//input[@id='cBotMadHatterUseThreeSignals']").click()
        # ERROR: Caught exception [unknown command [elseif]]
        if driver.find_element_by_xpath("//input[@id='cBotMadHatterUseThreeSignals']").is_selected():
            driver.find_element_by_xpath(
                "//input[@id='cBotMadHatterUseThreeSignals']").click()
        # ERROR: Caught exception [ERROR: Unsupported command [endIf |  | ]]
        # ERROR: Caught exception [ERROR: Unsupported command [if | ${icc}==1 | ]]
        if not driver.find_element_by_xpath("//input[@id='cBotMadHatterIncludeCurrentCandle']").is_selected():
            driver.find_element_by_xpath(
                "//input[@id='cBotMadHatterIncludeCurrentCandle']").click()
        # ERROR: Caught exception [unknown command [elseif]]
        if driver.find_element_by_xpath("//input[@id='cBotMadHatterIncludeCurrentCandle']").is_selected():
            driver.find_element_by_xpath(
                "//input[@id='cBotMadHatterIncludeCurrentCandle']").click()
        # ERROR: Caught exception [ERROR: Unsupported command [endIf |  | ]]
        # ERROR: Caught exception [ERROR: Unsupported command [if | ${resetmid}==1 | ]]
        if not driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Reset Middle'])[1]/following::input[1]").is_selected():
            driver.find_element_by_xpath(
                "(.//*[normalize-space(text()) and normalize-space(.)='Reset Middle'])[1]/following::input[1]").click()
        # ERROR: Caught exception [unknown command [elseif]]
        if driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Reset Middle'])[1]/following::input[1]").is_selected():
            driver.find_element_by_xpath(
                "(.//*[normalize-space(text()) and normalize-space(.)='Reset Middle'])[1]/following::input[1]").click()
        # ERROR: Caught exception [ERROR: Unsupported command [endIf |  | ]]
        # ERROR: Caught exception [ERROR: Unsupported command [if | ${requirefcc}==1 | ]]
        if not driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Require FCC'])[1]/following::input[1]").is_selected():
            driver.find_element_by_xpath(
                "(.//*[normalize-space(text()) and normalize-space(.)='Require FCC'])[1]/following::input[1]").click()
        # ERROR: Caught exception [unknown command [elseif]]
        if driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Require FCC'])[1]/following::input[1]").is_selected():
            driver.find_element_by_xpath(
                "(.//*[normalize-space(text()) and normalize-space(.)='Require FCC'])[1]/following::input[1]").click()
        # ERROR: Caught exception [ERROR: Unsupported command [endIf |  | ]]
        # ERROR: Caught exception [ERROR: Unsupported command [if | ${allowmidsell}==1 | ]]
        if not driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Allow Mid Sells'])[1]/following::input[1]").is_selected():
            driver.find_element_by_xpath(
                "(.//*[normalize-space(text()) and normalize-space(.)='Allow Mid Sells'])[1]/following::input[1]").click()
        # ERROR: Caught exception [unknown command [elseif]]
        if driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Allow Mid Sells'])[1]/following::input[1]").is_selected():
            driver.find_element_by_xpath(
                "(.//*[normalize-space(text()) and normalize-space(.)='Allow Mid Sells'])[1]/following::input[1]").click()
        # ERROR: Caught exception [ERROR: Unsupported command [endIf |  | ]]
        # ERROR: Caught exception [unknown command [#]]
        driver.find_element_by_css_selector("DIV#botRemoteStartCustom").click()
        dbt = driver.find_element_by_xpath("//div[@id='cBotRoi']").text
        # ERROR: Caught exception [ERROR: Unsupported command [getEval | storedVars['dbt'].match(/\D*\d+.\d+/); | ]]
        # ERROR: Caught exception [unknown command [#]]
        # ERROR: Caught exception [ERROR: Unsupported command [if | ${roiin}>=${goodroi} | ]]
        driver.find_element_by_id("cBotMadHatterName").clear()
        driver.find_element_by_id("cBotMadHatterName").send_keys(roiin)
        driver.find_element_by_css_selector(
            "#cBotMadHatterSave > span").click()
        driver.find_element_by_css_selector("DIV#cBotMadHatterClone").click()
        driver.find_element_by_css_selector("div.btn-grad.button").click()
        # ERROR: Caught exception [ERROR: Unsupported command [endIf |  | ]]
        # ERROR: Caught exception [ERROR: Unsupported command [endLoadVars |  | ]]

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
