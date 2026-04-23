# 农产品溯源系统

## 项目简介

农产品溯源系统，用于扫描二维码查询农产品从生产到销售的全链路信息。

## 技术栈

- 后端：Python + FastAPI
- 数据库：SQLite（开发）/ PostgreSQL（生产）
- 前端：响应式 Web 页面
- 部署：Railway + GitHub Pages

## 目录结构

```
.
├── backend/           # 后端 API
│   ├── main.py        # FastAPI 主程序
│   ├── database.py    # 数据库配置
│   ├── models.py      # 数据模型
│   └── requirements.txt
├── frontend/          # 前端页面
│   └── index.html
└── docs/              # 文档
    └── README.md
```

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0.0 | 2026-04-22 | 初始版本，包含基础功能 |