import pymysql
import re
import json
from selenium import webdriver







#解析网页
def parse_one_page(html):
    pattern = re.compile('<tr height="32">'
    					 '.*?"middle">(.*?)</td>'
                         '.*?<a href=".*?">(.*?)</a>'
                         '.*?<a href=".*?">(.*?)</a>'
                         '.*?</tr>',re.S)
    items = re.findall(pattern, html)
    print(items)
    for item in items:
        yield {
            'id':item[0].strip().strip('&nbsp;'),     #序号
            'name':item[1].strip().strip('&nbsp;'),   #组织名称
            'code':item[2].strip().strip('&nbsp;'),   #组织代码
        }


#写入到result.txt中
def write_to_file(content):
    with open('result.txt','a',encoding='utf-8') as f:
        print(type(json.dumps(content)))
        f.write(json.dumps(content,ensure_ascii=False)+'\n')
def write_sql(data):
    '''登录MYSQL,连接至social_organization数据库'''
    db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='social_organization')
    cursor = db.cursor()

    print(data)
    table = 'org'
    keys = ','.join(data.keys())
    values = ','.join(['%s'] * len(data))
    sql = 'INSERT INTO {table}({keys}) VALUE ({values})'.format(table=table, keys=keys, values=values)
    try:
        if cursor.execute(sql, tuple(data.values())):
            print("successful")
            db.commit()
    except:
        print('Failed')
        db.rollback()
    db.close()

def main():
    browser = webdriver.Chrome()
    browser.implicitly_wait(10)#隐式时间等待
    browser.get('http://www.chinanpo.gov.cn/search/orgcx.html')

    for i in range(1):
        html = browser.page_source
        for item in parse_one_page(html):
            write_sql(item)


        button = browser.find_element_by_css_selector("a[onclick=\"f_goto_page(searchOrgFormM, 'next');\"]")
        button.click()
        browser.implicitly_wait(10)  # 隐式时间等待
main()





