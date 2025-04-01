import open3d as o3d

# 读取PLY文件
def read_ply(file_path):
    # 加载点云
    point_cloud = o3d.io.read_point_cloud(file_path)
    
    # 显示点云基本信息
    print(f"点云中点的数量: {len(point_cloud.points)}")
    print(f"点云包含颜色信息: {point_cloud.has_colors()}")
    print(f"点云包含法向量信息: {point_cloud.has_normals()}")
    
    # 返回点云对象
    return point_cloud

# 可选：显示点云
def visualize_point_cloud(point_cloud):
    o3d.visualization.draw_geometries([point_cloud])

if __name__ == "__main__":
    # 请修改为您的PLY文件路径
    file_path = r"D:\code\rgb-point\final.ply"
    
    # 读取点云
    pcd = read_ply(file_path)
    
    # 可视化点云（如果不需要可视化，可以注释掉这一行）
    visualize_point_cloud(pcd) 