import time

import yaml, logging, requests
from bs4 import BeautifulSoup
from multiprocessing import Pool

from xmissy import common

# 全局变量
headers = {
    'Accept': "application/json, text/javascript, */*, q=0.01",
    'Accept-Encoding': "gzip, deflate, br",
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}


# 列表页
def get_list(uri):
    try:
        res = requests.get(uri, headers=headers, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 获取列表页的规则
        lis = soup.select(config["list_rule"])
        i = 0
        for li in lis:
            i = i + 1
            logging.info("proceed is %d and total is %d." % (i, len(lis)))
            # 获取列表页中详情页的链接
            a_tag = li.select(config["list_a_rule"])
            uri = a_tag[0].attrs["href"]
            if config["domain"] in uri:
                # 获取详情页
                logging.info(uri)
                more_detail(uri)
            time.sleep(1)
    except requests.exceptions.RequestException as e:
        logging.error(e)


# 详情页
def more_detail(url):
    arr = str.split(url, "/")
    new_arr = [x for x in arr if x != '']
    # 去掉空字符串
    folder_name = new_arr[-1]
    logging.info(folder_name)
    path = common.mk_dir(folder_name)
    try:
        res = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')
        lis = soup.select(config["detail_rule"])
        p = Pool(8)
        for li in lis:
            a_tag = li.select(config["detail_a_rule"])
            link = a_tag[0].attrs["href"]
            if "data-srcset" in a_tag[0]:
                pic_arr = a_tag[0].attrs["data-srcset"].split(" ")
                link = pic_arr[0]
            logging.info(link)
            p.apply_async(common.download_pic, args=(link, path))
        p.close()
        p.join()
    except requests.exceptions.RequestException as e:
        logging.error(e)


if __name__ == "__main__":
    # 设置日志等级
    logging.basicConfig(level=logging.INFO)
    # 加载配置
    with open("config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    # 读取列表
    get_list(config["host"])
    logging.info("done")
