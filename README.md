<div align="center">

# NVIC-质象

**把一个概念，变成一段可以播放的知识动画。**

一个本地优先的 AI 科普向视频生成 Web 应用：输入科普视频主题，模型自动生成科普视频。

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)
![SSE](https://img.shields.io/badge/Streaming-SSE-black?style=flat-square)

</div>

---

## 为什么做质象？

很多知识并不适合只用文字解释。

**NVIC-质象** 希望把「一个概念」快速转化为「一段可视化动画」：

- 讲清一个抽象概念
- 展示一个动态过程
- 生成适合课堂、演示、短视频或知识科普的视觉内容
- 保留完整 HTML 结果，方便继续编辑、保存和二次使用

你只需要输入：

```text
黑洞是如何形成的
```

质象会尝试生成一个完整的动态网页动画，并直接在浏览器中播放。

## 预览

> 当前项目为本地运行应用。启动后访问 `http://127.0.0.1:8000` 即可使用。

你可以用它生成：

- 数学公式推导动画
- 物理过程解释动画
- 算法运行过程动画
- 科普类知识短片原型
- 产品概念演示页面
- 教学课件中的动态片段

## 核心特性

### 流式生成

后端使用 SSE 将模型输出实时推送给前端，用户可以看到代码逐步生成，而不是等待完整响应结束。

### 自动渲染

前端会从模型响应中提取 HTML 代码块，校验后自动放入 sandbox iframe 中播放。

### 多轮修改

生成后可以继续输入修改意见，前端会携带历史对话，让模型基于已有结果继续迭代。

### 专业生成配置

内置生成面板，可配置：

- 视觉风格：电影级、极简、教学、未来科技
- 视频节奏：短、中、长
- 画幅比例：16:9、9:16、1:1
- 容器尺寸：720p、1080p、2K
- 讲解深度：入门、标准、专业
- 是否强化旁白
- 是否生成双语字幕
- 是否使用 MathJax

### 访问控制

支持暗号访问控制，适合本地演示或小范围分享。

如果不需要暗号，只需在 `credentials.json` 中设置：

```json
"ACCESS_PASSPHRASES": []
```

### Docker 支持

项目内置 Dockerfile 和 docker-compose.yml，可以直接容器化部署。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 后端 | FastAPI |
| 流式传输 | Server-Sent Events |
| 模型调用 | OpenAI-compatible API |
| 前端 | 原生 HTML / CSS / JavaScript |
| 模板 | Jinja2 |
| 容器化 | Docker / Docker Compose |

## 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd ZhiXiang
```

### 2. 安装依赖

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
    "ENABLE_DEBUG_OUTPUT": true,
    "MAX_CONCURRENT_GENERATION_TASKS": 1,
    "ACCESS_PASSPHRASES": ["Test1", "Test2"]
}
```

### 4. 启动应用

推荐使用本地启动脚本：

```bash
python start_zhixiang.py
```

或者直接启动 FastAPI：

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

然后访问：

```text
http://127.0.0.1:8000
```

## Docker 部署

### Docker Compose

确保根目录存在 `credentials.json`，然后运行：

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
| `ACCESS_PASSPHRASES` | 否 | `null` | 暗号列表；为空时不启用暗号 |

说明：

- 后端使用 OpenAI 兼容客户端调用模型。
- `credentials.json` 包含敏感信息，请不要提交到公开仓库。

## 项目结构

```text
.
├── app.py                 # FastAPI 后端、配置读取、模型调用和 SSE 接口
├── start_zhixiang.py      # 本地启动脚本
├── requirements.txt       # Python 依赖
├── Dockerfile             # Docker 镜像构建文件
├── docker-compose.yml     # Docker Compose 配置
├── example.json           # credentials.json 示例
├── static/                # 前端脚本、样式、字体和静态资源
└── templates/             # Jinja2 页面模板
```

## 使用建议

为了获得更稳定的动画结果，提示词可以包含：

- 想解释的核心概念
- 受众水平
- 希望呈现的视觉风格
- 是否需要公式、步骤、对比或时间线

示例：

```text
用适合高中生理解的方式，解释牛顿第二定律 F=ma，要求有力、质量、加速度之间关系的动态示意。
```

## 安全提示

- 不要公开提交 `credentials.json`。
- 生成的 HTML 会在 sandbox iframe 中运行，但仍建议只在可信环境中使用。
- 如果部署到公网，请配置暗号、反向代理鉴权或其他访问控制。
