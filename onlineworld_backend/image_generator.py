import requests
import base64
import os
import time
import random
import json
from datetime import datetime
from onlineworld_backend.config import Config
from PIL import Image
import io

# 配置API信息
SILICON_FLOW_API_KEY = Config.SILICON_FLOW_API_KEY
SILICON_FLOW_API_URL = Config.SILICON_FLOW_IMAGE_API_URL

# 确保保存目录存在
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

# 保存图片到文件
def save_image(image_data, width, height):
    # 确保保存目录存在
    save_dir = ensure_directory_exists(os.path.join(os.path.dirname(__file__), 'static', 'images'))
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    filename = f"generated_image_{timestamp}.png"
    filepath = os.path.join(save_dir, filename)
    
    # 保存图片
    try:
        # 如果是字节数据，直接写入文件
        if isinstance(image_data, bytes):
            with open(filepath, 'wb') as f:
                f.write(image_data)
        # 如果是PIL Image对象，保存为PNG
        elif hasattr(image_data, 'save'):
            image_data.save(filepath, 'PNG')
        else:
            raise TypeError("无法识别的图像数据类型")
        
        print(f"图片已保存: {filepath}")
        return filepath
    except Exception as e:
        print(f"保存图片失败: {str(e)}")
        raise

# 验证尺寸是否为支持的格式
def validate_dimensions(width, height):
    valid_dimensions = [(512, 512), (1024, 512)]
    if (width, height) not in valid_dimensions:
        raise ValueError(f"不支持的图片尺寸: {width}x{height}。请使用以下尺寸之一: {valid_dimensions}")
    return True

# 生成单张图片
def generate_image(prompt, width=512, height=512):
    """
    使用硅基流动大模型生成一张图片
    
    参数:
        prompt (str): 图像生成提示词
        
    返回:
        str: 生成的图片保存路径
    """
    
    try:
        # 构建请求头
        headers = {
            "Authorization": f"Bearer {SILICON_FLOW_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 构建请求体
        payload = {
            "model": Config.AI_IMAGE_MODEL_NAME,  # 使用Stable Diffusion模型
            "prompt": "真实世界实拍，冷色调，" + prompt,
            "image_size": f"{width}x{height}",
            "batch_size": 1,  # 生成1张图片
            "num_inference_steps": 20,
            "guidance_scale": 7.5,
            "cfg": 10.05,
        }
        
        # 发送请求
        print(f"正在生成图片: {prompt} ({width}x{height})")
        response = requests.post(SILICON_FLOW_API_URL, headers=headers, json=payload)
        
        # 打印完整的API响应内容，帮助调试
        # print("\n=== API响应详情 ===")
        # print(f"状态码: {response.status_code}")
        # print(f"响应头: {response.headers}")
        # print(f"响应内容: {response.text}")
        # print("==================\n")
        
        response.raise_for_status()
        
        # 解析响应数据
        data = response.json()
        
        # 处理响应
        # 检查响应是否包含图片数据 - 尝试多种可能的数据结构
        if 'data' in data and len(data['data']) > 0:
            if 'b64_json' in data['data'][0]:
                # 解码base64图片数据
                image_data = base64.b64decode(data['data'][0]['b64_json'])
            elif 'b64' in data['data'][0]:
                base64_image = data['data'][0]['b64']
                # 移除可能的前缀
                if base64_image.startswith('data:image/'):
                    base64_image = base64_image.split(',')[1]
                image_data = base64.b64decode(base64_image)
            elif 'url' in data['data'][0]:
                # 从URL获取图片数据
                # print(f"从URL获取图片: {data['data'][0]['url']}")
                image_response = requests.get(data['data'][0]['url'])
                image_response.raise_for_status()
                image_data = image_response.content
            else:
                # 打印响应数据结构，帮助调试
                print("错误: API响应中不包含可识别的图片数据格式！")
                print(f"响应数据结构: {json.dumps(data, ensure_ascii=False, indent=2)}")
                raise ValueError("API响应中不包含可识别的图片数据格式")
        else:
            # 打印响应数据结构，帮助调试
            print("错误: API响应中不包含图片数据！")
            print(f"响应数据结构: {json.dumps(data, ensure_ascii=False, indent=2)}")
            raise ValueError("API响应中不包含图片数据")
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"generated_image_{timestamp}.png"
        
        # 确保保存目录存在
        save_dir = ensure_directory_exists(os.path.join(os.path.dirname(__file__), 'static', 'images'))
        filepath = os.path.join(save_dir, filename)
        
        # 保存图片
        with open(filepath, 'wb') as f:
            f.write(image_data)
            
        print(f"图片已保存: {filepath}")
        return filepath
    
    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {str(e)}")
        raise
    
    except Exception as e:
        print(f"图片生成过程中发生未知错误: {str(e)}")
        raise

# 批量生成多张图片
def generate_multiple_images(prompts, width=512, height=512):
    """
    批量生成多张图片
    
    参数:
        prompts (list): 提示词列表，每个提示词生成一张图片
        
    返回:
        list: 生成的图片路径列表
    """
    
    image_paths = []
    for i, prompt in enumerate(prompts):
        try:
            print(f"正在生成图片: {prompt} (image {i+1}/{len(prompts)})")
            image_path = generate_image(prompt, width, height)
            image_paths.append(image_path)
        except Exception as e:
            print(f"生成图片失败 (image {i+1}): {str(e)}")
            # 继续尝试生成其他图片
    
    return image_paths

if __name__ == "__main__":
    # 示例使用
    try:
        # 生成单张图片
        print("===== 生成单张图片 =====")
        image_path = generate_image(
            prompt="一个简单的小房子",
            width=512,
            height=512
        )
        print(f"单张图片生成完成: {image_path}")
        
        # # 生成多张不同尺寸的图片
        # print("\n===== 生成多张图片 =====")
        # prompts = [
        #     "像素风格的树",
        #     "像素风格的人物",
        #     "像素风格的风景"
        # ]
        # multiple_paths = generate_multiple_images(
        #     prompts=prompts,
        #     width=1024,
        #     height=512
        # )
        # print(f"多张图片生成完成，成功生成 {len(multiple_paths)} 张图片")
        
    except Exception as e:
        print(f"程序运行出错: {str(e)}")