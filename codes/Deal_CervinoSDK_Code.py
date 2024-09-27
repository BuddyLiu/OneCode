import json
import pandas as pd
from tool.Utils import StringUtils, NetworkUtils, NumberUtils

def get_names_from_json(file_path):
    # 从JSON文件中提取parameter_config下的parameters数组中的name字段
    """
    从指定的JSON文件中读取并提取parameter_config下的parameters数组中每个参数的name。

    参数:
    file_path: JSON文件的路径。

    返回:
    包含所有提取的name的列表，如果未找到相应结构，则返回空列表。
    """

    with open(file_path, 'r') as file:
        data = json.load(file)

    strU = StringUtils()
    reverseStr = strU.reverse_string("ABC")
    # 寻找parameter_config下的parameters数组
    if 'parameter_config' in data and 'parameters' in data['parameter_config']:
        parameters = data['parameter_config']['parameters']

        # 提取每个字典中的name
        names = [param['name'] for param in parameters]
        return names
    else:
        return []

# 读取Excel文件中的特定工作表，并根据映射关系提取数据
def read_excel_sheets(file_path):
    """
    从Excel文件中读取多个指定工作表的数据，根据给定的映射关系提取并格式化数据。

    参数:
    file_path: Excel文件的路径。

    返回:
    包含从工作表中提取并格式化后的数据的列表。
    """
    xlsx = pd.ExcelFile(file_path)

    # 定义两个工作表的映射
    sheet_mappings = {
        "B02-2 CM3B控制类参数表": {"param_name": "参数名", "param_len": "长度", "param_type": "类型", "param_auth": "SDK验配模式", "param_auth_user": "SDK用户模式", "param_des": "功能描述", "param_default":"默认值", "param_range":"取值范围"},
        "B10 外观层-配置层映射": {"param_name": "上位机下发参数", "param_len": "数据长度", "param_type": "数据类型", "param_auth": "sdk验配模式", "param_auth_user": "sdk用户模式", "param_des": "功能描述", "param_default":"默认值", "param_range":"合法取值范围", "param_des_detail": "释义"}
    }

    results = []

    # 遍历每个工作表
    for sheet_name, mapping in sheet_mappings.items():
        # 读取工作表
        df = pd.read_excel(xlsx, sheet_name=sheet_name)

        # 检查DataFrame的列
        expected_cols = list(mapping.values())
        if not all(col in df.columns for col in expected_cols):
            print(f"Worksheet '{sheet_name}' does not contain all expected columns: {expected_cols}")
            continue
        # 根据映射提取数据
        for index, row in df.iterrows():
            if sheet_name == "B10 外观层-配置层映射":
                value = row["上位机下发参数"]
                if pd.isna(value):
                    continue
                if "_start" in value and "_submit" in value and "\n" in value:
                    values = filter_chinese_and_split(value)
                    values_index = 0
                    for item in values:
                        result = {}
                        for key, col in mapping.items():
                            if not pd.isna(row[col]):
                                if "_start" in values[values_index] or "_submit" in values[values_index]:
                                    result["param_name"] = values[values_index]
                                    result["param_len"] = 1
                                    result["param_type"] = "uint24"
                                    result["param_auth"] = "W"
                                    result["param_auth_user"] = "W"
                                    if not pd.isna(row["功能描述"]):
                                        result["param_des"] = row["功能描述"]
                                    else:
                                        result["param_des"] = "NA"
                                    result["param_default"] = "NA"
                                    result["param_range"] = "NA"
                                    if not pd.isna(row["释义"]):
                                        result["param_des_detail"] = row["释义"]
                                    else:
                                        result["param_des_detail"] = "NA"
                                    break
                                else:
                                    tmp_row = df.iloc()[index+values_index-1]
                                    if col == "上位机下发参数":
                                        result["param_name"] = values[values_index]
                                    else:
                                        if not pd.isna(tmp_row[col]):
                                            result[key] = tmp_row[col]
                                        else:
                                            result[key] = "NA"
                            else:
                                result[key] = "NA"
                        values_index += 1
                        if len(result) > 0 and "NA" not in result["param_name"]:
                            value_key = values[0].split("_start")[0]
                            extra_msg = f"该参数为组合命令{value_key}的其中一个参数，组合顺序为：\n{value}"
                            result["param_extra"] = extra_msg
                            results.append(result)
                else:
                    result = {}
                    for key, col in mapping.items():
                        if not pd.isna(row[col]):
                            result[key] = row[col]
                        else:
                            result[key] = "NA"
                    if len(result) > 0 and "NA" not in result["param_name"]:
                        results.append(result)
            else:
                result = {}
                for key, col in mapping.items():
                    if not pd.isna(row[col]):
                        result[key] = row[col]
                    else:
                        result[key] = "NA"
                if len(result) > 0 and "NA" not in result["param_name"]:
                    results.append(result)
    return results

# 确保字符串在换行前有足够的空格
def ensure_spaces_before_newline(s, n):
    """
    在字符串的每行前添加指定数量的空格（不包括首行），以确保对齐。
    参数:
    s: 输入的字符串。
    n: 每行前需要添加的空格总数。

    返回:
    处理后的字符串，其中每行前都有足够的空格。
    """ 
    if '\n' not in f"{s}":
        return ' ' * 8 + "* " + ' '*(n-8-1) + f"{s}"
    # 分割字符串到行
    lines = s.split('\n')
    # 创建一个列表来存储处理后的行
    processed_lines = []

    for line in lines:
        # 计算需要添加的空格数
        num_spaces_to_add = n - len(line) + len(line.lstrip())
        if num_spaces_to_add > 0:
            # 如果需要添加空格，则添加并在行尾加上换行符
            processed_line = ' ' * 8 + "* " + ' '*(num_spaces_to_add-8-1) + line
        else:
            # 如果不需要添加空格，则直接使用原行
            processed_line = line
        # 添加到处理后的行列表中
        processed_lines.append(processed_line)

    # 将处理后的行列表连接成一个字符串并返回
    return '\n'.join(processed_lines)

# 根据参数类型和长度确定参数类型（如数组或基本类型）
def get_param_type(param_type, param_len):
    """
    根据参数的类型和长度，返回合适的参数类型表示（如Int, String, [Int]等）。

    参数:
    param_type: 参数的原始类型。
    param_len: 参数的长度，用于判断是否为数组类型。

    返回:
    处理后的参数类型字符串。
    """
    if param_type in ["uint24", "int24", "uint32"]:
        return "Int" if param_len == 1 else "[Int]"
    elif param_type == "string":
        return "String"
    else:
        return param_type

# 移除字符串中的空行或仅包含空格的行
def remove_empty_or_whitespace_lines(s):
    """
    移除多行字符串中的空行或仅包含空格的行。

    参数:
    s: 输入的多行字符串。

    返回:
    处理后的字符串，不包含空行或仅包含空格的行。
    """ 
    # 使用字符串的splitlines方法将多行字符串分割成单个行的列表
    lines = s.splitlines()
    # 使用列表推导式遍历每一行，只保留那些不是只包含空格的行
    filtered_lines = [line for line in lines if line.strip()]
    # 使用join方法将处理后的行列表重新组合成一个多行字符串，并返回
    return '\n'.join(filtered_lines)

# 生成参数的代码块
def generate_code_block(param_des, param_len, param_auth, param_auth_user, name, param_type, param_default, param_range, param_des_detail, extra_msg=""):
    """
    根据提供的参数信息生成Swift代码块。

    参数:
    param_des: 参数的功能描述。
    param_len: 参数的长度。
    param_auth: SDK验配模式。
    param_auth_user: SDK用户模式。
    name: 参数名。
    param_type: 参数的类型。
    param_default: 参数的默认值。
    param_range: 参数的取值范围。
    param_des_detail: 参数的详细释义。
    extra_msg: 额外的消息（如果有）。

    返回:
    生成的Swift代码块字符串。
    """
    auth_section = f"SDK验配模式：{param_auth}\nSDK用户模式：{param_auth_user}"
    space_count_level1 = 9
    space_count_level2 = 13
    if extra_msg == "":
    # 生成代码块
        code = f"""{"        /*"}
{ensure_spaces_before_newline(f"功能描述：", space_count_level1)}
{ensure_spaces_before_newline(param_des, space_count_level2)}
{ensure_spaces_before_newline(f"释义：", space_count_level1)}
{ensure_spaces_before_newline(param_des_detail, space_count_level2)}
{ensure_spaces_before_newline(f"参数取值范围：", space_count_level1)}
{ensure_spaces_before_newline(param_range, space_count_level2)}
{ensure_spaces_before_newline(f"参数默认值：", space_count_level1)}
{ensure_spaces_before_newline(param_default, space_count_level2)}
{ensure_spaces_before_newline(f"长度：{param_len}", space_count_level1)}
{ensure_spaces_before_newline(auth_section, space_count_level1)}
{"        **/"}
        public static let {name}: FWParameter<{param_type}> = FWParameter<{param_type}>.define("{name}")
        """
    else:
        code = f"""{"        /*"}
{ensure_spaces_before_newline(f"功能描述：", space_count_level1)}
{ensure_spaces_before_newline(param_des, space_count_level2)}
{ensure_spaces_before_newline(f"释义：", space_count_level1)}
{ensure_spaces_before_newline(param_des_detail, space_count_level2)}
{ensure_spaces_before_newline(f"参数取值范围：", space_count_level1)}
{ensure_spaces_before_newline(param_range, space_count_level2)}
{ensure_spaces_before_newline(f"参数默认值：", space_count_level1)}
{ensure_spaces_before_newline(param_default, space_count_level2)}
{ensure_spaces_before_newline(f"长度：{param_len}", space_count_level1)}
{ensure_spaces_before_newline(extra_msg, space_count_level1)}
{ensure_spaces_before_newline(auth_section, space_count_level1)}
{"        **/"}
        public static let {name}: FWParameter<{param_type}> = FWParameter<{param_type}>.define("{name}")
        """

    return remove_empty_or_whitespace_lines(code)

# 过滤掉包含中文字符的行
def filter_chinese_and_split(input_str):
    """
    从输入字符串中分割并过滤掉包含中文字符的行。

    参数:
    input_str: 输入的字符串，可能包含多行。

    返回:
    包含非中文字符行的列表。
    """ 
    # 按照换行符分割字符串
    lines = input_str.split('\n')

    # 创建一个新的数组，用于存储不包含中文字符的项
    filtered_lines = []

    # 遍历分割后的数组
    for line in lines:
        # 如果项不包含中文字符，则添加到新数组中
        if not any('\u4e00' <= char <= '\u9fff' for char in line):
            filtered_lines.append(line)

    # 返回处理后的数组
    return filtered_lines

# 生成代码的函数
def generate_code(names, data):
    result_list = []
    generated_code_key = []
    for name in names:
        if name in generated_code_key:
            continue
        data_index = 0
        for item in data:
            param_auth = item["param_auth"]
            param_auth_user = item["param_auth_user"]
            if param_auth == "NA" and param_auth_user == "NA":
                continue
            param_name = item["param_name"]
            param_des = item["param_des"]

            param_default = f"{item["param_default"]}"
            if "off" == str.lower(param_default):
                param_default = f"Off(0)"
            if "on" == str.lower(param_default):
                param_default = f"On(1)"

            param_range = item["param_range"]
            if "On/Off" == param_range:
                param_range = f"{param_range}(On:1, Off:0)"

            param_des_detail = "NA"
            if "param_des_detail" in item:
                param_des_detail = item["param_des_detail"]

            param_len = 0
            if "NA" not in f"{item["param_len"]}":
                param_len = int(item["param_len"])
            param_type = get_param_type(item["param_type"], param_len)

            if param_name == name:
                # 规则2的处理
                if "param_extra" in item:
                    code = generate_code_block(param_des, param_len, param_auth, param_auth_user, name, param_type, param_default, param_range, param_des_detail, item["param_extra"])
                else:
                    code = generate_code_block(param_des, param_len, param_auth, param_auth_user, name, param_type, param_default, param_range, param_des_detail)
                result_list.append(code)
                generated_code_key.append(name)
                break
            data_index += 1

    if len(result_list) > 0:
        print("生成成功！")
        write_string_to_file("/Users/bo.liu/Downloads/CervinoSDK/Cervino.swift", "\n\n".join(result_list))
    else:
        print("没有生成Code")

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

def main():
    file_path = '/Users/bo.liu/Downloads/CervinoSDK/0826/parameter_config630.json'
    names = get_names_from_json(file_path)
    print(names)

    xlsx_file_path = '/Users/bo.liu/Downloads/CervinoSDK/0826/Cervino全参数列表-0826.xlsx'
    data = read_excel_sheets(xlsx_file_path)
    print(data)

    # 调用函数生成代码
    generate_code(names, data)


if __name__ == '__main__':
    main()