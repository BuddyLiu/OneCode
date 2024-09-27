import os

def find_swift_files(directory):
    swift_files = []
    directory_structure = {}

    # 遍历目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.swift'):
                # 将文件路径添加到字典中，按照目录结构组织
                relative_root = os.path.relpath(root, directory)
                if relative_root.startswith('Pods'):
                    continue
                if relative_root not in directory_structure:
                    directory_structure[relative_root] = []

                directory_structure[relative_root].append(file)

    # 将字典转换为列表，以便按照目录层级排序
    sorted_structure = sorted(directory_structure.items(), key=lambda x: x[0])

    # 生成带有目录层级的文件列表
    formatted_files = []
    for path, files in sorted_structure:
        formatted_path = path.replace(os.sep, '/')  # 将路径分隔符替换为/，以符合Markdown习惯
        formatted_files.append(f'## {formatted_path}/')
        for file in files:
            formatted_files.append(f'  ### {file}')

    return formatted_files

def write_markdown(formatted_files, output_file):
    with open(output_file, 'w') as f:
        f.write('# Swift Files\n\n')
        for line in formatted_files:
            f.write(line + '\n')

        f.write(f'\nTotal Swift files: {len(formatted_files) - len(formatted_files) // 2}')

def main():
    directory = "/Users/bo.liu/Documents/Buddy/Code/UIMHearing/UIMHearing" #input("Enter the directory path: ")
    output_file = "/Users/bo.liu/Documents/Buddy/Code/swift_files.md"
    formatted_files = find_swift_files(directory)
    write_markdown(formatted_files, output_file)
    print(f'Markdown file has been saved to {output_file}')

if __name__ == '__main__':
    main()