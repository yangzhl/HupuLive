#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Hupu Live:
    Proudly presented by Hupu JRs.

Usage:
    hupu -l | --list
    hupu -s | --shedule
    hupu -w | --watch <gameNumber>
    hupu -d | --data  <gameNumber>
    hupu -n | --news  <gameNumber>
    hupu -h | --help
    hupu -v | --version

Tips:
    Please hit Ctrl-C on the keyborad when you want to interrupt the game live.

Arguments:
    gameNumber     Obtained by command 'hupu -l'

Options:
    -h --help        Show this help message and exit.
    -v --version     Show version.
    -l --list        Show game live list.
    -w --watch       Select a game live to watch.
    -d --data        Show game statistical data (like points, rebounds, assists)
    -n --news        Show postgame news
    -s --schedule    Show game schedule

modify by yang zhi long 
time: 2018.10.3
"""

from __future__ import print_function
import time
import re

from docopt import docopt
import requests
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

class Hupu():

    __headers__ = {'X-Requested-With': 'XMLHttpRequest',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                                 '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

    def __init__(self, **kwargs):
        self._args = kwargs
        self._namelst = []
        self._hreflst = []
        self._datalst = []
        self._headers = self.__headers__
        self.get_gamelist()

    def get_command(self):
        """ 处理命令行参数 """
        if self._args.get('-l') or self._args.get('--list'):
            if self._namelst:
                print("\n 比赛\t\t\t| 比赛场次\n", "-" * 35)
                for i, v in enumerate(self._namelst):
                    print(" {}\t| {}\n".format(v, i), "-" * 35)
            else:
                print(">>  暂无比赛直播")
        if self._args.get('-w') or self._args.get('--watch'):
            if self._args.get('<gameNumber>') == None:
                print(">>  请输入观看的场次序号(可通过'hupu -l'获取)")
                raise SystemExit
            try:
                self.live_game(self._hreflst[int(self._args.get('<gameNumber>'))])
            except Exception:
                print(">>  无该比赛场次文字直播")
        if self._args.get('-d') or self._args.get('--data'):
            if self._args.get('<gameNumber>') == None:
                print(">>  请输入观看的场次序号以获取球员数据(可通过'hupu -l'获取)")
                raise SystemExit
            try:
                self.show_data(self._datalst[int(self._args.get('<gameNumber>'))])
            except Exception:
                print(">>  无该比赛场次球员数据")
        if self._args.get('-n') or self._args.get('--news'):
            if self._args.get('<gameNumber>') == None:
                print(">>  请输入观看的场次序号以获取赛后新闻(可通过'hupu -l'获取)")
                raise SystemExit
            try:
                self.show_news(int(self._args.get('<gameNumber>')))
            except Exception:
                print(">>  无该比赛场次赛后新闻")
        if self._args.get('-s') or self._args.get('--schedule'):
            try:
                self.show_schedule()
            except Exception:
                print(">>  无法查询到比赛的赛程")

    def get_gamelist(self):
        """ 获取直播场次列表 """
        url = "https://nba.hupu.com/games"
        try:
            r = requests.get(url, headers=self._headers, timeout=6).text
            game_href = BeautifulSoup(r, 'lxml').find_all('a', target="_self")
            for href in game_href:
                h = href['href']
                if "playbyplay" in h:
                    self._hreflst.append(h)
                    game = BeautifulSoup(requests.get(h).text, 'lxml').find('p', class_="bread-crumbs").text
                    self._namelst.append(str(game).strip().split()[1])     
                    """ 获取对阵双方"""
                if "boxscore" in h:
                    self._datalst.append(h)
        except requests.exceptions.ConnectTimeout:
            print(">>  获取比赛场次失败,请检查您的网络连接情况")

    def show_data_title(self, url):
        """" 显示比赛统计数据的各项标题，如得分，篮板 """
        r = requests.get(url, headers=self.__headers__, timeout=6).text
        title = BeautifulSoup(r, 'lxml').find('tr', class_="title bg_a").find_all('td')
        print()
        for i, v in enumerate([t.text for t in title]):
            if i == 0:
                print("  位置", end="")
            elif i <= 15:
                print(v, end="\t")
        print("球员\n")

    def show_data(self, url):
        """ 显示比赛统计数据 """
        self.show_data_title(url)
        r = requests.get(url, headers=self.__headers__, timeout=6).text
        players = BeautifulSoup(r, 'lxml').find_all('tr', style="background-color: rgb(255, 255, 255);")
        for index, player in enumerate(players):
            if index == 15:
                print("-" * 135)
                self.show_data_title(url)
            tdlst = [td.text for td in player.find_all('td')]
            for i, v in enumerate(tdlst):
                if i > 0:
                    if i == 1:
                        print(" ", v.replace("\n", ""), end="\t")
                    elif i == 13:
                        print(v.replace("\n", ""), end="\t")
                    else:
                        print(v.replace("\n", ""), end="\t")
            print(tdlst[0], "\n")

    def show_news(self, index):
        """ 显示赛后新闻 """
        r = requests.get(self._hreflst[index], headers=self._headers, timeout=6).text
        print(self._hreflst[index])
        news_href = BeautifulSoup(r, 'lxml').find_all('a', target="_self")
        for href in news_href:
            h = href['href']
            if "recap" in h:
                r = requests.get(h, headers=self._headers, timeout=6).text
                news = BeautifulSoup(r, 'lxml').find("div", class_="news_box").text
                print(str(news).replace("\n", "\n\n"))
                return
        print(">> 无该比赛场次赛后新闻")

    def show_schedule(self):
        """ 显示赛程 """
        url = "https://nba.hupu.com/schedule"
        r = requests.get(url, headers=self._headers, timeout=6).text
        result = str(BeautifulSoup(r, 'lxml').find('table', class_="players_table").text).split()
        schedule = [r for r in result if r not in ["数据统计", "比赛视频", "比赛前瞻", "视频直播"]]
        index = 0
        print()
        for i, v in enumerate(schedule):
            if i < 3:
                print(v, end=" ")
            elif i == 3:
                print(v)
            else:
                if index % 4 == 0 and index != 0:
                    index = 0
                    print()
                if re.findall(r"\d{2}月\d{2}日", v):
                    print("\n" + v, end=" ")
                elif re.findall(r"星期[一二三四五六日]", v):
                    print(v, end="\n")
                else:
                    index += 1
                    print(v, end=" ")
        print()

    def live_order(self, trlst, currid_cnt, table):
        """ 调整比赛直播顺序 """
        for tr in trlst:
            if currid_cnt <= len(trlst):
                currid_cnt += 1
                td = [t.text for t in table.find('tr', id=tr['id']).find_all('td')]
                if len(td) == 4:
                    gtime, gteam, gevent, gscore = td
                    if len(gteam) < 5:  # 补全空格，使显示格式对齐，强迫症
                        gteam += int(5 - len(gteam)) * 2 * " "
                    print("\t{} \t {} \t {}\t{}\n".format(gtime, gscore, gteam[1:], gevent))
                elif len(td) == 1:      # 显示如比赛暂停，第一节结束等非比分信息
                    print("", td[0], "\n")
                    if td[0] == "比赛结束":
                        return
        return currid_cnt

    def live_game(self, url):
        """ 循环文字直播比赛 """
        currid_cnt = 1
        r = requests.get(url, headers=self._headers, timeout=6).text
        title = BeautifulSoup(r, 'lxml').find('tr', class_="title bg_a").find_all('td')
        print("\n\t{} \t {}\n".format(title[0].text, title[3].text))        # 获取比赛标题信息
        table = BeautifulSoup(r, 'lxml').find('div', class_="table_list_live playbyplay_td table_overflow")

        # 比赛结束时序列是升序的，比赛中序列是降序的，匹配比赛是否结束然后选择排序方法
        # 由于直播的 tr 的 id 不按套路出牌时大时小，所以不能根据 id 大小来判断直播顺序了，要按 id 数量
        # 所以分两部分进行，第一部先一次性打印出已经存在的直播内容，第二部分循环直播接下来的内容
        if re.findall(r'team_num">(\S+)</div>', r):
            trlst = [tr for tr in reversed(table.find('table').find_all('tr'))]
            currid_cnt = self.live_order(trlst, 1, table)
        else:
            trlst = table.find('table').find_all('tr')
            self.live_order(trlst, currid_cnt, table)
            return
        while True:
            try:
                r = requests.get(url, headers=self._headers, timeout=6).text
                table = BeautifulSoup(r, 'lxml').find('div', class_="table_list_live playbyplay_td table_overflow")
                tr = list(table.find('table').find_all('tr'))
                if currid_cnt <= len(tr):
                    currid_cnt += 1
                    td = [t.text for t in table.find('tr', id=tr[0]['id']).find_all('td')]
                    if len(td) == 4:
                        gtime, gteam, gevent, gscore = td
                        if len(gteam) < 5:
                            gteam += int(5 - len(gteam)) * 2 * " "
                        print("\t{} \t {} \t {}\t{}\n".format(gtime, gscore, gteam[1:], gevent))
                    elif len(td) == 1:
                        print("", td[0], "\n")
                        if td[0] == "比赛结束":
                            return
                time.sleep(10)                       # 刷新频率
            except requests.exceptions.ConnectTimeout:
                print(">>  网络连接失败，无法获得直播数据")
            except KeyboardInterrupt:
                print(">>  您已中断直播")


def cli():
    """ 入口方法 """
    args = docopt(__doc__, version='Hupu Live 1.4')
    Hupu(**args).get_command()

if __name__ == '__main__':
    cli()
