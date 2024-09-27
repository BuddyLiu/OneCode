import subprocess
import shutil
import os
from datetime import datetime

def generate_framework(project_path, project_name, target_name, output_dir, custom_platform, configuration="Release"):
    # 构建Framework的命令
    build_command = [
        "xcodebuild",
        "archive",
        "-project", f"{project_path}/{project_name}.xcodeproj",
        "-scheme", target_name,
        "-configuration", configuration,
        "-destination", f"generic/platform={custom_platform}",
        "-archivePath", f"{makeArchive_Path(output_dir,custom_platform, target_name)}",
        "SKIP_INSTALL=NO"
    ]
    subprocess.run(build_command, check=True)

def create_xcframework(output_dir, simulator_framework_path, device_framework_path):
    # 创建XCFramework的命令
    xcframework_command = [
        "xcodebuild",
        "-create-xcframework",
        "-framework", simulator_framework_path,
        "-framework", device_framework_path,
        "-output", f"{output_dir}/{os.path.splitext(os.path.basename(device_framework_path))[0]}.xcframework"
    ]
    subprocess.run(xcframework_command, check=True)

def prepare_output_dir(base_path, default_subdir="XCFrameworkOutput"):
    # 构造默认的输出目录路径
    output_dir = os.path.join(base_path, default_subdir)

    # 如果输出目录不存在，则创建它
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        # 如果输出目录存在且有文件，则备份这些文件
        if os.listdir(output_dir):
            # 创建备份目录
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            backup_dir = os.path.join(base_path, f"backup_{timestamp}")
            os.makedirs(backup_dir)
            # 移动所有文件到备份目录
            for filename in os.listdir(output_dir):
                shutil.move(os.path.join(output_dir, filename), backup_dir)

    return output_dir

def makeArchive_Path(output_dir, custom_platform, target_name):
    if 'simulator' in f"{custom_platform}".lower():
        custom_platform = "simulator"
    return f"{output_dir}/archives/{custom_platform}/{target_name}.xcarchive"

def main():
    # 读取用户输入的项目路径
    project_path_input = input("请输入项目路径（不带项目名）: ")

    # 去除路径尾部的斜杠
    if project_path_input.endswith('/'):
        project_path_input = project_path_input[:-1]

    # 提取最后一级目录作为项目名
    project_name = os.path.basename(project_path_input)
    target_name = project_name  #target默认与项目名相同

    # 准备输出目录
    output_dir = prepare_output_dir(project_path_input)

    # 项目根路径
    project_path = project_path_input

    # 构建Framework
    custom_platform_iphone = "iOS"
    generate_framework(project_path, project_name, target_name, output_dir, custom_platform=custom_platform_iphone)
    custom_platform_simulator = "iOS Simulator"
    generate_framework(project_path, project_name, target_name, output_dir, custom_platform=custom_platform_simulator)

    device_framework_path = f"{makeArchive_Path(output_dir,custom_platform_iphone, target_name)}/Products/Library/Frameworks/{target_name}.framework"
    simulator_framework_path = f"{makeArchive_Path(output_dir,custom_platform_simulator, target_name)}/Products/Library/Frameworks/{target_name}.framework"

    # 创建XCFramework
    create_xcframework(output_dir, simulator_framework_path, device_framework_path)

    # 打印生成的XCFramework路径
    xcframework_path = f"{output_dir}/{os.path.splitext(os.path.basename(device_framework_path))[0]}.xcframework"
    print(f"XCFramework已生成在: {xcframework_path}")

    # 在Finder中打开
    subprocess.run(["open", output_dir])

if __name__ == "__main__":
    main()