import asyncio
import json
import os
from datetime import datetime
from typing import AsyncGenerator, List, Optional, Dict, Any

import pytz
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
try:
    import google.generativeai as genai
except ModuleNotFoundError:
    from google import genai
# -----------------------------------------------------------------------
# 0. 配置
# -----------------------------------------------------------------------
shanghai_tz = pytz.timezone("Asia/Shanghai")

credentials = json.load(open("credentials.json"))
API_KEY = credentials["API_KEY"]
BASE_URL = credentials.get("BASE_URL", "")
MODEL = credentials.get("MODEL", "")
ENABLE_DEBUG_OUTPUT = credentials.get("ENABLE_DEBUG_OUTPUT", True)
MAX_CONCURRENT_GENERATION_TASKS = credentials.get("MAX_CONCURRENT_GENERATION_TASKS", 1)
ACCESS_PASSPHRASES = credentials.get("ACCESS_PASSPHRASES")
generation_semaphore = asyncio.Semaphore(MAX_CONCURRENT_GENERATION_TASKS)


def debug_llm(label: str, value=None):
    if not ENABLE_DEBUG_OUTPUT:
        return
    print(f"\n===== LLM DEBUG: {label} =====", flush=True)
    if value is not None:
        if isinstance(value, (dict, list)):
            print(json.dumps(value, ensure_ascii=False, indent=2), flush=True)
        else:
            print(value, flush=True)
    print(f"===== END LLM DEBUG: {label} =====\n", flush=True)


def debug_conversation(provider: str, model: str, messages: List[dict], settings: Dict[str, Any]):
    debug_llm("conversation request", {
        "provider": provider,
        "model": model,
        "settings": settings,
        "messages": messages,
    })


def debug_response_start(provider: str):
    debug_llm("conversation response started", {"provider": provider})


def debug_response_chunk(chunk: str):
    if not ENABLE_DEBUG_OUTPUT or not chunk:
        return
    print(chunk, end="", flush=True)


def debug_response_end():
    if ENABLE_DEBUG_OUTPUT:
        print("\n===== END LLM DEBUG: conversation response =====\n", flush=True)

if API_KEY.startswith("sk-"):
    # 为 OpenRouter 添加应用标识
    extra_headers = {}    
    client = AsyncOpenAI(
        api_key=API_KEY, 
        base_url=BASE_URL,
    )

if API_KEY.startswith("sk-REPLACE_ME"):
    raise RuntimeError("请在环境变量里配置 API_KEY")

templates = Jinja2Templates(directory="templates")

# -----------------------------------------------------------------------
# 1. FastAPI 初始化
# -----------------------------------------------------------------------
app = FastAPI(title="AI Animation Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    topic: str
    history: Optional[List[dict]] = None
    settings: Optional[Dict[str, Any]] = None


class PassphraseRequest(BaseModel):
    passphrase: str

# -----------------------------------------------------------------------
# 2. 核心：流式生成器 (现在会使用 history)
# -----------------------------------------------------------------------
async def llm_event_stream(
    topic: str,
    history: Optional[List[dict]] = None,
    model: str = None, # Will use MODEL from config if not specified
    settings: Optional[Dict[str, Any]] = None,
) -> AsyncGenerator[str, None]:
    history = history or []
    settings = settings or {}
    allowed_styles = {
        "cinematic": "电影级叙事：镜头感强、节奏完整、视觉层次丰富。",
        "minimal": "极简专业：留白克制、信息清晰、图形精准。",
        "academic": "教学讲解：结构严谨、步骤明确、适合课堂演示。",
        "futuristic": "未来科技：高对比、科技感视觉、动态 HUD 元素。",
    }
    allowed_durations = {
        "short": "约 30 秒，重点突出，快速讲清核心概念。",
        "medium": "约 60 秒，完整讲解主要过程。",
        "long": "约 90 秒，包含更细的铺垫、推演和总结。",
    }
    allowed_ratios = {
        "16:9": "16:9 横屏画布，适合网页和演示。",
        "9:16": "9:16 竖屏画布，适合移动端短视频。",
        "1:1": "1:1 方形画布，适合社交媒体展示。",
    }
    allowed_depths = {
        "starter": "入门深度：避免术语堆叠，适合第一次接触该主题的观众。",
        "standard": "标准深度：兼顾直观解释和关键专业细节。",
        "expert": "专业深度：加入必要术语、推导逻辑和边界条件。",
    }
    allowed_resolutions = {
        "720p": "1280 × 720 的 720p 容器。",
        "1080p": "1920 × 1080 的 1080p 容器。",
        "2k": "2048 × 1152 的 2K 容器。",
    }
    style_instruction = allowed_styles.get(settings.get("style"), allowed_styles["cinematic"])
    duration_instruction = allowed_durations.get(settings.get("duration"), allowed_durations["medium"])
    ratio_instruction = allowed_ratios.get(settings.get("ratio"), allowed_ratios["16:9"])
    depth_instruction = allowed_depths.get(settings.get("depth"), allowed_depths["standard"])
    resolution_instruction = allowed_resolutions.get(settings.get("resolution"), allowed_resolutions["1080p"])
    narration_instruction = "旁白文案要更丰富，字幕节奏要清楚。" if settings.get("narration") else "旁白文字保持精炼，只保留关键解释。"
    bilingual_instruction = "必须提供中英双语字幕。" if settings.get("bilingual", True) else "只使用用户当前语言输出字幕。"
    mathjax_instruction = "需要使用 MathJax 渲染数学公式；请在生成的单文件 HTML 中引入 MathJax CDN，并用 LaTeX 语法书写公式。" if settings.get("mathjax") else "不要引入 MathJax，数学表达使用普通文本或 SVG 图形呈现。"
    
    # Use configured model if not specified
    if model is None:
        model = MODEL

    debug_llm("request received", {
        "provider": "openai-compatible",
        "model": model,
        "topic": topic,
        "history": history,
        "settings": settings,
    })

    # The system prompt is now more focused
    system_prompt = f"""请你生成一个非常精美的动态动画,讲讲 {topic}
要动态的,要像一个完整的,正在播放的视频。包含一个完整的过程，能把知识点讲清楚。
页面极为精美，好看，有设计感，同时能够很好的传达知识。知识和图像要准确
生成规格：
- 风格：{style_instruction}
- 时长：{duration_instruction}
- 画幅：{ratio_instruction}
- 容器尺寸：{resolution_instruction}
- 讲解深度：{depth_instruction}
- 旁白：{narration_instruction}
- 字幕：{bilingual_instruction}
- 数学公式：{mathjax_instruction}
不需要任何互动按钮,直接开始播放
使用和谐好看，广泛采用的浅色配色方案，使用很多的，丰富的视觉元素。
**请保证任何一个元素都在指定分辨率的容器中被摆在了正确的位置，避免穿模，字幕遮挡，图形位置错误等等问题影响正确的视觉传达**
html+css+js+svg，放进一个html里，直接只给出html，不用其它总结"""

    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": topic},
    ]

    debug_conversation("openai-compatible", model, messages, settings)

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            temperature=0.8, 
        )
    except OpenAIError as e:
        debug_llm("openai-compatible error", str(e))
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        return

    debug_response_start("openai-compatible")
    async for chunk in response:
        # 某些 OpenAI-compatible / OpenRouter 流式块可能没有 choices 或没有 content
        choices = getattr(chunk, "choices", None)
        if not choices:
            continue

        choice = choices[0]
        delta = getattr(choice, "delta", None)
        if not delta:
            continue

        token = getattr(delta, "content", None) or ""
        if not token:
            continue

        debug_response_chunk(token)
        payload = json.dumps({"token": token}, ensure_ascii=False)
        yield f"data: {payload}\n\n"
        await asyncio.sleep(0.001)

    debug_response_end()

    debug_llm("stream complete", "[DONE]")
    yield 'data: {"event":"[DONE]"}\n\n'

# -----------------------------------------------------------------------
# 3. 路由 (CHANGED: Now a POST request)
# -----------------------------------------------------------------------
@app.get("/config")
async def get_public_config():
    return {"requiresPassphrase": bool(ACCESS_PASSPHRASES)}


@app.post("/verify-passphrase")
async def verify_passphrase(passphrase_request: PassphraseRequest):
    if ACCESS_PASSPHRASES and passphrase_request.passphrase not in ACCESS_PASSPHRASES:
        raise HTTPException(status_code=403, detail="暗号错误")
    return {"ok": True}


@app.post("/generate")
async def generate(
    chat_request: ChatRequest, # CHANGED: Use the Pydantic model
    request: Request,
):
    """
    Main endpoint: POST /generate
    Accepts a JSON body with "topic" and optional "history".
    Returns an SSE stream.
    """
    accumulated_response = ""  # for caching flow results
    queued = generation_semaphore.locked()

    async def event_generator():
        nonlocal accumulated_response
        if queued:
            payload = json.dumps({"event": "queued"}, ensure_ascii=False)
            yield f"data: {payload}\n\n"

        async with generation_semaphore:
            if queued:
                payload = json.dumps({"event": "started"}, ensure_ascii=False)
                yield f"data: {payload}\n\n"

            try:
                async for chunk in llm_event_stream(chat_request.topic, chat_request.history, settings=chat_request.settings):
                    accumulated_response += chunk
                    if await request.is_disconnected():
                        debug_llm("client disconnected")
                        break
                    yield chunk
            except Exception as e:
                debug_llm("streaming error", str(e))
                yield f"data: {json.dumps({'error': str(e)})}\n\n"


    async def wrapped_stream():
        async for chunk in event_generator():
            yield chunk

    headers = {
        "Cache-Control": "no-store",
        "Content-Type": "text/event-stream; charset=utf-8",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(wrapped_stream(), headers=headers)

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"time": datetime.now(shanghai_tz).strftime("%Y%m%d%H%M%S")},
    )

# -----------------------------------------------------------------------
# 4. 本地启动命令
# -----------------------------------------------------------------------
# uvicorn app:app --reload --host 0.0.0.0 --port 8000


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
