# -*- coding:utf-8 -*-
"""
@version: 3.7
@time: 2021/2/19 15:20
@author: James
"""
"""
根据item获取商品（模拟浏览器，比较慢）
"""
import time
from lxml import etree
from pprint import pprint
import urllib3
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

executor = ThreadPoolExecutor(max_workers=10)

urllib3.disable_warnings()
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)


# driver = webdriver.PhantomJS()

def get_item_infos(item):
    return_value = {}
    try:
        # url = "https://www.amazon.com/dp/%s?language=zh_CN" % item
        url = "https://www.amazon.com/dp/%s?language=en_US" % item
        print(url)

        driver.get(url)
        page_source = driver.page_source
        root = etree.HTML(page_source)

        titles = root.xpath("//span[@id='productTitle']//text()")
        solds = root.xpath("//a[@id='sellerProfileTriggerId']//text()")
        star_levels = root.xpath("//span[@class='a-icon-alt']//text()")
        comments = root.xpath("//span[@id='acrCustomerReviewText']//text()")

        # 图片
        img_list = list(eval(re.search("main.*?}", re.search("colorImages.*?},", page_source)[0])[0][6:]).keys())
        return_value["imgs"] = img_list

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
        print("结果:")
        pprint(return_value)

    except Exception as e:
        pass
    finally:
        return return_value


def selenium_item_infos_run():
    t1 = time.time()
    items = ["B07FCMKK5X", "B08R2WG4D4", "B08GYKNCCP"]
    all_task = [executor.submit(get_item_infos, (item)) for item in items]

    for future in as_completed(all_task):
        data = future.result()
        print("data:{}".format(data))

    # for item in items:
    #     get_item_infos(item)
    try:
        driver.close()
    except Exception as e:
        pass

    print(time.time() - t1)


if __name__ == '__main__':
    selenium_item_infos_run()
