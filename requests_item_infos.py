# -*- coding:utf-8 -*-
"""
@version: 3.7
@time: 2021/2/19 15:20
@author: James
"""
"""
根据item获取商品
(中国站点 cn)只能是中文（中国ip）
(国外站点 com)可以是中文也可以说英文（国外ip）翻墙
根据IP地址进行反爬
"""
import requests
from lxml import etree
from pprint import pprint
import urllib3
from functools import wraps
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import random
from common.settings import headers as headers_
# from common.config import pool
import pymysql

headers = headers_
executor = ThreadPoolExecutor(max_workers=10)

urllib3.disable_warnings()

# base_url = "https://www.amazon.cn"
base_url = "https://www.amazon.com"


# 装饰器（用于计算时间）
def decorator_time(fun):
    @wraps(fun)
    def decorated(*args, **kwargs):
        t1 = time.time()
        result = fun(*args, **kwargs)
        print("运行时间:%s" % (time.time() - t1))
        return result

    return decorated


@decorator_time
def get_cookies():
    # 获取cookies
    rs = requests.get(base_url, headers=headers)
    cookies = dict(rs.cookies)
    print("cookies:%s" % cookies)
    return cookies


# 不是必须的,只是需要cookies这个字段
cookies = ""
cookies_ = get_cookies()
for ck, cv in cookies_.items():
    cookies = cookies + ck + "=" + cv + ";"

headers["cookies"] = cookies
print(headers)


@decorator_time
def get_item_infos(item, proxie):
    time.sleep(0.5)
    return_value = {}
    try:
        return_value["item"] = item
        if base_url.split(".")[-1] == 'cn':
            # .cn
            url = base_url + "/dp/{}".format(item)
        else:
            # .com
            url = base_url + "/dp/{}?language=en_US".format(item)
            # url = base_url+"/dp/{}?language=zh_CN".format(item)

        print("url:%s" % url)
        rs = requests.get(url=url, headers=headers, verify=False, proxies=proxie, timeout=5)
        html = rs.text
        root = etree.HTML(html)

        titles = root.xpath("//span[@id='productTitle']//text()")
        solds = root.xpath("//a[@id='sellerProfileTriggerId']//text()")
        star_levels = root.xpath("//span[@class='a-icon-alt']//text()")
        comments = root.xpath("//span[@id='acrCustomerReviewText']//text()")

        # 图片
        try:
            img_list = list(eval(re.search("main.*?}", re.search("colorImages.*?},", html)[0])[0][6:]).keys())
            return_value["imgs"] = img_list
        except Exception as e:
            pass

        # 标题
        title = ""
        if len(titles) > 0:
            title = "".join(titles)
            title = title.strip()
        return_value["title"] = title

        # 价格
        price = ""
        prices1 = root.xpath("//span[@id='price_inside_buybox']//text()")
        prices2 = root.xpath("//span[contains(@id, 'priceblock')]//text()")
        if len(prices1) > 0:
            price = prices1[0].strip().split('$')[-1].replace(",", "").strip()
        if price == "" and len(prices2) > 0:
            price = prices2[0].strip().split('$')[-1].replace(",", "").strip()
        return_value["price"] = price

        # 店铺
        sold = ""
        if len(solds) > 0:
            sold = solds[0].strip()
        return_value["sold"] = sold

        # 星级
        star_level = 0
        if len(star_levels) > 0:
            star_level = star_levels[0].split(" ")[0].strip()
        return_value["star_level"] = star_level

        # 评论
        comment = ""
        if len(comments) > 0:
            comment = comments[0].split(" ")[0].replace(",", "").strip()
        return_value["comment"] = comment

        # 排名
        real_rank = {}
        try:
            for i in range(50):
                rank = "".join(
                    root.xpath("//table[@id='productDetails_detailBullets_sections1']//tr[%s]//td//text()" % i))
                if rank == "":
                    continue
                if rank.strip().find("商品里排第") > -1:
                    for r in rank.split("\n"):
                        if r != "":
                            k = r.split("名")[-1].split("(")[0].strip()
                            v = r.split("第")[-1].split("名")[0].replace(",", "").strip()
                            real_rank[k] = v
                if rank.strip().find("#") > -1 and rank.strip()[0] == "#":
                    for r in rank.split("\n"):
                        if r != "":
                            k = r.split(" in ")[1].split("(")[0].strip()
                            v = r.split("#")[-1].split(" in ")[0].replace(",", "").strip()
                            real_rank[k] = v

        except Exception as e:
            pass

        if real_rank == "":
            try:
                rank = "".join(root.xpath("//li[@id='SalesRank']//text()"))
                if rank.strip().find("商品里排第") > -1:
                    for r in rank.split("\n"):
                        if r != "":
                            k = r.split("名")[-1].split("(")[0].strip()
                            v = r.split("第")[-1].split("名")[0].replace(",", "").strip()
                            real_rank[k] = v
                if rank.strip().find("#") > -1 and rank.strip()[0] == "#":
                    for r in rank.split("\n"):
                        if r != "":
                            k = r.split(" in ")[1].split("(")[0].strip()
                            v = r.split("#")[-1].split(" in ")[0].replace(",", "").strip()
                            real_rank[k] = v
            except Exception as e:
                pass
        return_value["rank"] = real_rank
        return_value["item"] = item

    except Exception as e:
        pass
    finally:
        pprint(return_value)
        return return_value


def requests_item_infos_run():
    t1 = time.time()
    # 获取代理
    with open("./files/proxys.txt", "r", encoding="utf-8") as f:
        proxy_list = f.readlines()
    if len(proxy_list) == 0:
        proxie = {}
    else:
        proxie = {"http": random.choice(proxy_list).strip()}

    # db = pool.connection()
    # cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    # sql = "SELECT item FROM ..."
    # cursor.execute(sql)
    # results = cursor.fetchall()
    # items = list(map(lambda x:x["item"],results))

    items = ["B07FCMKK5X", "B08R2WG4D4", "B08GYKNCCP"]
    # get_item_infos(items[0], proxie)

    proxies = [proxie] * len(items)
    all_task = [executor.submit(get_item_infos, item, proxie) for item, proxie in zip(items, proxies)]

    for future in as_completed(all_task):
        data = future.result()
        # logger.info("data:{}".format(data))
        print("data:{}".format(data))

    print(time.time() - t1)


if __name__ == '__main__':
    requests_item_infos_run()