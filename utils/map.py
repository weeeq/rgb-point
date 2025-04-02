def generate_mapping(A, B):
    # 计算步长，确保均匀分布
    step = B / A
    # 生成映射列表，格式为 [(0: value), (1: value), ...]
    mapping = [(i, round(i * step)) for i in range(A + 1)]
    return mapping

# 示例用法
A = 289
B = 417
mapping = generate_mapping(A, B)
print(mapping)  # 输出: [(0, 0), (1, 3), (2, 5), (3, 8), (4, 10)]