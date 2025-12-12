## 图书管理系统

一个基于 Python Flask 的图书管理系统，提供图书的增删改查、用户管理、分类管理等功能。

## 技术栈

- **后端框架**: Flask
- **数据库**: SQLite (开发环境) / PostgreSQL (生产环境)
- **ORM**: SQLAlchemy
- **表单**: WTForms
- **认证**: Flask-Login
- **前端**: HTML5, CSS3, JavaScript, Bootstrap 5

## 主要功能

- 用户注册、登录、权限管理
- 图书信息管理（增删改查）
- 图书分类管理
- 图书搜索和筛选
- 借阅管理
- 用户个人中心

## 项目结构

```
book_management_system/
├── app/                    # 应用主包
│   ├── models/            # 数据模型
│   ├── views/             # 视图控制器
│   ├── templates/         # HTML模板
│   ├── static/            # 静态文件
│   ├── forms/             # 表单类
│   └── utils/             # 工具函数
├── config/                # 配置文件
├── tests/                 # 测试文件
├── migrations/            # 数据库迁移文件
└── instance/              # 实例配置
```

## 安装和运行

1. 克隆项目
2. 安装依赖：`pip install -r requirements.txt`
3. 配置环境变量
4. 初始化数据库：`flask db upgrade`
5. 运行应用：`python run.py`

## 开发环境

- Python 3.8+
- Flask 2.x