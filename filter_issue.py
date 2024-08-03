import os
import json
import requests
import time
import re

# 指定json文件夹的路径
directory = input("Input path of all json files you want to process:")

# 遍历目录中的所有文件
for filename in os.listdir(directory):
    if filename.endswith(".json"):
        file_path = os.path.join(directory, filename)

        # 读取json文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 筛选出不包含'pull_request'键的json，并且评论数大于0的issue
        filtered_data = [item for item in data if 'pull_request' not in item and item['comments'] > 0]

        # 筛选出不包含'how to'的字典
        filtered_data = [d for d in filtered_data if 'how to' not in d['title'].lower()]

        result = {}

        # 遍历筛选后的json数据
        for item in filtered_data:
            html_url = item['html_url']
            timeline_url = item['timeline_url']
            print(f'正在对{html_url}进行筛选')

            # 发送GET请求，获取timeline_url对应的数据
            response = requests.get(timeline_url)

            # 检查请求是否成功
            if response.status_code == 200:
                timeline_data = response.json()

                # 遍历timeline_data，找到event为'cross-referenced'或'commented'的项
                for event in timeline_data:
                    if event['event'] == 'cross-referenced':
                        source = event['source']

                        # 将source添加到结果中
                        if html_url not in result:
                            result[html_url] = []
                        result[html_url].append(source)
                    elif event['event'] == 'commented':
                        body = event['body']

                        # 检查body是否包含链接
                        urls = re.findall(
                            'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', body)

                        # 将链接添加到结果中
                        for url in urls:
                            if html_url not in result:
                                result[html_url] = []
                            result[html_url].append(url)

            # 暂停2秒
            time.sleep(2)

        # 将结果保存到新的json文件中
        new_file_path = os.path.join(directory, 'new_' + filename)
        with open(new_file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f)
