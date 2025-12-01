#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图书管理系统启动文件
"""

import os
from app import create_app

# 从环境变量读取配置，默认为开发环境
app = create_app(os.getenv('FLASK_ENV') or 'development')

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=True
    )