import os

def replace_string(s, old, new):
    """
    替换字符串中的旧字符串为新字符串。
    """
    return s.replace(old, new)

def process_file(file_path, old_string, new_string):
    """
    处理文件内容，替换其中的旧字符串为新字符串。
    """
    # with open(file_path, 'r', encoding='utf-8') as file:
    #     content = file.read()
    # new_content = replace_string(content, old_string, new_string)
    # if new_content != content:
    #     with open(file_path, 'w', encoding='utf-8') as file:
    #         file.write(new_content)

def process_directory_helper(directory_path, old_string, new_string):
    """
    递归地处理目录及其子目录中的文件和文件夹名称。
    """
    for root, dirs, files in os.walk(directory_path, topdown=False):
        for name in files:
            if name.endswith(('.DS_Store', '.git')):
                continue  # 跳过这些文件
            file_path = os.path.join(root, name)
            new_name = replace_string(name, old_string, new_string)
            if new_name != name:
                new_file_path = os.path.join(root, new_name)
                os.rename(file_path, new_file_path)
                process_file(new_file_path, old_string, new_string)
            else:
                process_file(file_path, old_string, new_string)

        # 处理完文件后，再处理文件夹名称
        i = 0
        while i < len(dirs):
            dir_name = dirs[i]
            dir_path = os.path.join(root, dir_name)
            new_dir_name = replace_string(dir_name, old_string, new_string)
            if new_dir_name != dir_name:
                new_dir_path = os.path.join(root, new_dir_name)
                os.rename(dir_path, new_dir_path)
                # 更新dirs列表中的目录名，以便后续处理
                dirs[i] = new_dir_name
            i += 1

def process_directory(directory_path, old_string, new_string):
    """
    公开的函数接口，用于开始处理指定目录。
    """
    process_directory_helper(directory_path, old_string, new_string)
    # 也可以考虑处理directory_path本身的名称，如果需要的话
    new_directory_path = replace_string(directory_path, old_string, new_string)
    if new_directory_path != directory_path:
        os.rename(directory_path, new_directory_path)

def main():
    directory_path = "/Users/bo.liu/Documents/Buddy/Code/Swift/Template" #input("请输入目录路径: ")
    old_string = "UIMHearingBleScanModule" #input("请输入要替换的字符串: ")
    new_string = "BYPROJECT" #input("请输入新的字符串: ")
    process_directory(directory_path, old_string, new_string)
    print("处理完成。")

if __name__ == "__main__":
    main()