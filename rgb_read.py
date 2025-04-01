import msgpack
import json
import ast
import io
import os
from PIL import Image, ImageDraw, ImageFont
import datetime

def read_msg_file(file_name):
    # 创建保存帧和图片的目录
    if not os.path.exists("frames"):
        os.mkdir("frames")
    if not os.path.exists("pictures"):
        os.mkdir("pictures")
    
    # 以二进制方式读取文件
    with open(file_name, "rb") as f:
        # 使用流式解包
        unpacker = msgpack.Unpacker(f, raw=False)
        # 处理所有帧
        for i, unpacked_dict in enumerate(unpacker):
            # 将每帧保存为TXT文件，标题为序号
            frame_file = f"frames/frame_{i}.txt"
            with open(frame_file, 'w', encoding='utf-8') as txt_file:
                txt_file.write(str(unpacked_dict))
            print(f"已将第{i}帧保存到 {frame_file}")
            
            # 处理并保存每帧的图像
            process_image(frame_file, i)
    
    print(f"处理完成！")
    return

def process_image(frame_file, frame_number):
    # 读取文件内容
    with open(frame_file, 'r') as f:
        content = f.read()
    
    # 解析字符串为字典
    try:
        # 使用ast安全地评估字符串
        data_dict = ast.literal_eval(content)
        img_data = data_dict.get('img')
        
        # 获取时间戳并转换为可读格式
        unix_timestamp = data_dict.get('my_time_stamp')
        if unix_timestamp:
            # 转换Unix时间戳为可读时间
            timestamp = datetime.datetime.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        else:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    except (SyntaxError, ValueError) as e:
        print(f"解析文件内容时出错: {e}")
        return
    
    # 将二进制数据转换为图像
    try:
        image = Image.open(io.BytesIO(img_data))
        
        # 创建一个新图像，包含原始图像和标题
        draw = ImageDraw.Draw(image)
        
        # 使用默认字体
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()
        
        # 在图片顶部绘制时间戳和帧号
        draw.text((10, 10), f"FRAME: {frame_number} | TIME: {timestamp}", fill=(255, 0, 0), font=font)
        
        # 保存图像到pictures目录
        output_path = f"pictures/frame_{frame_number}.jpg"
        image.save(output_path)
        print(f"图像已保存为 {output_path}")
        
    except Exception as e:
        print(f"处理图像时出错: {e}")

if __name__ == "__main__":
    # 读取camera.msg文件的所有帧
    read_msg_file(r"D:\code\dog_data\3.31\camera.msg")