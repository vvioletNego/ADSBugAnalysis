import logging
import os
import sys
import time
from datetime import datetime
import pandas as pd
import requests
import json
import re
#  通过GIT API爬取每个补丁对应的修改文件路径以及修改行数等信息，按照模块名进行分类

def read_access():
    if not os.path.isfile('../access'):
        print("please place a Github access token in this directory.")
        sys.exit()

    with open('../access', 'r') as accestoken:
        access = accestoken.readline().replace("\n", "")
    return access


myheaders = {'Accept': 'application/vnd.github+json', 'Authorization': 'Token ' + read_access()}


def process_url(url):
    if 'pull' not in url:  # 如果不是pull直接返回None
        return None
    # 修改URL格式
    new_url = url.replace('https://github.com/', 'https://api.github.com/repos/')
    new_url = new_url.replace('/pull/', '/pulls/')
    print(new_url)

    try:
        # 通过GIT API访问这个修改后的url
        response = requests.get(new_url, headers=myheaders)
        response.raise_for_status()

        # 记录日志
        logging.info(f'Accessed URL: {new_url} at {datetime.now()}')

        # 得到的结果是一个json文件
        json_data = response.json()

        # 访问字典中的 "commits", "additions", "deletions", "changed_files"
        commits = json_data['commits']
        additions = json_data['additions']
        deletions = json_data['deletions']
        changed_files = json_data['changed_files']

        # 访问 "diff_url"中的diff_url对应的url
        diff_url = json_data['diff_url']
        while True:
            try:
                diff_response = requests.get(diff_url, headers=myheaders)
                diff_response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                # 记录异常
                logging.error(f'Exception occurred: {e} at {datetime.now()}')

                # 停止3秒重新访问没有访问成功的url
                time.sleep(3)

        # 得到的结果是一个diff文件
        diff_text = diff_response.text

        import os

        file_changes = re.findall(r'diff --git a/(.*?) b/(.*?)\n(.*?)(?=diff --git a/|\Z)', diff_text, re.DOTALL)
        module_changes = {}
        for a, b, c in file_changes:
            # 提取模块名
            if 'modules/' in a:
                module_name = a.split('modules/')[1].split('/')[0]
            elif 'ros/src/' in a:
                module_name = a.split('ros/src/')[1].split('/')[0]
            else:
                path_parts = a.split('/')
                if len(path_parts) > 1:
                    module_name = path_parts[0]
                else:
                    module_name = os.path.splitext(a)[0]

            # 计算修改的行数
            changes = re.findall(r'^(\+|-)', c, re.MULTILINE)
            changes_count = len(changes)

            # 更新模块的修改行数
            if module_name in module_changes:
                module_changes[module_name]['changes'] += changes_count
                module_changes[module_name]['filename'].append({a: changes_count})
            else:
                module_changes[module_name] = {'module_name': module_name, 'filename': [{a: changes_count}],
                                               'changes': changes_count}


        # 将访问的url， "commits", "additions", "deletions", "changed_files"以及解析diff得到的字典数组保存为一个字典
        result_dict = {
            'url': url,
            'commits': commits,
            'additions': additions,
            'deletions': deletions,
            'changed_files': changed_files,
            'file_changes': module_changes
        }

        return result_dict

    except requests.exceptions.RequestException as e:
        # 记录异常
        logging.error(f'Exception occurred: {e} at {datetime.now()}')

        # 停止3秒重新访问没有访问成功的url
        time.sleep(3)

        # 返回None表示处理失败
        return None


# 读取目录下的所有Excel文件
directory = input("Input path of excel files you want to process:")
for filename in os.listdir(directory):
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        # 设置日志文件的名称为Excel文件的名称
        log_filename = f'{filename}_app.log'
        logging.basicConfig(filename=log_filename, filemode='w', format='%(name)s - %(levelname)s - %(message)s')

        # 读取Excel文件的第一列
        df = pd.read_excel(os.path.join(directory, filename))
        urls = df.iloc[:, 0].tolist()  # 第一列的所有内容，不包括表头

        result_list = []
        failed_urls = []
        for url in urls:
            result_dict = process_url(url)
            time.sleep(1)
            if result_dict is not None:
                result_list.append(result_dict)
            else:
                failed_urls.append(url)
                # 遇到异常保存，避免丢失结果
                with open(f'{filename}.json', 'w') as f:
                    json.dump(result_list, f)
                # 保存所有访问失败的URL
                with open(f'{filename}_failed_urls.json', 'w') as f:
                    json.dump(failed_urls, f)
        # 保存
        # 把整个excel文件中的所有url做这样的操作以后得到一个字典数组。以excel文件名为参考保存为一个json文件
        with open(f'{filename}.json', 'w') as f:
            json.dump(result_list, f)
        # 保存所有访问失败的URL
        with open(f'{filename}_failed_urls.json', 'w') as f:
            json.dump(failed_urls, f)
