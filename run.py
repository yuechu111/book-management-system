#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图书管理系统启动文件
"""
from app import create_app
from app import db
# 从环境变量读取配置，默认为开发环境
app = create_app()

if __name__ == '__main__':

    app.run(debug=True)