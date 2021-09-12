# coding=utf-8
import os

import requests, json
from os import system

system("title 白金之星-大乐透另类分析工具-v1.1")

# 白金之星-双色球分析工具-v1.0
# author Hermit_xx
# Email: medivh_yx@qq.com

# 此处输入聚合数据的app_key
app_key = ''


def save(s):
    f = open('data\\dlt\\history.txt', 'w')
    f.write(s)
    f.close()


def update(app_key):
    url = 'http://apis.juhe.cn/lottery/history'
    para = {'key': app_key,
            'lottery_id': 'dlt',
            'page_size': '50',
            }
    all_list = []
    print(para)
    # 取第一页
    r = requests.get(url, params=para)
    print('HTTP状态码:', r.status_code)
    print('返回内容:', r.text)
    res = json.loads(r.text)
    if (str(res['error_code']) != '0'):
        print('出现异常，错误码：', res['error_code'])
        return False
    print('总页数:', res['result']['totalPage'])
    total_page = int(res['result']['totalPage']) + 1

    # 遍历内容
    for item in res['result']['lotteryResList']:
        number = item['lottery_res'].split(',')
        save_item = {'n': item['lottery_no'],
                     'f': number[0:5],
                     'b': number[-2:]
                     }
        all_list.append(save_item)

    if not os.path.isdir('data\\dlt\\part'):
        print('数据目录不存在，自动创建')
        os.makedirs('data\\dlt\\part')

    f = open('data\\dlt\\part\\1.txt', 'w')
    f.write(json.dumps(all_list))
    f.close()

    # 遍历2+页
    for index in range(2, total_page):
        part_list = []
        print('正在爬取第', str(index), '页')
        para['page'] = index
        r = requests.get(url, params=para)
        res = json.loads(r.text)
        if (str(res['error_code']) != '0'):
            print('出现异常，错误码：', res['error_code'])
            return False

        res = json.loads(r.text)

        # 遍历内容
        for item in res['result']['lotteryResList']:
            number = item['lottery_res'].split(',')
            save_item = {'n': item['lottery_no'],
                         'f': number[0:5],
                         'b': number[-2:]
                         }
            part_list.append(save_item)
            all_list.append(save_item)

        f = open('data\\dlt\\part\\' + str(index) + '.txt', 'w')
        f.write(json.dumps(part_list))
        f.close()

    save(json.dumps(all_list))
    print('更新完成！')


def getPrize(s):
    if s == '5+2':
        return 1
    elif s == '5+1':
        return 2
    elif s == '5+0':
        return 3
    elif s == '4+2':
        return 4
    elif s == '4+1':
        return 5
    elif s == '3+2':
        return 6
    elif s == '4+0':
        return 7
    elif s in ('3+1', '2+2'):
        return 8
    elif s in ('3+0', '1+2', '2+1', '2+0'):
        return 9
    else:
        return 100


def find():
    while True:
        no = input('====================\n'
                   '输入号码，先输入5个前区，后输入2个后区，无需排序，每个数字之间用空格分隔。\n'
                   '输入举例 01 02 03 04 15 19 16\n'
                   '直接输入回车返回菜单\n')
        if no == '':
            return True
        arr = no.split(' ')
        if (len(arr) != 7):
            print('输入有误，重新输入。\n')
            return False
        else:
            print('测试号码 前区：', arr[:-2], '后区：', arr[-2:])

        custom_front = arr[:-2]
        custom_back = arr[-2:]

        global data_arr

        max_prize = 100
        max_list = []

        # 利用三重积分、曲面积分、离散傅里叶级数公式构造核心算法
        for item in data_arr:
            red = len(set(custom_front).intersection(set(item['f'])))
            blue = len(set(custom_back).intersection(set(item['b'])))

            if red + blue <= 1:
                continue

            raw_prize = str(red) + '+' + str(blue)
            prize = getPrize(raw_prize)

            if prize < max_prize:
                max_prize = prize
                # 符合条件
                item['get'] = raw_prize
                max_list = [item, ]
            elif prize == max_prize:
                # 符合条件
                item['get'] = raw_prize
                max_list.append(item)

        if max_prize == 0:
            print('该注号码在历史未中奖。（这是不可能的，如果出现了，请提issue）')
        else:
            print('该注号码历史最高 ', str(max_prize), '等奖！')
            print('最高奖中奖次数：', len(max_list))
            for item in max_list:
                print('期数：', item['n'], '中奖号码：', ' '.join(item['f'])
                      + '-' + ' '.join(item['b']), '符合条件：', item['get'])


def cal(limit=100):
    if (limit == ''):
        limit = 100
    else:
        limit = int(limit)
    f = open('data\\dlt\\history.txt', 'r')
    json_str = f.read()
    data_arr = json.loads(json_str)
    red_stat = {}
    blue_stat = {}
    first_no = ''
    last_no = ''
    for i in range(1, 36):
        red_stat[str(i)] = 0
    for i in range(1, 13):
        blue_stat[str(i)] = 0
    index = 0
    for item in data_arr:
        if index == 0:
            first_no = item['n']
        for red_ball in item['f']:
            red_stat[str(int(red_ball))] += 1
        for back_ball in item['b']:
            blue_stat[str(int(back_ball))] += 1
        index += 1
        if index > limit:
            last_no = item['n']
            break
    print('开始期数：', first_no)
    print('结束期数：', last_no)

    red_stat = sorted(red_stat.items(), key=lambda item: item[1])
    blue_stat = sorted(blue_stat.items(), key=lambda item: item[1])
    # print('红球统计结果：', red_stat)
    # print('蓝球统计结果：', blue_stat)
    print('最近', limit, '期前区出现次数统计(由多到少排序)')
    for i in range(1, 36):
        print(red_stat[i * -1][0], ':出现', red_stat[i * -1][1], '次')

    print('最近', limit, '期后区出现次数统计(由多到少排序)')
    for i in range(1, 13):
        print(blue_stat[i * -1][0], ':出现', blue_stat[i * -1][1], '次')


def loadData():
    global data_arr
    f = open('data\\dlt\\history.txt', 'r')
    json_str = f.read()
    data_arr = json.loads(json_str)
    print('当前数据库最新期数为：', data_arr[1]['n'])


if __name__ == '__main__':
    try:
        loadData()
    except FileNotFoundError:
        print('\033[31m未找到数据库，请先更新数据\033[0m')

    while True:
        mode = input('======Link Start!======\n'
                     'By Hermit_小新\n'
                     '请输入功能序号\n'
                     '1、辉煌历史：某注号码历史记录中最高奖\n'
                     '2、硬核分析：分析最近n期每个号码出现的次数\n'
                     '3、更新数据（需要有聚合数据的app_key）\n')
        if (mode == '1'):
            find()
        elif (mode == '2'):
            mode = input('请输入期数范围，输入50表示统计最近50期号码。\n不输入默认为100期。')
            cal(mode)
        elif (mode == '3'):
            key = input('输入聚合数据彩票接口的app_key')
            update(key)
            loadData()
