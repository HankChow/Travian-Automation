#!/usr/bin/env python3
# coding: utf-8

from bs4 import BeautifulSoup
from pprint import pprint
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
        world_list = self.driver.find_elements_by_css_selector('div.worldGroup div')
        for item in world_list:
            if item.text.lower() == self.server.lower():
                item.click()
                break
        else:
            print('No such server.')
            exit()
        input_username = self.driver.find_element_by_css_selector('input[name=usernameOrEmail]')
        input_username.send_keys(self.username)
        input_password = self.driver.find_element_by_css_selector('input[name=password]')
        input_password.send_keys(self.password)
        btn_submit_login = self.driver.find_element_by_css_selector('button#id')
        btn_submit_login.click()
        self.driver.implicitly_wait(10)
        print('Successfully logged in.')

    # 装饰器，当页面不在 dorf1 或 dorf2 时，跳转到 dorf1
    def switch_to_dorf(func):
        def switch(self, *args, **kwargs):
            if 'dorf' not in self.driver.current_url:
                ul_navigation = self.driver.find_element_by_css_selector('ul#navigation')
                ul_navigation.find_element_by_css_selector('li#n1 a').click()
                self.driver.implicitly_wait(5)
            return func(self, *args, **kwargs)
        return switch

    # 装饰器，当页面不在 dorf1 时，跳转到 dorf1
    def switch_to_dorf1(func):
        def switch(self, *args, **kwargs):
            if 'dorf1.php' not in self.driver.current_url:
                ul_navigation = self.driver.find_element_by_css_selector('ul#navigation')
                ul_navigation.find_element_by_css_selector('li#n1 a').click()
                self.driver.implicitly_wait(5)
            return func(self, *args, **kwargs)
        return switch

    # 装饰器，当页面不在 dorf2 时，跳转到 dorf2
    def switch_to_dorf2(func):
        def switch(self, *args, **kwargs):
            if 'dorf2.php' not in self.driver.current_url:
                ul_navigation = self.driver.find_element_by_css_selector('ul#navigation')
                ul_navigation.find_element_by_css_selector('li#n2 a').click()
                self.driver.implicitly_wait(5)
            return func(self, *args, **kwargs)
        return switch

    # 装饰器，跳转到英雄页面
    def switch_to_hero(func):
        def switch(self, *args, **kwargs):
            btn_hero = self.driver.find_element_by_css_selector('button.heroImageButton')
            btn_hero.click()
            self.driver.implicitly_wait(5)
            return func(self, *args, **kwargs)
        return switch

    def logout(self):
        btn_logout = self.driver.find_element_by_css_selector('a[href="logout.php"]')
        btn_logout.click()
        print('Successfully logged out.')

    def close_browser(self):
        self.driver.quit()


class TravianGetter(Travian):

    @Travian.switch_to_dorf
    def get_villages(self):
        village_box = self.driver.find_element_by_css_selector('div#sidebarBoxVillagelist')
        box_content = village_box.find_element_by_css_selector('div.content')
        villages = box_content.find_elements_by_css_selector('li')
        vlg = list(map(lambda x: {
            'current': True if x.get_attribute('class').strip() == 'active' else False,
            'name': x.find_element_by_css_selector('div.name').text.strip(),
            'coordsX': int(x.find_element_by_css_selector('span.coordinateX').text[1:].strip('\u202d\u202c')),
            'coordsY': int(x.find_element_by_css_selector('span.coordinateY').text[:-1].strip('\u202d\u202c'))
        }, villages))
        return vlg

    @Travian.switch_to_dorf1
    def get_current_village_production(self):
        production_list = self.driver.find_elements_by_css_selector('table#production tbody tr')
        cvp = {}
        for item in production_list:
            cvp[item.find_element_by_css_selector('td.res').text.strip(':')] = \
                int(item.find_element_by_css_selector('td.num').text.strip('\u202d\u202c'))
        return cvp

    @Travian.switch_to_dorf1
    def get_current_village_troops(self):
        troops_list = self.driver.find_elements_by_css_selector('table#troops tdoby tr')
        cvt = {}
        for item in troops_list:
            cvt[item.find_element_by_css_selector('td.un').text.strip()] = \
                int(item.find_element_by_css_selector('td.num').text.strip('\u202d\u202c'))
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

    @Travian.switch_to_dorf1
    def get_current_village_fields(self):
        field_map = self.driver.find_element_by_css_selector('map#rx')
        fields = field_map.find_elements_by_css_selector('area')
        cvf = list(map(lambda x: {
            'id': int(x.get_attribute('href').split('=')[1]),
            'type': x.get_attribute('alt').split(' Level ')[0],
            'level': int(x.get_attribute('alt').split(' Level ')[1])
        }, list(filter(lambda x: 'id' in x.get_attribute('href'), fields))))
        return cvf

    @Travian.switch_to_dorf2
    def get_current_village_buildings(self):
        building_map = self.driver.find_element_by_css_selector('map#clickareas')
        buildings = building_map.find_elements_by_css_selector('area')
        # 如果某个位置未有建筑，其 alt 属性为"Building site"
        # 如果某个位置已有建筑，其 alt 属性为一段 HTML ，因此先将 alt 置为 None ，随后再用 BeautifulSoup 去解析
        cvb = list(map(lambda x: {
            'id': int(x.get_attribute('href').split('=')[1]),
            'type': 'empty' if x.get_attribute('alt') == 'Building site' else None,
            'level': 0 if x.get_attribute('alt') == 'Building site' else None,
            'alt': None if x.get_attribute('alt') == 'Building site' else x.get_attribute('alt')
        }, buildings))
        for item in cvb:
            if not item['type']:
                alt_soup = BeautifulSoup(item['alt'], 'lxml')
                item['type'] = list(alt_soup.find('p').strings)[0].strip()
                item['level'] = int(alt_soup.find('span', class_='level').string.split(' ')[1])
                item['alt'] = None
        return cvb

    @Travian.switch_to_dorf
    def get_current_village_upgrading(self):
        anchor = self.driver.find_elements_by_css_selector('h5')
        if len(anchor) == 0:
            cvu = []
            return cvu
        else:
            anchor = anchor[0]
            upgrades = anchor.find_elements_by_xpath('../ul/li')
            cvu = list(map(lambda x: {
                'type': x.find_element_by_css_selector('div.name').text.split(' Level ')[0].strip(),
                'level': int(x.find_element_by_css_selector('div.name').text.split(' Level ')[1].strip()),
                'finish': x.find_element_by_css_selector('div.buildDuration').text.split(' ')[-1].strip()
            }, upgrades))
            return cvu

    @Travian.switch_to_hero
    def get_available_hero_adventures(self):
        self.switch_to_hero()
        tab_adventure = self.driver.find_element_by_css_selector('div.favorKey3')
        tab_adventure.click()
        self.driver.implicitly_wait(5)
        adventures = self.driver.find_elements_by_css_selector('form#adventureListForm table tbody tr')
        aha = list(map(lambda x: {
            'type': x.find_element_by_css_selector('td.location').text.strip(),
            'coordsX': int(x.find_element_by_css_selector('span.coordinateX').text[1:].strip('\u202d\u202c')),
            'coordsY': int(x.find_element_by_css_selector('span.coordinateY').text[:-1].strip('\u202d\u202c')),
            'duration': x.find_element_by_css_selector('td.moveTime').text.strip(),
            'danger': x.find_element_by_css_selector('td.difficulty img').get_attribute('alt'),
            'lefttime': x.find_element_by_css_selector('td.timeLeft').text.strip()
        }, adventures))
        return aha



class TravianSetter(Travian):

    @Travian.switch_to_dorf
    def set_upgrade(self, uid):
        upgrade_url = '/'.join(self.driver.current_url.split('/')[:-1]) + 'build.php?id={uid}'.format(uid=uid)
        self.driver.get(upgrade_url)
        self.driver.implicitly_wait(5)


if __name__ == '__main__':
    tg = TravianGetter('', '', '')
    tg.login()
    pprint(tg.get_current_village_buildings())
    tg.logout()
    tg.close_browser()
