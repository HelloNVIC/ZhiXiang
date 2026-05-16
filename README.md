<div align="center">

# NVIC-质象

把一个概念或一篇论文，变成一段可以播放的知识动画。

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white)
![SSE](https://img.shields.io/badge/Streaming-SSE-black?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-Check%20Repository-lightgrey?style=flat-square)

一个本地优先的 AI 科普视频生成 Web 应用。输入主题或上传 PDF 论文，模型会生成可直接播放的单文件 HTML 动画页面。

</div>

---

## 目录

- [项目简介](#项目简介)
- [功能亮点](#功能亮点)
- [预览与使用场景](#预览与使用场景)
- [快速开始](#快速开始)
- [使用方式](#使用方式)
- [Docker 部署](#docker-部署)
- [配置说明](#配置说明)
- [接口说明](#接口说明)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [使用建议](#使用建议)
- [常见限制](#常见限制)
- [安全提示](#安全提示)

## 项目简介

很多知识并不适合只用文字解释。质象希望把「抽象概念」「动态过程」「论文方法」快速转化为一段可视化动画，方便用于课堂、演示、短视频原型、知识科普和技术讲解。

你可以输入：

```text
黑洞是如何形成的
```

也可以上传一篇 PDF 论文，并指定讲解重点：

```text
第三章方法、Transformer 注意力机制、实验结果
```

质象会尝试生成完整的 HTML/CSS/JavaScript/SVG 动画页面，并在浏览器中自动播放。

## 功能亮点

| 功能 | 说明 |
| --- | --- |
| 概念动画生成 | 输入一个知识点，生成可播放的动态网页动画 |
| 论文解释 | 上传 PDF 论文，生成论文动画讲解页面 |
| 指定论文重点 | 可聚焦章节、术语、模型结构、实验结果或结论 |
| SSE 流式输出 | 后端实时推送模型输出，前端逐 token 展示生成过程 |
| 自动渲染 | 自动提取模型返回的 HTML，并放入 sandbox iframe 播放 |
| 多轮修改 | 生成后可继续输入修改意见，基于历史上下文迭代 |
| 专业生成配置 | 支持风格、节奏、比例、分辨率、讲解深度、字幕和 MathJax |
| 分享链接 | 可创建带密码和过期时间的 HTML 分享链接 |
| 访问控制 | 支持暗号入口，适合本地演示或小范围分享 |
| Docker 部署 | 内置 Dockerfile 与 docker-compose.yml |

## 预览与使用场景

启动后访问：

```text
http://127.0.0.1:8000
```

适合生成：

- 数学公式推导动画
- 物理过程解释动画
- 算法运行过程动画
- PDF 论文动画讲解
- 模型结构和数据流程演示
- 科普类知识短片原型
- 教学课件中的动态片段
- 产品概念或技术方案演示页面

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/HelloNVIC/ZhiXiang.git
cd ZhiXiang
```

### 2. 安装依赖

建议使用 Python 3.10 或更高版本。

```bash
pip install -r requirements.txt
```

### 3. 创建配置文件

复制示例配置：

```bash
cp example.json credentials.json
```

编辑 `credentials.json`：

```json
{
    "API_KEY": "",
    "BASE_URL": "",
    "MODEL": "",
    "ENABLE_DEBUG_OUTPUT": false,
    "MAX_CONCURRENT_GENERATION_TASKS": 1,
    "ACCESS_PASSPHRASES": ["NVIC"]
}
```

如果不需要暗号访问，把 `ACCESS_PASSPHRASES` 设置为空数组：

```json
"ACCESS_PASSPHRASES": []
```

### 4. 启动应用

推荐使用本地启动脚本：

```bash
python start_zhixiang.py
```

也可以直接启动 FastAPI：

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

打开浏览器访问：

```text
http://127.0.0.1:8000
```

## 使用方式

### 生成概念动画

在首页输入要解释的概念或主题，选择生成配置后开始生成。生成完成后，页面会自动解析模型返回的 HTML 并在浏览器中播放。

示例：

```text
用适合高中生理解的方式，解释牛顿第二定律 F=ma，要求有力、质量、加速度之间关系的动态示意。
```

### 生成论文解释动画

点击首页的「论文解释」按钮，上传 PDF 论文。可以留空重点输入框生成整篇论文讲解，也可以填写具体章节、术语、模型结构或实验结果作为重点。

论文解释会尝试覆盖：

- 研究背景
- 核心问题
- 方法框架
- 关键公式、模型结构或数据流程
- 实验对比和结果
- 结论与启发

> 论文解释依赖 PDF 可提取文本。扫描版或纯图片型 PDF 需要先 OCR。

## Docker 部署

### Docker Compose

确保项目根目录存在 `credentials.json`，然后运行：

```bash
docker-compose up -d
```

默认访问：

```text
http://127.0.0.1:8000
```

### 手动构建镜像

```bash
docker build -t zhixiang:latest .
```

运行：

```bash
docker run --rm -p 8000:8000 -v "$(pwd)/credentials.json:/app/credentials.json:ro" zhixiang:latest
```

## 配置说明

| 字段 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `API_KEY` | 是 | 无 | 大模型 API Key |
| `BASE_URL` | 否 | 空字符串 | OpenAI 兼容接口地址 |
| `MODEL` | 否 | 空字符串 | 模型名称 |
| `ENABLE_DEBUG_OUTPUT` | 否 | `true` | 是否打印 LLM 请求和响应调试信息 |
| `MAX_CONCURRENT_GENERATION_TASKS` | 否 | `1` | 最大并发生成任务数 |
| `MAX_PAPER_UPLOAD_BYTES` | 否 | `10485760` | PDF 论文最大上传体积，最大不超过 10MB |
| `MAX_PAPER_TEXT_CHARS` | 否 | `120000` | 从论文中送入模型的最大文本字符数 |
| `ACCESS_PASSPHRASES` | 否 | `null` | 暗号列表；为空时不启用暗号 |

补充说明：

- 后端使用 OpenAI 兼容客户端调用模型。
- 论文解释使用 `pypdf` 提取 PDF 文本。
- 如果论文超过文本上限，后端会截断后再送入模型。
- `credentials.json` 包含敏感信息，请不要提交到公开仓库。

## 接口说明

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/` | Web 页面入口 |
| `GET` | `/config` | 获取公开配置，例如是否需要暗号 |
| `POST` | `/verify-passphrase` | 校验访问暗号 |
| `POST` | `/generate` | 根据主题生成动画，返回 SSE 流 |
| `POST` | `/paper/generate` | 上传 PDF 并生成论文解释动画，返回 SSE 流 |
| `POST` | `/share` | 创建 HTML 分享链接 |
| `GET` | `/share/{share_id}` | 访问分享页面 |
| `POST` | `/share/{share_id}` | 校验分享密码并打开分享页面 |

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 后端 | FastAPI |
| 流式传输 | Server-Sent Events |
| 模型调用 | OpenAI-compatible API |
| PDF 解析 | pypdf |
| 前端 | 原生 HTML / CSS / JavaScript |
| 模板 | Jinja2 |
| 容器化 | Docker / Docker Compose |

## 项目结构

```text
.
├── app.py                 # FastAPI 后端、配置读取、模型调用、PDF 解析和 SSE 接口
├── start_zhixiang.py      # 本地启动脚本
├── requirements.txt       # Python 依赖
├── Dockerfile             # Docker 镜像构建文件
├── docker-compose.yml     # Docker Compose 配置
├── example.json           # credentials.json 示例
├── shared_html/           # 分享链接生成的 HTML 与元数据
├── static/                # 前端脚本、样式、字体和静态资源
└── templates/             # Jinja2 页面模板
```

## 使用建议

为了获得更稳定的动画结果，提示词可以包含：

- 想解释的核心概念
- 受众水平
- 希望呈现的视觉风格
- 是否需要公式、步骤、对比或时间线
- 希望强调的教学目标或结论

论文解释建议：

- 优先上传可复制文本的 PDF
- 对长论文指定重点章节或概念
- 如果论文包含复杂公式或结构图，开启 MathJax 或在重点中明确说明
- 对实验结果类论文，指定要解释的表格、指标或对比结论

## 常见限制

- 模型输出质量取决于所选模型和提示词。
- 生成的 HTML 是模型生成内容，复杂动画可能需要二次调整。
- PDF 解析依赖文本层，扫描版论文需要 OCR。
- 长论文会受 `MAX_PAPER_TEXT_CHARS` 限制，超过部分会被截断。
- 移动端预览能力有限，建议在 PC 端使用。

## 安全提示

- 不要公开提交 `credentials.json`。
- 部署到公网时，请配置暗号、反向代理鉴权或其他访问控制。
- 生成的 HTML 会在 sandbox iframe 中运行，但仍建议只在可信环境中使用。
- 分享链接可能包含模型生成的完整 HTML 内容，请谨慎设置密码和过期时间。
