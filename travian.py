#!/usr/bin/env python3
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class Travian(object):

    def __init__(self, username, passwd, server):
        self.username = username
        self.password = passwd
        self.server = server

    def init_webdriver(self):
        #self.driver = webdriver.Firefox()
        self.driver = webdriver.PhantomJS()

    def login(self):
        self.driver.get('https://www.travian.com/international')
        self.driver.implicitly_wait(20)
        # 首页的 LOGIN 按钮在 phantomjs 引擎下会谜之不可见
        # 因此无法用常规的 click() 来模拟点击，只能用原生 js 定位这个不可见元素后点击
        self.driver.execute_script('document.evaluate(\'//a[@href="#login"]\', document, null, XPathResult.ANY_TYPE, null).iterateNext().click();')
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
        self.driver.implicitly_wait(10)
        print('Successfully logged in.')

    def get_current_village_production(self):
        tbl_production = self.driver.find_element_by_css_selector('table#production')
        production_list = tbl_production.find_element_by_xpath('tbody').find_elements_by_xpath('tr')
        cvp = {}
        for item in production_list:
            cvp[item.find_element_by_class_name('res').text.strip(':')] = \
                int(item.find_element_by_class_name('num').text.strip('\u202d\u202c'))
        return cvp

    def logout(self):
        btn_logout = self.driver.find_element_by_xpath('//a[@href="logout.php"]')
        btn_logout.click()
        print('Successfully logged out.')

    def close_browser(self):
        self.driver.quit()

if __name__ == '__main__':
    t = Travian('', '', '')
    t.init_webdriver()
    t.login()
    print(t.get_current_village_production())
    t.logout()
    t.close_browser()
