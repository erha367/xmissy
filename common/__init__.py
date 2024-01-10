import os, requests, logging


# 检测目录
def mk_dir(name):
    current = os.getcwd()
    path = current + os.path.sep + name
    if not os.path.exists(path):
        os.makedirs(name, 0o777)
    return path


# 下载单个图片
def download_pic(url, path):
    # 获取文件名
    arr = str.split(url, "/")
    file_name = arr[-1]
    try:
        res = requests.get(url, timeout=30)
        img = res.content
        loc_file = path + os.path.sep + file_name
        logging.info(loc_file)
        with open(loc_file, 'wb') as f:
            f.write(img)
    except requests.exceptions.RequestException as e:
        logging.error(e)
