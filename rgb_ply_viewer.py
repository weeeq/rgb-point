import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import open3d as o3d
import sys
import re
import matplotlib
from matplotlib.font_manager import FontProperties

# 假设这些是您项目中的模块
sys.path.append('dog_data')
try:
    from utils.map import get_mapping_relationship  # 导入您的映射关系函数
    from utils.datetrans import convert_time  # 如果需要时间转换
except ImportError:
    print("无法导入映射模块，请确保路径正确")

# 设置支持中文显示的字体
# 尝试设置微软雅黑或其他支持中文的字体
try:
    # 可以尝试多种中文字体
    font_paths = [
        'C:/Windows/Fonts/SimHei.ttf',  # 黑体
        'C:/Windows/Fonts/SimSun.ttf',  # 宋体
        'C:/Windows/Fonts/Microsoft YaHei.ttf',  # 微软雅黑
        'C:/Windows/Fonts/msyh.ttf',  # 微软雅黑（另一个可能的文件名）
        '/System/Library/Fonts/PingFang.ttc'  # macOS 中文字体
    ]
    
    # 检查字体文件是否存在，使用第一个找到的字体
    chinese_font_path = None
    for path in font_paths:
        if os.path.exists(path):
            chinese_font_path = path
            break
    
    if chinese_font_path:
        chinese_font = FontProperties(fname=chinese_font_path)
        matplotlib.rcParams['font.family'] = ['sans-serif']
        # 对于某些matplotlib版本可能需要以下设置
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
        plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
    else:
        print("警告：未找到中文字体文件，将使用英文标题")
        # 如果找不到中文字体，就使用英文标题
        use_english_titles = True
except Exception as e:
    print(f"设置中文字体时出错: {e}")
    use_english_titles = True
    
# 默认使用中文标题
use_english_titles = False

# 添加全局变量来保存视图参数
last_view_params = {
    'elev': None,
    'azim': None,
    'xlim': None,
    'ylim': None,
    'zlim': None
}

# 直接定义PLY读取函数，不再从外部模块导入
def read_ply(ply_path):
    """读取PLY文件并返回点云数据"""
    pcd = o3d.io.read_point_cloud(ply_path)
    return pcd

def find_corresponding_files(rgb_dir, ply_dir):
    """
    根据特定的映射关系找到对应的RGB图像和PLY文件
    """
    # 定义精确的映射关系 - (rgb索引, ply索引)
    index_mapping = [
        (0, 0), (1, 1), (2, 3), (3, 4), (4, 6), (5, 7), (6, 9), (7, 10), (8, 12), (9, 13), 
        (10, 14), (11, 16), (12, 17), (13, 19), (14, 20), (15, 22), (16, 23), (17, 25), 
        (18, 26), (19, 27), (20, 29), (21, 30), (22, 32), (23, 33), (24, 35), (25, 36), 
        (26, 38), (27, 39), (28, 40), (29, 42), (30, 43), (31, 45), (32, 46), (33, 48), 
        (34, 49), (35, 51), (36, 52), (37, 53), (38, 55), (39, 56), (40, 58), (41, 59), 
        (42, 61), (43, 62), (44, 63), (45, 65), (46, 66), (47, 68), (48, 69), (49, 71), 
        (50, 72), (51, 74), (52, 75), (53, 76), (54, 78), (55, 79), (56, 81), (57, 82), 
        (58, 84), (59, 85), (60, 87), (61, 88), (62, 89), (63, 91), (64, 92), (65, 94), 
        (66, 95), (67, 97), (68, 98), (69, 100), (70, 101), (71, 102), (72, 104), (73, 105), 
        (74, 107), (75, 108), (76, 110), (77, 111), (78, 113), (79, 114), (80, 115), (81, 117), 
        (82, 118), (83, 120), (84, 121), (85, 123), (86, 124), (87, 126), (88, 127), (89, 128), 
        (90, 130), (91, 131), (92, 133), (93, 134), (94, 136), (95, 137), (96, 139), (97, 140), 
        (98, 141), (99, 143), (100, 144), (101, 146), (102, 147), (103, 149), (104, 150), 
        (105, 152), (106, 153), (107, 154), (108, 156), (109, 157), (110, 159), (111, 160), 
        (112, 162), (113, 163), (114, 164), (115, 166), (116, 167), (117, 169), (118, 170), 
        (119, 172), (120, 173), (121, 175), (122, 176), (123, 177), (124, 179), (125, 180),
        (126, 182), (127, 183), (128, 185), (129, 186), (130, 188), (131, 189), (132, 190), 
        (133, 192), (134, 193), (135, 195), (136, 196), (137, 198), (138, 199), (139, 201), 
        (140, 202), (141, 203), (142, 205), (143, 206), (144, 208), (145, 209), (146, 211), 
        (147, 212), (148, 214), (149, 215), (150, 216), (151, 218), (152, 219), (153, 221), 
        (154, 222), (155, 224), (156, 225), (157, 227), (158, 228), (159, 229), (160, 231), 
        (161, 232), (162, 234), (163, 235), (164, 237), (165, 238), (166, 240), (167, 241), 
        (168, 242), (169, 244), (170, 245), (171, 247), (172, 248), (173, 250), (174, 251), 
        (175, 253), (176, 254), (177, 255), (178, 257), (179, 258), (180, 260), (181, 261), 
        (182, 263), (183, 264), (184, 265), (185, 267), (186, 268), (187, 270), (188, 271), 
        (189, 273), (190, 274), (191, 276), (192, 277), (193, 278), (194, 280), (195, 281), 
        (196, 283), (197, 284), (198, 286), (199, 287), (200, 289), (201, 290), (202, 291), 
        (203, 293), (204, 294), (205, 296), (206, 297), (207, 299), (208, 300), (209, 302), 
        (210, 303), (211, 304), (212, 306), (213, 307), (214, 309), (215, 310), (216, 312), 
        (217, 313), (218, 315), (219, 316), (220, 317), (221, 319), (222, 320), (223, 322), 
        (224, 323), (225, 325), (226, 326), (227, 328), (228, 329), (229, 330), (230, 332), 
        (231, 333), (232, 335), (233, 336), (234, 338), (235, 339), (236, 341), (237, 342), 
        (238, 343), (239, 345), (240, 346), (241, 348), (242, 349), (243, 351), (244, 352), 
        (245, 354), (246, 355), (247, 356), (248, 358), (249, 359), (250, 361), (251, 362), 
        (252, 364), (253, 365), (254, 366), (255, 368), (256, 369), (257, 371), (258, 372), 
        (259, 374), (260, 375), (261, 377), (262, 378), (263, 379), (264, 381), (265, 382), 
        (266, 384), (267, 385), (268, 387), (269, 388), (270, 390), (271, 391), (272, 392), 
        (273, 394), (274, 395), (275, 397), (276, 398), (277, 400), (278, 401), (279, 403), 
        (280, 404), (281, 405), (282, 407), (283, 408), (284, 410), (285, 411), (286, 413), 
        (287, 414), (288, 416), (289, 417)
    ]
    
    # 获取文件列表
    rgb_files = [f for f in os.listdir(rgb_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    ply_files = [f for f in os.listdir(ply_dir) if f.endswith('.ply')]
    
    # 确保文件名按数字顺序排序
    # 从文件名中提取数字
    def extract_number(filename):
        match = re.search(r'(\d+)', filename)
        if match:
            return int(match.group(1))
        return 0
    
    # 按数字排序
    rgb_files = sorted(rgb_files, key=extract_number)
    ply_files = sorted(ply_files, key=extract_number)
    
    # 创建映射字典
    mapping = {}
    for rgb_idx, ply_idx in index_mapping:
        if rgb_idx < len(rgb_files) and ply_idx < len(ply_files):
            rgb_file = rgb_files[rgb_idx]
            ply_file = ply_files[ply_idx]
            mapping[rgb_file] = ply_file
            print(f"匹配: RGB索引 {rgb_idx} ({rgb_file}) -> PLY索引 {ply_idx} ({ply_file})")
        else:
            print(f"警告：索引超出范围 - RGB索引: {rgb_idx}, PLY索引: {ply_idx}")
    
    return mapping, index_mapping

def merge_point_clouds(pcd_list):
    """合并多个点云数据"""
    merged_pcd = o3d.geometry.PointCloud()
    for pcd in pcd_list:
        merged_pcd += pcd
    return merged_pcd

def get_surrounding_ply_files(ply_files, current_idx, range_before=15, range_after=15):
    """获取当前PLY文件前后指定范围内的PLY文件"""
    start_idx = max(0, current_idx - range_before)
    end_idx = min(len(ply_files), current_idx + range_after + 1)
    return ply_files[start_idx:end_idx]

def display_rgb_and_merged_ply(rgb_path, current_ply_path, ply_dir, ply_files, current_ply_idx):
    """显示RGB图像和合并的PLY点云数据"""
    global last_view_params  # 使用全局视图参数
    
    # 创建一个有两个子图的图形
    fig = plt.figure(figsize=(15, 7))
    
    # 读取RGB图像
    img = Image.open(rgb_path)
    
    # 在图像上直接添加标题文本
    try:
        # 准备绘图和字体
        draw = ImageDraw.Draw(img)
        
        # 使用之前找到的中文字体，或尝试使用系统默认字体
        font_size = 30
        if 'chinese_font_path' in locals() and chinese_font_path:
            try:
                font = ImageFont.truetype(chinese_font_path, font_size)
            except:
                # 如果加载指定字体失败，尝试系统字体
                font = ImageFont.load_default()
        else:
            # 尝试其他常见位置的字体
            try:
                # 再次尝试查找系统字体
                system_fonts = [
                    'C:/Windows/Fonts/simhei.ttf',  # Windows黑体
                    'C:/Windows/Fonts/simsun.ttc',  # Windows宋体
                    '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',  # Linux
                    '/System/Library/Fonts/PingFang.ttc'  # macOS
                ]
                
                font_found = False
                for font_path in system_fonts:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, font_size)
                        font_found = True
                        break
                
                if not font_found:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
        
        # 提取文件名，用于显示
        rgb_filename = os.path.basename(rgb_path)
        ply_filename = os.path.basename(ply_files[current_ply_idx])
        
        # 准备显示的文本
        title_text = f"RGB图像: {rgb_filename}"
        
        # 在图像顶部绘制白色背景条
        text_width, text_height = draw.textsize(title_text, font=font) if hasattr(draw, 'textsize') else (font_size * len(title_text) * 0.6, font_size * 1.5)
        padding = 10
        draw.rectangle([(0, 0), (img.width, text_height + padding*2)], fill=(0, 0, 0, 180))
        
        # 在背景上绘制白色文本
        text_position = (padding, padding)
        draw.text(text_position, title_text, fill=(255, 255, 255), font=font)
    except Exception as e:
        print(f"在图像上添加文本时出错: {e}")
    
    # 显示RGB图像(不使用标题)
    ax1 = fig.add_subplot(121)
    ax1.imshow(img)
    ax1.axis('off')
    
    # 获取前后15帧的PLY文件
    surrounding_ply_files = get_surrounding_ply_files(ply_files, current_ply_idx)
    
    # 加载并合并点云
    pcd_list = []
    for ply_file in surrounding_ply_files:
        ply_path = os.path.join(ply_dir, ply_file)
        pcd = read_ply(ply_path)
        pcd_list.append(pcd)
    
    # 合并点云
    merged_pcd = merge_point_clouds(pcd_list)
    
    # 显示合并的PLY数据
    ax2 = fig.add_subplot(122, projection='3d')
    points = np.asarray(merged_pcd.points)
    
    # 如果点云有颜色
    if merged_pcd.has_colors():
        colors = np.asarray(merged_pcd.colors)
        ax2.scatter(points[:, 0], points[:, 1], points[:, 2], c=colors, s=1)
    else:
        # 否则使用深度作为颜色
        ax2.scatter(points[:, 0], points[:, 1], points[:, 2], c=points[:, 2], cmap='viridis', s=1)
    
    title_text = f'合并点云: {ply_filename} (前后共{len(surrounding_ply_files)}帧)'
    if use_english_titles:
        ax2.set_title(f'Merged Cloud: {ply_filename} (Total {len(surrounding_ply_files)} frames)')
    else:
        ax2.set_title(title_text, fontproperties=chinese_font if 'chinese_font' in locals() else None)
    
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_zlabel('Z')
    
    # 应用之前保存的视图参数（如果有）
    if last_view_params['elev'] is not None:
        ax2.view_init(elev=last_view_params['elev'], azim=last_view_params['azim'])
        if last_view_params['xlim'] is not None:
            ax2.set_xlim(last_view_params['xlim'])
            ax2.set_ylim(last_view_params['ylim'])
            ax2.set_zlim(last_view_params['zlim'])
    
    plt.tight_layout()
    
    # 显示图像并保存关闭前的视图参数
    plt.show(block=False)  # 非阻塞显示
    
    # 等待用户调整视图并关闭窗口
    while plt.fignum_exists(fig.number):
        plt.pause(0.1)  # 短暂暂停以便处理GUI事件
        # 保存当前视图参数
        last_view_params['elev'] = ax2.elev
        last_view_params['azim'] = ax2.azim
        last_view_params['xlim'] = ax2.get_xlim()
        last_view_params['ylim'] = ax2.get_ylim()
        last_view_params['zlim'] = ax2.get_zlim()
    
    # 用户关闭窗口后继续

def main():
    # 设置RGB图像和PLY文件的目录
    rgb_dir = r'D:\code\dog_data\3.31\pictures'  # 请替换为实际的RGB图像目录
    ply_dir = r'D:\code\dog_data\3.31\pictures_lidar'  # 请替换为实际的PLY文件目录
    
    # 找到对应的文件
    mapping, index_mapping = find_corresponding_files(rgb_dir, ply_dir)
    
    if not mapping:
        print("未找到匹配的文件对")
        return
    
    # 获取RGB文件列表和PLY文件列表并按数字排序
    rgb_files = [f for f in os.listdir(rgb_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    ply_files = [f for f in os.listdir(ply_dir) if f.endswith('.ply')]
    
    def extract_number(filename):
        match = re.search(r'(\d+)', filename)
        if match:
            return int(match.group(1))
        return 0
    
    rgb_files = sorted(rgb_files, key=extract_number)
    ply_files = sorted(ply_files, key=extract_number)
    
    # 按照映射关系顺序显示
    processed_pairs = set()  # 跟踪已处理的文件对
    
    for rgb_idx, ply_idx in index_mapping:
        if rgb_idx < len(rgb_files):
            rgb_file = rgb_files[rgb_idx]
            if rgb_file in mapping:
                ply_file = mapping[rgb_file]
                pair_key = (rgb_file, ply_file)
                
                # 确保每对文件只处理一次
                if pair_key not in processed_pairs:
                    processed_pairs.add(pair_key)
                    
                    rgb_path = os.path.join(rgb_dir, rgb_file)
                    current_ply_path = os.path.join(ply_dir, ply_file)
                    
                    # 获取当前PLY文件在ply_files中的索引
                    try:
                        current_ply_idx = ply_files.index(ply_file)
                    except ValueError:
                        print(f"错误：找不到PLY文件 {ply_file} 在文件列表中的索引")
                        continue
                    
                    print(f"显示: {rgb_file} 和 {ply_file} 及其周围PLY点云")
                    display_rgb_and_merged_ply(rgb_path, current_ply_path, ply_dir, ply_files, current_ply_idx)
                    # 当用户关闭窗口后，自动显示下一对图像
                    
    print("所有图像和点云已显示完毕")

if __name__ == "__main__":
    main() 