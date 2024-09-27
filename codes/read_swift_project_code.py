import os
from time import sleep

def find_swift_files(directory, suffix):
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

def append_swift_contents_to_file(swift_files, temp_file_path):
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
        for swift_file in swift_files:
            with open(swift_file, 'r') as file:
                # 读取swift文件内容并追加到临时文件中
                temp_file.write(file.read() + '\n')  # 在每个文件内容后添加一个换行符以分隔

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

def main():
    directory_path = '/Users/bo.liu/Documents/Buddy/Code/UIMHearing'
    output_path = '/Users/bo.liu/Documents/Buddy/Code/tmp/tmp_code.swift'
    result_path = '/Users/bo.liu/Documents/Buddy/Code/tmp/1.txt'
    # 读取项目中的代码
    swift_files = find_swift_files(directory_path, ".swift")
    # 将所有代码存入临时文件 用于查找比对
    append_swift_contents_to_file(swift_files, output_path)

    process_file(output_path, result_path)

if __name__ == "__main__":
    main()