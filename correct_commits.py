# 修正commit的数量，去掉merge的commit
import os
import sys
import time

import pandas as pd
import requests


# 获取GITHUB的Token
def read_access():
    if not os.path.isfile('access'):
        print("please place a Github access token in this directory.")
        sys.exit()

    with open('access', 'r') as accestoken:
        access = accestoken.readline().replace("\n", "")
    return access


def get_sha(url):
    # 使用GIT API获取PR中所有的commit的SHA
    data = []
    try:
        url = url.replace('https://github.com/', 'https://api.github.com/repos/').replace('/pull/', '/pulls/')
        myheaders = {'Accept': 'application/vnd.github+json', 'Authorization': 'Token ' + read_access()}
        response = requests.get(url, headers=myheaders)
        response.raise_for_status()
        url += "/commits"
        response = requests.get(url, headers=myheaders)
        response.raise_for_status()
        for item in response.json():
            if 'Merge'.lower() not in item['commit']['message'].lower():
                data.append(item['commit']['message'])

        # print(data)
        time.sleep(1)
        return len(data)
    except Exception as e:
        print(f"Error when accessing {url}: {e}")
        return None


def process_excel(path):
    df = pd.read_excel(path)
    df['commits_no_merge'] = 0  # 添加新的列
    try:
        for index, row in df.iterrows():
            url = row['html_url']
            commits_count = get_sha(url)
            if commits_count is not None:
                df.at[index, 'commits_no_merge'] = commits_count  # 更新列的值
        df.to_excel(path, index=False)  # 将结果保存回Excel文件
    except Exception as e:
        print(f"{e}")
        df.to_excel(path, index=False)  # 将结果保存回Excel文件


def process_directory(directory):
    # 遍历目录下的所有excel文件
    for filename in os.listdir(directory):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            path = os.path.join(directory, filename)
            process_excel(path)


if __name__ == "__main__":
    path = input("Input excel path of pull request you want to process:")
    process_directory(path)