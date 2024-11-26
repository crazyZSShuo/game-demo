import pygame
import os
from PIL import Image

def create_game_icon(size=256):
    """创建一个现代风格的俄罗斯方块图标"""
    pygame.init()
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    block_size = size // 4
    
    # 创建T形方块的形状（现代设计）
    t_shape = [
        [0, 1, 0],
        [1, 1, 1]
    ]
    
    # 定义渐变色（现代蓝色调）
    base_color = (64, 169, 255)  # 明亮的蓝色
    
    # 计算中心位置
    center_x = (size - len(t_shape[0]) * block_size) // 2
    center_y = (size - len(t_shape) * block_size) // 2
    
    # 绘制T形方块
    for i, row in enumerate(t_shape):
        for j, cell in enumerate(row):
            if cell:
                x = center_x + j * block_size
                y = center_y + i * block_size
                
                # 创建方块表面
                block = pygame.Surface((block_size, block_size), pygame.SRCALPHA)
                
                # 计算渐变色
                gradient_factor = 0.8 + 0.2 * (i + j) / 3
                color = tuple(min(255, int(c * gradient_factor)) for c in base_color)
                
                # 绘制主体
                pygame.draw.rect(block, (*color, 255), 
                               (1, 1, block_size-2, block_size-2), border_radius=block_size//8)
                
                # 添加高光效果
                highlight_color = tuple(min(255, int(c * 1.3)) for c in color)
                pygame.draw.rect(block, (*highlight_color, 180), 
                               (1, 1, block_size-2, block_size-2), 
                               width=2, border_radius=block_size//8)
                
                # 将方块绘制到主表面
                surface.blit(block, (x, y))
    
    # 保存为PNG
    pygame.image.save(surface, "app_icon_256.png")
    
    # 转换为ICO
    img = Image.open("app_icon_256.png")
    # 创建多个尺寸的图标
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    icons = []
    for size in icon_sizes:
        icons.append(img.resize(size, Image.Resampling.LANCZOS))
    
    # 确保assets/textures目录存在
    os.makedirs("assets/textures", exist_ok=True)
    
    # 保存为ICO文件
    icons[0].save("assets/textures/app_icon.ico", 
                 format='ICO', 
                 sizes=icon_sizes,
                 quality=95)
    
    # 清理临时文件
    os.remove("app_icon_256.png")

if __name__ == "__main__":
    create_game_icon()
