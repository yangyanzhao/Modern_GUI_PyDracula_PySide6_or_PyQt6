def hex_to_rgb(hex_color):
    """将16进制颜色转换为RGB元组"""
    hex_color = hex_color.lstrip('#')  # 去掉 # 号
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    """将RGB元组转换为16进制颜色"""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def invert_color(hex_color):
    """计算16进制颜色的反色"""
    # 将16进制颜色转换为RGB
    rgb = hex_to_rgb(hex_color)
    # 对每个RGB分量取反
    inverted_rgb = tuple(255 - value for value in rgb)
    # 将反色RGB转换回16进制
    return rgb_to_hex(inverted_rgb)


def calculate_luminance(rgb):
    """计算颜色的相对亮度"""
    r, g, b = [x / 255.0 for x in rgb]
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def calculate_contrast(color1, color2):
    """计算两种颜色的对比度"""
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    luminance1 = calculate_luminance(rgb1)
    luminance2 = calculate_luminance(rgb2)
    if luminance1 > luminance2:
        return (luminance1 + 0.05) / (luminance2 + 0.05)
    else:
        return (luminance2 + 0.05) / (luminance1 + 0.05)


def get_max_contrast_color(hex_color):
    """计算与给定颜色对比度最高的颜色（纯黑或纯白）"""
    black = "#000000"
    white = "#FFFFFF"
    contrast_with_black = calculate_contrast(hex_color, black)
    contrast_with_white = calculate_contrast(hex_color, white)
    return black if contrast_with_black > contrast_with_white else white


def find_closest_color_optimized(target_luminance):
    """优化版：找到与目标亮度最接近的16进制颜色"""
    min_diff = float('inf')
    closest_color = "#000000"
    # 限制搜索范围（亮度在目标亮度的 ±0.1 范围内）
    lower_bound = max(0, int((target_luminance - 0.1) * 255))
    upper_bound = min(255, int((target_luminance + 0.1) * 255))
    for r in range(lower_bound, upper_bound + 1):
        for g in range(lower_bound, upper_bound + 1):
            for b in range(lower_bound, upper_bound + 1):
                rgb = (r, g, b)
                luminance = calculate_luminance(rgb)
                diff = abs(luminance - target_luminance)
                if diff < min_diff:
                    min_diff = diff
                    closest_color = rgb_to_hex(rgb)
    return closest_color


def get_color_with_contrast(hex_color, target_contrast):
    """根据给定颜色和目标对比度，计算对应的16进制颜色"""
    # 计算给定颜色的相对亮度
    rgb = hex_to_rgb(hex_color)
    luminance1 = calculate_luminance(rgb)
    # 计算目标颜色的相对亮度
    luminance2 = (luminance1 + 0.05) / target_contrast - 0.05
    # 找到与目标亮度最接近的颜色
    return find_closest_color_optimized(luminance2)


def calculate_brightness(rgb):
    """计算颜色的亮度"""
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def adjust_brightness(hex_color, factor):
    """调整颜色的亮度"""
    rgb = hex_to_rgb(hex_color)
    brightness = calculate_brightness(rgb)

    # 调整亮度
    new_rgb = tuple(min(max(int(c * factor), 0), 255) for c in rgb)

    return rgb_to_hex(new_rgb)


if __name__ == '__main__':
    # 示例一
    hex_color = "#336699"  # 输入16进制颜色
    inverted_color = invert_color(hex_color)
    print(f"底色: {hex_color}, 反色: {inverted_color}")
    # 示例二
    hex_color = "#336699"  # 输入16进制颜色
    max_contrast_color = get_max_contrast_color(hex_color)
    print(f"底色: {hex_color}, 对比度最高的颜色: {max_contrast_color}")
    # 示例三
    hex_color = "#336699"  # 输入16进制颜色
    target_contrast = 3  # 目标对比度
    result_color = get_color_with_contrast(hex_color, target_contrast)
    print(f"底色: {hex_color}, 目标对比度: {target_contrast}:1, 对应颜色: {result_color}")
    # 示例四
    hex_color = "#4a90e2"
    low_brightness_color = adjust_brightness(hex_color, 0.5)  # 降低亮度
    high_brightness_color = adjust_brightness(hex_color, 1.5)  # 增加亮度

    print(f"原始颜色: {hex_color}")
    print(f"低亮度颜色: {low_brightness_color}")
    print(f"高亮度颜色: {high_brightness_color}")
