# 筛选出所有的错误修复PR
import os
import json

# 指定pull request json文件夹的路径
directory = input("Input path of pull request json files you want to process")

# 定义需要查找的关键词列表
keywords = ['fix', 'defect', 'error', 'bug', 'issue', 'mistake', 'incorrect', 'fault', 'flaw', 'bug']

# 遍历目录中的所有文件
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
            matched_items = []  # 用于存储匹配的字典
            print('筛选之前:' + str(len(data)))
            # 遍历文件中的所有字典
            for item in data:
                title = item.get('title', '').lower()  # 获取title并转换为小写
                body = item.get('body', '').lower() if item.get('body', '') else ''  # 获取body并转换为小写
                merged_at = item.get("merged_at", '')
                # 检查title是否包含任何关键词
                if (any(keyword in title for keyword in keywords) or any(keyword in body for keyword in keywords)) and merged_at:
                    matched_items.append(item)  # 将匹配的字典添加到列表中

            # 将匹配的字典保存到新的json文件中
            print('筛选之前:' + str(len(matched_items)))
            with open(os.path.join(directory, 'matched_' + filename), 'w') as f:
                json.dump(matched_items, f)
