[app]

# 游戏标题和包名
title = 硕哥的俄罗斯方块
package.name = tetris
package.domain = org.game

# 源代码设置
source.dir = .
source.include_exts = py,png,jpg,wav,mp3,json
source.include_patterns = assets/*
source.exclude_dirs = tests, bin, venv, .buildozer

# 版本信息
version = 1.0
requirements = python3,\
    pygame==2.5.2,\
    numpy==1.24.3,\
    pillow

# Android specific
android.permissions = INTERNET
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.arch = arm64-v8a

# Gradle 设置
android.gradle_version = 8.0
android.build_tools_version = 33.0.0
android.gradle_dependencies = org.pygame:pygame-android:2.5.2

# 应用图标
android.presplash.color = #000000
android.icon.filename = %(source.dir)s/assets/textures/app_icon.png
android.presplash.filename = %(source.dir)s/assets/textures/splash.png

# 构建设置
fullscreen = 1
orientation = portrait

# Python-for-android 选项
p4a.bootstrap = sdl2
p4a.branch = master
p4a.use_setup_py = False

# 构建选项
android.release_artifact = apk
android.allow_backup = True
android.numeric_version = 1

[buildozer]
log_level = 2
warn_on_root = 1
