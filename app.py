import asyncio
import base64
import html
import io
import json
import os
import secrets
from datetime import datetime, timedelta
from typing import AsyncGenerator, List, Optional, Dict, Any
from urllib.parse import parse_qs

import pytz
import qrcode
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pypdf import PdfReader
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
MAX_PAPER_UPLOAD_BYTES = credentials.get("MAX_PAPER_UPLOAD_BYTES", 20 * 1024 * 1024)
MAX_PAPER_TEXT_CHARS = credentials.get("MAX_PAPER_TEXT_CHARS", 120000)
ACCESS_PASSPHRASES = credentials.get("ACCESS_PASSPHRASES")
generation_semaphore = asyncio.Semaphore(MAX_CONCURRENT_GENERATION_TASKS)
shared_html_links = {}
SHARE_STORAGE_DIR = os.path.join(os.path.dirname(__file__), "shared_html")
SHARE_CLEANUP_INTERVAL_SECONDS = 300


SHARE_EXPIRATION_SECONDS = {
    "1h": 60 * 60,
    "3h": 3 * 60 * 60,
    "6h": 6 * 60 * 60,
    "8h": 8 * 60 * 60,
    "1d": 24 * 60 * 60,
    "3d": 3 * 24 * 60 * 60,
    "7d": 7 * 24 * 60 * 60,
    "forever": None,
}


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


class ThoughtProcessFilter:
    START_MARKERS = (
        "<think>",
        "<thinking>",
        "<reasoning>",
        "思考过程：",
        "思考过程:",
    )
    END_MARKERS = (
        "</think>",
        "</thinking>",
        "</reasoning>",
        "最终答案：",
        "最终答案:",
        "答案：",
        "答案:",
    )

    def __init__(self):
        self.buffer = ""
        self.in_thought = False
        self.max_start_marker_length = max(len(marker) for marker in self.START_MARKERS)
        self.max_end_marker_length = max(len(marker) for marker in self.END_MARKERS)

    @staticmethod
    def _find_first_marker(text: str, markers: tuple[str, ...]):
        found_index = -1
        found_marker = None
        lower_text = text.lower()
        for marker in markers:
            index = lower_text.find(marker.lower())
            if index != -1 and (found_index == -1 or index < found_index):
                found_index = index
                found_marker = marker
        return found_index, found_marker

    def feed(self, text: str) -> str:
        if not text:
            return ""

        self.buffer += text
        visible_parts = []

        while self.buffer:
            if self.in_thought:
                index, marker = self._find_first_marker(self.buffer, self.END_MARKERS)
                if index == -1:
                    self.buffer = self.buffer[-(self.max_end_marker_length - 1):]
                    break
                self.buffer = self.buffer[index + len(marker):]
                self.in_thought = False
                continue

            index, marker = self._find_first_marker(self.buffer, self.START_MARKERS)
            if index == -1:
                keep_length = self.max_start_marker_length - 1
                if len(self.buffer) <= keep_length:
                    break
                visible_parts.append(self.buffer[:-keep_length])
                self.buffer = self.buffer[-keep_length:]
                break

            visible_parts.append(self.buffer[:index])
            self.buffer = self.buffer[index + len(marker):]
            self.in_thought = True

        return "".join(visible_parts)

    def flush(self) -> str:
        if self.in_thought:
            self.buffer = ""
            return ""
        visible = self.buffer
        self.buffer = ""
        return visible

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


class ShareRequest(BaseModel):
    html: str
    expiresIn: str
    password: str = Field(pattern=r"^\d{4,20}$")
    sourceWidth: int = 1920
    sourceHeight: int = 1080


def build_generation_setting_instructions(settings: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    settings = settings or {}
    allowed_styles = {
        "cinematic": "电影级叙事：镜头感强、节奏完整、视觉层次丰富。",
        "minimal": "极简专业：留白克制、信息清晰、图形精准。",
        "academic": "教学讲解：结构严谨、步骤明确、适合课堂演示。",
        "futuristic": "未来科技：高对比、科技感视觉、动态 HUD 元素。",
    }
    allowed_durations = {
        "preview": "快速预览：只生成一页，用来快速展示整体视觉效果；不要制作完整视频流程，不需要多段转场或长时间动画。",
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
    return {
        "style": allowed_styles.get(settings.get("style"), allowed_styles["cinematic"]),
        "duration": allowed_durations.get(settings.get("duration"), allowed_durations["medium"]),
        "ratio": allowed_ratios.get(settings.get("ratio"), allowed_ratios["16:9"]),
        "depth": allowed_depths.get(settings.get("depth"), allowed_depths["standard"]),
        "resolution": allowed_resolutions.get(settings.get("resolution"), allowed_resolutions["1080p"]),
        "narration": "旁白文案要更丰富，字幕节奏要清楚。" if settings.get("narration") else "旁白文字保持精炼，只保留关键解释。",
        "bilingual": "必须提供中英双语字幕。" if settings.get("bilingual", True) else "只使用用户当前语言输出字幕。",
        "mathjax": "需要使用 MathJax 渲染数学公式；请在生成的单文件 HTML 中引入 MathJax CDN，并用 LaTeX 语法书写公式。" if settings.get("mathjax") else "不要引入 MathJax，数学表达使用普通文本或 SVG 图形呈现。",
    }


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
    setting_instructions = build_generation_setting_instructions(settings)

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
- 风格：{setting_instructions['style']}
- 时长：{setting_instructions['duration']}
- 画幅：{setting_instructions['ratio']}
- 容器尺寸：{setting_instructions['resolution']}
- 讲解深度：{setting_instructions['depth']}
- 旁白：{setting_instructions['narration']}
- 字幕：{setting_instructions['bilingual']}
- 数学公式：{setting_instructions['mathjax']}
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
    thought_filter = ThoughtProcessFilter()
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

        visible_token = thought_filter.feed(token)
        if not visible_token:
            continue

        debug_response_chunk(visible_token)
        payload = json.dumps({"token": visible_token}, ensure_ascii=False)
        yield f"data: {payload}\n\n"
        await asyncio.sleep(0.001)

    remaining_token = thought_filter.flush()
    if remaining_token:
        debug_response_chunk(remaining_token)
        payload = json.dumps({"token": remaining_token}, ensure_ascii=False)
        yield f"data: {payload}\n\n"

    debug_response_end()

    debug_llm("stream complete", "[DONE]")
    yield 'data: {"event":"[DONE]"}\n\n'


def parse_settings_form(settings: str) -> Dict[str, Any]:
    try:
        parsed = json.loads(settings or "{}")
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


async def extract_pdf_text(pdf_file: UploadFile) -> Dict[str, Any]:
    filename = pdf_file.filename or "paper.pdf"
    content_type = pdf_file.content_type or ""
    if not filename.lower().endswith(".pdf") and "pdf" not in content_type.lower():
        raise ValueError("请上传 PDF 文件")

    content = await pdf_file.read()
    if not content:
        raise ValueError("PDF 文件为空")
    if len(content) > MAX_PAPER_UPLOAD_BYTES:
        raise ValueError(f"PDF 文件过大，请上传不超过 {MAX_PAPER_UPLOAD_BYTES // 1024 // 1024}MB 的文件")

    try:
        reader = PdfReader(io.BytesIO(content))
    except Exception as exc:
        raise ValueError("PDF 解析失败，请确认文件未损坏") from exc

    page_texts = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            page_texts.append(f"[Page {index}]\n{text}")

    paper_text = "\n\n".join(page_texts).strip()
    if not paper_text:
        raise ValueError("未能从 PDF 中提取文字，暂不支持扫描版或图片型论文")

    truncated = len(paper_text) > MAX_PAPER_TEXT_CHARS
    if truncated:
        paper_text = paper_text[:MAX_PAPER_TEXT_CHARS]

    return {
        "filename": filename,
        "text": paper_text,
        "page_count": len(reader.pages),
        "truncated": truncated,
    }


async def paper_llm_event_stream(
    paper_text: str,
    filename: str,
    focus: str = "",
    model: str = None,
    settings: Optional[Dict[str, Any]] = None,
    truncated: bool = False,
) -> AsyncGenerator[str, None]:
    settings = settings or {}
    setting_instructions = build_generation_setting_instructions(settings)
    if model is None:
        model = MODEL

    focus_instruction = (
        f"用户指定重点：{focus}。请围绕该章节或概念展开，但必须结合整篇论文上下文说明其动机、方法和意义。"
        if focus.strip()
        else "用户未指定重点。请生成整篇论文的动画讲解，覆盖研究背景、核心问题、方法框架、关键实验/结果、结论与启发。"
    )
    truncation_instruction = "论文原文因长度限制已被截断，请基于已提供内容生成，并避免声称看到了未提供的部分。" if truncated else "论文原文已完整提供给你。"

    system_prompt = f"""你是一个论文动画讲解视频导演和技术讲师。请根据用户上传的 PDF 论文内容，生成一个非常精美、可直接播放的动态动画讲解页面。
{focus_instruction}
{truncation_instruction}
生成规格：
- 风格：{setting_instructions['style']}
- 时长：{setting_instructions['duration']}
- 画幅：{setting_instructions['ratio']}
- 容器尺寸：{setting_instructions['resolution']}
- 讲解深度：{setting_instructions['depth']}
- 旁白：{setting_instructions['narration']}
- 字幕：{setting_instructions['bilingual']}
- 数学公式：{setting_instructions['mathjax']}
内容要求：
- 把论文讲成一个完整的视频脚本和视觉叙事，而不是静态摘要。
- 需要准确呈现论文的核心贡献、关键术语、方法流程和因果关系。
- 如果论文包含公式、模型结构、实验对比或数据流程，请用 SVG/HTML/CSS 动画清晰表达。
- 不需要任何互动按钮，打开后直接开始播放。
- 使用和谐好看、广泛采用的浅色配色方案，使用丰富的视觉元素。
- 请保证任何元素都在指定分辨率的容器中正确摆放，避免字幕遮挡、图形穿模和布局错位。
输出要求：
- 只输出一个完整的单文件 HTML。
- HTML 内联 CSS、JS、SVG；不要输出解释、总结或 Markdown 代码块外的文字。"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"论文文件名：{filename}\n\n论文内容：\n{paper_text}"},
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
    thought_filter = ThoughtProcessFilter()
    async for chunk in response:
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

        visible_token = thought_filter.feed(token)
        if not visible_token:
            continue

        debug_response_chunk(visible_token)
        payload = json.dumps({"token": visible_token}, ensure_ascii=False)
        yield f"data: {payload}\n\n"
        await asyncio.sleep(0.001)

    remaining_token = thought_filter.flush()
    if remaining_token:
        debug_response_chunk(remaining_token)
        payload = json.dumps({"token": remaining_token}, ensure_ascii=False)
        yield f"data: {payload}\n\n"

    debug_response_end()
    debug_llm("paper stream complete", "[DONE]")
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


def build_share_access_page(error_message: str = ""):
    error_html = f'<p class="error">{html.escape(error_message)}</p>' if error_message else ""
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>访问分享动画</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 24px; font-family: 'MiSans', 'HarmonyOS Sans SC', 'Microsoft YaHei', sans-serif; color: #000; background: linear-gradient(90deg, rgba(0,0,0,.06) 1px, transparent 1px), linear-gradient(0deg, rgba(0,0,0,.06) 1px, transparent 1px), #fff; background-size: 48px 48px; }}
        .card {{ width: min(420px, 100%); padding: 28px; background: #fff; border: 1px solid #000; box-shadow: 12px 12px 0 #000; display: grid; gap: 14px; }}
        p {{ margin: 0; font-size: .72rem; font-weight: 900; letter-spacing: .18em; }}
        h1 {{ margin: 0; font-size: clamp(2rem, 7vw, 4rem); letter-spacing: -.08em; line-height: .95; }}
        input {{ min-height: 52px; border: 1px solid #000; padding: 0 14px; font: inherit; }}
        input:focus, button:focus-visible {{ outline: 2px solid #000; outline-offset: 3px; }}
        button {{ min-height: 50px; border: 1px solid #000; background: #000; color: #fff; font: inherit; font-weight: 900; cursor: pointer; }}
        button:hover {{ background: #fff; color: #000; }}
        .error {{ color: #b10000; letter-spacing: 0; }}
    </style>
</head>
<body>
    <form class="card" method="post">
        <p>SHARED ANIMATION</p>
        <h1>请输入访问密码</h1>
        {error_html}
        <input name="password" type="password" placeholder="访问密码" required autofocus>
        <button type="submit">进入</button>
    </form>
</body>
</html>"""


def create_qr_data_url(value: str):
    image = qrcode.make(value)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def build_shared_viewer_page(html_content: str, source_width: int, source_height: int):
    safe_width = min(max(source_width, 320), 4096)
    safe_height = min(max(source_height, 320), 4096)
    escaped_srcdoc = html.escape(html_content, quote=True)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>NVIC-质象分享</title>
    <style>
        * {{ box-sizing: border-box; }}
        html, body {{ width: 100%; height: 100%; margin: 0; overflow: hidden; background: #fff; }}
        body {{ display: grid; place-items: center; font-family: 'MiSans', 'HarmonyOS Sans SC', 'Microsoft YaHei', sans-serif; }}
        .viewer {{ width: min(100vw, calc(100vh * {safe_width} / {safe_height})); height: min(100vh, calc(100vw * {safe_height} / {safe_width})); border: 1px solid #000; background: #111; overflow: hidden; }}
        iframe {{ width: {safe_width}px; height: {safe_height}px; border: 0; display: block; background: #fff; transform: scale(var(--viewer-scale, 1)); transform-origin: top left; }}
        .orientation-prompt {{ position: fixed; inset: 0; z-index: 10; display: none; place-items: center; padding: 24px; background: rgba(255, 255, 255, .94); color: #000; text-align: center; font-weight: 900; }}
        .orientation-prompt.visible {{ display: grid; }}
        .orientation-card {{ display: grid; gap: 16px; max-width: 420px; padding: 24px; border: 1px solid #000; background: #fff; box-shadow: 8px 8px 0 #000; }}
        .orientation-card button {{ min-height: 44px; padding: 0 16px; border: 1px solid #000; background: #000; color: #fff; font: inherit; font-weight: 900; cursor: pointer; }}
    </style>
</head>
<body>
    <main class="viewer"><iframe sandbox="allow-scripts allow-same-origin" srcdoc="{escaped_srcdoc}"></iframe></main>
    <div id="orientation-prompt" class="orientation-prompt">
        <div class="orientation-card">
            <div>移动端适配较差，推荐PC端查看</div>
            <button type="button" id="orientation-dismiss">继续竖屏观看</button>
        </div>
    </div>
    <script>
        (function () {{
            var dismissed = false;
            var prompt = document.getElementById('orientation-prompt');
            var viewer = document.querySelector('.viewer');
            var sourceWidth = {safe_width};
            var sourceHeight = {safe_height};
            document.getElementById('orientation-dismiss').addEventListener('click', function () {{
                dismissed = true;
                prompt.classList.remove('visible');
            }});
            function fitViewer() {{
                var scale = Math.min(viewer.clientWidth / sourceWidth, viewer.clientHeight / sourceHeight);
                viewer.style.setProperty('--viewer-scale', scale.toString());
            }}
            function shouldShowMobilePrompt() {{
                return !dismissed && /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent);
            }}
            function updatePrompt() {{
                fitViewer();
                prompt.classList.toggle('visible', shouldShowMobilePrompt());
            }}
            window.addEventListener('resize', updatePrompt);
            window.addEventListener('orientationchange', updatePrompt);
            updatePrompt();
        }})();
    </script>
</body>
</html>"""


def get_share_paths(share_id: str):
    return {
        "meta": os.path.join(SHARE_STORAGE_DIR, f"{share_id}.json"),
        "html": os.path.join(SHARE_STORAGE_DIR, f"{share_id}.html"),
    }


def serialize_share_record(record: Dict[str, Any]):
    return {
        "password": record["password"],
        "created_at": record["created_at"].isoformat(),
        "expires_at": record["expires_at"].isoformat() if record["expires_at"] else None,
    }


def parse_share_datetime(value: str):
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return shanghai_tz.localize(parsed)
    return parsed.astimezone(shanghai_tz)


def load_share_from_disk(share_id: str):
    paths = get_share_paths(share_id)
    if not os.path.exists(paths["meta"]) or not os.path.exists(paths["html"]):
        return None
    with open(paths["meta"], "r", encoding="utf-8") as file:
        meta = json.load(file)
    with open(paths["html"], "r", encoding="utf-8") as file:
        html_content = file.read()
    record = {
        "html": html_content,
        "password": meta["password"],
        "created_at": parse_share_datetime(meta["created_at"]),
        "expires_at": parse_share_datetime(meta["expires_at"]) if meta.get("expires_at") else None,
    }
    shared_html_links[share_id] = record
    return record


def save_share_to_disk(share_id: str, record: Dict[str, Any]):
    os.makedirs(SHARE_STORAGE_DIR, exist_ok=True)
    paths = get_share_paths(share_id)
    with open(paths["html"], "w", encoding="utf-8") as file:
        file.write(record["html"])
    with open(paths["meta"], "w", encoding="utf-8") as file:
        json.dump(serialize_share_record(record), file, ensure_ascii=False, indent=2)


def delete_share(share_id: str):
    shared_html_links.pop(share_id, None)
    for path in get_share_paths(share_id).values():
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


def get_share_record(share_id: str):
    record = shared_html_links.get(share_id) or load_share_from_disk(share_id)
    if not record:
        return None
    if record["expires_at"] and record["expires_at"] <= datetime.now(shanghai_tz):
        delete_share(share_id)
        return None
    return record


def cleanup_expired_shares_once():
    now = datetime.now(shanghai_tz)
    os.makedirs(SHARE_STORAGE_DIR, exist_ok=True)
    for share_id, record in list(shared_html_links.items()):
        if record["expires_at"] and record["expires_at"] <= now:
            delete_share(share_id)
    for filename in os.listdir(SHARE_STORAGE_DIR):
        if not filename.endswith(".json"):
            continue
        share_id = filename[:-5]
        record = load_share_from_disk(share_id)
        if record and record["expires_at"] <= now:
            delete_share(share_id)


async def cleanup_expired_shares_loop():
    while True:
        cleanup_expired_shares_once()
        await asyncio.sleep(SHARE_CLEANUP_INTERVAL_SECONDS)


@app.on_event("startup")
async def start_share_cleanup_task():
    cleanup_expired_shares_once()
    asyncio.create_task(cleanup_expired_shares_loop())


@app.post("/share")
async def create_share_link(share_request: ShareRequest, request: Request):
    ttl_seconds = SHARE_EXPIRATION_SECONDS.get(share_request.expiresIn)
    if share_request.expiresIn not in SHARE_EXPIRATION_SECONDS:
        raise HTTPException(status_code=400, detail="Invalid expiration")
    if not share_request.html.strip():
        raise HTTPException(status_code=400, detail="HTML content is required")

    share_id = secrets.token_urlsafe(16)
    created_at = datetime.now(shanghai_tz)
    expires_at = created_at + timedelta(seconds=ttl_seconds) if ttl_seconds else None
    record = {
        "html": build_shared_viewer_page(share_request.html, share_request.sourceWidth, share_request.sourceHeight),
        "password": share_request.password,
        "created_at": created_at,
        "expires_at": expires_at,
    }
    shared_html_links[share_id] = record
    save_share_to_disk(share_id, record)
    share_url = str(request.url_for("read_shared_html", share_id=share_id))
    return {
        "url": share_url,
        "qrCode": create_qr_data_url(share_url),
        "createdAt": created_at.isoformat(),
        "expiresAt": expires_at.isoformat() if expires_at else None,
        "password": share_request.password,
    }


@app.get("/share/{share_id}", response_class=HTMLResponse)
async def read_shared_html(share_id: str):
    shared = get_share_record(share_id)
    if not shared:
        raise HTTPException(status_code=404, detail="Share link expired or not found")
    if shared["password"]:
        return HTMLResponse(build_share_access_page())
    return HTMLResponse(shared["html"])


@app.post("/share/{share_id}", response_class=HTMLResponse)
async def verify_shared_html(share_id: str, request: Request):
    shared = get_share_record(share_id)
    if not shared:
        raise HTTPException(status_code=404, detail="Share link expired or not found")

    body = (await request.body()).decode()
    form = parse_qs(body)
    password = form.get("password", [""])[0]
    if shared["password"] and password != shared["password"]:
        return HTMLResponse(build_share_access_page("访问密码错误"), status_code=403)
    return HTMLResponse(shared["html"])


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


@app.post("/paper/generate")
async def generate_paper(
    request: Request,
    pdf: UploadFile = File(...),
    focus: str = Form(""),
    settings: str = Form("{}"),
):
    parsed_settings = parse_settings_form(settings)
    queued = generation_semaphore.locked()

    async def event_generator():
        if queued:
            payload = json.dumps({"event": "queued"}, ensure_ascii=False)
            yield f"data: {payload}\n\n"

        async with generation_semaphore:
            if queued:
                payload = json.dumps({"event": "started"}, ensure_ascii=False)
                yield f"data: {payload}\n\n"

            try:
                paper = await extract_pdf_text(pdf)
                async for chunk in paper_llm_event_stream(
                    paper["text"],
                    paper["filename"],
                    focus=focus.strip(),
                    settings=parsed_settings,
                    truncated=paper["truncated"],
                ):
                    if await request.is_disconnected():
                        debug_llm("paper client disconnected")
                        break
                    yield chunk
            except Exception as e:
                debug_llm("paper streaming error", str(e))
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    headers = {
        "Cache-Control": "no-store",
        "Content-Type": "text/event-stream; charset=utf-8",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(event_generator(), headers=headers)

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
