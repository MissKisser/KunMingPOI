# -*- coding: utf-8 -*-
# @author Hackerdallas
# POI数据格式转换与坐标标准化工具

import pandas as pd
import numpy as np
import os
import time


def generate_category_label(index):
    """
    根据序号生成类别标签
    0-25 → A-Z, 26-51 → AA-AZ, 52-77 → BA-BZ, ...
    """
    if index < 26:
        return chr(ord('A') + index)
    else:
        first = chr(ord('A') + (index // 26) - 1)
        second = chr(ord('A') + (index % 26))
        return first + second


def min_max_normalize(values, scale_factor=2000):
    """
    Min-Max线性缩放标准化
    将数值映射到 [0, scale_factor] 范围
    """
    v_min = values.min()
    v_max = values.max()
    if v_max == v_min:
        return np.zeros(len(values))
    return (values - v_min) / (v_max - v_min) * scale_factor


def detect_encoding(file_path):
    """
    自动检测CSV文件编码，通过实际解析验证
    """
    encodings = ['utf-8-sig', 'utf-8', 'gb18030', 'gbk', 'gb2312', 'latin-1']
    for enc in encodings:
        try:
            pd.read_csv(file_path, encoding=enc, nrows=10)
            return enc
        except Exception:
            continue
    return 'utf-8'


def convert_poi_data(input_csv, output_data, scale_factor=2000):
    """
    将POI CSV数据转换为算法所需的 .data 格式

    参数:
        input_csv: 输入CSV文件路径
        output_data: 输出.data文件路径
        scale_factor: 标准化缩放系数，默认2000
    """
    start_time = time.time()

    # 检测编码并读取CSV
    encoding = detect_encoding(input_csv)
    print(f"检测到文件编码: {encoding}")
    print(f"正在读取CSV文件...")

    df = pd.read_csv(input_csv, encoding=encoding)
    total_rows = len(df)
    print(f"读取完成，共 {total_rows} 条数据")

    # 获取列名
    col_names = df.columns.tolist()
    print(f"列名: {col_names}")

    # 根据列索引定位（名称, 大类, 中类, 经度, 纬度, 省份, 地级市, 区县）
    col_category = col_names[1]   # 大类列
    col_lng = col_names[3]        # 经度列
    col_lat = col_names[4]        # 纬度列

    # 执行经纬度特征字段的数值向量化校验与非标准格式元组剔除
    df[col_lng] = pd.to_numeric(df[col_lng], errors='coerce')
    df[col_lat] = pd.to_numeric(df[col_lat], errors='coerce')
    invalid_count = df[col_lng].isna().sum() + df[col_lat].isna().sum()
    if invalid_count > 0:
        print(f"发现 {invalid_count} 个无效经纬度值，已移除对应行")
        df = df.dropna(subset=[col_lng, col_lat])

    # 统计大类信息
    categories = df[col_category].unique()
    print(f"共发现 {len(categories)} 个大类: {list(categories)}")

    # 构建大类 → 字母标签的映射（按首次出现顺序）
    category_order = df[col_category].drop_duplicates().tolist()
    category_map = {}
    for i, cat in enumerate(category_order):
        category_map[cat] = generate_category_label(i)
    print("大类映射表:")
    for cat, label in category_map.items():
        count = (df[col_category] == cat).sum()
        print(f"  {cat} → {label} ({count} 条)")

    # Min-Max 标准化经纬度
    print(f"\n标准化前 - 经度范围: [{df[col_lng].min():.6f}, {df[col_lng].max():.6f}]")
    print(f"标准化前 - 纬度范围: [{df[col_lat].min():.6f}, {df[col_lat].max():.6f}]")

    df['norm_lng'] = min_max_normalize(df[col_lng].values, scale_factor)
    df['norm_lat'] = min_max_normalize(df[col_lat].values, scale_factor)

    print(f"标准化后 - 经度范围: [{df['norm_lng'].min():.6f}, {df['norm_lng'].max():.6f}]")
    print(f"标准化后 - 纬度范围: [{df['norm_lat'].min():.6f}, {df['norm_lat'].max():.6f}]")

    # 分配类别字母标签
    df['label'] = df[col_category].map(category_map)

    # 按类别分组生成组内序号（每个类别从1开始）
    df['seq'] = df.groupby('label').cumcount() + 1

    # 按类别字母排序，保证同类别的数据连续排列
    df = df.sort_values(by=['label', 'seq']).reset_index(drop=True)

    # 写出 .data 文件（制表符分隔: 序号 类别 标准化经度 标准化纬度）
    print(f"\n正在写入输出文件: {output_data}")
    output_df = df[['seq', 'label', 'norm_lng', 'norm_lat']]
    output_df.to_csv(output_data, sep='\t', header=False, index=False)

    elapsed = time.time() - start_time
    print(f"\n转换完成！")
    print(f"  输入行数: {total_rows}")
    print(f"  输出行数: {len(output_df)}")
    print(f"  类别数量: {len(category_map)}")
    print(f"  缩放系数: {scale_factor}")
    print(f"  耗时: {elapsed:.2f} 秒")
    print(f"  输出文件: {os.path.abspath(output_data)}")

    return category_map


if __name__ == "__main__":
    input_file = r"d:\document\Projects\KunmingPIO\昆明市POI数据.csv"
    output_file = r"d:\document\Projects\KunmingPIO\kunming_poi.data"
    scale = 2000

    category_map = convert_poi_data(input_file, output_file, scale)

    # 输出映射表到文件，供后续参考
    map_file = r"d:\document\Projects\KunmingPIO\category_map.txt"
    with open(map_file, 'w', encoding='utf-8') as f:
        f.write("大类名称\t映射字母\n")
        for cat, label in category_map.items():
            f.write(f"{cat}\t{label}\n")
    print(f"\n映射表已保存: {map_file}")
