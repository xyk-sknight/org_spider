def write_to_file(spider_record):
    with open('result.txt','a',encoding='utf-8') as f:
        print(type(spider_record))
        f.write(spider_record+'\n')