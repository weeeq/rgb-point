import os
import open3d as o3d
import numpy as np

# 直接在代码中定义配置
CONFIG = {
    "folder_path":r"D:\code\dog_data\3.31\pictures_lidar",
    "max_files": 300
}

def read_ply_files_in_folder(folder_path, max_files=-1):
    """
    读取指定文件夹中的PLY文件
    
    参数:
        folder_path: 包含PLY文件的文件夹路径
        max_files: 最大读取文件数，-1表示读取全部
        
    返回:
        point_clouds: 包含所有点云的列表
        file_names: 对应的文件名列表
    """
    point_clouds = []
    file_names = []
    
    # 确保文件夹路径存在
    if not os.path.exists(folder_path):
        raise ValueError(f"文件夹路径不存在: {folder_path}")
    
    # 遍历文件夹中的所有文件
    ply_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.ply')]
    
    # 限制文件数量
    if max_files > 0 and max_files < len(ply_files):
        ply_files = ply_files[:max_files]
    
    for file_name in ply_files:
        file_path = os.path.join(folder_path, file_name)
        print(f"正在读取: {file_path}")
        
        try:
            # 使用Open3D读取PLY文件
            pcd = o3d.io.read_point_cloud(file_path)
            point_clouds.append(pcd)
            file_names.append(file_name)
            
            # 打印点云的基本信息
            print(f"点数量: {len(pcd.points)}")
            if pcd.has_colors():
                print(f"包含颜色信息")
            if pcd.has_normals():
                print(f"包含法线信息")
            
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {str(e)}")
    
    print(f"共读取了 {len(point_clouds)} 个PLY文件")
    return point_clouds, file_names

def visualize_point_clouds(point_clouds, file_names=None):
    """
    可视化点云数据
    
    参数:
        point_clouds: 点云对象的列表
        file_names: 对应的文件名列表(可选)
    """
    if not point_clouds:
        print("没有点云可以显示")
        return
    
    # 如果只有一个点云，直接显示
    if len(point_clouds) == 1:
        o3d.visualization.draw_geometries([point_clouds[0]], 
                                         window_name=file_names[0] if file_names else "点云显示")
        return
    
    # 如果有多个点云，可以选择合并显示或单独显示
    print("1. 合并所有点云显示")
    print("2. 单独显示每个点云")
    choice = input("请选择显示方式 (1/2): ")
    
    if choice == "1":
        # 合并所有点云
        combined = o3d.geometry.PointCloud()
        for i, pcd in enumerate(point_clouds):
            # 为每个点云设置不同的颜色以区分
            if not pcd.has_colors():
                # 随机生成一个颜色
                color = np.random.rand(3)
                pcd.paint_uniform_color(color)
            combined += pcd
        
        o3d.visualization.draw_geometries([combined], window_name="合并点云显示")
    else:
        # 单独显示每个点云
        for i, pcd in enumerate(point_clouds):
            o3d.visualization.draw_geometries([pcd], 
                                             window_name=file_names[i] if file_names else f"点云 {i+1}")

if __name__ == "__main__":
    # 使用内部配置
    folder_path = CONFIG["folder_path"]
    max_files = CONFIG["max_files"]
    
    print(f"使用内部配置: 文件夹路径={folder_path}, 最大文件数={max_files}")
    
    # 读取PLY文件
    point_clouds, file_names = read_ply_files_in_folder(folder_path, max_files)
    
    # 可视化点云
    if point_clouds:
        visualize_point_clouds(point_clouds, file_names) 