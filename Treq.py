#!/usr/bin/env python3
# coding: utf-8

from bs4 import BeautifulSoup
from pprint import pprint
import requests
import time


class Treq(object):

    def __init__(self, username, password, server):
        self.username = username
        self.password = password
        self.server = server
        self.req = requests.Session()

    def login(self):
        url = 'https://{server}.travian.com/dorf1.php'.format(server=self.server)
        login_data = {
            'login': int(time.time()),
            'name': self.username,
            'password': self.password,
            's1': 'Login',
            'w': '1366:768'
        }
        self.req.post(url, data=login_data)

    def get_villages(self):
        url = 'https://{server}.travian.com/dorf1.php'.format(server=self.server)
        soup = BeautifulSoup(self.req.get(url).text, 'lxml')
        village_list = soup.select('div#sidebarBoxVillagelist div.content li')
        vlg = list(map(lambda x: {
            'current': True if 'active' in x['class'] else False,
            'name': x.select('div.name')[0].string.strip(),
            'coordsX': x.select('span.coordinateX')[0].string[1:].strip('\u202d\u202c'),
            'coordsY': x.select('span.coordinateY')[0].string[:-1].strip('\u202d\u202c')
        }, village_list))
        return vlg

    def get_current_village_production(self):
        url = 'https://{server}.travian.com/dorf1.php'.format(server=self.server)
        soup = BeautifulSoup(self.req.get(url).text, 'lxml')
        production_list = soup.select('table#production tbody tr')
        cvp = {
            'lumber': int(production_list[0].select('td.num')[0].string.strip().strip('\u202d\u202c')),
            'clay': int(production_list[1].select('td.num')[0].string.strip().strip('\u202d\u202c')),
            'iron': int(production_list[2].select('td.num')[0].string.strip().strip('\u202d\u202c')),
            'crop': int(production_list[3].select('td.num')[0].string.strip().strip('\u202d\u202c'))
        }
        return cvp

    def get_current_village_troops(self):
        url = 'https://{server}.travian.com/dorf1.php'.format(server=self.server)
        soup = BeautifulSoup(self.req.get(url).text, 'lxml')
        troops_list = soup.select('table#troops tbody tr')
        cvt = {}
        for item in troops_list:
            cvt[item.select('td.un')[0].string.strip()] = \
                int(item.select('td.num')[0].string.strip().strip('\u202d\u202c'))
        return cvt

    def get_current_village_resources(self):
        url = 'https://{server}.travian.com/dorf1.php'.format(server=self.server)
        soup = BeautifulSoup(self.req.get(url).text, 'lxml')
        stockbar = soup.select('ul#stockBar')[0]
        cvr = {
            'warehouse': stockbar.select('span#stockBarWarehouse')[0].string.strip().strip('\u202d\u202c'),
            'granary': stockbar.select('span#stockBarGranary')[0].string.strip().strip('\u202d\u202c'),
            'lumber': stockbar.select('span#l1')[0].string.strip().strip('\u202d\u202c'),
            'clay': stockbar.select('span#l2')[0].string.strip().strip('\u202d\u202c'),
            'iron': stockbar.select('span#l3')[0].string.strip().strip('\u202d\u202c'),
            'crop': stockbar.select('span#l4')[0].string.strip().strip('\u202d\u202c'),
            'free': stockbar.select('span#stockBarFreeCrop').string.strip('\u202d\u202c')
        }
        for k in cvr.keys():
            cvr[k] = int(cvr[k].replace('.', ''))
        return cvr

    def get_current_village_fields(self):
        url = 'https://{server}.travian.com/dorf1.php'.format(server=self.server)
        soup = BeautifulSoup(self.req.get(url).text, 'lxml')
        field_list = soup.select('map#rx area')
        cvf = list(map(lambda x: {
            'id': int(x['href'].split('=')[1]),
            'type': x['alt'].split(' Level ')[0],
            'level': int(x['alt'].split(' Level ')[1])
        }, list(filter(lambda x: 'id' in x['href'], field_list))))
        return cvf

    def get_current_village_buildings(self):
        url = 'https://{server}.travian.com/dorf2.php'.format(server=self.server)
        soup = BeautifulSoup(self.req.get(url).text, 'lxml')
        building_list = soup.select('map#clickareas area')
        # 如果某个位置未有建筑，其 alt 属性为"Building site"
        # 如果某个位置已有建筑，其 alt 属性为一段 HTML ，因此先将 alt 置为 None ，随后再用进一步解析
        cvb = list(map(lambda x: {
            'id': int(x['href'].split('=')[1]),
            'type': 'empty' if x['alt'] == 'Building site' else None,
            'level': 0 if x['alt'] == 'Building site' else None,
            'alt': None if x['alt'] == 'Building site' else x['alt']
        }, building_list))
        for item in cvb:
            if not item['type']:
                alt_soup = BeautifulSoup(item['alt'], 'lxml')
                item['type'] = list(alt_soup.find('p').strings)[0].strip()
                item['level'] = int(alt_soup.find('span', class_='level').string.split()[1])
                item['alt'] = None
        return cvb

    def get_current_village_upgrading(self):
        url = 'https://{server}.travian.com/dorf2.php'.format(server=self.server)
        soup = BeautifulSoup(self.req.get(url).text, 'lxml')
        anchor = soup.select('h5')
        if len(anchor) == 0:
            cvu = []
            return cvu
        else:
            anchor = anchor[0]
            upgrade_list = list(filter(lambda x: x.name == 'ul', list(anchor.next_siblings)))[0].select('li')
            cvu = list(map(lambda x: {
                'type': list(x.select('div.name')[0].strings)[0].strip(),
                'level': int(list(x.select('div.name')[0].strings)[1].split()[1]),
                'finish': list(x.select('div.buildDuration')[0].strings)[-1].split()[-1].strip()
            }, upgrade_list))
            return cvu

    def get_position_upgrade_cost(self, position, new_type=None):
        if 1 <= position <= 40:
            url = 'https://{server}.travian.com/build.php?id={id}'.format(server=self.server, id=position)
            soup = BeautifulSoup(self.req.get(url).text, 'lxml')
            # 如果该位置已有建筑，在标题应有一个 span 标签显示建筑等级
            # 根据是否有该 span 标签来判断某个位置是否已有建筑
            if position >= 19 and not len(soup.select('h1.titleInHeader span.level')):
                building_block = soup.select('div#contract_building{new_type}'.format(new_type=new_type))[0]
                cost_list = building_block.select('div.showCosts span')
                time_cost = building_block.select('div.showCosts span.clocks')
            else:
                cost_list = soup.select('div.contractCosts span')
                time_cost = soup.select('div.upgradeButtonsContainer span.clocks')
            puc = {
                'lumber': int(list(cost_list[0].strings)[0]),
                'clay': int(list(cost_list[1].strings)[0]),
                'iron': int(list(cost_list[2].strings)[0]),
                'crop': int(list(cost_list[3].strings)[0]),
                'free': int(list(cost_list[4].strings)[0]),
                'time': list(time_cost[0].strings)[0]
            }
            return puc
        else:
            print('Inavailable position.')

    def do_upgrade(self, position, new_type=None):
        if 1 <= position <= 40:
            url = 'https://{server}.travian.com/build.php?id={id}'.format(server=self.server, id=position)
            soup = BeautifulSoup(self.req.get(url).text, 'lxml')
            if position >= 19 and not len(soup.select('h1.titleInHeader span.level')):
                building_block = soup.select('div#contract_building{new_type}'.format(new_type=new_type))[0]
                btn_upgrade = building_block.select('div.contractLink button')[0]
            else:
                btn_upgrade = soup.select('div.upgradeButtonsContainer div.section1 button')[0]
            shortlink = btn_upgrade['onclick'].split('\'')[1]
            upgrade_link = 'https://{server}.travian.com/{shortlink}'.format(server=self.server, shortlink=shortlink)
            self.req.get(upgrade_link)
        else:
            print('Inavailable position.')

    def get_available_hero_adventure(self):
        url = 'https://{server}.travian.com/hero.php?t=3'.format(server=self.server)
        soup = BeautifulSoup(self.req.get(url).text, 'lxml')
        adventure_list = soup.select('form#adventureListForm table tbody tr')
        aha = list(map(lambda x: {
            'type': list(x.select('td.location')[0].strings)[0].strip(),
            'coordsX': x.select('span.coordinateX')[0].string[1:].strip('\u202d\u202c'),
            'coordsY': x.select('span.coordinateY')[0].string[:-1].strip('\u202d\u202c'),
            'duration': x.select('td.moveTime')[0].string.strip(),
            'danger': x.select('td.difficulty img')[0]['alt'],
            'lefttime': x.select('td.timeLeft span')[0].string.strip()
        }, adventure_list))
        return aha

    def logout(self):
        url = 'https://{server}.travian.com/logout.php'.format(server=self.server)
        self.req.get(url)


if __name__ == '__main__':
    t = Treq('hank47', 'zc_7r4v14n', 'ts7')
    t.login()
    pprint(t.get_position_upgrade_cost(31))
