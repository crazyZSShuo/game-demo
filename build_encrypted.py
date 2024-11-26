import os
import shutil
from pyarmor.pyarmor import main as pyarmor_main

def encrypt_and_build():
    # 清理之前的构建
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # 使用 PyArmor 加密代码
    pyarmor_main(['obfuscate', 
                 '--recursive',
                 '--output', 'dist',
                 '--bootstrap', '3',
                 '--advanced', '2',
                 'main.py'])
    
    # 复制资源文件
    shutil.copytree('assets', os.path.join('dist', 'assets'))
    
    # 使用 PyInstaller 打包加密后的代码
    os.system('pyinstaller --name="疯狂俄罗斯方块" '
             '--windowed '
             '--onefile '
             '--add-data "dist/assets;assets" '
             '--icon=assets/textures/app_icon.ico '
             '--clean '
             '--noconfirm '
             'dist/main.py')

if __name__ == '__main__':
    encrypt_and_build()
