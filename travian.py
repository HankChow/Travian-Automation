#!/usr/bin/env python3
# coding: utf-8

import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver

class Travian(object):

    def __init__(self, username, passwd, server):
        self.username = username
        self.password = passwd
        self.server = server

    def init_webdriver(self):
        self.driver = webdriver.Firefox()

    def login(self):
        self.driver.get('https://www.travian.com/international')
        self.driver.implicitly_wait(20)
        btn_login = self.driver.find_element_by_xpath('//a[@href="#login"]')
        btn_login.click()
        # 服务器列表
        world_list = self.driver.find_element_by_class_name('worldGroup').find_elements_by_xpath('div')
        for item in world_list:
            if item.text.lower() == self.server.lower():
                item.click()
                break
        else:
            print('No such server.')
            exit()
        input_username = self.driver.find_element_by_name('usernameOrEmail')
        input_username.send_keys(self.username)
        input_password = self.driver.find_element_by_name('password')
        input_password.send_keys(self.password)
        btn_submit_login = self.driver.find_element_by_id('id')
        btn_submit_login.click()

    def logout(self):
        

    def close_browser(self):
        self.driver.quit()

if __name__ == '__main__':
    t = Travian('', '', '')
    t.init_webdriver()
    t.login()
    time.sleep(30)
    t.close_browser()
