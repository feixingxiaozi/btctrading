[app]
title = BitgetTrading
package.name = bitgettrading
package.domain = org.bitget

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.include_patterns = assets/*,images/*
source.exclude_dirs = tests, bin, venv

version = 0.1

# 极简依赖配置
requirements = python3,kivy

orientation = portrait
fullscreen = 0

# 基本权限
android.permissions = INTERNET

# 基础Android设置
android.api = 28
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

# 启用SDK授权
android.accept_sdk_license = True

# 禁用WebView (解决常见错误)
android.enable_androidx = True
android.add_dependencies = com.android.support:support-v4:28.0.0

[buildozer]
log_level = 2
warn_on_root = 1
