import os
from datetime import datetime

def rename_templates(directory):
    # 获取当前日期
    current_date = datetime.now().strftime('%Y-%m-%d')

    root = os.walk(directory)
    # 遍历指定目录下的所有文件
    for root, dirs, files in os.walk(directory):
        print(root, dirs)
        for file in files:
            if file.endswith('.md') and current_date not in file:
                file_path = os.path.join(root, file)
                newfile_name = current_date+'-'+file
                new_file_path = os.path.join(root, newfile_name)
                os.rename(file_path, new_file_path)

def insert_template_to_md(directory):
    # 获取当前日期
    current_date = datetime.now().strftime('%Y-%m-%d')

    root = os.walk(directory)
    # 遍历指定目录下的所有文件
    for root, dirs, files in os.walk(directory):
        print(root, dirs)
        for file in files:
            if file.endswith('.md') and current_date not in file:
                file_path = os.path.join(root, file)
                # 读取原始文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()

                # 构建要插入的模板字符串
                template = f"""---
title:      {file}
date:       {current_date}
tags:
- swift
- source code
---

"""
                # 将模板字符串插入到原始内容前面
                new_content = template + original_content

                # 将新内容写回文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

def change_template_to_md(directory):
    # 获取当前日期
    current_date = datetime.now().strftime('%Y-%m-%d')
    root = os.walk(directory)
    # 遍历指定目录下的所有文件
    for root, dirs, files in os.walk(directory):
        print(root, dirs)
        for file in files:
            if file.endswith('.md') and current_date in file:
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                # 将模板字符串插入到原始内容前面
                new_content = original_content.replace(""".md
""","""
""")
                # 将新内容写回文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

# 使用示例
directory = "/Users/bo.liu/Documents/Buddy/Code/github/swift/_posts"
# insert_template_to_md(directory)
change_template_to_md(directory)