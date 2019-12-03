# jpeg

#### 介绍
使用Python对jpg图片进行批量处理：
1. 修复Exif时间
2. 根据Exif信息对图片重命名
3. 压缩图片（保留原始Exif信息）

#### 依赖的库
需要安装PIL和piexif：
pip install pillow
pip install piexif

#### 使用方法
1.  修改全局常量 WORK_DIR 设置工作目录
2.  设置错误时间列表 BAD_TIME
3.  fix_exifs() # 批量修复Exif时间
4.  rename_jpgs() # 根据Exif信息批量重命名
5.  zip_jpgs() # 压缩图片

#### 安卓手机
使用 Pydroid 3
