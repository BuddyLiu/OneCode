import requests
from datetime import datetime
import os
import pandas as pd

def read_excel_to_dict_list(file_path, sheet_name):
    # 读取Excel文件的指定工作表
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    except Exception as e:
        print(f"读取Excel文件失败: {e}")
        return None

    # 检查表头是否存在
    if df.columns.isnull().any():
        print("表头不存在或表头中有空值")
        return None

    # 将DataFrame每行转换为字典，空值处理为空字符串，非字符串处理为字符串
    data_list = []
    for _, row in df.iterrows():
        row_dict = {}
        for col in df.columns:
            value = row[col]
            if pd.isnull(value):
                value = ""
            else:
                value = str(value)
            row_dict[col] = value
        data_list.append(row_dict)
    return data_list

# 确保字符串在换行前有足够的空格
def ensure_spaces_before_newline(s, n):
    """
    在字符串的每行前添加指定数量的空格（不包括首行），以确保对齐。
    参数:
    s: 输入的字符串。
    n: 每行前需要添加的空格总数。最小为9
    返回:
    处理后的字符串，其中每行前都有足够的空格。
    """
    if n < 9:
        return s
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

def append_files_contents_to_tmp_file(files, temp_file_path):
    """
    将所有swift文件的内容追加到指定的临时文件中。
    :param swift_files: 包含swift文件路径的列表
    :param temp_file_path: 临时文件的路径
    """
    # 如果临时文件已存在，则删除
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
    # 打开临时文件准备追加内容
    with open(temp_file_path, 'a') as temp_file:
        for swift_file in files:
            with open(swift_file, 'r') as file:
                # 读取swift文件内容并追加到临时文件中
                temp_file.write(file.read() + '\n')  # 在每个文件内容后添加一个换行符以分隔

def find_spec_suffix_files(directory, suffix):
    """
    遍历指定目录，查找所有后缀名为suffix的文件。
    :param directory: 要遍历的目录路径
    :return: 包含所有找到的swift文件路径的列表
    """
    swift_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(suffix):
                swift_files.append(os.path.join(root, file))
    return swift_files

class StringUtils:
    @staticmethod
    def reverse_string(input_string, default_value=""):
        """
        反转字符串。

        :param input_string: 要反转的字符串
        :param default_value: 如果输入不是字符串，返回的默认值
        :return: 反转后的字符串
        """
        try:
            if not isinstance(input_string, str):
                return default_value
            return input_string[::-1]
        except Exception as e:
            print(f"Error reversing string: {e}")
            return default_value

    @staticmethod
    def to_uppercase(input_string, default_value=""):
        """
        将字符串转换为大写。

        :param input_string: 要转换的字符串
        :param default_value: 如果输入不是字符串，返回的默认值
        :return: 大写字符串
        """
        try:
            if not isinstance(input_string, str):
                return default_value
            return input_string.upper()
        except Exception as e:
            print(f"Error converting string to uppercase: {e}")
            return default_value

class NumberUtils:
    @staticmethod
    def add(a, b, default_value=0):
        """
        两个数相加。

        :param a: 第一个数
        :param b: 第二个数
        :param default_value: 如果输入不是数值类型，返回的默认值
        :return: 相加后的结果
        """
        try:
            return float(a) + float(b)
        except (ValueError, TypeError):
            print(f"Error adding numbers: invalid input {a} or {b}")
            return default_value

    @staticmethod
    def multiply(a, b, default_value=0):
        """
        两个数相乘。

        :param a: 第一个数
        :param b: 第二个数
        :param default_value: 如果输入不是数值类型，返回的默认值
        :return: 相乘后的结果
        """
        try:
            return float(a) * float(b)
        except (ValueError, TypeError):
            print(f"Error multiplying numbers: invalid input {a} or {b}")
            return default_value

class DateTimeUtils:
    @staticmethod
    def current_timestamp(format_str="%Y-%m-%d %H:%M:%S"):
        """
        获取当前时间戳。

        :param format_str: 时间格式，默认 "%Y-%m-%d %H:%M:%S"
        :return: 格式化后的当前时间戳
        """
        try:
            return datetime.now().strftime(format_str)
        except Exception as e:
            print(f"Error getting current timestamp: {e}")
            return ""

    @staticmethod
    def convert_to_date(date_str, format_str="%Y-%m-%d"):
        """
        将字符串转换为日期对象。

        :param date_str: 日期字符串
        :param format_str: 日期格式，默认 "%Y-%m-%d"
        :return: 转换后的日期对象，如果转换失败返回None
        """
        try:
            return datetime.strptime(date_str, format_str).date()
        except ValueError:
            print(f"Error converting string to date: invalid date format {date_str}")
            return None
        except Exception as e:
            print(f"Error converting string to date: {e}")
            return None

class NetworkUtils:
    @staticmethod
    def fetch_url(url, timeout=10, default_response=None):
        """
        发送HTTP GET请求获取响应内容。

        :param url: 目标URL
        :param timeout: 请求超时时间，默认10秒
        :param default_response: 请求失败时返回的默认值
        :return: 响应内容，如果请求失败返回默认值
        """
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return default_response