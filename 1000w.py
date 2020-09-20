# coding=utf-8
import requests, json
from os import system
system("title 白金彩票-另类分析工具")

# 白金彩票-双色球分析工具-v1.0
# author Hermit_xx
# Email: medivh_yx@qq.com

# 此处输入聚合数据的app_key
app_key = ''


def save(s):
    f = open('data\\history.txt', 'w')
    f.write(s)
    f.close()


def update(key):
    url = 'http://apis.juhe.cn/lottery/history'
    para = {'key': app_key,
            'lottery_id': 'ssq',
            'page_size': '50',
            }
    all_list = []
    # 取第一页
    r = requests.get(url, params=para)
    # print('HTTP状态码:', r.status_code)
    # print('返回内容:',r.text)
    res = json.loads(r.text)
    if (str(res['error_code']) != '0'):
        print('出现异常，错误码：', res['error_code'])
        return False
    print('总页数:', res['result']['totalPage'])
    total_page = int(res['result']['totalPage']) + 1

    # 遍历内容
    for item in res['result']['lotteryResList']:
        number = item['lottery_res'].split(',')
        save_item = {'no': item['lottery_no'],
                     'red': number[0:6],
                     'blue': number[-1]
                     }
        all_list.append(save_item)

    f = open('data\\part\\1.txt', 'w')
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
            save_item = {'no': item['lottery_no'],
                         'red': number[0:6],
                         'blue': number[-1]
                         }
            part_list.append(save_item)
            all_list.append(save_item)

        f = open('data\\part\\' + str(index) + '.txt', 'w')
        f.write(json.dumps(part_list))
        f.close()

    save(json.dumps(all_list))
    print('更新完成！')


def moneyConvert(s):
    if s == '6+1':
        return '一等奖'
    elif s == '6+0':
        return '二等奖'
    elif s == '5+1':
        return '三等奖'
    elif s in ('5+0', '4+1'):
        return '四等奖'
    elif s in ('4+0', '3+1'):
        return '五等奖'


def find():

    no = input('输入号码，先输入红球，红球大小无需排序，最后输入蓝球，每个数字之间用空格分隔。\n输入举例 01 02 03 04 15 19 16\n')
    arr = no.split(' ')
    if (len(arr[:-1]) != 6):
        print('输入有误，重新输入。\n')
        return False
    else:
        print('红球：', arr[:-1], '蓝球：', arr[-1])

    custom_red = arr[:-1]
    custom_blue = arr[-1]

    global data_arr

    max_count = 0

    max_list = []

    # 利用三重积分、曲面积分、离散傅里叶级数公式构造核心算法
    for item in data_arr:
        red = len(set(custom_red).intersection(set(item['red'])))
        if custom_blue == item['blue']:
            blue = 1
        else:
            blue = 0
        if red + blue <= 3:
            continue
        count = red + blue
        if count > max_count:
            max_count = count
            item['get'] = str(red) + '+' + str(blue)
            max_list = [item, ]
        elif count == max_count:
            item['get'] = str(red) + '+' + str(blue)
            max_list.append(item)

    if max_count == 0:
        print('该注号码在历史中奖记录中没有大于 3 个号码相符的情况。')
    else:
        print('该注号码在历史中奖记录中最多有', max_count, '个号码正确！')
        print('测试号码：' + ' '.join(custom_red) + '-' + custom_blue)
        print('最高奖中奖次数：', len(max_list))
        for item in max_list:
            print('期数：', item['no'], '中奖号码：', ' '.join(item['red'])
                  + '-' + item['blue'], '符合条件：', item['get'],
                  '奖级：', moneyConvert(item['get']))


def cal(limit=100):
    if(limit == ''):
        limit = 100
    else:
        limit = int(limit)
    f = open('data\\history.txt', 'r')
    json_str = f.read()
    data_arr = json.loads(json_str)
    red_stat = {}
    blue_stat = {}
    first_no = ''
    last_no = ''
    for i in range(1, 34):
        red_stat[str(i)] = 0
    for i in range(1, 17):
        blue_stat[str(i)] = 0
    index = 0
    for item in data_arr:
        if index == 0:
            first_no = item['no']
        for red_ball in item['red']:
            red_stat[str(int(red_ball))] += 1
        blue_stat[str(int(item['blue']))] += 1
        index += 1
        if index > limit:
            last_no = item['no']
            break
    print('开始期数：', first_no)
    print('结束期数：', last_no)

    red_stat = sorted(red_stat.items(), key=lambda item: item[1])
    blue_stat = sorted(blue_stat.items(), key=lambda item: item[1])
    # print('红球统计结果：', red_stat)
    # print('蓝球统计结果：', blue_stat)
    print('最近', limit, '期红球出现次数统计(由多到少排序)')
    for i in range(1, 34):
        print(red_stat[i * -1][0], ':出现', red_stat[i * -1][1], '次')

    print('最近', limit, '期蓝球出现次数统计(由多到少排序)')
    for i in range(1, 17):
        print(blue_stat[i * -1][0], ':出现', blue_stat[i * -1][1], '次')

def loadData():
    global data_arr
    f = open('data\\history.txt', 'r')
    json_str = f.read()
    data_arr = json.loads(json_str)
    print('当前数据库最新双色球期数为：', data_arr[1]['no'])

if __name__ == '__main__':

    loadData()

    while True:
        mode = input('======Link Start!======\n请输入功能序号\n1、辉煌历史：某注号码历史记录中最高奖\n2、硬核分析：分析最近n期每个号码出现的次数\n'
                     '3、更新数据（需要有聚合数据的app_key）\n')
        if(mode == '1'):
            find()
        elif(mode == '2'):
            mode = input('请输入期数范围，输入50表示统计最近50期号码。\n不输入默认为100期。')
            cal(mode)
        elif(mode == '3'):
            key = input(app_key)
            update(app_key)
            loadData()

