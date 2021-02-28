# -*- coding:utf-8 -*-
"""
@version: 3.7
@time: 2021/2/19 15:20
@author: James
"""

"""
爬取66ip
"""
import requests
from lxml import etree
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from common.settings import headers
import telnetlib
import traceback
import os

# from common.config import LOGGING
# import logging.config
#
# # 日志
# logging.config.dictConfig(LOGGING)
# logger = logging.getLogger('default')

executor = ThreadPoolExecutor(max_workers=10)


# 获取ip地址
def get_proxys(url):
    # logger.info(url)
    print(url)
    rs = requests.get(url, headers=headers)
    html = rs.content.decode("gbk")
    table_html = re.search("<table.*?>[\s\S]*</table>", html)[0]
    root = etree.HTML(table_html)
    ips = root.xpath("//div[@id='main']//tr//td[1]//text()")
    ports = root.xpath("//div[@id='main']//tr//td[2]//text()")
    locations = root.xpath("//div[@id='main']//tr//td[3]//text()")
    proxy_list = []

    for ip, port, location in zip(ips[1:], ports[1:], locations[1:]):
        proxy_dict = {}
        proxy_dict["ip"] = ip
        proxy_dict["port"] = port
        proxy_dict["location"] = location
        if location.find("省") > -1 or location.find("市") > -1:
            continue
        flag = check_proxy(ip, port)
        if flag == True:
            # logger.info(proxy_dict)
            print(proxy_dict)
            proxy_list.append(proxy_dict)
            try:
                with open("./files/proxys.txt", "a+", encoding="utf-8") as f:
                    f.write("http://{ip}:{port}\n".format(ip=ip, port=port))
            except Exception as e:
                # logger.error(traceback.format_exc())
                print(traceback.format_exc())

    return proxy_list


# 检测ip
def check_proxy(ip, port):
    try:
        telnetlib.Telnet(ip, port, timeout=5)
        return True
    except Exception as e:
        return False


def get_proxy_run():
    try:
        os.remove("./files/proxys.txt")
    except Exception as e:
        pass

    urls = ["http://www.66ip.cn/{}.html".format(i) for i in range(1, 11)]
    urls.append("http://www.66ip.cn/areaindex_33/1.html")
    all_task = [executor.submit(get_proxys, (url)) for url in urls]

    # for future in as_completed(all_task):
    #     data = future.result()
    #     # logger.info("data:{}".format(data))
    #     print("data:{}".format(data))


if __name__ == '__main__':
    get_proxy_run()
