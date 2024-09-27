import json
import re
import pandas as pd
from tool.Utils import find_spec_suffix_files, append_files_contents_to_tmp_file, remove_empty_or_whitespace_lines

def read_and_parse_file(file_path):
    result = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 2):
            # Ensure we have a complete set of three lines
            if i + 1 >= len(lines):
                break
            # Extract the relevant lines
            header = lines[i].strip()
            ui_log = lines[i + 1].strip()
            # Create a dictionary from the extracted lines
            entry = {
                "header": header,
                "ui_log": ui_log
            }
            result.append(entry)
    return result

# 读取Excel文件中的特定工作表，并根据映射关系提取数据
def read_excel_sheets(file_path):
    # 读取Excel文件的指定工作表
    df = pd.read_excel(file_path, sheet_name="埋点 V1.5.6.1")

    # 检查所需的列是否都存在
    required_columns = ["功能", "Subject", "Action", "SubjectID", "Data", "说明"]
    if not all(column in df.columns for column in required_columns):
        raise ValueError("Excel文件中缺少必要的列")

    # 提取指定的列并重命名
    df_renamed = df[required_columns].rename(columns={
        "功能": "func",
        "Subject": "subject",
        "Action": "action",
        "SubjectID": "subjectId",
        "Data": "data",
        "说明": "des"
    })

    # 将DataFrame转换为字典列表
    dict_list = df_renamed.to_dict(orient='records')

    return dict_list

# 生成参数的代码块
def generate_template_code(param):
    """
    根据提供的参数信息生成Swift代码块。

    参数:
    param:参数字典

    返回:
    生成的Swift代码块字符串。
    """
    subjectType = ""
    subject = param["subject"]
    if subject == "APP":
        subjectType = "trackApp"
    elif subject == "PAGE":
        subjectType = "trackPage"
    elif subject == "BUTTON":
        subjectType = "trackButton"
    elif subject == "AREA":
        subjectType = "trackArea"
    elif subject == "PICKER":
        subjectType = "trackPicker"

    if subjectType == "":
        return "生成失败"
    data = f"{param["data"]}"
    comment_str = ""
    json_data = ""
    if data and "{" in data and "}" in data:
        json_data, comment_str = process_json_with_comments(data)
        if json_data != "":
            json_data = f", \"{json_data}\""
        if comment_str != "":
            comment_str = f" {comment_str}"
    # 生成代码块
    code = f"""
{"/// Track: "}{param["func"]} {param["des"]}{comment_str}
UIMLog.{subjectType}("{param["subjectId"]}"{json_data})
"""
    return remove_empty_or_whitespace_lines(code)

def write_string_to_file(file_path, string):
    """
    将指定字符串写入指定文件。
    如果文件不存在，将创建该文件。
    如果文件已存在，将覆盖该文件。

    参数:
    file_path: 要写入的文件的路径。
    string: 要写入文件的字符串。
    """
    with open(file_path, 'w') as file:
        file.write(string)

def process_json_with_comments(data_str):
    # 用来存储标准json的键值对
    json_dict = {}
    # 用来存储每行的键和对应的注释
    comments = ""

    # 逐行处理数据
    lines = data_str.strip('{}').strip().split('\n')
    for line in lines:
        # 通过正则表达式分离键值对和注释
        match = re.match(r'"(.*?)"\s*:\s*"(.*?)"\s*//\s*(.*)', line)
        if match:
            key, value, comment = match.groups()
            json_dict[key] = value
            comments += f"{key}: {comment} "

    # 生成标准的json字符串
    standard_json_str = json.dumps(json_dict, ensure_ascii=False)

    while f': \"' in standard_json_str:
        standard_json_str = standard_json_str.replace(f': \"', f':\"')
    while f'\"' in standard_json_str:
        standard_json_str = standard_json_str.replace(f'\"', f'++_++')
    while f'++_++' in standard_json_str:
        standard_json_str = standard_json_str.replace(f'++_++', f'\\\"')
    return standard_json_str, comments

def find_duplicates(str_list):
    # 使用字典来存储字符串出现的次数
    str_count = {}

    # 遍历数组，统计每个字符串的出现次数
    for string in str_list:
        if string in str_count:
            str_count[string] += 1
        else:
            str_count[string] = 1

    # 找出出现次数大于1的字符串
    duplicates = [string for string, count in str_count.items() if count > 1]

    return duplicates

def process_file(input_filename, output_filename):
    try:
        with open(input_filename, 'r', encoding='utf-8') as infile, open(output_filename, 'w', encoding='utf-8') as outfile:
            lines = infile.readlines()

            i = 0
            while i < len(lines) - 1:
                if "/// Track:" in lines[i]:
                    # 读取当前行和下一行
                    current_line = lines[i].strip()
                    next_line = lines[i + 1].strip()

                    # 移除开头的多余空格
                    current_line = current_line.lstrip()
                    next_line = next_line.lstrip()

                    # 写入到输出文件
                    outfile.write(current_line + '\n')
                    outfile.write(next_line + '\n')

                    # 跳过下一行
                    i += 1
                i += 1

        print(f"处理完成，结果已写入 {output_filename}")
    except Exception as e:
        print(f"处理文件时发生错误: {e}")

def generate_codes_with(origin_data, tracked_list):
    code = ""
    # 调用函数生成代码
    for tmp_code in origin_data:
        isTrcked = False
        for tracked_code in tracked_list:
            if tmp_code["subjectId"] in tracked_code["ui_log"]:
                isTrcked = True
                break
        if not isTrcked:
            code += f"\n{generate_template_code(tmp_code)}\n"
    return code

def main():
    root_path = '/Users/bo.liu/Documents/Buddy/Code/'
    directory_path = '/Users/bo.liu/Documents/Buddy/Code/UIMHearing'
    output_path = f'{root_path}tmp/tmp_code.swift'
    result_path = f'{root_path}tmp/1.txt'
    log_path = f'{root_path}tmp/log.txt'
    xlsx_file_path = '/Users/bo.liu/Documents/Buddy/文档/1.5.6.1/xlsx/0925/数据埋点-联影听觉管家0925113201.xlsx'
    output_path = '/Users/bo.liu/Documents/Buddy/文档/1.5.6.1/xlsx/0925/数据埋点-联影听觉管家0925113201.txt'
    # 读取项目中的代码
    swift_files = find_spec_suffix_files(directory_path, ".swift")
    # 将所有代码存入临时文件 用于查找比对
    append_files_contents_to_tmp_file(swift_files, output_path)
    process_file(output_path, result_path)
    # 读取到所有已添加的埋点代码，未去重
    tracked_list = read_and_parse_file(result_path)
    # 读取最新埋点表格数据
    origin_data = read_excel_sheets(xlsx_file_path)
    # 根据表格按照埋点代码模板生成埋点代码
    code = generate_codes_with(origin_data, tracked_list)
    write_string_to_file(output_path, code)
    # 筛选数据 找出原始埋点表格中所有的subjectId数组
    filter_origin_data = []
    for item in origin_data:
        filter_origin_data.append(item["subjectId"])
    # 筛选数据 找出已经埋过的点的subjectId数组
    filter_tracked_list = []
    for item in tracked_list:
        filter_tracked_list.append(item["ui_log"].split("(\"")[1].split("\"")[0])
    # 利用集合为原始埋点表格中所有的subjectId去重
    set_origin_data = set(filter_origin_data)
    write_string_to_file(log_path, f"所有要埋的点：{find_duplicates(filter_origin_data)}")
    # 利用集合为已经埋过的点的subjectId数组去重
    set_tracked_list = set(filter_tracked_list)
    write_string_to_file(log_path, f"所有已经埋的点{find_duplicates(filter_tracked_list)}")
    # 求差集，找出遗漏或多埋的点
    write_string_to_file(log_path, f"已经埋但表格里没有的点：{set_tracked_list - set_origin_data}")
    write_string_to_file(log_path, f"表格里有还没埋的点：{set_origin_data - set_tracked_list}")

if __name__ == '__main__':
    main()