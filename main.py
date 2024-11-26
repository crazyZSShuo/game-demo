import asyncio
import pygame
import random
import json
import os
import numpy as np
from enum import Enum
import math
import sys

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# 创建和设置游戏图标
def create_game_icon(size=32):
    """创建一个现代风格的俄罗斯方块图标"""
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

# Constants
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# 资源路径
ASSETS_DIR = resource_path('assets')
AUDIO_DIR = os.path.join(ASSETS_DIR, 'audio')
TEXTURES_DIR = os.path.join(ASSETS_DIR, 'textures')

# 创建资源目录（仅在开发模式下）
if not hasattr(sys, '_MEIPASS'):
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(TEXTURES_DIR, exist_ok=True)

# Colors (金属质感色彩)
BLACK = (20, 20, 25)
WHITE = (240, 240, 245)
GRAY = (128, 128, 140)
COLORS = [
    (120, 180, 210),  # I - 浅蓝金属
    (100, 130, 180),  # J - 深蓝金属
    (180, 140, 100),  # L - 古铜金属
    (190, 180, 120),  # O - 金色金属
    (130, 170, 130),  # S - 绿色金属
    (150, 120, 160),  # T - 紫色金属
    (170, 120, 120),  # Z - 红色金属
]

# 3D效果参数
LIGHT_DIR = np.array([0.5, 0.5, 1.0])
METALLIC_SHINE = 0.8
ROUGHNESS = 0.2

# 动画效果参数
CLEAR_ANIMATION_DURATION = 800  # 毫秒
PARTICLE_COUNT = 50  # 粒子数量
PARTICLE_LIFETIME = 600  # 毫秒
GRID_ALPHA = 40  # 网格线透明度 (0-255)
FLASH_WAVES = 3  # 闪光波数

# 游戏机制参数
COMBO_TIMEOUT = 2000  # 连击超时时间（毫秒）
COMBO_BONUS = 50  # 每次连击的基础奖励分数
RAINBOW_EFFECT_DURATION = 3000  # 彩虹特效持续时间（毫秒）
LEVEL_UP_ANIMATION_DURATION = 1000  # 升级动画持续时间（毫秒）

# 彩虹色彩序列
RAINBOW_COLORS = [
    (255, 0, 0),    # 红
    (255, 165, 0),  # 橙
    (255, 255, 0),  # 黄
    (0, 255, 0),    # 绿
    (0, 0, 255),    # 蓝
    (75, 0, 130),   # 靛
    (238, 130, 238) # 紫
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0],      # J
     [1, 1, 1]],
    [[0, 0, 1],      # L
     [1, 1, 1]],
    [[1, 1],         # O
     [1, 1]],
    [[0, 1, 1],      # S
     [1, 1, 0]],
    [[0, 1, 0],      # T
     [1, 1, 1]],
    [[1, 1, 0],      # Z
     [0, 1, 1]]
]

class GameState(Enum):
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.original_color = color
        self.color = self._generate_particle_color(color)
        # 增加初始速度的变化范围
        self.vx = random.uniform(-8, 8)
        self.vy = random.uniform(-15, -5)
        self.lifetime = PARTICLE_LIFETIME
        self.original_lifetime = PARTICLE_LIFETIME
        self.size = random.randint(3, 6)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
        self.alpha = 255
        self.sparkle_timer = 0
        
    def _generate_particle_color(self, base_color):
        """生成基于基础颜色的随机粒子颜色"""
        r, g, b = base_color[:3]
        # 增加一些随机的明亮变化
        brightness = random.uniform(0.8, 1.2)
        r = min(255, max(0, int(r * brightness)))
        g = min(255, max(0, int(g * brightness)))
        b = min(255, max(0, int(b * brightness)))
        return (r, g, b)
        
    def update(self, dt):
        self.x += self.vx
        self.vy += 0.3  # 减小重力，使粒子飘得更久
        self.y += self.vy
        self.lifetime -= dt
        
        # 粒子旋转
        self.rotation += self.rotation_speed
        
        # 闪烁效果
        self.sparkle_timer += dt
        sparkle_factor = abs(math.sin(self.sparkle_timer * 0.01))
        self.alpha = max(0, int(255 * (self.lifetime / self.original_lifetime) * (0.7 + 0.3 * sparkle_factor)))
        
        # 随机改变速度，增加不规则性
        if random.random() < 0.1:
            self.vx += random.uniform(-0.5, 0.5)
            self.vy += random.uniform(-0.5, 0.5)
            
        return self.lifetime > 0
        
    def draw(self, screen):
        if self.alpha <= 0:
            return
            
        # 创建旋转的粒子表面
        size = self.size * 2
        particle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # 绘制发光效果
        glow_radius = self.size * 2
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_color = (*self.color[:3], 50)  # 半透明的发光
        pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
        
        # 绘制核心粒子
        color = (*self.color[:3], self.alpha)
        if random.random() < 0.5:  # 50%概率绘制方形粒子
            pygame.draw.rect(particle_surface, color, 
                           (size//4, size//4, size//2, size//2))
        else:  # 50%概率绘制圆形粒子
            pygame.draw.circle(particle_surface, color,
                             (size//2, size//2), self.size)
        
        # 旋转粒子
        rotated_particle = pygame.transform.rotate(particle_surface, self.rotation)
        
        # 绘制发光效果和粒子
        screen.blit(glow_surface, 
                   (int(self.x - glow_radius), int(self.y - glow_radius)))
        screen.blit(rotated_particle,
                   (int(self.x - rotated_particle.get_width()//2),
                    int(self.y - rotated_particle.get_height()//2)))

class ClearAnimation:
    def __init__(self, y, color):
        self.y = y * BLOCK_SIZE
        self.particles = []
        self.start_time = pygame.time.get_ticks()
        self.active = True
        self.flash_count = 0
        self.last_flash_time = self.start_time
        self.flash_interval = CLEAR_ANIMATION_DURATION / (FLASH_WAVES * 2)
        
        # 创建更多的粒子，分布在整行
        for _ in range(PARTICLE_COUNT):
            x = random.randint(0, GRID_WIDTH * BLOCK_SIZE)
            self.particles.append(Particle(x, self.y + BLOCK_SIZE/2, color))
    
    def update(self):
        current_time = pygame.time.get_ticks()
        dt = current_time - self.last_flash_time
        
        # 更新粒子
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # 更新闪光效果
        if dt >= self.flash_interval:
            self.flash_count += 1
            self.last_flash_time = current_time
        
        # 检查动画是否结束
        animation_time = current_time - self.start_time
        if animation_time >= CLEAR_ANIMATION_DURATION:
            self.active = len(self.particles) > 0
            
        return self.active
    
    def draw(self, screen):
        # 绘制闪光效果
        if self.flash_count < FLASH_WAVES * 2:
            flash_progress = (pygame.time.get_ticks() - self.last_flash_time) / self.flash_interval
            flash_alpha = int(255 * (1 - flash_progress) * 0.5)
            if flash_alpha > 0:
                flash_surface = pygame.Surface((GRID_WIDTH * BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                flash_surface.fill((255, 255, 255, flash_alpha))
                screen.blit(flash_surface, (0, self.y))
        
        # 绘制所有粒子
        for particle in self.particles:
            particle.draw(screen)

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('疯狂俄罗斯方块')
        
        # 设置游戏图标
        icon = create_game_icon(32)
        pygame.display.set_icon(icon)
        
        # Game state
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece = None
        self.piece_pos = [0, 0]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.state = GameState.PLAYING
        self.fall_time = 0
        self.fall_speed = 1000  # Start with 1 second
        
        # Touch control variables
        self.touch_start = None
        self.last_touch_move = None
        
        # Initialize pieces
        self.new_piece()
        
        # Load high score
        self.high_score = self.load_high_score()
        
        # Initialize clock
        self.clock = pygame.time.Clock()
        
        # 初始化音效字典
        self.sounds = {}
        
        # 尝试加载音效
        try:
            self.sounds = {
                'background': self._load_sound('background.mp3'),
                'clear': self._load_sound('clear.wav'),
                'rotate': self._load_sound('rotate.wav'),
                'drop': self._load_sound('drop.wav'),
                'move': self._load_sound('move.wav'),
                'gameover': self._load_sound('gameover.wav'),
                'level_up': self._load_sound('level_up.wav'),  # 新增等级提升音效
                'combo': self._load_sound('combo.wav')         # 新增连击音效
            }
            
            # 设置音量
            for sound in self.sounds.values():
                if sound:
                    sound.set_volume(0.3)
            if self.sounds.get('background'):
                self.sounds['background'].set_volume(0.1)
                self.sounds['background'].play(-1)
                
            # 特殊音效音量
            if self.sounds.get('level_up'):
                self.sounds['level_up'].set_volume(0.4)
            if self.sounds.get('combo'):
                self.sounds['combo'].set_volume(0.35)
        except Exception as e:
            print(f"Warning: Could not load some audio files: {e}")
        
        # 尝试加载材质
        try:
            self.block_texture = pygame.image.load(os.path.join(TEXTURES_DIR, 'block_metallic.png'))
            self.block_texture = pygame.transform.scale(self.block_texture, (BLOCK_SIZE, BLOCK_SIZE))
        except:
            # 创建默认的方块材质
            self.block_texture = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(self.block_texture, (255, 255, 255, 200), 
                           (0, 0, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.block_texture, (255, 255, 255, 100),
                           (2, 2, BLOCK_SIZE-4, BLOCK_SIZE-4))
        
        try:
            self.background = pygame.image.load(os.path.join(TEXTURES_DIR, 'background.jpg'))
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            # 创建默认的渐变背景
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            for y in range(SCREEN_HEIGHT):
                color = (
                    max(0, min(255, 20 + y * 0.1)),
                    max(0, min(255, 20 + y * 0.05)),
                    max(0, min(255, 35 + y * 0.15))
                )
                pygame.draw.line(self.background, color, (0, y), (SCREEN_WIDTH, y))
        
        # 存储消除动画
        self.clear_animations = []
        
        # 创建半透明的网格线surface
        self.grid_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._draw_grid()
        
        # 游戏增强功能变量
        self.combo_count = 0  # 当前连击数
        self.last_clear_time = 0  # 上次消除时间
        self.rainbow_effect_start = 0  # 彩虹特效开始时间
        self.level_up_animation_start = 0  # 等级提升动画开始时间
        self.previous_level = 1  # 用于检测等级提升
        self.show_ghost_piece = True  # 是否显示预览阴影
        
    def _load_sound(self, filename):
        """安全加载音效文件"""
        try:
            return pygame.mixer.Sound(os.path.join(AUDIO_DIR, filename))
        except:
            return None
            
    def play_sound(self, sound_name):
        """安全播放音效"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()
            
    def load_high_score(self):
        try:
            with open('high_score.json', 'r') as f:
                return json.load(f)['high_score']
        except:
            return 0
            
    def save_high_score(self):
        with open('high_score.json', 'w') as f:
            json.dump({'high_score': self.high_score}, f)
            
    def new_piece(self):
        if self.next_piece is None:
            self.next_piece = random.randint(0, len(SHAPES) - 1)
        self.current_piece = self.next_piece
        self.next_piece = random.randint(0, len(SHAPES) - 1)
        self.piece_pos = [0, GRID_WIDTH // 2 - len(SHAPES[self.current_piece][0]) // 2]
        
        # Check if game is over
        if self.check_collision():
            self.state = GameState.GAME_OVER
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
                
    def rotate_piece(self):
        if self.current_piece is None:
            return
            
        # 播放旋转音效
        self.play_sound('rotate')
        
        # Get the current shape
        current_shape = SHAPES[self.current_piece]
        # Create new rotated shape
        rotated = list(zip(*current_shape[::-1]))
        
        # Store original position and shape
        original_pos = self.piece_pos[:]
        original_shape = SHAPES[self.current_piece]
        
        # Try rotation
        SHAPES[self.current_piece] = rotated
        if self.check_collision():
            # If collision, revert back
            SHAPES[self.current_piece] = original_shape
            self.piece_pos = original_pos
            
    def check_collision(self, row_offset=0, col_offset=0):
        """检查碰撞，可以指定偏移量进行预判断"""
        if self.current_piece is None:
            return False
            
        shape = SHAPES[self.current_piece]
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    new_row = self.piece_pos[0] + i + row_offset
                    new_col = self.piece_pos[1] + j + col_offset
                    
                    if (new_row >= GRID_HEIGHT or  # 触底
                        new_col < 0 or            # 触左边界
                        new_col >= GRID_WIDTH or  # 触右边界
                        new_row >= 0 and self.grid[new_row][new_col]):  # 与其他方块重叠
                        return True
        return False
        
    def merge_piece(self):
        """将当前方块合并到网格中，并检查是否有可消除的行"""
        if self.current_piece is None:
            return
            
        shape = SHAPES[self.current_piece]
        piece_color = self.current_piece + 1
        
        # 记录受影响的行
        affected_rows = set()
        
        # 将当前方块合并到网格中
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    grid_row = self.piece_pos[0] + i
                    grid_col = self.piece_pos[1] + j
                    if grid_row >= 0:
                        self.grid[grid_row][grid_col] = piece_color
                        affected_rows.add(grid_row)
        
        # 检查受影响的行是否可以消除
        lines_to_clear = []
        for row in sorted(affected_rows):
            if all(cell != 0 for cell in self.grid[row]):
                lines_to_clear.append(row)
        
        if lines_to_clear:
            self.clear_lines(lines_to_clear)
            
        self.new_piece()
        
    def clear_lines(self, lines):
        """清除指定的行并更新分数"""
        if not lines:
            return
            
        current_time = pygame.time.get_ticks()
        
        # 更新连击状态
        if current_time - self.last_clear_time < COMBO_TIMEOUT:
            self.combo_count += 1
        else:
            self.combo_count = 1
        self.last_clear_time = current_time
        
        # 计算分数
        lines_count = len(lines)
        base_score = lines_count * 100 * self.level
        combo_bonus = self.combo_count * COMBO_BONUS * self.level
        self.score += base_score + combo_bonus
        
        # 更新等级
        old_level = self.level
        self.lines_cleared += lines_count
        self.level = self.lines_cleared // 10 + 1
        self.fall_speed = max(100, 1000 - (self.level - 1) * 100)
        
        # 处理等级提升
        if self.level > old_level:
            self.level_up_animation_start = current_time
            self.play_sound('level_up')
        
        # 处理连击特效
        if self.combo_count >= 2:
            self.rainbow_effect_start = current_time
            self.play_sound('combo')
        
        # 创建消除动画
        for line in lines:
            color = COLORS[random.randint(0, len(COLORS)-1)]
            self.clear_animations.append(ClearAnimation(line, color))
        
        # 从下往上清除行并移动上方的方块
        new_grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(len(lines))]
        remaining_grid = []
        
        # 收集未被清除的行
        for i in range(GRID_HEIGHT):
            if i not in lines:
                remaining_grid.append(self.grid[i])
        
        # 重建网格
        self.grid = new_grid + remaining_grid
        
        # 播放音效
        self.play_sound('clear')

    def update_animations(self):
        """更新所有动画效果"""
        current_time = pygame.time.get_ticks()
        
        # 更新消除动画
        self.clear_animations = [anim for anim in self.clear_animations if anim.update()]
        
        # 更新连击状态
        if self.combo_count > 0 and current_time - self.last_clear_time > COMBO_TIMEOUT:
            self.combo_count = 0
            self.rainbow_effect_start = 0
        
        # 更新等级提升动画
        if self.level_up_animation_start and current_time - self.level_up_animation_start > LEVEL_UP_ANIMATION_DURATION:
            self.level_up_animation_start = 0

    def get_ghost_piece_position(self):
        """获取方块预览位置"""
        if not self.current_piece:
            return None
            
        ghost_pos = self.piece_pos.copy()
        while not self.check_collision(row_offset=ghost_pos[0] - self.piece_pos[0] + 1):
            ghost_pos[0] += 1
        return ghost_pos
        
    def draw_ghost_piece(self):
        """绘制方块预览阴影"""
        if not self.show_ghost_piece or not self.current_piece:
            return
            
        ghost_pos = self.get_ghost_piece_position()
        if not ghost_pos:
            return
            
        shape = SHAPES[self.current_piece]
        color = COLORS[self.current_piece]
        
        # 使用原始颜色但降低饱和度和亮度
        ghost_color = (
            min(255, int(color[0] * 0.6 + 255 * 0.1)),  # 降低亮度
            min(255, int(color[1] * 0.6 + 255 * 0.1)),
            min(255, int(color[2] * 0.6 + 255 * 0.1)),
            120  # 增加透明度
        )
        
        # 边框颜色（比主体颜色稍暗）
        border_color = (
            min(255, int(color[0] * 0.7 + 255 * 0.1)),
            min(255, int(color[1] * 0.7 + 255 * 0.1)),
            min(255, int(color[2] * 0.7 + 255 * 0.1)),
            140  # 增加边框透明度
        )
        
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    x = (ghost_pos[1] + j) * BLOCK_SIZE
                    y = (ghost_pos[0] + i) * BLOCK_SIZE
                    
                    # 创建透明表面
                    ghost_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                    
                    # 绘制填充
                    pygame.draw.rect(ghost_surface, ghost_color, 
                                  (2, 2, BLOCK_SIZE-4, BLOCK_SIZE-4))
                    
                    # 绘制更密集的虚线边框
                    dash_length = 3  # 减小虚线段长度
                    gap_length = 2   # 减小虚线间隔长度
                    
                    # 绘制四条边的虚线
                    for edge in range(4):
                        start_pos = [0, 0]
                        if edge == 1:  # 右边
                            start_pos = [BLOCK_SIZE-1, 0]
                        elif edge == 2:  # 下边
                            start_pos = [0, BLOCK_SIZE-1]
                        elif edge == 3:  # 左边
                            start_pos = [0, 0]
                        
                        current_pos = start_pos.copy()
                        is_drawing = True  # 控制是否绘制当前段
                        
                        while True:
                            # 计算终点位置
                            end_pos = current_pos.copy()
                            if edge in [0, 2]:  # 水平线
                                end_pos[0] = min(current_pos[0] + dash_length, BLOCK_SIZE)
                            else:  # 垂直线
                                end_pos[1] = min(current_pos[1] + dash_length, BLOCK_SIZE)
                            
                            # 如果是绘制阶段，画出当前虚线段
                            if is_drawing:
                                pygame.draw.line(ghost_surface, border_color,
                                               current_pos, end_pos, 2)
                            
                            # 更新位置
                            if edge in [0, 2]:  # 水平线
                                current_pos[0] = end_pos[0] + gap_length
                                if current_pos[0] >= BLOCK_SIZE:
                                    break
                            else:  # 垂直线
                                current_pos[1] = end_pos[1] + gap_length
                                if current_pos[1] >= BLOCK_SIZE:
                                    break
                            
                            # 切换绘制状态
                            is_drawing = not is_drawing
                    
                    self.screen.blit(ghost_surface, (x, y))
                    
    def draw_level_up_animation(self):
        """绘制等级提升动画"""
        if not self.level_up_animation_start:
            return
            
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.level_up_animation_start
        
        if elapsed > LEVEL_UP_ANIMATION_DURATION:
            self.level_up_animation_start = 0
            return
            
        # 创建闪光效果
        progress = elapsed / LEVEL_UP_ANIMATION_DURATION
        alpha = int(255 * (1 - progress))
        flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        flash_surface.fill((255, 255, 255, alpha // 4))
        self.screen.blit(flash_surface, (0, 0))
        
        # 显示等级提升文本
        font = pygame.font.Font(None, 72)
        text = font.render(f'LEVEL {self.level}!', True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        
        # 添加缩放效果
        scale = 1 + math.sin(progress * math.pi) * 0.3
        scaled_text = pygame.transform.scale(text, 
                                          (int(text_rect.width * scale), 
                                           int(text_rect.height * scale)))
        scaled_rect = scaled_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(scaled_text, scaled_rect)
        
    def apply_rainbow_effect(self, color):
        """应用彩虹特效到方块颜色"""
        if not self.rainbow_effect_start:
            return color
            
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.rainbow_effect_start
        
        if elapsed > RAINBOW_EFFECT_DURATION:
            self.rainbow_effect_start = 0
            return color
            
        # 计算彩虹颜色
        rainbow_index = int((elapsed / 200) % len(RAINBOW_COLORS))
        rainbow_color = RAINBOW_COLORS[rainbow_index]
        
        # 混合原始颜色和彩虹颜色
        blend_factor = 0.5 + math.sin(elapsed * 0.01) * 0.5
        return tuple(int(c1 * blend_factor + c2 * (1 - blend_factor))
                    for c1, c2 in zip(color, rainbow_color))
        
    def apply_metallic_effect(self, surface, color, pos):
        """应用金属质感3D效果"""
        x, y = pos
        normal = np.array([0.0, 0.0, 1.0])
        
        # 计算光照
        light_dir = LIGHT_DIR / np.linalg.norm(LIGHT_DIR)
        diffuse = max(0, np.dot(normal, light_dir))
        
        # 计算反射光
        reflect = normal * 2 * np.dot(normal, light_dir) - light_dir
        specular = pow(max(0, reflect[2]), 1/ROUGHNESS) * METALLIC_SHINE
        
        # 调整颜色
        r, g, b = color
        r = min(255, int(r * diffuse + 255 * specular))
        g = min(255, int(g * diffuse + 255 * specular))
        b = min(255, int(b * diffuse + 255 * specular))
        
        # 绘制带有金属质感的方块
        metallic_surface = self.block_texture.copy()
        metallic_surface.fill((r, g, b), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(metallic_surface, (x, y))
        
    def _draw_grid(self):
        """预渲染网格线"""
        self.grid_surface.fill((0, 0, 0, 0))
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(self.grid_surface, (*GRAY, GRID_ALPHA),
                               [x * BLOCK_SIZE, y * BLOCK_SIZE,
                                BLOCK_SIZE, BLOCK_SIZE], 1)
                                
    def draw(self):
        # 绘制背景
        self.screen.blit(self.background, (0, 0))
        
        # 绘制网格线
        self.screen.blit(self.grid_surface, (0, 0))
        
        # 绘制已落下的方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    color = self.apply_rainbow_effect(COLORS[self.grid[y][x] - 1])
                    self.apply_metallic_effect(
                        self.screen,
                        color,
                        (x * BLOCK_SIZE, y * BLOCK_SIZE)
                    )
                    
        # 绘制当前方块
        if self.current_piece is not None:
            shape = SHAPES[self.current_piece]
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        color = self.apply_rainbow_effect(COLORS[self.current_piece])
                        self.apply_metallic_effect(
                            self.screen,
                            color,
                            ((self.piece_pos[1] + x) * BLOCK_SIZE,
                             (self.piece_pos[0] + y) * BLOCK_SIZE)
                        )
                        
        # Draw next piece preview
        preview_x = GRID_WIDTH * BLOCK_SIZE + BLOCK_SIZE
        preview_y = BLOCK_SIZE
        pygame.draw.rect(self.screen, GRAY,
                        [preview_x, preview_y,
                         4 * BLOCK_SIZE, 4 * BLOCK_SIZE], 1)
                         
        if self.next_piece is not None:
            shape = SHAPES[self.next_piece]
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        color = COLORS[self.next_piece]
                        self.apply_metallic_effect(
                            self.screen,
                            color,
                            (preview_x + (x + 1) * BLOCK_SIZE,
                             preview_y + (y + 1) * BLOCK_SIZE)
                        )
                        
        # 绘制消除动画
        for animation in self.clear_animations:
            animation.draw(self.screen)
            
        # 绘制预览阴影
        self.draw_ghost_piece()
        
        # 绘制等级提升动画
        self.draw_level_up_animation()
        
        # Draw score and level
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        level_text = font.render(f'Level: {self.level}', True, WHITE)
        high_score_text = font.render(f'High Score: {self.high_score}', True, WHITE)
        
        self.screen.blit(score_text, [GRID_WIDTH * BLOCK_SIZE + BLOCK_SIZE, 200])
        self.screen.blit(level_text, [GRID_WIDTH * BLOCK_SIZE + BLOCK_SIZE, 240])
        self.screen.blit(high_score_text, [GRID_WIDTH * BLOCK_SIZE + BLOCK_SIZE, 280])
        
        # Draw game state messages
        if self.state == GameState.PAUSED:
            # 创建半透明的暂停背景
            pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 128))  # 半透明黑色
            self.screen.blit(pause_overlay, (0, 0))
            
            # 绘制暂停文本
            pause_font = pygame.font.Font(None, 72)
            pause_text = pause_font.render('PAUSED', True, WHITE)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            
            # 绘制提示文本
            hint_font = pygame.font.Font(None, 36)
            hint_text = hint_font.render('Press ESC to continue', True, WHITE)
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(pause_text, pause_rect)
            self.screen.blit(hint_text, hint_rect)
            
        elif self.state == GameState.GAME_OVER:
            # 创建半透明的游戏结束背景
            game_over_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            game_over_overlay.fill((0, 0, 0, 128))  # 半透明黑色
            self.screen.blit(game_over_overlay, (0, 0))
            
            # 绘制游戏结束文本
            game_over_font = pygame.font.Font(None, 72)
            game_over_text = game_over_font.render('GAME OVER', True, WHITE)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            
            # 绘制重新开始提示
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render('Press SPACE to restart', True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(restart_text, restart_rect)
            
            # 播放游戏结束音效（仅播放一次）
            if not hasattr(self, '_game_over_sound_played'):
                self.play_sound('gameover')
                self._game_over_sound_played = True
            
        pygame.display.flip()
        
    def move_piece(self, dx, dy):
        """移动方块"""
        self.piece_pos[1] += dx
        self.piece_pos[0] += dy
        
        if self.check_collision():
            self.piece_pos[1] -= dx
            self.piece_pos[0] -= dy
            if dy > 0:  # If moving down caused collision
                self.merge_piece()
                self.play_sound('drop')
        else:
            if dx != 0:  # 水平移动时播放音效
                self.play_sound('move')

    def rotate_piece(self):
        """旋转方块"""
        if self.current_piece is None:
            return
            
        # 保存原始形状以便还原
        original_shape = SHAPES[self.current_piece]
        
        # 创建新的旋转后的形状
        rotated = list(zip(*original_shape[::-1]))
        SHAPES[self.current_piece] = rotated
        
        # 检查碰撞
        if self.check_collision():
            # 如果发生碰撞，尝试左右移动来适应
            for offset in [1, -1, 2, -2]:  # 尝试不同的水平偏移
                self.piece_pos[1] += offset
                if not self.check_collision():
                    self.play_sound('rotate')
                    return
                self.piece_pos[1] -= offset
                
            # 如果所有偏移都不行，恢复原始形状
            SHAPES[self.current_piece] = original_shape
        else:
            self.play_sound('rotate')
            
    def handle_input(self):
        """处理用户输入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                # ESC键处理 - 在PLAYING和PAUSED状态之间切换
                if event.key == pygame.K_ESCAPE:
                    if self.state in [GameState.PLAYING, GameState.PAUSED]:
                        self.state = GameState.PAUSED if self.state == GameState.PLAYING else GameState.PLAYING
                    return True
                    
                # 游戏结束状态下只响应空格键
                if self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        # 重置游戏状态
                        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
                        self.score = 0
                        self.level = 1
                        self.lines_cleared = 0
                        self.state = GameState.PLAYING
                        self.fall_time = pygame.time.get_ticks()  # 重置下落时间
                        self.fall_speed = 1000
                        self.clear_animations = []
                        self.current_piece = None  # 清除当前方块
                        self.next_piece = None     # 清除下一个方块
                        self.new_piece()           # 生成新方块
                        # 重置特效相关变量
                        self.combo_count = 0
                        self.last_clear_time = 0
                        self.rainbow_effect_start = 0
                        self.level_up_animation_start = 0
                    return True
                
                # 暂停状态下只响应ESC键继续游戏
                if self.state == GameState.PAUSED:
                    return True
                
                # 游戏进行状态下的按键处理
                if self.state == GameState.PLAYING:
                    if event.key == pygame.K_LEFT:
                        self.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_piece(1, 0)
                    elif event.key == pygame.K_UP:
                        self.rotate_piece()
                        self.play_sound('rotate')
                    elif event.key == pygame.K_DOWN:
                        self.move_piece(0, 1)
                    elif event.key == pygame.K_SPACE:
                        while not self.check_collision():
                            self.piece_pos[0] += 1
                        self.piece_pos[0] -= 1
                        self.merge_piece()
                    elif event.key == pygame.K_h:  # 按H键切换预览阴影
                        self.show_ghost_piece = not self.show_ghost_piece
                
            # Touch controls (只在游戏进行状态下响应)
            elif self.state == GameState.PLAYING:
                if event.type == pygame.FINGERDOWN:
                    self.touch_start = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT)
                    self.last_touch_move = self.touch_start
                    
                elif event.type == pygame.FINGERMOTION:
                    if self.touch_start is None:
                        continue
                        
                    current_pos = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT)
                    dx = current_pos[0] - self.last_touch_move[0]
                    dy = current_pos[1] - self.last_touch_move[1]
                    
                    # Horizontal movement
                    if abs(dx) > BLOCK_SIZE:
                        self.move_piece(1 if dx > 0 else -1, 0)
                        self.last_touch_move = current_pos
                        
                    # Vertical movement (soft drop)
                    if dy > BLOCK_SIZE:
                        self.move_piece(0, 1)
                        self.last_touch_move = current_pos
                        
                elif event.type == pygame.FINGERUP:
                    if self.touch_start is not None:
                        end_pos = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT)
                        dx = end_pos[0] - self.touch_start[0]
                        dy = end_pos[1] - self.touch_start[0]
                        
                        # Tap for rotation
                        if abs(dx) < BLOCK_SIZE and abs(dy) < BLOCK_SIZE:
                            self.rotate_piece()
                            
                        self.touch_start = None
                        self.last_touch_move = None
                    
        return True

    async def run(self):
        while True:
            if not self.handle_input():
                break
                
            current_time = pygame.time.get_ticks()
            
            # 更新游戏状态
            if self.state == GameState.PLAYING:
                # 方块自动下落
                if current_time - self.fall_time > self.fall_speed:
                    self.move_piece(0, 1)
                    self.fall_time = current_time
            
            # 更新动画
            self.update_animations()
            
            # 绘制游戏画面
            self.draw()
            
            # 检查是否有新的最高分
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            
            # 维持帧率
            self.clock.tick(60)
            await asyncio.sleep(0)
            
        pygame.quit()

# Create and run game
game = Tetris()
asyncio.run(game.run())
