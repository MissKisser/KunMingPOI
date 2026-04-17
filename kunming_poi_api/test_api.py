"""
后端API测试脚本 - 验证数据接口是否正常返回
作者：Hackerdallas
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_global_summary():
    """测试全局汇总接口"""
    print("\n" + "="*50)
    print("测试1: 全局汇总接口")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/global-summary", timeout=5)
        data = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if 'poi_total' in data:
            print(f"✓ POI总数: {data['poi_total']}")
        else:
            print("✗ 缺少 poi_total 字段")
            
        if 'pattern_total' in data:
            print(f"✓ 模式总数: {data['pattern_total']}")
        else:
            print("✗ 缺少 pattern_total 字段")
            
    except Exception as e:
        print(f"✗ 请求失败: {e}")

def test_category_stats():
    """测试类别统计接口"""
    print("\n" + "="*50)
    print("测试2: 类别统计接口")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/category-stats", timeout=5)
        data = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"类别数量: {len(data)}")
        
        if data:
            print("前3个类别:")
            for cat in data[:3]:
                print(f"  - {cat.get('category_name')}: {cat.get('poi_count')} 个POI")
        else:
            print("✗ 返回空数据")
            
    except Exception as e:
        print(f"✗ 请求失败: {e}")

def test_heatmap_data():
    """测试热力图数据接口"""
    print("\n" + "="*50)
    print("测试3: 热力图数据接口")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/poi-heatmap-data?limit=10", timeout=5)
        data = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"数据类型: {type(data)}")
        print(f"数据长度: {len(data)}")
        
        if isinstance(data, list) and len(data) > 0:
            print(f"✓ 返回数组，长度: {len(data)}")
            print("前3个POI数据:")
            for i, point in enumerate(data[:3]):
                print(f"  [{i+1}] lng={point.get('lng')}, lat={point.get('lat')}")
                
            # 验证数据格式
            first_point = data[0]
            if 'lng' in first_point and 'lat' in first_point:
                print(f"✓ 数据格式正确，包含 lng 和 lat 字段")
            else:
                print(f"✗ 数据格式错误: {list(first_point.keys())}")
        else:
            print("✗ 返回空数据或格式错误")
            
    except Exception as e:
        print(f"✗ 请求失败: {e}")

def test_fpi_ranking():
    """测试FPI排行榜接口"""
    print("\n" + "="*50)
    print("测试4: FPI排行榜接口")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/fpi-ranking?limit=5", timeout=5)
        data = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"模式数量: {len(data)}")
        
        if data:
            print("前5个高频模式:")
            for i, pattern in enumerate(data[:5]):
                print(f"  [{i+1}] {pattern.get('pattern_name')}: FPI={pattern.get('fpi_score')}")
                
            # 获取第一个pattern_id用于后续测试
            if data and 'pattern_id' in data[0]:
                return data[0]['pattern_id']
        else:
            print("✗ 返回空数据")
            
    except Exception as e:
        print(f"✗ 请求失败: {e}")
    
    return None

def test_pattern_instances(pattern_id):
    """测试模式实例接口"""
    if not pattern_id:
        print("\n" + "="*50)
        print("测试5: 模式实例接口")
        print("="*50)
        print("✗ 缺少 pattern_id，跳过测试")
        return
        
    print("\n" + "="*50)
    print(f"测试5: 模式实例接口 (pattern_id={pattern_id})")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/pattern-instances/{{pattern_id}}", timeout=5)
        data = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"实例数量: {len(data)}")
        
        if data:
            total_pois = sum(len(inst.get('pois', [])) for inst in data)
            print(f"✓ 返回 {len(data)} 个实例，包含 {total_pois} 个POI")
            
            # 验证第一个实例的数据结构
            first_inst = data[0]
            print(f"\n第一个实例结构:")
            print(f"  - instance_id: {first_inst.get('instance_id')}")
            print(f"  - center_lng: {first_inst.get('center_lng')}")
            print(f"  - center_lat: {first_inst.get('center_lat')}")
            print(f"  - pois数量: {len(first_inst.get('pois', []))}")
            
            if first_inst.get('pois'):
                print(f"\n第一个POI数据:")
                poi = first_inst['pois'][0]
                print(f"  - poi_id: {poi.get('poi_id')}")
                print(f"  - poi_name: {poi.get('poi_name')}")
                print(f"  - category_name: {poi.get('category_name')}")
                print(f"  - lng: {poi.get('lng')}")
                print(f"  - lat: {poi.get('lat')}")
        else:
            print("✗ 返回空数据")
            
    except Exception as e:
        print(f"✗ 请求失败: {e}")

def test_database_connection():
    """测试数据库连接"""
    print("\n" + "="*50)
    print("测试0: 数据库连接")
    print("="*50)
    
    try:
        # 通过全局汇总接口测试数据库连接
        response = requests.get(f"{BASE_URL}/global-summary", timeout=5)
        
        if response.status_code == 200:
            print("✓ 数据库连接正常")
            return True
        else:
            print(f"✗ 数据库连接异常，状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到后端服务，请确认:")
        print("   1. FastAPI 服务是否已启动 (python kunming_poi_api/main.py)")
        print("   2. 服务是否运行在 http://127.0.0.1:8000")
        return False
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("POI大屏后端API测试")
    print("作者: Hackerdallas")
    print("="*50)
    
    # 测试数据库连接
    if not test_database_connection():
        print("\n请先启动后端服务:")
        print("  cd kunming_poi_api")
        print("  python main.py")
        exit(1)
    
    # 执行所有测试
    test_global_summary()
    test_category_stats()
    test_heatmap_data()
    pattern_id = test_fpi_ranking()
    test_pattern_instances(pattern_id)
    
    print("\n" + "="*50)
    print("测试完成")
    print("="*50)