import pygame
import numpy as np
import os

def create_app_icon(size=512):
    """创建应用图标"""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # 填充渐变背景
    for y in range(size):
        progress = y / size
        color = (
            int(20 + 40 * progress),
            int(41 + 82 * progress),
            int(82 + 164 * progress)
        )
        pygame.draw.line(surface, color, (0, y), (size, y))
    
    # 创建Tetris方块组合
    block_size = size // 6
    shapes = [
        # T形
        {'shape': [(0, 0), (1, 0), (2, 0), (1, 1)], 'color': (64, 169, 255)},
        # L形
        {'shape': [(3, 1), (3, 2), (3, 3), (4, 3)], 'color': (255, 140, 0)},
        # I形
        {'shape': [(0, 4), (1, 4), (2, 4), (3, 4)], 'color': (0, 255, 255)}
    ]
    
    # 绘制方块
    for shape_data in shapes:
        shape = shape_data['shape']
        base_color = shape_data['color']
        
        for block in shape:
            x, y = block
            rect = pygame.Rect(
                size//4 + x * block_size,
                size//4 + y * block_size,
                block_size - 4,
                block_size - 4
            )
            
            # 绘制主体
            pygame.draw.rect(surface, base_color, rect)
            
            # 添加高光
            highlight = tuple(min(255, c + 50) for c in base_color)
            pygame.draw.line(surface, highlight, rect.topleft, rect.topright, 2)
            pygame.draw.line(surface, highlight, rect.topleft, rect.bottomleft, 2)
            
            # 添加阴影
            shadow = tuple(max(0, c - 50) for c in base_color)
            pygame.draw.line(surface, shadow, rect.bottomleft, rect.bottomright, 2)
            pygame.draw.line(surface, shadow, rect.topright, rect.bottomright, 2)
    
    return surface

def create_splash_screen(width=1080, height=1920):
    """创建启动画面"""
    surface = pygame.Surface((width, height))
    
    # 创建渐变背景
    for y in range(height):
        progress = y / height
        color = (
            int(20 + 20 * progress),
            int(41 + 41 * progress),
            int(82 + 82 * progress)
        )
        pygame.draw.line(surface, color, (0, y), (width, y))
    
    # 添加游戏标题
    font_size = width // 10
    try:
        font = pygame.font.Font(None, font_size)
    except:
        font = pygame.font.SysFont('arial', font_size)
    
    title = font.render("俄罗斯方块", True, (255, 255, 255))
    title_rect = title.get_rect(center=(width//2, height//2))
    
    # 添加光晕效果
    glow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(20, 0, -1):
        glow_color = (255, 255, 255, i)
        glow_rect = title.get_rect(center=(width//2, height//2))
        glow_rect.inflate_ip(i*2, i*2)
        pygame.draw.rect(glow_surface, glow_color, glow_rect)
    
    surface.blit(glow_surface, (0, 0))
    surface.blit(title, title_rect)
    
    return surface

def save_assets():
    """保存应用图标和启动画面"""
    pygame.init()
    
    # 确保目录存在
    os.makedirs("assets/textures", exist_ok=True)
    
    # 创建并保存图标
    icon = create_app_icon(512)
    pygame.image.save(icon, "assets/textures/app_icon.png")
    
    # 创建并保存启动画面
    splash = create_splash_screen(1080, 1920)
    pygame.image.save(splash, "assets/textures/splash.png")
    
    pygame.quit()

if __name__ == "__main__":
    save_assets()
