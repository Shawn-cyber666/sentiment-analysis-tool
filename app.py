
import streamlit as st
import requests
import datetime
import base64
import re
import urllib.parse
from html import escape


# =========================
# Page config
# =========================
st.set_page_config(
    page_title="Signal Studio｜产品研判平台",
    page_icon="◌",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================
# Light, clean UI
# =========================
def inject_css():
    st.markdown(
        """
        <style>
        :root {
            --bg: #f8fbff;
            --ink: #162033;
            --muted: #66748a;
            --blue: #5d78ff;
            --blue-deep: #23366f;
            --blue-soft: #edf2ff;
            --warm: #b88758;
            --line: rgba(93,120,255,0.14);
            --panel: rgba(255,255,255,0.86);
            --shadow: 0 22px 58px rgba(22, 32, 51, 0.08);
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 8%, rgba(93,120,255,0.10), transparent 24%),
                radial-gradient(circle at 94% 6%, rgba(184,135,88,0.08), transparent 24%),
                linear-gradient(180deg, #fbfdff 0%, #f3f7fd 100%);
            color: var(--ink);
        }

        .block-container {
            max-width: 1260px;
            padding-top: 1.4rem;
            padding-bottom: 4rem;
        }

        header[data-testid="stHeader"] {
            background: rgba(251,253,255,0.88);
            backdrop-filter: blur(14px);
            border-bottom: 1px solid rgba(93,120,255,0.06);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(248,251,255,0.98) 0%, rgba(238,244,255,0.98) 100%);
            border-right: 1px solid rgba(93,120,255,0.12);
        }
        section[data-testid="stSidebar"] * { color: var(--ink) !important; }
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] .stCaption {
            color: var(--muted) !important;
        }
        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] textarea,
        section[data-testid="stSidebar"] [data-baseweb="select"] > div,
        section[data-testid="stSidebar"] [data-baseweb="base-input"] {
            background: rgba(255,255,255,0.96) !important;
            border: 1px solid rgba(93,120,255,0.16) !important;
            border-radius: 16px !important;
            color: var(--ink) !important;
            box-shadow: none !important;
        }
        input::placeholder, textarea::placeholder {
            color: #95a1b5 !important;
            opacity: 1 !important;
        }

        h1, h2, h3, h4 { letter-spacing: -0.03em; }

        .top-hero {
            padding: 28px 30px;
            border-radius: 28px;
            background: linear-gradient(135deg, rgba(255,255,255,0.94) 0%, rgba(240,246,255,0.96) 100%);
            border: 1px solid rgba(93,120,255,0.12);
            box-shadow: var(--shadow);
            margin-bottom: 18px;
        }
        .eyebrow {
            font-size: 12px;
            letter-spacing: 0.28em;
            color: var(--blue);
            font-weight: 800;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .hero-title {
            font-size: clamp(34px, 4.8vw, 58px);
            line-height: 1;
            color: var(--blue-deep);
            font-weight: 760;
            margin-bottom: 10px;
        }
        .hero-title span { color: var(--blue); font-weight: 520; }
        .hero-desc {
            max-width: 760px;
            color: var(--muted);
            font-size: 14px;
            line-height: 1.78;
            margin: 0;
        }
        .mini-steps {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 16px;
        }
        .mini-chip {
            padding: 8px 12px;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(93,120,255,0.10);
            border-radius: 999px;
            color: var(--blue-deep);
            font-size: 12px;
            font-weight: 650;
        }

        .soft-card {
            padding: 20px;
            border-radius: 24px;
            background: var(--panel);
            border: 1px solid rgba(93,120,255,0.10);
            box-shadow: var(--shadow);
            margin-bottom: 18px;
        }
        .card-title {
            color: var(--ink);
            font-size: 22px;
            font-weight: 760;
            margin-bottom: 4px;
        }
        .card-desc {
            color: var(--muted);
            font-size: 13px;
            line-height: 1.72;
            margin-bottom: 6px;
        }
        .section-kicker {
            font-size: 12px;
            letter-spacing: 0.18em;
            color: var(--blue);
            font-weight: 800;
            text-transform: uppercase;
            margin: 10px 0 8px;
        }
        .query-preview {
            padding: 10px 12px;
            background: var(--blue-soft);
            border: 1px solid rgba(93,120,255,0.12);
            border-radius: 16px;
            color: var(--blue-deep);
            font-size: 13px;
            margin: 8px 0 12px;
        }

        .stTextInput label, .stTextArea label, .stSelectbox label, .stMultiSelect label, .stRadio label {
            color: var(--ink) !important;
            font-weight: 650;
        }
        .stTextInput input,
        .stTextArea textarea,
        [data-baseweb="select"] > div,
        [data-baseweb="base-input"] {
            background: rgba(255,255,255,0.90) !important;
            border: 1px solid rgba(93,120,255,0.12) !important;
            border-radius: 16px !important;
            color: var(--ink) !important;
            box-shadow: none !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: rgba(93,120,255,0.32) !important;
            box-shadow: 0 0 0 4px rgba(93,120,255,0.08) !important;
        }

        .stButton > button, .stDownloadButton > button {
            min-height: 46px;
            border-radius: 999px !important;
            border: 1px solid rgba(93,120,255,0.16) !important;
            background: linear-gradient(135deg, #4968ee 0%, #7087ff 100%) !important;
            color: #ffffff !important;
            font-size: 13px;
            font-weight: 760;
            letter-spacing: 0.04em;
            box-shadow: 0 14px 30px rgba(73,104,238,0.16);
            transition: all .18s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 20px 36px rgba(73,104,238,0.22);
        }

        div[data-testid="stLinkButton"] a {
            border-radius: 18px !important;
            border: 1px solid rgba(93,120,255,0.12) !important;
            background: rgba(255,255,255,0.92) !important;
            color: var(--blue-deep) !important;
            min-height: 48px !important;
            box-shadow: 0 12px 24px rgba(22,32,51,0.05) !important;
            font-weight: 700 !important;
        }
        div[data-testid="stLinkButton"] a:hover {
            border-color: rgba(93,120,255,0.28) !important;
            transform: translateY(-1px);
        }

        div[data-testid="stAlert"] {
            background: rgba(255,255,255,0.78);
            border: 1px solid rgba(93,120,255,0.10);
            border-radius: 18px;
        }
        div[data-testid="stExpander"] {
            background: rgba(255,255,255,0.74) !important;
            border: 1px solid rgba(93,120,255,0.10) !important;
            border-radius: 18px !important;
        }
        .report-preview {
            background: rgba(255,255,255,0.86);
            border: 1px solid rgba(93,120,255,0.10);
            border-radius: 24px;
            padding: 22px;
            box-shadow: var(--shadow);
        }
        .download-link {
            display: inline-block;
            text-decoration: none !important;
            padding: 12px 18px;
            margin-top: 12px;
            border-radius: 999px;
            background: linear-gradient(135deg, #4968ee 0%, #7087ff 100%);
            color: white !important;
            font-size: 13px;
            font-weight: 760;
        }
        .hint-box {
            background: rgba(255,255,255,0.78);
            border: 1px solid rgba(93,120,255,0.10);
            border-radius: 18px;
            padding: 14px 16px;
            color: var(--muted);
            line-height: 1.75;
            font-size: 13px;
        }
        .micro-tip { color: var(--muted); font-size: 12px; line-height: 1.7; }

        @media (max-width: 800px) {
            .top-hero { padding: 22px; }
            .hero-title { font-size: 38px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# =========================
# Search definitions
# =========================
INTENT_SUFFIX = {
    "全网口碑": "口碑 体验 测评",
    "吐槽痛点": "吐槽 缺点 问题 避雷",
    "测评体验": "测评 体验 上手 深度评测",
    "争议翻车": "争议 翻车 差评 售后",
    "购买建议": "值得买吗 购买建议 真实体验",
    "价格价值感": "价格 值不值得 性价比 贵不贵",
    "竞品对比": "对比 vs 区别 怎么选",
}

SEARCH_ENGINES = [
    {"group": "UGC 社媒", "name": "小红书", "url": "https://www.xiaohongshu.com/search_result?keyword={q}"},
    {"group": "UGC 社媒", "name": "微博", "url": "https://s.weibo.com/weibo?q={q}"},
    {"group": "UGC 社媒", "name": "知乎", "url": "https://www.zhihu.com/search?type=content&q={q}"},
    {"group": "UGC 社媒", "name": "微信文章", "url": "https://weixin.sogou.com/weixin?type=2&query={q}"},
    {"group": "视频测评", "name": "抖音", "url": "https://www.douyin.com/search/{q}"},
    {"group": "视频测评", "name": "B站", "url": "https://search.bilibili.com/all?keyword={q}"},
    {"group": "视频测评", "name": "快手", "url": "https://www.kuaishou.com/search/video?searchKey={q}"},
    {"group": "搜索引擎", "name": "百度", "url": "https://www.baidu.com/s?wd={q}"},
    {"group": "搜索引擎", "name": "Google", "url": "https://www.google.com/search?q={q}"},
    {"group": "搜索引擎", "name": "必应", "url": "https://www.bing.com/search?q={q}"},
    {"group": "电商口碑", "name": "京东", "url": "https://search.jd.com/Search?keyword={q}"},
    {"group": "电商口碑", "name": "什么值得买", "url": "https://search.smzdm.com/?c=home&s={q}"},
]


API_PRESETS = {
    "阿里云 DashScope": {
        "base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": ["deepseek-v3", "qwen-max", "qwen-plus", "qwen-turbo"],
    },
    "OpenRouter": {
        "base": "https://openrouter.ai/api/v1",
        "models": ["deepseek/deepseek-chat-v3-0324:free", "openai/gpt-4.1-mini", "google/gemini-2.5-flash-preview"],
    },
    "SiliconFlow": {
        "base": "https://api.siliconflow.cn/v1",
        "models": ["deepseek-ai/DeepSeek-V3", "Qwen/Qwen2.5-72B-Instruct", "THUDM/GLM-4-9B-Chat"],
    },
}


def compose_query(product: str, intent: str, aliases: str = "", competitor: str = "") -> str:
    parts = [product.strip()]
    if competitor.strip():
        parts.append(competitor.strip())
    if aliases.strip():
        parts.append(aliases.strip())
    parts.append(INTENT_SUFFIX.get(intent, "口碑 体验 测评"))
    return " ".join([p for p in parts if p]).strip()


def build_search_links(query: str, groups: list[str] | None = None):
    links = []
    for engine in SEARCH_ENGINES:
        if groups and engine["group"] not in groups:
            continue
        encoded = urllib.parse.quote(query)
        links.append({
            "group": engine["group"],
            "name": engine["name"],
            "url": engine["url"].format(q=encoded),
        })
    return links


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|\s]+", "_", name.strip())
    return name[:80] or "product_report"


def is_ready_to_analyze(api_key: str, *texts: str) -> bool:
    if not api_key.strip():
        st.warning("请先在侧边配置栏输入 API Key。")
        return False
    if any(not text.strip() for text in texts):
        st.warning("请先填写产品名，并粘贴真实语料。")
        return False
    return True


def get_corpus_template(product_name: str = "产品名") -> str:
    product_name = product_name.strip() or "产品名"
    return f"""【产品】{product_name}
【采集日期】{datetime.date.today()}
【平台】小红书 / 微博 / 抖音 / B站 / 京东 / 其他
【搜索词】{product_name} 体验 吐槽 测评

【原始语料】
1. 平台：
   用户原话/评论摘录：
   互动情况：点赞/评论/转发，如无可不填
   初步标签：价格 / 影像 / 外观 / 系统 / 售后 / 购买建议

2. 平台：
   用户原话/评论摘录：
   互动情况：
   初步标签：

【备注】
- 尽量保留用户原话，不要提前改写。
- 不确定的信息不要补充，让模型在报告中写“暂无提及”。"""


# =========================
# Rendering helpers
# =========================
def render_header():
    st.markdown(
        """
        <section class="top-hero">
            <div class="eyebrow">SIGNAL STUDIO · PRODUCT INTELLIGENCE</div>
            <div class="hero-title">Strategy <span>Signal Deck</span></div>
            <p class="hero-desc">
            轻量产品情报台：先用便携搜索坞快速取证，再粘贴真实语料生成单品研判或竞品攻防。
            页面已简化成“搜索—整理—分析”三步，不再堆叠复杂装饰。
            </p>
            <div class="mini-steps">
                <span class="mini-chip">01 搜索取证</span>
                <span class="mini-chip">02 粘贴语料</span>
                <span class="mini-chip">03 生成简报</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_link_buttons(links: list[dict], columns_per_row: int = 4):
    for start in range(0, len(links), columns_per_row):
        row = links[start:start + columns_per_row]
        cols = st.columns(columns_per_row)
        for idx, col in enumerate(cols):
            if idx < len(row):
                item = row[idx]
                col.link_button(
                    f"{item['name']} · {item['group']}",
                    item["url"],
                    use_container_width=True,
                )


def render_search_dock():
    if "quick_product" not in st.session_state:
        st.session_state.quick_product = ""
    if "single_product_name" not in st.session_state:
        st.session_state.single_product_name = ""
    if "main_product" not in st.session_state:
        st.session_state.main_product = ""
    if "competitor_product" not in st.session_state:
        st.session_state.competitor_product = ""

    with st.container(border=True):
        st.markdown("### 便携搜索坞")
        st.caption("输入产品名后，直接打开各平台搜索入口。这里全部改成原生按钮，不再用 HTML 卡片，避免页面把代码渲染出来。")

        c1, c2, c3, c4 = st.columns([1.35, 0.9, 1.0, 0.95])
        with c1:
            product = st.text_input("产品关键词", key="quick_product", placeholder="例如：vivo X Fold5 / OPPO Find N6")
        with c2:
            intent = st.selectbox("搜索意图", list(INTENT_SUFFIX.keys()), index=0)
        with c3:
            aliases = st.text_input("补充词 / 别名", placeholder="例如：折叠屏 蓝厂")
        with c4:
            competitor = st.text_input("竞品词，可空", placeholder="例如：Find N6")

        query = compose_query(product, intent, aliases, competitor)

        if product.strip():
            st.markdown(f"<div class='query-preview'>当前搜索式：{escape(query)}</div>", unsafe_allow_html=True)

            sync_cols = st.columns(3)
            if sync_cols[0].button("同步到单品分析", use_container_width=True):
                st.session_state.single_product_name = product.strip()
                st.rerun()
            if sync_cols[1].button("同步为本品", use_container_width=True):
                st.session_state.main_product = product.strip()
                st.rerun()
            if sync_cols[2].button("同步为竞品", use_container_width=True):
                st.session_state.competitor_product = product.strip()
                st.rerun()

            group_tabs = st.tabs(["常用入口", "UGC 社媒", "视频测评", "搜索引擎", "电商口碑"])
            with group_tabs[0]:
                common = build_search_links(query, ["UGC 社媒", "视频测评", "搜索引擎"])[:8]
                render_link_buttons(common, columns_per_row=4)
            with group_tabs[1]:
                render_link_buttons(build_search_links(query, ["UGC 社媒"]), columns_per_row=4)
            with group_tabs[2]:
                render_link_buttons(build_search_links(query, ["视频测评"]), columns_per_row=3)
            with group_tabs[3]:
                render_link_buttons(build_search_links(query, ["搜索引擎"]), columns_per_row=3)
            with group_tabs[4]:
                render_link_buttons(build_search_links(query, ["电商口碑"]), columns_per_row=2)

            with st.expander("复制搜索式 / URL 清单"):
                st.code(query, language="text")
                url_lines = [f"{item['name']}：{item['url']}" for item in build_search_links(query)]
                st.code("\n".join(url_lines), language="text")
        else:
            st.info("先输入产品关键词，系统会生成小红书、微博、抖音、B站、搜索引擎、电商评价入口。")


def render_evidence_helper(product_name: str):
    with st.expander("语料整理模板 / 证据质量提示", expanded=False):
        st.markdown(
            """
            <div class="hint-box">
            建议至少收集 3 类语料：社媒真实吐槽、媒体/博主测评摘录、电商评价或购买问答。
            分析前不要把评论过度润色，保留原话更容易生成有效洞察。
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.code(get_corpus_template(product_name), language="text")


# =========================
# LLM engine and prompt templates
# =========================
def analyze_with_llm(prompt: str, api_key: str, model_name: str, api_base: str):
    url = api_base.rstrip("/") + "/chat/completions"
    headers = {"Authorization": "Bearer " + api_key.strip(), "Content-Type": "application/json"}
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
                    "每个核心判断都要尽量对应语料证据。"
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


def build_single_prompt(product_name: str, product_type: str, focus: list[str], corpus: str) -> str:
    focus_text = "、".join(focus) if focus else "用户体验、核心卖点、负面反馈、购买阻力、传播机会"
    return f"""
请仅根据下方语料，撰写《{product_name} 单品深度研判报告》。

产品名称：{product_name}
产品类型：{product_type}
重点关注：{focus_text}

输出要求：
- 严禁编造参数、销量、发布时间、官方动作或用户评价。
- 所有判断必须能从语料中找到依据。
- 如果信息不足，明确写“暂无提及”。
- 报告要像产品/市场/PMM 内部简报，结论清晰、动作可执行。

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

六、下一轮取证建议
- 说明还应该去哪些平台/关键词补充搜索。

七、信息缺口
- 列出当前语料不足以判断的内容。

真实语料如下：
{corpus}
""".strip()


def build_compare_prompt(main_product: str, competitor_product: str, product_type: str, focus: list[str], main_corpus: str, competitor_corpus: str) -> str:
    focus_text = "、".join(focus) if focus else "用户体验、核心卖点、负面反馈、购买阻力、传播机会"
    return f"""
请仅根据下方两组语料，撰写《{main_product} vs {competitor_product} 竞品攻防研判报告》。

本品：{main_product}
竞品：{competitor_product}
产品类型：{product_type}
重点关注：{focus_text}

输出要求：
- 严禁编造参数、销量、发布时间、官方动作或用户评价。
- 对比结论必须同时考虑本品语料与竞品语料。
- 如果某一方证据不足，明确写“暂无提及”。
- 不要为了形成对比而强行制造差异。

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

七、下一轮取证建议
- 说明双方还应补充哪些平台/关键词。

八、信息缺口
- 列出当前语料不足以判断的内容。

【本品真实语料】
{main_corpus}

【竞品真实语料】
{competitor_corpus}
""".strip()


def generate_html_report(text_content: str, title: str):
    html_template = """
    <html><head><meta charset="utf-8"><style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
        background: linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
        padding: 40px;
        color: #162033;
    }
    .report-card {
        max-width: 980px;
        margin: 0 auto;
        background: rgba(255,255,255,0.96);
        padding: 54px;
        border-radius: 24px;
        border: 1px solid rgba(93,120,255,0.12);
        box-shadow: 0 30px 80px rgba(17, 28, 55, 0.12);
    }
    .eyebrow {
        text-align: center;
        color: #5d78ff;
        font-size: 11px;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        margin-bottom: 16px;
        font-weight: 700;
    }
    h1 {
        text-align: center;
        font-weight: 700;
        font-size: 34px;
        color: #162033;
        margin: 0 0 10px 0;
        letter-spacing: -0.03em;
    }
    .meta {
        text-align: center;
        color: #697385;
        font-size: 12px;
        margin-bottom: 34px;
        border-bottom: 1px solid rgba(93,120,255,0.12);
        padding-bottom: 22px;
    }
    h2 {
        font-weight: 700;
        font-size: 22px;
        color: #23366f;
        margin: 34px 0 16px 0;
        padding-top: 18px;
        border-top: 1px solid rgba(93,120,255,0.12);
    }
    .quote-box {
        background: #f5efe9;
        border-left: 3px solid #b88758;
        padding: 15px 18px;
        margin: 14px 0;
        color: #3a465c;
        font-size: 15px;
        line-height: 1.75;
        border-radius: 12px;
    }
    p { line-height: 1.82; margin: 9px 0; }
    table { width: 100%; border-collapse: collapse; margin: 22px 0; font-size: 13px; }
    th, td { padding: 13px; border: 1px solid rgba(93,120,255,0.12); text-align: left; vertical-align: top; }
    th { background: #eff4ff; font-weight: 700; color: #162033; }
    .footer {
        text-align: center;
        margin-top: 46px;
        padding-top: 20px;
        border-top: 1px solid rgba(93,120,255,0.12);
        font-size: 11px;
        color: #697385;
        letter-spacing: 0.08em;
    }
    </style></head><body>
    <div class="report-card">
        <div class="eyebrow">SIGNAL STUDIO · PRODUCT STRATEGY BRIEF</div>
        <h1>{{TITLE}}</h1>
        <div class="meta">生成日期：{{DATE}} · 基于用户提供语料自动生成，仅供内部分析参考</div>
        {{BODY}}
        <div class="footer">EVIDENCE-BASED · STRUCTURED · STRATEGY-READY</div>
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

        if any(line.startswith(prefix) for prefix in ["一、", "二、", "三、", "四、", "五、", "六、", "七、", "八、"]):
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
    return f'<a class="download-link" href="data:text/html;base64,{b64}" download="{filename}.html">导出报告 · HTML/PDF</a>'


# =========================
# Sidebar controls
# =========================
with st.sidebar:
    st.markdown("## Signal Studio")
    st.caption("PRODUCT INTELLIGENCE")

    api_key = st.text_input("API Key", type="password", placeholder="请输入你的 API Key")
    provider_name = st.selectbox("服务商预设", list(API_PRESETS.keys()), index=0)
    provider_info = API_PRESETS[provider_name]
    api_base = st.selectbox("接口地址", [provider_info["base"]], index=0)
    model_name = st.selectbox("模型代号", provider_info["models"], index=0)

    st.divider()
    mode = st.radio("任务模式", ["单品深度研判", "竞品对比攻防"])
    product_type = st.selectbox("产品类型", ["手机/消费电子", "汽车/智能座舱", "家电/IOT", "软件/App", "旅游/酒店产品", "其他"])
    focus = st.multiselect(
        "分析重点",
        ["用户痛点", "卖点感知", "价格价值感", "品牌认知", "系统/软件体验", "影像/性能", "外观设计", "渠道/服务", "传播话术"],
        default=["用户痛点", "卖点感知", "价格价值感", "传播话术"],
    )
    st.markdown("<div class='micro-tip'>配置栏默认收起。接口地址和模型代号均为预设选择，用户不用手动输入。</div>", unsafe_allow_html=True)


# =========================
# Main UI
# =========================
render_header()
render_search_dock()

if mode == "单品深度研判":
    with st.container(border=True):
        st.markdown("### 单品深度研判")
        st.caption("分析某一款产品的真实用户反馈、核心卖点感知、主要痛点与下一步传播建议。")

        product_name = st.text_input("产品名称", key="single_product_name", placeholder="例如：vivo X Fold5、OPPO Find N6、iPhone 17")
        if product_name.strip():
            default_query = compose_query(product_name, "全网口碑")
            with st.expander("快捷取证入口", expanded=False):
                render_link_buttons(build_search_links(default_query, ["UGC 社媒", "视频测评", "搜索引擎"])[:8], columns_per_row=4)
        else:
            st.info("先输入产品名称，或在上方搜索坞输入后点击“同步到单品分析”。")

        render_evidence_helper(product_name)

        user_input = st.text_area(
            "真实语料",
            height=300,
            placeholder="建议按平台分段粘贴，例如：\n【小红书】……\n【微博】……\n【B站】……\n【京东】……",
        )

        if st.button("生成单品研判报告", type="primary", use_container_width=True):
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
    with st.container(border=True):
        st.markdown("### 竞品对比攻防")
        st.caption("把本品与竞品的 UGC 反馈放在同一张策略桌上，判断防守点、进攻点与可用传播话术。")

        col1, col2 = st.columns(2, gap="large")
        with col1:
            main_product = st.text_input("本品名称", key="main_product", placeholder="例如：vivo X Fold5")
            if main_product.strip():
                with st.expander("本品快捷入口", expanded=False):
                    q = compose_query(main_product, "全网口碑")
                    render_link_buttons(build_search_links(q, ["UGC 社媒", "视频测评"])[:6], columns_per_row=3)
            main_input = st.text_area("本品真实语料", height=300, placeholder="粘贴本品评论/测评/用户反馈...")

        with col2:
            competitor_product = st.text_input("竞品名称", key="competitor_product", placeholder="例如：OPPO Find N6 / 华为 Mate X 系列")
            if competitor_product.strip():
                with st.expander("竞品快捷入口", expanded=False):
                    q = compose_query(competitor_product, "全网口碑")
                    render_link_buttons(build_search_links(q, ["UGC 社媒", "视频测评"])[:6], columns_per_row=3)
            competitor_input = st.text_area("竞品真实语料", height=300, placeholder="粘贴竞品评论/测评/用户反馈...")

        render_evidence_helper(main_product or competitor_product)

        if st.button("生成竞品攻防报告", type="primary", use_container_width=True):
            if is_ready_to_analyze(api_key, main_product, competitor_product, main_input, competitor_input):
                with st.spinner("正在构建竞品攻防研判报告..."):
                    prompt = build_compare_prompt(main_product.strip(), competitor_product.strip(), product_type, focus, main_input.strip(), competitor_input.strip())
                    report = analyze_with_llm(prompt, api_key, model_name, api_base)
                    title = f"{main_product.strip()}_vs_{competitor_product.strip()}_竞品攻防研判报告"
                    st.markdown("### 报告预览")
                    st.markdown("<div class='report-preview'>", unsafe_allow_html=True)
                    st.markdown(report)
                    st.markdown(generate_html_report(report, title), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
