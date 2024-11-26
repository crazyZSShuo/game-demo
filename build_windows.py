import PyInstaller.__main__
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 定义资源文件夹路径
assets_dir = os.path.join(current_dir, 'assets')

PyInstaller.__main__.run([
    'main.py',
    '--name=疯狂俄罗斯方块',
    '--windowed',
    '--onefile',
    f'--add-data={assets_dir}{os.pathsep}assets',
    '--icon=assets/textures/app_icon.ico',  # 如果你有图标的话
    '--clean',
    '--noconfirm',
])
