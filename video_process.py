import os
import cv2
import time
import numpy as np
import re
import argparse

def extract_number(filename):
    """
    从文件名中提取数字部分
    例如: "image_001.jpg" 将返回 1
    """
    numbers = re.findall(r'\d+', filename)
    if numbers:
        return int(numbers[0])
    return 0

def save_images_as_video(folder_path, output_file, fps=10):
    """
    将文件夹中的图片保存为视频文件
    
    参数:
        folder_path: 包含图片的文件夹路径
        output_file: 输出视频文件的路径
        fps: 视频帧率，默认为10
    """
    # 获取文件夹中所有图片文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    files = [f for f in os.listdir(folder_path) if os.path.splitext(f.lower())[1] in image_extensions]
    
    # 按照文件名中的数字部分排序
    files.sort(key=extract_number)
    
    if not files:
        print(f"在 {folder_path} 中没有找到图片")
        return False
    
    # 读取第一张图片以获取尺寸
    first_img_path = os.path.join(folder_path, files[0])
    first_img = cv2.imread(first_img_path)
    if first_img is None:
        print(f"无法读取图片: {first_img_path}")
        return False
    
    height, width, _ = first_img.shape
    
    # 定义编解码器并创建VideoWriter对象
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 可以根据需要更改编解码器
    video_writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
    
    print(f"开始创建视频文件: {output_file}")
    
    # 遍历所有图片并写入视频
    for i, file in enumerate(files):
        img_path = os.path.join(folder_path, file)
        img = cv2.imread(img_path)
        
        if img is None:
            print(f"无法读取图片: {img_path}")
            continue
            
        # 确保所有图片尺寸一致
        if img.shape[0] != height or img.shape[1] != width:
            img = cv2.resize(img, (width, height))
            
        # 写入视频帧
        video_writer.write(img)
        
        # 显示进度
        if (i+1) % 10 == 0 or i == len(files)-1:
            print(f"处理进度: {i+1}/{len(files)} 图片")
    
    # 释放资源
    video_writer.release()
    print(f"视频已保存到: {output_file}")
    return True

def play_images_as_video(folder_path, fps=10):
    """
    按照文件名中的数字顺序播放文件夹中的图片，速度为指定的fps
    
    参数:
        folder_path: 包含图片的文件夹路径
        fps: 每秒显示的图片数量，默认为10
    """
    # 获取文件夹中所有图片文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    files = [f for f in os.listdir(folder_path) if os.path.splitext(f.lower())[1] in image_extensions]
    
    # 按照文件名中的数字部分排序
    files.sort(key=extract_number)
    
    if not files:
        print(f"在 {folder_path} 中没有找到图片")
        return
    
    # 计算每帧的显示时间（秒）
    frame_time = 1.0 / fps
    
    # 创建窗口
    window_name = "picture series"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    print(f"开始播放 {len(files)} 张图片，速度为每秒 {fps} 张")
    print("按 'q' 键退出，按空格键暂停/继续")
    
    paused = False
    i = 0
    
    while i < len(files):
        if not paused:
            # 读取图片
            img_path = os.path.join(folder_path, files[i])
            img = cv2.imread(img_path)
            
            if img is None:
                print(f"无法读取图片: {img_path}")
                i += 1
                continue
            
            # 显示当前图片的文件名和进度信息（在右上角）
            text_img = img.copy()
            text = f"{files[i]} ({i+1}/{len(files)})"
            
            # 获取文本大小以便正确放置在右上角
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            text_x = img.shape[1] - text_size[0] - 10  # 右边缘减去文本宽度和边距
            text_y = 30  # 顶部边距
            
            cv2.putText(text_img, text, 
                        (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # 显示图片
            cv2.imshow(window_name, text_img)
            i += 1
        
        # 等待按键，等待时间为frame_time*1000毫秒
        key = cv2.waitKey(int(frame_time * 1000))
        
        # 按 'q' 退出
        if key == ord('q'):
            break
        # 按空格键暂停/继续
        elif key == 32:  # 空格键的ASCII码
            paused = not paused
            print("暂停" if paused else "继续")
    
    cv2.destroyAllWindows()
    print("播放结束")
    
    return files

if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='按顺序播放图片文件夹中的图片或保存为视频')
    parser.add_argument('--folder', type=str, default='', help='图片文件夹路径')
    parser.add_argument('--fps', type=float, default=24, help='播放/视频的帧率')
    parser.add_argument('--mode', type=str, choices=['play', 'save', 'both', 'interactive'], 
                        default='interactive', help='操作模式: play=仅播放, save=仅保存视频, both=播放并保存, interactive=交互式选择')
    parser.add_argument('--output', type=str, default='', help='保存视频的文件名')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 交互式模式
    if args.mode == 'interactive':
        print("欢迎使用图片序列处理工具")
        
        # 让用户选择图片文件夹
        if not args.folder:
            while True:
                folder_path = input("请输入图片文件夹路径: ")
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    args.folder = folder_path
                    break
                else:
                    print(f"错误: '{folder_path}' 不是有效的文件夹路径，请重新输入")
        
        # 让用户选择帧率
        fps_input = input(f"请输入帧率 (默认 {args.fps}): ")
        if fps_input.strip():
            try:
                args.fps = float(fps_input)
            except ValueError:
                print(f"无效的帧率，将使用默认值 {args.fps}")
        
        # 选择操作模式
        print("\n请选择操作模式:")
        print("1. 播放图片序列")
        print("2. 保存为视频文件")
        print("3. 先播放再保存为视频")
        
        while True:
            mode_choice = input("请选择 (1/2/3): ")
            if mode_choice == '1':
                args.mode = 'play'
                break
            elif mode_choice == '2':
                args.mode = 'save'
                break
            elif mode_choice == '3':
                args.mode = 'both'
                break
            else:
                print("无效的选择，请重新输入")
        
        # 如需保存视频，获取输出文件名
        if args.mode in ['save', 'both']:
            if not args.output:
                while True:
                    output_file = input("请输入输出视频文件名 (例如: output.mp4): ")
                    if output_file.strip():
                        args.output = output_file
                        break
                    else:
                        print("请输入有效的文件名")
    
    # 检查文件夹是否存在
    if not args.folder:
        print("错误：未指定图片文件夹路径")
        exit(1)
    
    if not os.path.exists(args.folder):
        print(f"错误：找不到文件夹 '{args.folder}'")
        exit(1)
    
    # 如果选择保存视频，则构建完整的输出文件路径
    output_path = None
    if args.mode in ['save', 'both']:
        if not args.output:
            # 如果未指定输出文件名，使用默认名称
            args.output = 'output.mp4'
            print(f"未指定输出文件名，将使用默认名称: {args.output}")
        
        # 检查输出文件名是否提供了路径
        if os.path.dirname(args.output):
            # 如果提供了路径，则直接使用
            output_path = args.output
        else:
            # 否则使用当前工作目录
            output_path = os.path.join(os.getcwd(), args.output)
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"已创建输出目录: {output_dir}")
            except Exception as e:
                print(f"无法创建输出目录: {e}")
                exit(1)
    
    # 根据模式执行操作
    if args.mode == 'play' or args.mode == 'both':
        # 播放图片
        files = play_images_as_video(args.folder, fps=args.fps)
    else:
        # 仅保存模式，获取文件列表
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        files = [f for f in os.listdir(args.folder) if os.path.splitext(f.lower())[1] in image_extensions]
        files.sort(key=extract_number)
        
    # 保存视频
    if args.mode in ['save', 'both'] and files:
        save_images_as_video(args.folder, output_path, fps=args.fps) 