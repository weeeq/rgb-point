import os
import open3d as o3d
import numpy as np
import time

# 直接在代码中定义配置
CONFIG = {
    "folder_path":r"D:\code\dog_data\3.31\pictures_lidar",
    "max_files": 200
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

def visualize_point_clouds_animation(point_clouds, file_names=None, delay_time=0.5):
    """
    以动画方式逐步显示点云叠加过程
    
    参数:
        point_clouds: 点云对象的列表
        file_names: 对应的文件名列表(可选)
        delay_time: 每次添加新点云的延迟时间(秒)，控制动画速度
    """
    if not point_clouds or len(point_clouds) == 0:
        print("没有点云可以显示")
        return
        
    # 创建累积点云系列（不添加颜色）
    cumulative_pcds = []
    current_combined = o3d.geometry.PointCloud()
    
    for i, pcd in enumerate(point_clouds):
        # 创建新点云
        temp_pcd = o3d.geometry.PointCloud()
        temp_pcd.points = o3d.utility.Vector3dVector(np.asarray(pcd.points))
        
        # 添加到当前累积点云
        current_combined += temp_pcd
        
        # 创建当前累积点云的副本
        current_copy = o3d.geometry.PointCloud()
        current_copy.points = o3d.utility.Vector3dVector(np.asarray(current_combined.points))
        
        # 添加到序列
        cumulative_pcds.append(current_copy)
        
        if file_names:
            print(f"准备点云: {file_names[i]}")
    
    print(f"已准备 {len(cumulative_pcds)} 个累积点云")
    
    # 创建自定义动画回调函数
    global current_frame
    current_frame = 0
    
    def animation_callback(vis):
        global current_frame
        if current_frame < len(cumulative_pcds):
            # 删除之前的几何体
            vis.clear_geometries()
            
            # 添加当前帧的累积点云
            vis.add_geometry(cumulative_pcds[current_frame], reset_bounding_box=False)
            
            if file_names and current_frame < len(file_names):
                print(f"添加点云: {file_names[current_frame]}")
                
            current_frame += 1
            
            # 如果是最后一帧，暂停更长时间
            time_to_wait = delay_time * 3 if current_frame == len(cumulative_pcds) else delay_time
            time.sleep(time_to_wait)
            
            return True
        else:
            return False
    
    # 创建自定义可视化器
    try:
        print("开始动画显示，请等待...")
        custom_draw_geometries_with_animation_callback(
            [cumulative_pcds[0]],  # 起始只显示第一个点云
            animation_callback,
            window_name="点云动画显示",
            width=1024,
            height=768
        )
        
        # 保存最终的叠加结果为final.ply
        if len(cumulative_pcds) > 0:
            final_pcd = cumulative_pcds[-1]
            output_path = "final.ply"
            try:
                o3d.io.write_point_cloud(output_path, final_pcd)
                print(f"最终点云已保存为: {output_path}")
            except Exception as save_error:
                print(f"保存点云文件失败: {str(save_error)}")
                
    except Exception as e:
        print(f"动画显示失败: {str(e)}")
        # 作为备选，显示最终合并的点云
        try:
            o3d.visualization.draw_geometries([cumulative_pcds[-1]], 
                                           window_name="合并点云显示",
                                           width=1024,
                                           height=768)
            
            # 即使动画显示失败，仍尝试保存最终点云
            output_path = "final.ply"
            try:
                o3d.io.write_point_cloud(output_path, cumulative_pcds[-1])
                print(f"最终点云已保存为: {output_path}")
            except Exception as save_error:
                print(f"保存点云文件失败: {str(save_error)}")
                
        except Exception as e2:
            print(f"备选显示方法也失败: {str(e2)}")

# 自定义函数，修改自Open3D的draw_geometries_with_animation_callback
def custom_draw_geometries_with_animation_callback(
    geometries, callback_function, window_name="Open3D", width=1024, height=768
):
    """
    自定义动画回调函数，解决Open3D动画问题
    """
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name=window_name, width=width, height=height)
    
    # 设置渲染选项
    opt = vis.get_render_option()
    opt.background_color = np.array([0, 0, 0])  # 黑色背景
    opt.point_size = 3.0  # 点的大小
    
    # 添加所有几何体
    for geometry in geometries:
        vis.add_geometry(geometry)
    
    # 注册回调
    vis.register_animation_callback(callback_function)
    
    # 运行可视化器
    vis.run()
    vis.destroy_window()

if __name__ == "__main__":
    # 使用内部配置
    folder_path = CONFIG["folder_path"]
    max_files = CONFIG["max_files"]
    
    print(f"使用内部配置: 文件夹路径={folder_path}, 最大文件数={max_files}")
    
    # 读取PLY文件
    point_clouds, file_names = read_ply_files_in_folder(folder_path, max_files)
    
    # 可视化点云 - 使用动画方式
    if point_clouds:
        # 设置动画速度（秒）- 数值越小，动画越快
        animation_speed = 0.5
        visualize_point_clouds_animation(point_clouds, file_names, delay_time=animation_speed)
        
        # 如果您仍想显示合并后的静态视图，可以取消下面的注释
        # visualize_point_clouds(point_clouds, file_names) 