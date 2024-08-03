import pandas as pd
import json
# 排除指定后缀的文件后重新统计代码行数的文件数

# 读取Excel文件
file_path = input("Input file path of pr info:")
df = pd.read_excel(file_path, engine="openpyxl")

# 定义要排除的文件名字符串
exclude_files = ['yarn.lock', 'testdata', '.obj']


# 处理file_changes列，计算修改行数总和（排除特定文件）
def calculate_changes(json_str):
    try:
        data = json.loads(json_str.replace("'", '"'))
        total_changes = 0
        for module in data.values():
            for filename_dict in module.get('filename', []):
                for filename, change_count in filename_dict.items():
                    if not any(exclude in filename for exclude in exclude_files):
                        total_changes += change_count
        return total_changes
    except json.JSONDecodeError:
        return None  # 如果JSON格式错误，返回None


# 应用函数并添加新列
df['total_changes'] = df['file_changes'].apply(calculate_changes)


df.to_excel('correct_lens_and_files_bugs.xlsx', index=False)