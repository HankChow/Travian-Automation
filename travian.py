#!/usr/bin/env python3
# coding: utf-8

from selenium import webdriver


class Travian(object):

    def __init__(self, username, passwd, server):
        self.username = username
        self.password = passwd
        self.server = server
        # self.driver = webdriver.Firefox()
        self.driver = webdriver.PhantomJS()

    def login(self):
        self.driver.get('https://www.travian.com/international')
        self.driver.implicitly_wait(20)
        # 首页的 LOGIN 按钮在 phantomjs 引擎下会谜之不可见
        # 因此无法用常规的 click() 来模拟点击，只能用原生 js 定位这个不可见元素后点击
        self.driver.execute_script(
            'document.evaluate(\'//a[@href="#login"]\',document,null,XPathResult.ANY_TYPE,null).iterateNext().click();')
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

    # 需要设为装饰器，未测试
    def switch_to_dorf1(self):
        if 'dorf1.php' not in self.driver.current_url:
            ul_navigation = self.driver.find_element_by_css_selector('ul#navigation')
            ul_navigation.find_element_by_css_selector('li#n1').find_element_by_tag_name('a').click()
            self.driver.implicitly_wait(5)

    # 需要设为装饰器，未测试
    def switch_to_dorf2(self):
        if 'dorf2.php' not in self.driver.current_url:
            ul_navigation = self.driver.find_element_by_css_selector('ul#navigation')
            ul_navigation.find_element_by_css_selector('li#n2').find_element_by_tag_name('a').click()
            self.driver.implicitly_wait(5)

    def get_current_village_production(self):
        tbl_production = self.driver.find_element_by_css_selector('table#production')
        production_list = tbl_production.find_element_by_xpath('tbody').find_elements_by_xpath('tr')
        cvp = {}
        for item in production_list:
            cvp[item.find_element_by_class_name('res').text.strip(':')] = \
                int(item.find_element_by_class_name('num').text.strip('\u202d\u202c'))
        return cvp

    def get_current_village_troops(self):
        tbl_troops = self.driver.find_element_by_css_selector('table#troops')
        troops_list = tbl_troops.find_element_by_xpath('tbody').find_elements_by_xpath('tr')
        cvt = {}
        for item in troops_list:
            cvt[item.find_element_by_class_name('un').text.strip()] = \
                int(item.find_element_by_class_name('num').text.strip('\u202d\u202c'))
        return cvt

    def get_current_village_resources(self):
        ul_stockbar = self.driver.find_element_by_css_selector('ul#stockBar')
        warehouse_limit = ul_stockbar.find_element_by_css_selector('span#stockBarWarehouse').text.strip('\u202d\u202c')
        granary_limit = ul_stockbar.find_element_by_css_selector('span#stockBarGranary').text.strip('\u202d\u202c')
        lumber = ul_stockbar.find_element_by_css_selector('span#l1').text.strip('\u202d\u202c')
        clay = ul_stockbar.find_element_by_css_selector('span#l2').text.strip('\u202d\u202c')
        iron = ul_stockbar.find_element_by_css_selector('span#l3').text.strip('\u202d\u202c')
        crop = ul_stockbar.find_element_by_css_selector('span#l4').text.strip('\u202d\u202c')
        free = ul_stockbar.find_element_by_css_selector('span#stockBarFreeCrop').text.strip('\u202d\u202c')
        cvr = {
            'warehouse': warehouse_limit,
            'granary': granary_limit,
            'lumber': lumber,
            'clay': clay,
            'iron': iron,
            'crop': crop,
            'free': free
        }
        return cvr

    def get_current_village_fields(self):
        field_map = self.driver.find_element_by_css_selector('map#rx')
        fields = field_map.find_elements_by_css_selector('area')
        cvf = list(map(lambda x: {
            'id': x.get_attribute('href').split('=')[1],
            'type': x.get_attribute('alt').split(' Level ')[0],
            'level': x.get_attribute('alt').split(' Level ')[1]
        }, list(filter(lambda x: 'id' in x.get_attribute('href'), fields))))
        return cvf

    def logout(self):
        btn_logout = self.driver.find_element_by_xpath('//a[@href="logout.php"]')
        btn_logout.click()
        print('Successfully logged out.')

    def close_browser(self):
        self.driver.quit()


if __name__ == '__main__':
    t = Travian('', '', '')
    t.login()
    print(t.get_current_village_production())
    print(t.get_current_village_troops())
    print(t.get_current_village_resources())
    print(t.get_current_village_fields())
    t.logout()
    t.close_browser()
