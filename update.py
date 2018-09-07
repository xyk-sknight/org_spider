#coding:UTF-8
import pymysql
import re
from selenium import webdriver
from lxml import etree
import time
import json
from selenium.webdriver.chrome.options import Options
import math


def browser_ini():
    chrome_options = Options()
    chrome_options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
    chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
    chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    #chrome_options.add_argument('--headless')  # 浏览器无窗口化
    browser = webdriver.Chrome(chrome_options=chrome_options)
    return browser


'''打开组织信息界面'''


def org_page_open(browser, orgnum):
    org_page = browser.find_element_by_xpath('//table/tbody/tr['+str(orgnum)+']/td/a')
    org_page.click()
    browser.implicitly_wait(30)
    time.sleep(2)  # 假装看网页
    browser.switch_to.frame(0)
    text= browser.page_source
    html = etree.HTML(text)
    '''分析页面数据'''
    for item in org_item(html):
        write_sql(item)#写入数据库
        write_to_log(item['name']+';'+item['info_write_time'])#写入日志
    browser.switch_to.parent_frame()
    org_page_close = browser.find_element_by_css_selector("a[class=\"layui-layer-ico layui-layer-close layui-layer-close2\"]")
    org_page_close.click()
    time.sleep(1)


def org_item(html):
    ''''''
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
    tel = tel[0].split()
    '''企业登记时间'''
    ini_time = html.xpath('//table/tbody/tr[2]/td[4]/text()')
    ini_time = ini_time[0].split()
    '''写入时间'''
    info_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    #print(info_time)
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
    '''登录MYSQL,连接至social_organization数据库'''
    db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='social_organization')
    cursor = db.cursor()
    table = 'org2'
    keys = ','.join(data.keys())
    values = ','.join(['%s'] * len(data))
    sql = 'INSERT INTO {table}({keys}) VALUE ({values})'.format(table=table, keys=keys, values=values)
    try:
        if cursor.execute(sql, tuple(data.values())):
            print(data)
            print("successful")
            db.commit()
    except:
        print(data)
        print('已存在')
        db.rollback()
    db.close()


'''查询数据库中最新数据的登记日期'''
def finial_date_get():
    '''登录MYSQL,连接至social_organization数据库'''
    db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='social_organization')
    cursor = db.cursor()
    sql = "SELECT ini_date FROM social_organization.org2 WHERE ini_date<>'' ORDER BY ini_date DESC LIMIT 1"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        result = cursor.fetchone()
        return result[0]
    except:
        pass
    db.close()




'''用于初始查询页面定位'''


def write_to_file(content):
    with open('page_log.txt', 'a', encoding='utf-8') as f:
        print(type(json.dumps(content)))
        f.write(json.dumps(content, ensure_ascii=False)+';')


'''爬取记录'''


def write_to_log(content):
    with open('update_log.txt', 'a', encoding='utf-8') as f:
        print(type(json.dumps(content)))
        f.write(json.dumps(content, ensure_ascii=False)+'\n')


def main():
    browser = browser_ini()
    '''初始化'''
    browser.get('http://www.chinanpo.gov.cn/search/orgindex.html')  # 打开组织查询主页面
    browser.implicitly_wait(10)  # 隐式时间等待
    time.sleep(1)
    update_post(browser)
    '''切换到地方登记页面'''
    button_local = browser.find_element_by_css_selector('a[href="javascript:changeTab(2);"]')
    button_local.click()
    data_num_total = totalnum(browser)
    dnt = int(data_num_total)
    data_num = 0
    page_num = int(math.ceil(data_num_total/20))
    for page in range(page_num):
        time.sleep(1)  # 休息一下
        '''对当前页面下20个组织进行：打开页面抓取数据后关闭'''
        for org_pageNo in range(1, 21):
            time.sleep(1)
            org_page_open(browser, org_pageNo)
            data_num += 1
            if data_num == dnt:
                break

        time.sleep(1)  # 休息一下
        button = browser.find_element_by_css_selector("a[onclick=\"f_goto_page(searchOrgFormL, 'next');\"]")  # 获取下一页按钮
        button.click()  # 点击下一页
        browser.implicitly_wait(10)  # 隐式时间等待
    print('从'+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'到')
    print ('finial_date_get()')
    print('更新完成，共更新'+str(dnt)+'条数据')
    browser.close()

def update_post(browser):
    regdate = browser.find_element_by_xpath('/html/body/center/div/div[2]/div/form/div[5]/div/div[2]/input[1]')
    regdate.send_keys(finial_date_get()) #查询开始日期
    regdateEnd = browser.find_element_by_xpath('//html/body/center/div/div[2]/div/form/div[5]/div/div[2]/input[2]')
    regdateEnd.send_keys(time.strftime('%Y-%m-%d',time.localtime(time.time()))) #当前日期
    form_post = browser.find_element_by_xpath('//*[@id="img_qg"]')
    form_post.click()

def totalnum(browser):
    mzb = int(browser.find_element_by_xpath('/html/body/center/div/div[2]/div/div[1]/span[1]/font[2]/b').text)
    total = int(browser.find_element_by_xpath('/html/body/center/div/div[2]/div/div[1]/span[1]/font[1]/b').text)
    return total-mzb

main()
