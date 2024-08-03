import os
import requests
import sys
import json
import time
import logging


# 利用REST API爬取Pull Request,传入页号
def scratch_pr(pnum, repo):
    # 请求参数
    params = (
        ('per_page', 25), ('state', 'closed'), ('page', pnum)
    )
    # 请求头
    myheaders = get_header()
    # 请求的url
    link = "https://api.github.com/repos/" + repo + "/pulls"
    response = requests.get(link, headers=myheaders, params=params)
    pulls = response.json()  # 爬取到的所有pull
    return pulls


def get_header():  # 读取本地的access token生成所需的请求头
    # 获取本地access token以扩大访问速度限制
    if not os.path.isfile('access'):
        print("please place a Github access token in this directory.")
        sys.exit()
    with open('access', 'r') as accestoken:
        access = accestoken.readline().replace("\n", "")
    # 请求头
    myheaders = {'Accept': 'application/vnd.github+json', 'Authorization': 'token ' + access}
    return myheaders


def save_to_json(pull_info, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(pull_info, f, ensure_ascii=False, indent=4)


def scratch_and_save_all_pulls(repo, total_pnum):
    logger = setup_logger(repo)
    all_pulls = []
    for pnum in range(1, total_pnum + 1):
        if pnum % 30 == 0:  # 每三十页保存一次
            save_to_json(all_pulls, f'{repo.replace("/", "_")}_all_pulls.json')
            logger.info(f'Saved page 1-' + str(pnum) + 'pulls to json file.')
        try:
            pulls = scratch_pr(pnum, repo)
        except Exception as e:
            save_to_json(all_pulls, f'{repo.replace("/", "_")}_all_pulls.json')  # 如果出现异常直接保存
            logger.exception(e)
            logger.info(f'Saved page 1-' + str(pnum) + 'pulls to json file.')
            sys.exit(-1)
        all_pulls.extend(pulls)
        logger.info(f'Added pulls from page {pnum} to list.')
        time.sleep(2)  # 休眠2秒以避免频繁请求
    save_to_json(all_pulls, f'{repo.replace("/", "_")}_all_pulls.json')
    logger.info(f'Saved all pulls to json file.')


def setup_logger(repo):
    # 创建一个logger
    logger = logging.getLogger(repo)
    logger.setLevel(logging.DEBUG)

    # 创建一个handler，用于写入日志文件
    fh = logging.FileHandler(f'{repo.replace("/", "_")}_log.log')
    fh.setLevel(logging.DEBUG)

    # 定义handler的输出格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # 给logger添加handler
    logger.addHandler(fh)

    return logger


apollo_total_pnum = 435  # pull的总页数
autoware_universe_total_pnum = 172
autoware_total_pnum = 59
repo_pnum_dic = {'ApolloAuto/apollo': apollo_total_pnum,
                 'autowarefoundation/autoware': autoware_total_pnum,
                 'autowarefoundation/autoware.universe': autoware_universe_total_pnum,}
for repo, total_pnum in repo_pnum_dic.items():
    scratch_and_save_all_pulls(repo, total_pnum)