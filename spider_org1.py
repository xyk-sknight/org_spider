# Python爬取组织机构代码
# 作者: SK

import pymysql
import re
from selenium import webdriver
from lxml import etree
import time
import json
from selenium.webdriver.chrome.options import Options

'''
爬取（社会组织）地方登记所有数据
存入字段：组织名称，统一信用代码，组织类型，法人，联系电话，成立登记时间，数据记录时间

'''
def browser_ini():
    chrome_options = Options()
    chrome_options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
    chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
    chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    browser = webdriver.Chrome(chrome_options=chrome_options)
    return browser


'''打开组织信息界面'''


def org_page_open(browser, orgnum):
    '''
    分析详细信息页面数据
    :param browser: 浏览器当前页面
    :param orgnum:  检索页面组织序号，从1到20
    :return:
    '''
    org_page = browser.find_element_by_xpath('//table/tbody/tr['+str(orgnum)+']/td/a')
    org_page.click()#进入当前组织详细信息iframe页面
    browser.implicitly_wait(30)
    time.sleep(2)  # 假装看网页
    browser.switch_to.frame(0) # 切换到内嵌页面
    text= browser.page_source# 获得当前页面JS渲染后源代码
    html = etree.HTML(text)# 页面代码格式化为xpath可用形式
    for item in org_item(html):
        write_sql(item)# 调用函数写入数据库
    browser.switch_to.parent_frame()
    org_page_close = browser.find_element_by_css_selector("a[class=\"layui-layer-ico layui-layer-close layui-layer-close2\"]")
    org_page_close.click()# 关闭iframe
    time.sleep(1)


def org_item(html):
    '''
    对详细信息页面进行爬取，获得所需要的字段信息
    :param html: 格式化后的详细信息页面html代码
    :return: 爬取后的字段存入到字典并返回
    '''
    '''企业名称+信用代码'''
    name_code = html.xpath('//div/h3/text()')
    name = re.findall('(.*?)\xa0\xa0', ''.join(name_code))
    code = re.findall('：(.*$)', ''.join(name_code))
    '''组织类型'''
    type = html.xpath('//table/tbody/tr[4]/td[2]/text()')
    type = ''.join(type).split()
    '''企业地址'''
    address = html.xpath('//table/tbody/tr[5]/td[2]/text()')
    a = []
    for add in address:
        if (add.split() != []):
            a.append(''.join(add.split()))
    address = [''.join(a)]
    '''法人'''
    representative = html.xpath('//table/tbody/tr[2]/td[2]/text()')
    representative = ''.join(representative).split()
    '''电话'''
    tel = html.xpath('//table/tbody/tr[6]/td[2]/text()')
    tel = ''.join(tel).split()
    '''企业登记时间'''
    ini_time = html.xpath('//table/tbody/tr[2]/td[4]/text()')
    ini_time = ini_time[0].split()
    '''写入时间'''
    info_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    yield {
        'name': ''.join(name),
        'code': ''.join(code),
        'type': ''.join(type),
        'address': ''.join(address),
        'representative': ''.join(representative),
        'tel': ''.join(tel),
        'ini_date': ''.join(ini_time),
        'info_write_time': info_time
    }


'''写入数据库'''


def write_sql(data):
    '''
    登录MYSQL,连接至social_organization数据库,写入数据
    :param data: 单个组织的数据字典
    :return:
    '''
    db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='social_organization')
    cursor = db.cursor()
    table = 'org2'
    keys = ','.join(data.keys())
    values = ','.join(['%s'] * len(data))
    sql = 'INSERT INTO {table}({keys}) VALUE ({values})'.format(table=table, keys=keys, values=values)
    try:
        if cursor.execute(sql, tuple(data.values())):
            print("successful")
            db.commit()
    except:
        print(data)
        print('Failed')
        write_to_log(data)
        db.rollback()
    db.close()


'''查询初始化'''


def page_start(spider_num):
    '''
    多线程断点续爬
    :param spider_num: 爬虫线程编号
    :return:
    '''
    with open('page_log['+str(spider_num)+'].txt', 'r')as f:
        text = re.findall('(.*?);', f.read())
    page = int(text[-1])#开始页面
    return  page


'''跳转到开始查询的页面'''


def go_to_page(browser,page):
    time.sleep(1)
    input_goTopage = browser.find_element_by_css_selector('input[name="to_page"]')
    input_goTopage.send_keys(str(page))
    time.sleep(1)
    button_goTopage = browser.find_element_by_css_selector(
        'a[onclick="f_goto_page(searchOrgFormL, searchOrgFormL.to_page.value);"]')
    button_goTopage.click()


'''爬取进度用于初始查询页面定位'''


def write_to_file(content,spider_num):
    with open('page_log['+str(spider_num)+'].txt', 'a', encoding='utf-8') as f:
        print(type(json.dumps(content)))
        f.write(json.dumps(content, ensure_ascii=False)+';')


'''爬取失败记录'''


def write_to_log(content):
    with open('data_log.txt', 'a', encoding='utf-8') as f:
        print(type(json.dumps(content)))
        f.write(json.dumps(content, ensure_ascii=False)+'\n')


def main(page_tag,spider_num):
    browser = browser_ini()
    browser.get('http://www.chinanpo.gov.cn/search/orgindex.html')  # 打开组织查询主页面
    browser.implicitly_wait(10)  # 隐式时间等待
    '''切换到地方登记页面'''
    button_local = browser.find_element_by_css_selector('a[href="javascript:changeTab(2);"]')
    button_local.click()

    page_s = page_start(spider_num)  # 获得开始页面
    go_to_page(browser, page_s)  # 前往开始页面

    for page in range(page_tag-page_s):#目标页数-初始页数
        write_to_file(page + page_s,spider_num)  # 写入当前页数
        time.sleep(1)  # 休息一下
        '''对当前页面下20个组织进行：打开页面抓取数据后关闭'''
        for org_pageNo in range(1, 21):
            time.sleep(1)
            org_page_open(browser, org_pageNo)
            print('第', page+page_s, '页', org_pageNo)

        time.sleep(1)  # 休息一下
        button = browser.find_element_by_css_selector("a[onclick=\"f_goto_page(searchOrgFormL, 'next');\"]")  # 获取下一页按钮
        button.click()  # 点击下一页
        browser.implicitly_wait(10)  # 隐式时间等待
    browser.close()

def page_log_create():
    for spider_num in range(10):
        with open('page_log[' + str(spider_num) + '].txt', 'a', encoding='utf-8') as f:
            first_page = 10000+spider_num*1000
            f.write(json.dumps(first_page, ensure_ascii=False) + ';')


'''创建初始页面记录文件'''
page_log_create()


import threading


'''多线程数组初始化'''
threads = []
for i in range(10): #
    print('main:(',1000+i*1000,'.',i,')') #开始页面+单个线程任务量
    t = threading.Thread(target=main,args=(11000+i*1000,i))
    threads.append(t)
'''多线程开始'''
if __name__ == '__main__':
    for t in threads:
        t.setDaemon(True)
        t.start()
    t.join()
    print('finished')


