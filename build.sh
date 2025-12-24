#!/bin/bash

APP_NAME="iOS多语言工具"
VERSION="1.0.0"

echo "🔨 开始打包..."

# 清理旧的构建
rm -rf build dist

# 使用 PyInstaller 打包
python3 -m PyInstaller iOS-LocalizationTool.spec --clean

# 检查是否成功
if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "❌ 打包失败"
    exit 1
fi

echo "✅ .app 打包完成"

# 创建 DMG
echo "📦 创建 DMG..."

create-dmg \
    --volname "${APP_NAME}" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "${APP_NAME}.app" 150 185 \
    --hide-extension "${APP_NAME}.app" \
    --app-drop-link 450 185 \
    "dist/${APP_NAME}-${VERSION}.dmg" \
    "dist/${APP_NAME}.app"

echo "✅ 完成！DMG 文件位于: dist/${APP_NAME}-${VERSION}.dmg"

