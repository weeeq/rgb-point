import numpy as np
import ast
import struct
import open3d as o3d
import os
import glob

def parse_point_cloud_data(file_path):
    """从txt文件解析点云数据"""
    with open(file_path, 'r') as f:
        data_str = f.read()
    
    # 将字符串转换为Python字典
    data_dict = ast.literal_eval(data_str)
    
    # 从数据字典中提取关键参数
    point_step = data_dict['point_step']
    width = data_dict['width']
    height = data_dict['height']
    data_bytes = bytes(data_dict['data'])
    
    # 计算总点数
    total_points = width * height
    
    # 创建NumPy数组以存储点云数据
    points = np.zeros((total_points, 3), dtype=np.float32)
    colors = np.zeros((total_points, 3), dtype=np.float32)
    
    for i in range(total_points):
        offset = i * point_step
        point_data = data_bytes[offset:offset+point_step]
        
        x = struct.unpack_from('f', point_data, 0)[0]
        y = struct.unpack_from('f', point_data, 4)[0]
        z = struct.unpack_from('f', point_data, 8)[0]
        intensity = struct.unpack_from('f', point_data, 12)[0]
        
        points[i] = [x, y, z]
        # 根据强度值设置颜色（灰度）
        norm_intensity = min(intensity / 255.0, 1.0)
        colors[i] = [norm_intensity, norm_intensity, norm_intensity]
    
    # 创建Open3D点云对象
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    
    return pcd

def main():
    # 定义输入和输出目录
    input_dir = r"D:\code\dog_data\3.31\frames_lidar"
    output_dir = r"D:\code\dog_data\3.31\pictures_lidar"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有输入文件并排序
    input_files = sorted(glob.glob(os.path.join(input_dir, "*.txt")))
    
    print(f"找到 {len(input_files)} 个点云数据文件")
    
    # 批量处理每个文件
    for i, input_file in enumerate(input_files):
        print(f"正在处理文件 {os.path.basename(input_file)} ({i+1}/{len(input_files)})...")
        
        # 解析点云数据
        pcd = parse_point_cloud_data(input_file)
        
        # 创建对应的输出文件名
        output_file = os.path.join(output_dir, f"{i}.ply")
        
        # 保存为PLY文件
        o3d.io.write_point_cloud(output_file, pcd)
        print(f"已解析 {len(pcd.points)} 个点，保存到 {output_file}")
    
    print("所有文件处理完成")

if __name__ == "__main__":
    main() 