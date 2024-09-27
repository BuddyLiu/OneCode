import os
import shutil
from time import sleep
import json

def sleep_run(sec = 0.0):
    """
    运行期间休眠 便于debug
    """
    sleep(sec)

def get_file_name(file_path_or_full_name):
    """
    读取文件名
    特殊情况是文件名中包含多个"."，
    此时，仅认为最后一个"."后面才是后缀名，如果没有"."，则直接返回入参
    """
    tmp_name = file_path_or_full_name
    if '/' in file_path_or_full_name:
        tmp_name = file_path_or_full_name.split('/')[-1]

    if '.' in tmp_name:
        tmp_name = tmp_name.replace(f'.{tmp_name.split(".")[-1]}', '')

    if tmp_name == '':
        return file_path_or_full_name
    else:
        return tmp_name

def log_to_file(file_path, content_str):
    """
    将文本content_str记录到日志文件file_path中
    file_path不存在，则自动创建，存在则追加
    """
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            print(f"已创建文件：{file_path}")
    with open(file_path, 'a') as temp_file:
        temp_file.write(content_str + '\n')

def move_to_destination(destination_dir, source_path):
    """
    将source_path指定的文件或文件夹移动到destination_dir指定的目录。
    如果目标目录不存在，则创建它；如果已存在，则备份后删除再创建。
    """
    # 检查目标目录是否存在
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    # 移动文件或文件夹到目标目录
    if os.path.exists(source_path):
        shutil.copytree(source_path, f'{destination_dir}/{source_path.split("/")[-1]}')
        shutil.rmtree(source_path)
        print(f"已将{source_path}移动到{destination_dir}")

def rename_images_and_update_json(dicts, directory_path):
    """
    重命名不符合标准的图片文件名
    """
    renames_img = []
    for d in dicts:
        img_name = d['img_name']
        img_group_name = d['img_group_name']
        img_group_full_name = d['img_group_full_name']
        img_path = d['img_path']
        img_group_path = d['img_group_path']
        if not os.path.exists(img_path):
            continue
        # 去除img_name的后缀名
        base_name = os.path.splitext(img_name)[0]
        if "@" in base_name:
            base_name = base_name.split('@')[0]
        if img_group_full_name.endswith('imageset') and base_name != img_group_name:
            # 更新Contents.json文件
            json_path = os.path.join(img_group_path, 'Contents.json')
            # 确定新的文件名
            new_filename = ""
            new_filepath = ""
            with open(json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for image in data['images']:
                if "filename" in image and 'scale' in image and img_name == image["filename"]:
                    scale_format = ""
                    if image["scale"] == "2x":
                        scale_format = "@2x"
                    elif image["scale"] == "3x":
                        scale_format = "@3x"
                    new_filename = f'{img_group_name}{scale_format}.{img_name.split('.')[-1]}'
                    new_filepath = os.path.join(img_group_path, new_filename)
                    image['filename'] = new_filename
                    break

            with open(json_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2)

            if new_filepath == "":
                print("*** rename fail，check {img_path}")
                renames_img.append(f"*** rename fail，check {img_path}")
            else:
                # 重命名文件
                os.rename(img_path, new_filepath)
                print(f'{img_name} rename to {new_filename}')
                renames_img.append(f'{img_group_name}: \"{img_name}\"  >>> \"{new_filename}\"')
            sleep_run()
    log_to_file(f'{directory_path}/renamed_images.log', '\n'.join(renames_img))

def is_contains_str(file_content, special_name):
    """
    判断文件内容中是否包含指定的字符串
    定制规则
    """
    is_con = False
    if special_name in file_content and \
        (f"\"{special_name}" in file_content or f"{special_name}.png" in file_content):
        is_con = True
    return is_con

def filter_img_group_names(file_path, img_dicts):
    """
    过滤代码中未使用的img_group_name和部分特殊标识的图片对象
    """
    # 读取文件内容
    with open(file_path, 'r') as file:
        file_content = file.read()

    # 用于存储不存在于文件内容中的字典
    filtered_dicts = []

    # 遍历数组中的字典
    for img_dict in img_dicts:
        img_group_name = img_dict['img_group_name']
        # 检查img_group_name是否不在文件内容中
        if "left" in img_group_name or \
            "right" in img_group_name or \
            "sele" in img_group_name or \
            "large" in img_group_name or \
            img_group_name.endswith("S"):
            continue
        elif f"\"{img_group_name}" not in file_content:
            # 如果不存在，则添加到filtered_dicts数组中
            filtered_dicts.append(img_dict)
    return filtered_dicts

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

def find_swift_files(directory):
    """
    遍历指定目录，查找所有后缀名为'swift'的文件。
    :param directory: 要遍历的目录路径
    :return: 包含所有找到的swift文件路径的列表
    """
    swift_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.swift'):
                swift_files.append(os.path.join(root, file))
    return swift_files

def find_images_in_directory(directory):
    """
    遍历指定目录下的所有文件，找出所有图片，并按照指定格式存储信息。
    :param directory: 要遍历的目录路径
    :return: 包含图片信息的列表，每个元素是一个字典，包括图片的名字、完整路径和分组路径
    """
    supported_image_formats = ('.png')
    images_info = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(supported_image_formats):
                img_name = file
                img_path = os.path.join(root, file)
                img_group_path = root
                img_group_name = ''
                img_group_full_name = ''
                if img_group_path.lower().endswith('.imageset') :
                    img_group_name = get_file_name(img_group_path.split('/')[-1])
                    img_group_full_name = img_group_path.split('/')[-1]
                    images_info.append({
                        "img_name": img_name,
                        "img_path": img_path,
                        "img_group_path": img_group_path,
                        'img_group_name': img_group_name,
                        'img_group_full_name': img_group_full_name,
                    })
    # 使用字典来保存每个img_group_name对应的元素
    unique_images = {}
    for img in images_info:
        img_group_name = img['img_group_name']
        if img_group_name not in unique_images:
            unique_images[img_group_name] = img
    # 将字典的值（即保留的图像）转换回列表
    filtered_images = list(unique_images.values())
    return filtered_images

def remove_ds_store_in_directory(directory):
    """
    遍历指定目录下的所有文件，移除所有.DS_Store文件缓存
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if '.DS_Store' in file:
                # 清除.DS_Store文件，XCode依赖该文件进行搜索
                os.remove(f'{root}/{file}')

def delete_file(group_path, backup_directory_path, log_output_path):
    """
    删除 group_path 文件目录，备份到 backup_directory_path ，将日志输出到 log_output_path
    """
    if os.path.exists(group_path):
        shutil.copytree(group_path, f'{backup_directory_path}/{group_path.split("/")[-1]}')
        shutil.rmtree(group_path)
        print(group_path)
        log_to_file(f'{log_output_path}/removed_images.log', get_file_name(group_path))

def remove_project_unused_img(output_path, images_info, swift_files):
    """
    移除项目中无用的图片
    """
    # 项目代码收集临时文件
    temp_file_path = f'{output_path}/tmp_code.swift'
    # 要移除的图片文件备份
    backup_directory_path = f"{output_path}/backup_removed_images"
    if os.path.exists(backup_directory_path):
        shutil.rmtree(backup_directory_path)
    os.makedirs(backup_directory_path)
    # 将所有代码存入临时文件 用于查找比对
    append_swift_contents_to_file(swift_files, temp_file_path)
    # 筛选出要删除的图片
    filtered_dicts = filter_img_group_names(temp_file_path, images_info)
    print(len(filtered_dicts))
    # 遍历要删除的图片文件，依次删除
    for img_dict in filtered_dicts:
        group_path = img_dict["img_group_path"]
        delete_file(group_path, backup_directory_path, output_path)
        group_path_S = group_path.replace(".imageset", "S.imageset")
        delete_file(group_path_S, backup_directory_path, output_path)
        group_path_selected = group_path.replace(".imageset", "_selected.imageset")
        delete_file(group_path_selected, backup_directory_path, output_path)
        sleep_run()

def main():
    directory_path = '/Users/bo.liu/Documents/Buddy/Code/UIMHearing'
    output_path = '/Users/bo.liu/Documents/Buddy/Code/tmp'
    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    # 获取项目中所有的图片
    images_info = find_images_in_directory(directory_path)
    # 读取项目中的代码
    swift_files = find_swift_files(directory_path)
    # 移除无用图片
    remove_project_unused_img(output_path, images_info, swift_files)
    # 重命名文件名与imageset名不同的文件
    rename_images_and_update_json(images_info, output_path)
    # 删除.DS_Store文件
    remove_ds_store_in_directory(directory_path)

if __name__ == "__main__":
    main()