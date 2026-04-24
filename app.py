import streamlit as st
import requests
import datetime
import base64
import re
import urllib.parse
from html import escape


# =========================
# 1. Page config
# =========================
st.set_page_config(
    page_title="Maison Insight｜产品研判平台",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================
# 2. Luxury-style UI CSS
# =========================
def inject_luxury_css():
    st.markdown(
        """
        <style>
        :root {
            --lux-black: #0B0A08;
            --lux-ink: #17120D;
            --lux-coffee: #3B2F24;
            --lux-gold: #B99A5B;
            --lux-gold-soft: #D8C49A;
            --lux-cream: #F7F1E7;
            --lux-porcelain: #FBF8F1;
            --lux-mist: #EFE7DA;
            --lux-muted: #8C806E;
            --lux-line: rgba(185, 154, 91, 0.28);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(185,154,91,0.16), transparent 30%),
                linear-gradient(135deg, #0B0A08 0%, #17120D 36%, #F7F1E7 36%, #FBF8F1 100%);
            color: var(--lux-ink);
        }

        /* Main content width */
        .block-container {
            padding-top: 2.2rem;
            padding-bottom: 4rem;
            max-width: 1280px;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #080706 0%, #17120D 100%);
            border-right: 1px solid rgba(185,154,91,0.28);
        }
        section[data-testid="stSidebar"] * {
            color: #F7F1E7 !important;
        }
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stCaption,
        section[data-testid="stSidebar"] p {
            color: rgba(247,241,231,0.72) !important;
        }
        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] textarea,
        section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
        section[data-testid="stSidebar"] div[data-baseweb="tag"] {
            background: rgba(255,255,255,0.07) !important;
            border: 1px solid rgba(185,154,91,0.35) !important;
            border-radius: 2px !important;
            color: #F7F1E7 !important;
        }
        section[data-testid="stSidebar"] hr {
            border-color: rgba(185,154,91,0.25);
        }

        /* Typography */
        h1, h2, h3 {
            letter-spacing: -0.03em;
        }
        .lux-hero {
            padding: 52px 56px 48px;
            border-radius: 0px;
            background:
                linear-gradient(120deg, rgba(11,10,8,0.96) 0%, rgba(23,18,13,0.93) 56%, rgba(59,47,36,0.84) 100%),
                radial-gradient(circle at 78% 18%, rgba(217,196,154,0.25), transparent 28%);
            border: 1px solid rgba(185,154,91,0.36);
            box-shadow: 0 30px 80px rgba(0,0,0,0.22);
            position: relative;
            overflow: hidden;
            margin-bottom: 26px;
        }
        .lux-hero:after {
            content: "";
            position: absolute;
            right: -120px;
            top: -160px;
            width: 420px;
            height: 420px;
            border: 1px solid rgba(216,196,154,0.18);
            transform: rotate(35deg);
        }
        .lux-eyebrow {
            font-size: 12px;
            letter-spacing: 0.32em;
            text-transform: uppercase;
            color: var(--lux-gold-soft);
            margin-bottom: 18px;
        }
        .lux-title {
            font-family: Georgia, 'Times New Roman', 'Songti SC', serif;
            font-size: clamp(48px, 6.5vw, 88px);
            line-height: 0.92;
            color: #F7F1E7;
            font-weight: 400;
            margin: 0 0 18px 0;
        }
        .lux-title span {
            color: var(--lux-gold-soft);
            font-style: italic;
        }
        .lux-subtitle {
            max-width: 760px;
            color: rgba(247,241,231,0.76);
            font-size: 17px;
            line-height: 1.8;
            margin-bottom: 28px;
        }
        .lux-meta-row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .lux-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 13px;
            border: 1px solid rgba(216,196,154,0.28);
            color: rgba(247,241,231,0.78);
            background: rgba(255,255,255,0.045);
            font-size: 12px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .lux-panel {
            background: rgba(251,248,241,0.92);
            border: 1px solid rgba(185,154,91,0.28);
            box-shadow: 0 18px 45px rgba(34,24,12,0.08);
            padding: 28px;
            margin: 16px 0 22px;
        }
        .lux-panel.dark {
            background: linear-gradient(135deg, #11100E 0%, #241B12 100%);
            color: #F7F1E7;
        }
        .lux-section-kicker {
            color: var(--lux-gold);
            font-size: 12px;
            letter-spacing: 0.26em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .lux-section-title {
            font-family: Georgia, 'Times New Roman', 'Songti SC', serif;
            font-size: 30px;
            font-weight: 400;
            color: var(--lux-ink);
            margin-bottom: 8px;
        }
        .lux-section-desc {
            color: var(--lux-muted);
            line-height: 1.75;
            font-size: 14px;
            margin-bottom: 12px;
        }
        .dark .lux-section-title { color: #F7F1E7; }
        .dark .lux-section-desc { color: rgba(247,241,231,0.68); }

        .lux-stat-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin: 18px 0 8px;
        }
        .lux-stat {
            padding: 18px 18px 16px;
            border: 1px solid rgba(185,154,91,0.25);
            background: rgba(255,255,255,0.52);
        }
        .lux-stat-num {
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 28px;
            color: var(--lux-coffee);
            margin-bottom: 4px;
        }
        .lux-stat-text {
            color: var(--lux-muted);
            font-size: 12px;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .source-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 12px;
            margin-top: 12px;
        }
        .source-card {
            display: block;
            min-height: 104px;
            padding: 18px 15px;
            text-decoration: none !important;
            border: 1px solid rgba(185,154,91,0.25);
            background: linear-gradient(180deg, rgba(255,255,255,0.70), rgba(247,241,231,0.76));
            color: var(--lux-ink) !important;
            transition: all .18s ease;
        }
        .source-card:hover {
            transform: translateY(-3px);
            border-color: rgba(185,154,91,0.68);
            box-shadow: 0 16px 32px rgba(59,47,36,0.10);
        }
        .source-index {
            font-family: Georgia, 'Times New Roman', serif;
            color: var(--lux-gold);
            font-size: 19px;
            margin-bottom: 14px;
        }
        .source-name {
            font-size: 14px;
            line-height: 1.35;
            font-weight: 600;
            color: var(--lux-ink);
        }
        .source-note {
            margin-top: 8px;
            font-size: 11px;
            color: var(--lux-muted);
            letter-spacing: 0.04em;
        }

        .stTextInput input, .stTextArea textarea {
            border-radius: 0 !important;
            border: 1px solid rgba(59,47,36,0.22) !important;
            background: rgba(255,255,255,0.78) !important;
            color: var(--lux-ink) !important;
            box-shadow: none !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: rgba(185,154,91,0.88) !important;
            box-shadow: 0 0 0 1px rgba(185,154,91,0.25) !important;
        }

        .stButton > button, .stDownloadButton > button {
            border-radius: 0 !important;
            border: 1px solid rgba(185,154,91,0.72) !important;
            background: linear-gradient(135deg, #11100E 0%, #3B2F24 100%) !important;
            color: #F7F1E7 !important;
            min-height: 48px;
            letter-spacing: 0.12em;
            font-size: 13px;
            text-transform: uppercase;
            box-shadow: 0 12px 28px rgba(11,10,8,0.18);
            transition: all .18s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            transform: translateY(-1px);
            border-color: #D8C49A !important;
            box-shadow: 0 18px 36px rgba(11,10,8,0.25);
        }

        div[data-testid="stAlert"] {
            border-radius: 0;
            border: 1px solid rgba(185,154,91,0.28);
            background: rgba(251,248,241,0.82);
        }
        div[data-testid="stExpander"] {
            border-radius: 0 !important;
            border: 1px solid rgba(185,154,91,0.28) !important;
            background: rgba(251,248,241,0.86) !important;
        }

        .report-preview {
            padding: 28px;
            border: 1px solid rgba(185,154,91,0.3);
            background: rgba(251,248,241,0.94);
            box-shadow: 0 18px 45px rgba(34,24,12,0.08);
        }
        .download-link {
            text-decoration: none !important;
            background: linear-gradient(135deg, #11100E 0%, #3B2F24 100%);
            color: #F7F1E7 !important;
            padding: 13px 24px;
            border: 1px solid rgba(216,196,154,0.72);
            display: inline-block;
            letter-spacing: 0.10em;
            font-size: 13px;
            margin-top: 12px;
        }

        @media (max-width: 900px) {
            .lux-hero { padding: 36px 28px; }
            .source-grid, .lux-stat-grid { grid-template-columns: 1fr; }
            .lux-title { font-size: 46px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_luxury_css()


# =========================
# 3. Search links and helpers
# =========================
def get_search_links(keyword: str):
    keyword = keyword.strip()
    enc = urllib.parse.quote(keyword)
    return {
        "小红书｜体验与痛点": f"https://www.xiaohongshu.com/search_result?keyword={enc}%20体验%20吐槽",
        "微博｜热议与争议": f"https://s.weibo.com/weibo?q={enc}%20争议%20翻车",
        "抖音｜短视频反馈": f"https://www.douyin.com/search/{enc}%20缺点%20体验",
        "B站｜深度测评": f"https://search.bilibili.com/all?keyword={enc}%20测评%20体验",
        "百度｜全网补充": f"https://www.baidu.com/s?wd={enc}%20口碑%20测评%20问题",
    }


def render_link_grid(links: dict[str, str]):
    cards = []
    for idx, (name, url) in enumerate(links.items(), start=1):
        cards.append(
            f"""
            <a class="source-card" href="{escape(url)}" target="_blank" rel="noopener noreferrer">
                <div class="source-index">{idx:02d}</div>
                <div class="source-name">{escape(name)}</div>
                <div class="source-note">OPEN SOURCE GATEWAY</div>
            </a>
            """
        )
    st.markdown(f"<div class='source-grid'>{''.join(cards)}</div>", unsafe_allow_html=True)


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|\s]+", "_", name.strip())
    return name[:80] or "product_report"


def is_ready_to_analyze(api_key: str, *texts: str) -> bool:
    if not api_key.strip():
        st.warning("请先在左侧输入 API Key。")
        return False
    if any(not text.strip() for text in texts):
        st.warning("请先填写产品名，并粘贴真实语料。")
        return False
    return True


def render_hero():
    st.markdown(
        """
        <section class="lux-hero">
            <div class="lux-eyebrow">MAISON INSIGHT · PRODUCT INTELLIGENCE</div>
            <h1 class="lux-title">Product<br><span>Intelligence</span> Atelier</h1>
            <div class="lux-subtitle">
                输入产品名，建立 UGC 取证链路；粘贴真实语料，输出单品研判与竞品攻防报告。
                保留工具效率，但视觉上更像一个高端品牌官网的策略工作台。
            </div>
            <div class="lux-meta-row">
                <span class="lux-pill">◆ Evidence-based</span>
                <span class="lux-pill">◆ No hallucination</span>
                <span class="lux-pill">◆ Strategy-ready</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_lux_panel(kicker: str, title: str, desc: str, dark: bool = False):
    klass = "lux-panel dark" if dark else "lux-panel"
    st.markdown(
        f"""
        <div class="{klass}">
            <div class="lux-section-kicker">{escape(kicker)}</div>
            <div class="lux-section-title">{escape(title)}</div>
            <div class="lux-section-desc">{escape(desc)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# 4. LLM engine
# =========================
def analyze_with_llm(prompt: str, api_key: str, model_name: str, api_base: str):
    url = api_base.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": "Bearer " + api_key.strip(),
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_name.strip(),
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是一名严谨的产品策略与用户舆情分析师。"
                    "你只能根据用户提供的真实语料进行分析，严禁编造参数、销量、配置、发布时间、品牌动作或用户评价。"
                    "如果语料中没有提到某个信息，必须写‘暂无提及’。"
                    "输出要像产品/市场团队内部简报：结论明确、问题分层、建议可执行。"
                    "表格请使用 Markdown 表格。"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.0,
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"ERROR: 引擎响应异常，请检查 API Key、模型名称或接口地址。错误信息：{e}"


# =========================
# 5. Prompt templates
# =========================
def build_single_prompt(product_name: str, product_type: str, focus: list[str], corpus: str) -> str:
    focus_text = "、".join(focus) if focus else "用户体验、核心卖点、负面反馈、购买阻力、传播机会"
    return f"""
请仅根据下方语料，撰写《{product_name} 单品深度研判报告》。

产品名称：{product_name}
产品类型：{product_type}
重点关注：{focus_text}

输出结构：
一、核心结论摘要
- 用 3 条以内说清楚当前用户反馈的主线。

二、用户原声直击
- 提取 3 条最有代表性的原话或近似原话。
- 如果语料中没有明显原声，写“暂无提及”。

三、问题反馈矩阵
请输出 Markdown 表格，字段为：
| 维度 | 用户反馈/痛点 | 证据摘录 | 严重程度 | 改进紧迫性 |
维度可根据语料自适应，例如：外观设计、影像/性能、系统体验、价格价值感、服务/渠道、品牌认知等。

四、机会点与可放大的卖点
- 只写语料中能够支撑的机会点。
- 不允许虚构产品参数。

五、产品/营销动作建议
- 分为“短期可做”“中期优化”“传播话术建议”。
- 每条建议必须能对应到语料中的问题或机会。

六、信息缺口
- 列出当前语料不足以判断的内容。

真实语料如下：
{corpus}
""".strip()


def build_compare_prompt(
    main_product: str,
    competitor_product: str,
    product_type: str,
    focus: list[str],
    main_corpus: str,
    competitor_corpus: str,
) -> str:
    focus_text = "、".join(focus) if focus else "用户体验、核心卖点、负面反馈、购买阻力、传播机会"
    return f"""
请仅根据下方两组语料，撰写《{main_product} vs {competitor_product} 竞品攻防研判报告》。

本品：{main_product}
竞品：{competitor_product}
产品类型：{product_type}
重点关注：{focus_text}

输出结构：
一、对比结论摘要
- 用 3 条以内说清楚本品与竞品的主要差异。

二、双方用户原声
- 分别列出本品和竞品各 2 条最有代表性的原声。
- 如果某一方语料不足，写“暂无提及”。

三、竞品攻防矩阵
请输出 Markdown 表格，字段为：
| 对比维度 | {main_product} 用户反馈 | {competitor_product} 用户反馈 | 本品风险 | 可用攻防策略 |
维度根据语料自适应，例如：外观设计、性能、系统、价格、品牌、高端认可度、服务体验等。

四、本品应重点防守的点
- 只基于语料，不虚构。

五、本品可主动进攻的点
- 只基于语料，不虚构。

六、传播话术建议
- 给出 3 条以内适合产品/市场团队使用的话术方向。
- 不得出现无证据支撑的夸张表达。

七、信息缺口
- 列出当前语料不足以判断的内容。

【本品真实语料】
{main_corpus}

【竞品真实语料】
{competitor_corpus}
""".strip()


# =========================
# 6. Luxury report export
# =========================
def generate_html_report(text_content: str, title: str):
    html_template = """
    <html><head><meta charset="utf-8"><style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
        background: #0B0A08;
        padding: 42px;
        color: #17120D;
    }
    .report-card {
        max-width: 960px;
        margin: 0 auto;
        background: #FBF8F1;
        padding: 54px;
        border: 1px solid rgba(185,154,91,0.45);
        box-shadow: 0 30px 80px rgba(0,0,0,0.30);
    }
    .eyebrow {
        text-align: center;
        color: #B99A5B;
        font-size: 11px;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        margin-bottom: 18px;
    }
    h1 {
        text-align: center;
        font-family: Georgia, 'Times New Roman', 'Songti SC', serif;
        font-weight: 400;
        font-size: 34px;
        color: #17120D;
        margin: 0 0 10px 0;
        letter-spacing: -0.03em;
    }
    .meta {
        text-align: center;
        color: #8C806E;
        font-size: 12px;
        margin-bottom: 34px;
        border-bottom: 1px solid rgba(185,154,91,0.30);
        padding-bottom: 22px;
    }
    h2 {
        font-family: Georgia, 'Times New Roman', 'Songti SC', serif;
        font-weight: 400;
        font-size: 23px;
        color: #3B2F24;
        margin: 34px 0 16px 0;
        padding-top: 18px;
        border-top: 1px solid rgba(185,154,91,0.26);
    }
    .quote-box {
        background: #F7F1E7;
        border-left: 3px solid #B99A5B;
        padding: 15px 18px;
        margin: 14px 0;
        color: #3B2F24;
        font-size: 15px;
        line-height: 1.75;
    }
    p { line-height: 1.82; margin: 9px 0; }
    table { width: 100%; border-collapse: collapse; margin: 22px 0; font-size: 13px; }
    th, td { padding: 13px; border: 1px solid rgba(185,154,91,0.25); text-align: left; vertical-align: top; }
    th { background: #F1E6D2; font-weight: 700; color: #17120D; }
    .footer {
        text-align: center;
        margin-top: 46px;
        padding-top: 20px;
        border-top: 1px solid rgba(185,154,91,0.26);
        font-size: 11px;
        color: #8C806E;
        letter-spacing: 0.08em;
    }
    </style></head><body>
    <div class="report-card">
        <div class="eyebrow">MAISON INSIGHT · PRODUCT STRATEGY BRIEF</div>
        <h1>{{TITLE}}</h1>
        <div class="meta">生成日期：{{DATE}} · 基于用户提供语料自动生成，仅供内部分析参考</div>
        {{BODY}}
        <div class="footer">EVIDENCE-BASED · STRATEGY-READY · NO HALLUCINATION</div>
    </div></body></html>
    """

    clean_text = re.sub(r"\|[-: ]+\|", "", text_content)
    clean_text = re.sub(r"[*#]", "", clean_text)

    body_html = ""
    lines = clean_text.split("\n")
    in_table = False
    is_quote_section = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if any(line.startswith(prefix) for prefix in ["一、", "二、", "三、", "四、", "五、", "六、", "七、"]):
            if in_table:
                body_html += "</tbody></table>"
                in_table = False
            is_quote_section = "原声" in line or "直击" in line
            body_html += f"<h2>{escape(line)}</h2>"
        elif "|" in line:
            cells = [escape(c.strip()) for c in line.split("|") if c.strip()]
            if len(cells) >= 2:
                row = "<tr>" + "".join([f"<td>{c}</td>" for c in cells]) + "</tr>"
                if not in_table:
                    body_html += "<table><thead>" + row.replace("td>", "th>") + "</thead><tbody>"
                    in_table = True
                else:
                    body_html += row
        else:
            if in_table:
                body_html += "</tbody></table>"
                in_table = False
            if is_quote_section and not line.startswith("-"):
                body_html += f"<div class='quote-box'>“{escape(line)}”</div>"
            else:
                body_html += f"<p>{escape(line)}</p>"

    if in_table:
        body_html += "</tbody></table>"

    res = html_template.replace("{{TITLE}}", escape(title))
    res = res.replace("{{DATE}}", str(datetime.date.today()))
    res = res.replace("{{BODY}}", body_html)

    b64 = base64.b64encode(res.encode("utf-8")).decode()
    filename = sanitize_filename(title)
    return (
        f'<a class="download-link" href="data:text/html;base64,{b64}" '
        f'download="{filename}.html">EXPORT REPORT · HTML/PDF</a>'
    )


# =========================
# 7. Sidebar controls
# =========================
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 18px 0 10px; border-bottom: 1px solid rgba(185,154,91,0.26); margin-bottom: 18px;">
            <div style="font-family: Georgia, serif; font-size: 28px; color: #F7F1E7; letter-spacing: -0.03em;">Maison Insight</div>
            <div style="font-size: 11px; color: rgba(247,241,231,0.58); letter-spacing: 0.22em; margin-top: 6px;">STRATEGY ATELIER</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("SYSTEM ACCESS")
    api_key = st.text_input("API Key", type="password", placeholder="sk-... / dashscope key")
    api_base = st.text_input(
        "接口地址",
        value="https://dashscope.aliyuncs.com/compatible-mode/v1",
        help="需兼容 OpenAI Chat Completions 格式。阿里云 DashScope 可保持默认。",
    )
    model_name = st.text_input("模型代号", value="deepseek-v3")

    st.divider()
    st.caption("ANALYSIS SETUP")
    mode = st.radio("任务模式", ["单品深度研判", "竞品对比攻防"])
    product_type = st.selectbox(
        "产品类型",
        ["手机/消费电子", "汽车/智能座舱", "家电/IOT", "软件/App", "旅游/酒店产品", "其他"],
    )
    focus = st.multiselect(
        "分析重点",
        ["用户痛点", "卖点感知", "价格价值感", "品牌认知", "系统/软件体验", "影像/性能", "外观设计", "渠道/服务", "传播话术"],
        default=["用户痛点", "卖点感知", "价格价值感", "传播话术"],
    )


# =========================
# 8. Main UI
# =========================
render_hero()

st.markdown(
    """
    <div class="lux-stat-grid">
        <div class="lux-stat"><div class="lux-stat-num">01</div><div class="lux-stat-text">Search Product</div></div>
        <div class="lux-stat"><div class="lux-stat-num">02</div><div class="lux-stat-text">Collect UGC Evidence</div></div>
        <div class="lux-stat"><div class="lux-stat-num">03</div><div class="lux-stat-text">Generate Strategy Brief</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)


if mode == "单品深度研判":
    render_lux_panel(
        "SINGLE PRODUCT STUDY",
        "单品深度研判",
        "适合分析某一款产品当前的真实用户反馈、主要痛点、机会卖点与下一步传播建议。",
    )

    product_name = st.text_input(
        "产品名称",
        placeholder="例如：vivo X Fold5、OPPO Find N6、iPhone 17、小米汽车 SU7",
    )

    if product_name.strip():
        st.markdown("#### 取证入口")
        st.caption("点击下方入口去外部平台收集真实语料，再粘贴回本页面。")
        render_link_grid(get_search_links(product_name))
    else:
        st.info("先输入产品名称，系统会自动生成小红书、微博、抖音、B站、百度的搜索入口。")

    st.markdown("#### 原始语料")
    user_input = st.text_area(
        "请粘贴真实评论、测评摘录、社媒反馈或客服反馈",
        height=300,
        placeholder="建议按平台分段粘贴，例如：\n【小红书】……\n【微博】……\n【B站】……",
    )

    if st.button("GENERATE SINGLE PRODUCT BRIEF", type="primary", use_container_width=True):
        if is_ready_to_analyze(api_key, product_name, user_input):
            with st.spinner("正在基于真实语料生成研判报告..."):
                prompt = build_single_prompt(product_name.strip(), product_type, focus, user_input.strip())
                report = analyze_with_llm(prompt, api_key, model_name, api_base)
                title = f"{product_name.strip()}_单品深度研判报告"
                st.markdown("### 报告预览")
                st.markdown("<div class='report-preview'>", unsafe_allow_html=True)
                st.markdown(report)
                st.markdown(generate_html_report(report, title), unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

else:
    render_lux_panel(
        "COMPETITIVE DUEL",
        "竞品对比攻防",
        "适合把本品与竞品的 UGC 反馈放在同一张策略桌上，判断防守点、进攻点与可用传播话术。",
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("#### 本品")
        main_product = st.text_input("本品名称", placeholder="例如：vivo X Fold5")
        if main_product.strip():
            render_link_grid(get_search_links(main_product))
        main_input = st.text_area(
            "贴入本品真实语料",
            height=300,
            placeholder="粘贴本品评论/测评/用户反馈...",
        )

    with col2:
        st.markdown("#### 竞品")
        competitor_product = st.text_input("竞品名称", placeholder="例如：OPPO Find N6 / 华为 Mate X 系列")
        if competitor_product.strip():
            render_link_grid(get_search_links(competitor_product))
        competitor_input = st.text_area(
            "贴入竞品真实语料",
            height=300,
            placeholder="粘贴竞品评论/测评/用户反馈...",
        )

    if st.button("GENERATE COMPETITIVE BRIEF", type="primary", use_container_width=True):
        if is_ready_to_analyze(api_key, main_product, competitor_product, main_input, competitor_input):
            with st.spinner("正在构建竞品攻防研判报告..."):
                prompt = build_compare_prompt(
                    main_product.strip(),
                    competitor_product.strip(),
                    product_type,
                    focus,
                    main_input.strip(),
                    competitor_input.strip(),
                )
                report = analyze_with_llm(prompt, api_key, model_name, api_base)
                title = f"{main_product.strip()}_vs_{competitor_product.strip()}_竞品攻防研判报告"
                st.markdown("### 报告预览")
                st.markdown("<div class='report-preview'>", unsafe_allow_html=True)
                st.markdown(report)
                st.markdown(generate_html_report(report, title), unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
