import pygame
import numpy as np

def create_icon(size=32):
    """创建一个现代风格的俄罗斯方块图标"""
    # 创建surface
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # 定义方块的大小
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
                               (1, 1, block_size-2, block_size-2))
                
                # 添加高光效果
                highlight_color = tuple(min(255, int(c * 1.3)) for c in color)
                pygame.draw.line(block, (*highlight_color, 180), 
                               (1, 1), (block_size-2, 1))
                pygame.draw.line(block, (*highlight_color, 180), 
                               (1, 1), (1, block_size-2))
                
                # 添加阴影效果
                shadow_color = tuple(int(c * 0.7) for c in color)
                pygame.draw.line(block, (*shadow_color, 180), 
                               (block_size-2, 1), (block_size-2, block_size-2))
                pygame.draw.line(block, (*shadow_color, 180), 
                               (1, block_size-2), (block_size-2, block_size-2))
                
                # 将方块绘制到主表面
                surface.blit(block, (x, y))
    
    return surface

def save_icon(size=32):
    """保存图标为文件"""
    icon = create_icon(size)
    pygame.image.save(icon, "assets/textures/icon.png")

if __name__ == "__main__":
    pygame.init()
    save_icon()
    pygame.quit()
