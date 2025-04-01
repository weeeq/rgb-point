import msgpack
import numpy as np
import os

def read_msg_file(file_name, output_dir=None):
    # 创建输出目录（如果不存在）
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 以二进制方式读取文件
    with open(file_name, "rb") as f:
        # 使用流式解包
        unpacker = msgpack.Unpacker(f, raw=False)
        
        # 处理所有帧数据
        frame_count = 0
        for unpacked_dict in unpacker:
            print(f"读取到第{frame_count}帧数据")
            
            # 将数据保存为txt文件
            if output_dir:
                output_file = os.path.join(output_dir, f"frame_{frame_count}.txt")
                save_to_txt(unpacked_dict, output_file)
            
            frame_count += 1
    
    print(f"总共处理了{frame_count}帧数据")
    return frame_count

def save_to_txt(data, output_file):
    """将点云数据保存为txt文件"""
    with open(output_file, 'w') as f:
        # 假设点云数据在'points'或'cloud'键中
        # 根据实际数据结构调整这部分
        if 'points' in data:
            points = data['points']
        elif 'cloud' in data:
            points = data['cloud']
        else:
            # 如果找不到预期的键，则直接保存整个字典
            f.write(str(data))
            return
        
        # 如果points是二进制数据，需要先转换
        if isinstance(points, bytes):
            # 假设点云格式为浮点数x,y,z，每个点12字节
            points_array = np.frombuffer(points, dtype=np.float32).reshape(-1, 3)
            for point in points_array:
                f.write(f"{point[0]} {point[1]} {point[2]}\n")
        elif isinstance(points, list):
            # 如果已经是列表格式
            for point in points:
                if isinstance(point, dict):
                    # 如果每个点是字典格式 {x:val, y:val, z:val}
                    f.write(f"{point.get('x', 0)} {point.get('y', 0)} {point.get('z', 0)}\n")
                else:
                    # 如果每个点是数组格式 [x,y,z]
                    values = ' '.join(map(str, point))
                    f.write(f"{values}\n")
        else:
            # 其他未知格式，直接写入
            f.write(str(points))

# 读取雷达数据并保存所有帧到frames_lidar目录
read_msg_file(r"D:\code\dog_data\3.31\rt_utlidar_cloud_deskewed.msg", "frames_lidar")