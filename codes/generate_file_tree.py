import os
import re
import argparse

Default_exclude_path=["*Pods*", "*.framework", "*.git", ".gitignore", "*.lock", "*.xcodeproj", "*.xcworkspace", ".DS_Store"]

def contains_forbidden_strings(path, forbidden_strings):
    for forbidden_string in forbidden_strings:
        # Check if the forbidden string is a regex pattern
        if forbidden_string.startswith('*') and forbidden_string.endswith('*'):
            # Remove the leading and trailing '*', and use re.search to match the pattern in the middle
            pattern = forbidden_string[1:-1]
            if re.search(pattern, path):
                return True
        elif forbidden_string.startswith('*'):
            # Remove the leading '*', and use re.search to match the pattern at the end
            pattern = forbidden_string[1:]
            if path.endswith(pattern):
                return True
        elif forbidden_string.endswith('*'):
            # Remove the trailing '*', and use re.search to match the pattern at the beginning
            pattern = forbidden_string[:-1]
            if path.startswith(pattern):
                return True
        else:
            # Simple string match
            if forbidden_string in path:
                return True
    return False

def generate_file_tree(
        root_dir,
        max_depth = 2,
        current_depth=0,
        is_show_file=False,
        need_comment=False,
        comment_placeholder_str="# ",
        exclude_path=Default_exclude_path,
        pre_special_indentation=" ",
        folder_mark="+",
        file_mark="|"
    ):
    """
    生成文件树
    :param root_dir: 根目录路径
    :param max_depth: 文件树的最大层数
    :param current_depth: 当前层数（递归使用）
    :param is_show_file: 是否展示文件
    :param need_comment: 是否需要注释
    :param comment_placeholder_str: 注释占位字符
    :param exclude_path: 排除的子目录
    :param pre_special_indentation: 目录缩进
    :param folder_mark: 文件夹标识
    :param file_mark: 文件标识
    :return: 文件树的字符串表示
    """
    if current_depth > max_depth:
        return ""

    tree_str = ""
    indent = pre_special_indentation * 4 * current_depth

    # 获取当前目录下的所有文件和文件夹
    try:
        items = os.listdir(root_dir)
    except PermissionError:
        # 如果没有权限访问某个目录，可以捕获异常并通知用户或跳过该目录
        items = []

    for item in items:
        item_path = os.path.join(root_dir, item)
        is_exclude = contains_forbidden_strings(item_path, exclude_path)
        if is_exclude :
            continue
        comment_str = ""
        if need_comment:
            comment_str = f" {comment_placeholder_str} "
        if os.path.isdir(item_path):
            tree_str += f"{indent}{folder_mark} {item}/{comment_str}\n"
            tree_str += generate_file_tree(
                item_path,
                max_depth,
                current_depth + 1,
                is_show_file=is_show_file,
                need_comment=need_comment,
                comment_placeholder_str=comment_placeholder_str,
                exclude_path=exclude_path,
                pre_special_indentation=pre_special_indentation,
                folder_mark=folder_mark,
                file_mark=file_mark
            )
        else:
            if is_show_file :
                tree_str += f"{indent}{file_mark} {item}{comment_str}\n"

    return tree_str

# root_directory = "/Users/bo.liu/Documents/Buddy/Code/UIMHearing"  # 替换为你要遍历的目录路径
# file_tree = generate_file_tree(root_directory, is_show_file=True, need_comment=True, comment_placeholder_str="# ")
# print(file_tree)

def main():
    parser = argparse.ArgumentParser(description="生成文件树")

    # 添加参数
    parser.add_argument("root_dir", type=str, help="根目录路径")
    parser.add_argument("--max_depth", type=int, default=2, help="文件树的最大层数")
    parser.add_argument("--is_show_file", action="store_true", help="是否展示文件")
    parser.add_argument("--need_comment", action="store_true", help="是否需要注释")
    parser.add_argument("--comment_placeholder_str", type=str, default="# ", help="注释占位字符")
    parser.add_argument("--exclude_path", type=str, nargs='*', default=Default_exclude_path, help="排除的子目录")
    parser.add_argument("--pre_special_indentation", type=str, default=" ", help="目录缩进")
    parser.add_argument("--folder_mark", type=str, default="+", help="文件夹标识")
    parser.add_argument("--file_mark", type=str, default="|", help="文件标识")

    # 解析参数
    args = parser.parse_args()
    # 检查根目录是否存在
    if not os.path.isdir(args.root_dir):
        print(f"错误: 根目录 {args.root_dir} 不存在")
        return

    # 调用 generate_file_tree 函数
    generate_file_tree(
        root_dir=args.root_dir,
        max_depth=args.max_depth,
        is_show_file=args.is_show_file,
        need_comment=args.need_comment,
        comment_placeholder_str=args.comment_placeholder_str,
        exclude_path=args.exclude_path,
        pre_special_indentation=args.pre_special_indentation,
        folder_mark=args.folder_mark,
        file_mark=args.file_mark
    )

if __name__ == "__main__":
    main()