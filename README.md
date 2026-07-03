# AI舆情分析日报系统

一个自动采集 AI 领域新闻、结构化处理、智能分析并生成日报的可视化系统。

## 项目架构

```
┌─────────────────────────────────────────────────────────────┐
│                     AI舆情分析日报系统                          │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│  阶段1: 数据层 │  阶段2: 结构化层 │  阶段3: 分析层  │   阶段4: 输出层      │
├─────────────┼─────────────┼─────────────┼─────────────────────┤
│ 获取AI新闻数据  │ Schema设计    │ 热点聚合排序   │ 日报Markdown生成    │
│ (10~20条)    │ 逐条结构化抽取  │ 事件深度分析   │ 可视化图表生成       │
│ 数据清洗去重   │ 数据校验      │ 趋势判断      │ HTML页面渲染       │
│ 存入JSON     │ 存入JSON      │ 风险/机会识别  │ 结果展示           │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
```

## 技术栈

- **后端**: Python 3.11 + 虚拟环境
- **前端**: Vue 3 + Vite + TypeScript + Element Plus + ECharts

## 目录结构

```
news2report/
├── backend/                 # 后端系统
│   ├── .venv/              # Python 虚拟环境
│   ├── data/               # 数据目录
│   │   ├── raw/           # 原始采集数据
│   │   ├── processed/     # 结构化后数据
│   │   └── output/        # 日报/图表输出
│   ├── src/               # 源码
│   │   ├── data/          # 数据采集与清洗
│   │   ├── schema/        # Schema 设计与校验
│   │   ├── analysis/      # 热点聚合与事件分析
│   │   ├── output/        # Markdown/图表/HTML 生成
│   │   └── utils/         # 工具函数
│   ├── requirements.txt   # Python 依赖
│   └── .env.example       # 后端环境变量示例
│
├── frontend/               # 前端展示页面
│   ├── node_modules/      # Node 依赖
│   ├── src/               # 源码
│   │   ├── components/    # 组件
│   │   ├── views/         # 页面
│   │   ├── utils/         # 工具函数
│   │   └── assets/        # 静态资源
│   ├── package.json       # Node 依赖配置
│   ├── vite.config.ts     # Vite 配置
│   └── .env.example       # 前端环境变量示例
│
└── README.md
```

## 环境搭建

### 后端

```bash
cd backend
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 API Key
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 运行

- 前端开发服务器: http://localhost:5173
- 后端 API 服务: http://localhost:8000 (待实现)

## 配置说明

复制 `.env.example` 为 `.env` 后，填入 OpenAI API Key 等必要配置。
