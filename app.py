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
    page_title="Signal Studio｜产品研判平台",
    page_icon="◌",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================
# 2. UI CSS: vivo-tech × Hermès restraint
# =========================
def inject_ui_css():
    st.markdown(
        """
        <style>
        :root {
            --bg: #f5f7fb;
            --bg-soft: #eef2f8;
            --ink: #101827;
            --ink-soft: #5d687a;
            --muted: #7a8495;
            --panel: rgba(255,255,255,0.76);
            --panel-strong: rgba(255,255,255,0.90);
            --line: rgba(88, 116, 255, 0.13);
            --line-strong: rgba(88, 116, 255, 0.30);
            --blue: #5e78ff;
            --blue-deep: #18295d;
            --blue-soft: #dde6ff;
            --warm: #b78458;
            --warm-soft: #f2e9df;
            --green: #39a78e;
            --shadow: 0 24px 70px rgba(17, 28, 55, 0.10);
            --radius: 24px;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 8%, rgba(94,120,255,0.11), transparent 24%),
                radial-gradient(circle at 92% 6%, rgba(183,132,88,0.10), transparent 22%),
                linear-gradient(180deg, #f7f9fc 0%, #eef3f9 100%);
            color: var(--ink);
        }

        .block-container {
            max-width: 1360px;
            padding-top: 1.45rem;
            padding-bottom: 4rem;
        }

        header[data-testid="stHeader"] {
            background: rgba(247,249,252,0.76);
            backdrop-filter: blur(14px);
            border-bottom: 1px solid rgba(88,116,255,0.08);
        }

        button[kind="header"] {
            border-radius: 999px !important;
            border: 1px solid rgba(88,116,255,0.16) !important;
            background: rgba(255,255,255,0.80) !important;
            box-shadow: 0 8px 24px rgba(17, 28, 55, 0.08) !important;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(13,20,35,0.98) 0%, rgba(18,31,62,0.98) 100%);
            border-right: 1px solid rgba(94,120,255,0.18);
        }
        section[data-testid="stSidebar"]::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at top left, rgba(94,120,255,0.18), transparent 24%),
                radial-gradient(circle at bottom right, rgba(183,132,88,0.12), transparent 22%);
            pointer-events: none;
        }
        section[data-testid="stSidebar"] * { color: #eef3ff !important; }
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] .stCaption { color: rgba(238,243,255,0.72) !important; }
        section[data-testid="stSidebar"] hr { border-color: rgba(94,120,255,0.16) !important; }
        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] textarea,
        section[data-testid="stSidebar"] [data-baseweb="select"] > div,
        section[data-testid="stSidebar"] [data-baseweb="tag"] {
            background: rgba(255,255,255,0.07) !important;
            border: 1px solid rgba(94,120,255,0.20) !important;
            border-radius: 14px !important;
            color: #eef3ff !important;
            box-shadow: none !important;
        }

        h1, h2, h3, h4 { letter-spacing: -0.03em; }

        .hero-shell {
            position: relative;
            overflow: hidden;
            padding: 42px 44px 40px;
            border-radius: 30px;
            border: 1px solid rgba(94,120,255,0.14);
            background: linear-gradient(135deg, rgba(12,19,34,0.97) 0%, rgba(24,36,73,0.96) 58%, rgba(26,42,84,0.92) 100%);
            box-shadow: 0 36px 90px rgba(13,20,35,0.22);
            margin-bottom: 18px;
        }
        .hero-shell::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 84% 18%, rgba(94,120,255,0.24), transparent 20%),
                radial-gradient(circle at 72% 80%, rgba(183,132,88,0.14), transparent 18%);
            pointer-events: none;
        }
        .hero-shell::after {
            content: "";
            position: absolute;
            right: -60px;
            top: -40px;
            width: 360px;
            height: 360px;
            border-radius: 50%;
            border: 1px solid rgba(255,255,255,0.07);
            box-shadow: inset 0 0 0 22px rgba(255,255,255,0.02), inset 0 0 0 64px rgba(255,255,255,0.015);
            opacity: 0.9;
        }
        .hero-content { position: relative; z-index: 2; }
        .hero-topline {
            font-size: 12px;
            letter-spacing: 0.28em;
            text-transform: uppercase;
            color: rgba(239,244,255,0.70);
            margin-bottom: 16px;
        }
        .hero-title {
            margin: 0;
            font-size: clamp(38px, 5.7vw, 78px);
            line-height: 0.94;
            color: #ffffff;
            font-weight: 660;
        }
        .hero-title span { color: #d5defe; font-weight: 430; }
        .hero-desc {
            margin-top: 18px;
            max-width: 790px;
            color: rgba(238,243,255,0.76);
            font-size: 15px;
            line-height: 1.85;
        }
        .hero-meta { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 22px; }
        .hero-chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 9px 13px;
            border-radius: 999px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.10);
            color: rgba(238,243,255,0.82);
            font-size: 12px;
        }
        .hero-note { margin-top: 16px; color: rgba(238,243,255,0.55); font-size: 12px; }

        .search-console {
            background: rgba(255,255,255,0.78);
            border: 1px solid rgba(94,120,255,0.12);
            border-radius: 28px;
            padding: 22px 22px 20px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(14px);
            margin: 0 0 18px 0;
        }
        .console-head {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 14px;
        }
        .console-kicker {
            font-size: 12px;
            letter-spacing: 0.24em;
            color: var(--blue);
            text-transform: uppercase;
            font-weight: 750;
            margin-bottom: 6px;
        }
        .console-title {
            font-size: 26px;
            font-weight: 720;
            color: var(--ink);
        }
        .console-desc { color: var(--ink-soft); line-height: 1.75; font-size: 13px; max-width: 620px; }
        .query-chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0 12px; }
        .query-chip {
            border-radius: 999px;
            padding: 7px 11px;
            background: #eef3ff;
            border: 1px solid rgba(94,120,255,0.12);
            color: #23366f;
            font-size: 12px;
            font-weight: 650;
        }

        .step-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin: 0 0 18px 0; }
        .step-card {
            border-radius: 20px;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(94,120,255,0.10);
            box-shadow: var(--shadow);
            padding: 18px 18px 17px;
            backdrop-filter: blur(14px);
        }
        .step-num { font-size: 12px; letter-spacing: 0.22em; color: var(--blue); text-transform: uppercase; margin-bottom: 8px; font-weight: 750; }
        .step-title { font-size: 18px; color: var(--ink); font-weight: 680; margin-bottom: 5px; }
        .step-desc { font-size: 13px; color: var(--ink-soft); line-height: 1.7; }

        .panel {
            background: rgba(255,255,255,0.76);
            border: 1px solid rgba(94,120,255,0.10);
            border-radius: 24px;
            padding: 24px 24px 20px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(14px);
            margin: 16px 0 20px;
        }
        .panel-kicker { font-size: 12px; letter-spacing: 0.24em; text-transform: uppercase; color: var(--blue); margin-bottom: 7px; font-weight: 750; }
        .panel-title { font-size: 30px; color: var(--ink); font-weight: 720; margin-bottom: 8px; }
        .panel-desc { color: var(--ink-soft); line-height: 1.8; font-size: 14px; }

        .section-caption {
            font-size: 12px;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            color: var(--blue);
            margin: 8px 0 10px;
            font-weight: 750;
        }

        .source-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 12px;
            margin-top: 12px;
            margin-bottom: 8px;
        }
        .source-grid.compact { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .source-card {
            display: block;
            position: relative;
            min-height: 108px;
            text-decoration: none !important;
            padding: 16px 16px 15px;
            border-radius: 18px;
            border: 1px solid rgba(94,120,255,0.12);
            background: linear-gradient(180deg, rgba(255,255,255,0.90) 0%, rgba(245,248,252,0.80) 100%);
            box-shadow: 0 18px 42px rgba(17, 28, 55, 0.07);
            transition: all .18s ease;
            overflow: hidden;
        }
        .source-card::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, var(--blue) 0%, var(--warm) 100%);
            opacity: 0.82;
        }
        .source-card:hover { transform: translateY(-3px); border-color: rgba(94,120,255,0.30); box-shadow: 0 24px 50px rgba(17, 28, 55, 0.11); }
        .source-index { color: var(--warm); font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 11px; font-weight: 750; }
        .source-name { color: var(--ink); font-size: 14px; line-height: 1.45; font-weight: 680; }
        .source-note { margin-top: 8px; color: var(--ink-soft); font-size: 11px; letter-spacing: 0.08em; }

        .stTextInput label, .stTextArea label, .stSelectbox label, .stMultiSelect label, .stRadio label {
            color: var(--ink) !important;
            font-weight: 650;
        }
        .stTextInput input,
        .stTextArea textarea,
        [data-baseweb="select"] > div,
        [data-baseweb="base-input"] {
            background: rgba(255,255,255,0.82) !important;
            border: 1px solid rgba(94,120,255,0.12) !important;
            border-radius: 16px !important;
            color: var(--ink) !important;
            box-shadow: none !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: rgba(94,120,255,0.38) !important;
            box-shadow: 0 0 0 4px rgba(94,120,255,0.08) !important;
        }

        .stButton > button, .stDownloadButton > button {
            min-height: 48px;
            border-radius: 999px !important;
            border: 1px solid rgba(94,120,255,0.18) !important;
            background: linear-gradient(135deg, rgba(20,31,59,0.98) 0%, rgba(40,59,118,0.98) 100%) !important;
            color: #ffffff !important;
            font-size: 13px;
            font-weight: 760;
            letter-spacing: 0.07em;
            box-shadow: 0 18px 38px rgba(26, 41, 82, 0.16);
            transition: all .18s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(-1px); box-shadow: 0 24px 44px rgba(26,41,82,0.22); border-color: rgba(94,120,255,0.28) !important; }

        div[data-testid="stAlert"] { background: rgba(255,255,255,0.72); border: 1px solid rgba(94,120,255,0.10); border-radius: 18px; }
        div[data-testid="stExpander"] { background: rgba(255,255,255,0.70) !important; border: 1px solid rgba(94,120,255,0.10) !important; border-radius: 18px !important; }
        div[data-testid="stTabs"] button { font-weight: 650; }

        .report-preview {
            background: rgba(255,255,255,0.76);
            border: 1px solid rgba(94,120,255,0.10);
            border-radius: 24px;
            padding: 24px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(14px);
        }
        .download-link {
            display: inline-block;
            text-decoration: none !important;
            padding: 12px 18px;
            margin-top: 12px;
            border-radius: 999px;
            border: 1px solid rgba(94,120,255,0.18);
            background: linear-gradient(135deg, rgba(20,31,59,0.98) 0%, rgba(40,59,118,0.98) 100%);
            color: #ffffff !important;
            font-size: 13px;
            font-weight: 760;
            letter-spacing: 0.06em;
        }

        .template-box {
            background: rgba(255,255,255,0.68);
            border: 1px solid rgba(94,120,255,0.10);
            border-radius: 18px;
            padding: 15px 16px;
            color: var(--ink-soft);
            line-height: 1.75;
            font-size: 13px;
        }
        .micro-tip { margin-top: 8px; color: rgba(238,243,255,0.60); font-size: 12px; line-height: 1.7; }

        @media (max-width: 1180px) {
            .source-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
            .source-grid.compact { grid-template-columns: 1fr; }
        }
        @media (max-width: 900px) {
            .source-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .step-grid { grid-template-columns: 1fr; }
            .hero-shell { padding: 32px 24px 30px; }
            .console-head { display: block; }
        }
        @media (max-width: 680px) {
            .source-grid { grid-template-columns: 1fr; }
            .hero-title { font-size: 42px; }
            .panel-title, .console-title { font-size: 24px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_ui_css()


# =========================
# 3. Search engines and helpers
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
    {"group": "UGC 社媒", "name": "小红书｜体验与痛点", "url": "https://www.xiaohongshu.com/search_result?keyword={q}"},
    {"group": "UGC 社媒", "name": "微博｜热议与争议", "url": "https://s.weibo.com/weibo?q={q}"},
    {"group": "UGC 社媒", "name": "知乎｜问答与口碑", "url": "https://www.zhihu.com/search?type=content&q={q}"},
    {"group": "UGC 社媒", "name": "微信文章｜长文观点", "url": "https://weixin.sogou.com/weixin?type=2&query={q}"},
    {"group": "视频测评", "name": "抖音｜短视频反馈", "url": "https://www.douyin.com/search/{q}"},
    {"group": "视频测评", "name": "B站｜深度测评", "url": "https://search.bilibili.com/all?keyword={q}"},
    {"group": "视频测评", "name": "快手｜下沉反馈", "url": "https://www.kuaishou.com/search/video?searchKey={q}"},
    {"group": "搜索引擎", "name": "百度｜中文全网", "url": "https://www.baidu.com/s?wd={q}"},
    {"group": "搜索引擎", "name": "Google｜海外/英文", "url": "https://www.google.com/search?q={q}"},
    {"group": "搜索引擎", "name": "必应｜补充检索", "url": "https://www.bing.com/search?q={q}"},
    {"group": "电商口碑", "name": "京东｜购买评价", "url": "https://search.jd.com/Search?keyword={q}"},
    {"group": "电商口碑", "name": "什么值得买｜消费决策", "url": "https://search.smzdm.com/?c=home&s={q}"},
]


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


def get_search_links(keyword: str):
    query = compose_query(keyword, "全网口碑")
    return {item["name"]: item["url"] for item in build_search_links(query, ["UGC 社媒", "视频测评", "搜索引擎"])}


def render_link_grid(links: list[dict] | dict, compact: bool = False):
    if isinstance(links, dict):
        iterable = [{"name": name, "url": url, "group": "Search"} for name, url in links.items()]
    else:
        iterable = links

    cards = []
    for idx, item in enumerate(iterable, start=1):
        cards.append(
            f"""
            <a class="source-card" href="{escape(item['url'])}" target="_blank" rel="noopener noreferrer">
                <div class="source-index">{escape(item.get('group', 'Search'))} · {idx:02d}</div>
                <div class="source-name">{escape(item['name'])}</div>
                <div class="source-note">OPEN SEARCH CHANNEL</div>
            </a>
            """
        )
    klass = "source-grid compact" if compact else "source-grid"
    st.markdown(f"<div class='{klass}'>{''.join(cards)}</div>", unsafe_allow_html=True)


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
【采集日期】2026-04-24
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
# 4. Header / quick search / panels
# =========================
def render_hero():
    st.markdown(
        """
        <section class="hero-shell">
            <div class="hero-content">
                <div class="hero-topline">SIGNAL STUDIO · PRODUCT INTELLIGENCE</div>
                <h1 class="hero-title">Strategy<br><span>Signal Deck</span></h1>
                <div class="hero-desc">
                    一个面向产品、市场与 PMM 的轻量研判工作台。输入产品名，快速生成跨平台取证入口；
                    粘贴真实语料，输出单品洞察、竞品攻防与传播建议。视觉保持科技感，同时保留高端品牌官网的克制留白。
                </div>
                <div class="hero-meta">
                    <span class="hero-chip">Portable Search Dock</span>
                    <span class="hero-chip">Evidence-based</span>
                    <span class="hero-chip">No Hallucination</span>
                    <span class="hero-chip">Strategy-ready</span>
                </div>
                <div class="hero-note">左上角可展开 / 收起配置侧边栏；搜索控制台已放回主页面，日常取证更顺手。</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_quick_search_console():
    st.markdown(
        """
        <section class="search-console">
            <div class="console-head">
                <div>
                    <div class="console-kicker">Portable Evidence Search</div>
                    <div class="console-title">便携取证搜索台</div>
                    <div class="console-desc">先在这里输入产品和搜索意图，下面会生成社媒、视频、搜索引擎、电商口碑入口。这个区域常驻主页面，不依赖左侧栏。</div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if "quick_product" not in st.session_state:
        st.session_state.quick_product = ""
    if "single_product_name" not in st.session_state:
        st.session_state.single_product_name = ""
    if "main_product" not in st.session_state:
        st.session_state.main_product = ""
    if "competitor_product" not in st.session_state:
        st.session_state.competitor_product = ""

    c1, c2, c3, c4 = st.columns([1.4, 1.0, 1.0, 1.0])
    with c1:
        quick_product = st.text_input("产品关键词", key="quick_product", placeholder="例如：vivo X Fold5 / OPPO Find N6 / iPhone 17")
    with c2:
        quick_intent = st.selectbox("搜索意图", list(INTENT_SUFFIX.keys()), index=0)
    with c3:
        quick_aliases = st.text_input("补充词 / 别名", placeholder="例如：折叠屏 蓝厂 体验")
    with c4:
        quick_competitor = st.text_input("竞品词，可空", placeholder="例如：Find N6 / Mate X")

    query = compose_query(quick_product, quick_intent, quick_aliases, quick_competitor)

    if quick_product.strip():
        st.markdown(
            f"""
            <div class="query-chip-row">
                <span class="query-chip">当前搜索式：{escape(query)}</span>
                <span class="query-chip">意图：{escape(quick_intent)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        sync1, sync2, sync3 = st.columns(3)
        with sync1:
            if st.button("同步到单品分析", use_container_width=True):
                st.session_state.single_product_name = quick_product.strip()
                st.rerun()
        with sync2:
            if st.button("同步为本品", use_container_width=True):
                st.session_state.main_product = quick_product.strip()
                st.rerun()
        with sync3:
            if st.button("同步为竞品", use_container_width=True):
                st.session_state.competitor_product = quick_product.strip()
                st.rerun()

        tab_ugc, tab_video, tab_engine, tab_ecom, tab_all = st.tabs(["UGC 社媒", "视频测评", "搜索引擎", "电商口碑", "全部入口"])
        with tab_ugc:
            render_link_grid(build_search_links(query, ["UGC 社媒"]))
        with tab_video:
            render_link_grid(build_search_links(query, ["视频测评"]))
        with tab_engine:
            render_link_grid(build_search_links(query, ["搜索引擎"]))
        with tab_ecom:
            render_link_grid(build_search_links(query, ["电商口碑"]))
        with tab_all:
            render_link_grid(build_search_links(query))

        with st.expander("复制搜索式 / URL 清单"):
            st.code(query, language="text")
            url_lines = [f"{item['name']}：{item['url']}" for item in build_search_links(query)]
            st.code("\n".join(url_lines), language="text")
    else:
        st.info("先输入产品关键词。比如：vivo X Fold5、OPPO Find N6、iPhone 17、小米汽车 SU7。")


def render_steps():
    st.markdown(
        """
        <div class="step-grid">
            <div class="step-card"><div class="step-num">Step 01</div><div class="step-title">Search Evidence</div><div class="step-desc">用便携搜索台生成多平台入口，保留不同平台的原始用户表达。</div></div>
            <div class="step-card"><div class="step-num">Step 02</div><div class="step-title">Paste Corpus</div><div class="step-desc">按平台分段粘贴评论、测评摘录、客服反馈或电商评价。</div></div>
            <div class="step-card"><div class="step-num">Step 03</div><div class="step-title">Generate Brief</div><div class="step-desc">生成结构化策略简报，强调证据、问题分层、攻防建议和信息缺口。</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_panel(kicker: str, title: str, desc: str):
    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-kicker">{escape(kicker)}</div>
            <div class="panel-title">{escape(title)}</div>
            <div class="panel-desc">{escape(desc)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_evidence_helper(product_name: str):
    with st.expander("语料整理模板 / 证据质量提示", expanded=False):
        st.markdown(
            """
            <div class="template-box">
            建议至少收集 3 类语料：① 社媒真实吐槽；② 媒体/博主测评摘录；③ 电商评价或购买问答。
            分析前不要把评论过度润色，保留原话更容易生成有效洞察。
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.code(get_corpus_template(product_name), language="text")


# =========================
# 5. LLM engine
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


# =========================
# 6. Prompt templates
# =========================
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


# =========================
# 7. Report export
# =========================
def generate_html_report(text_content: str, title: str):
    html_template = """
    <html><head><meta charset="utf-8"><style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
        background: linear-gradient(180deg, #f6f8fc 0%, #eef3f9 100%);
        padding: 40px;
        color: #101827;
    }
    .report-card {
        max-width: 980px;
        margin: 0 auto;
        background: rgba(255,255,255,0.94);
        padding: 54px;
        border-radius: 24px;
        border: 1px solid rgba(94,120,255,0.12);
        box-shadow: 0 30px 80px rgba(17, 28, 55, 0.12);
    }
    .eyebrow {
        text-align: center;
        color: #5e78ff;
        font-size: 11px;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        margin-bottom: 16px;
        font-weight: 700;
    }
    h1 {
        text-align: center;
        font-weight: 680;
        font-size: 34px;
        color: #101827;
        margin: 0 0 10px 0;
        letter-spacing: -0.03em;
    }
    .meta {
        text-align: center;
        color: #697385;
        font-size: 12px;
        margin-bottom: 34px;
        border-bottom: 1px solid rgba(94,120,255,0.12);
        padding-bottom: 22px;
    }
    h2 {
        font-weight: 680;
        font-size: 22px;
        color: #1e2f67;
        margin: 34px 0 16px 0;
        padding-top: 18px;
        border-top: 1px solid rgba(94,120,255,0.12);
    }
    .quote-box {
        background: #f5efe9;
        border-left: 3px solid #b78458;
        padding: 15px 18px;
        margin: 14px 0;
        color: #3a465c;
        font-size: 15px;
        line-height: 1.75;
        border-radius: 12px;
    }
    p { line-height: 1.82; margin: 9px 0; }
    table { width: 100%; border-collapse: collapse; margin: 22px 0; font-size: 13px; }
    th, td { padding: 13px; border: 1px solid rgba(94,120,255,0.12); text-align: left; vertical-align: top; }
    th { background: #eff4ff; font-weight: 700; color: #101827; }
    .footer {
        text-align: center;
        margin-top: 46px;
        padding-top: 20px;
        border-top: 1px solid rgba(94,120,255,0.12);
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
    return f'<a class="download-link" href="data:text/html;base64,{b64}" download="{filename}.html">EXPORT REPORT · HTML/PDF</a>'


# =========================
# 8. Sidebar controls
# =========================
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 18px 0 14px; border-bottom: 1px solid rgba(94,120,255,0.16); margin-bottom: 18px;">
            <div style="font-size: 28px; color: #ffffff; font-weight: 760; letter-spacing: -0.03em;">Signal Studio</div>
            <div style="font-size: 11px; color: rgba(238,243,255,0.58); letter-spacing: 0.22em; margin-top: 6px;">PRODUCT INTELLIGENCE</div>
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
    product_type = st.selectbox("产品类型", ["手机/消费电子", "汽车/智能座舱", "家电/IOT", "软件/App", "旅游/酒店产品", "其他"])
    focus = st.multiselect(
        "分析重点",
        ["用户痛点", "卖点感知", "价格价值感", "品牌认知", "系统/软件体验", "影像/性能", "外观设计", "渠道/服务", "传播话术"],
        default=["用户痛点", "卖点感知", "价格价值感", "传播话术"],
    )
    st.markdown("<div class='micro-tip'>侧边栏默认收起；主页面已保留便携搜索台，方便随时检索。</div>", unsafe_allow_html=True)


# =========================
# 9. Main UI
# =========================
render_hero()
render_quick_search_console()
render_steps()

if mode == "单品深度研判":
    render_panel(
        "SINGLE PRODUCT STUDY",
        "单品深度研判",
        "适合分析某一款产品当前的真实用户反馈、核心卖点感知、主要痛点、机会卖点与下一步传播建议。",
    )

    st.markdown("<div class='section-caption'>Product Input</div>", unsafe_allow_html=True)
    product_name = st.text_input("产品名称", key="single_product_name", placeholder="例如：vivo X Fold5、OPPO Find N6、iPhone 17、小米汽车 SU7")

    if product_name.strip():
        st.markdown("<div class='section-caption'>Quick Evidence Bundle</div>", unsafe_allow_html=True)
        st.caption("这里保留一组快捷入口；更完整的搜索意图切换请用上方便携搜索台。")
        default_query = compose_query(product_name, "全网口碑")
        render_link_grid(build_search_links(default_query, ["UGC 社媒", "视频测评", "搜索引擎"]), compact=False)
    else:
        st.info("先输入产品名称，或在上方搜索台输入后点击“同步到单品分析”。")

    render_evidence_helper(product_name)

    st.markdown("<div class='section-caption'>Raw Corpus</div>", unsafe_allow_html=True)
    user_input = st.text_area(
        "请粘贴真实评论、测评摘录、社媒反馈或客服反馈",
        height=310,
        placeholder="建议按平台分段粘贴，例如：\n【小红书】……\n【微博】……\n【B站】……\n【京东】……",
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
    render_panel(
        "COMPETITIVE DUEL",
        "竞品对比攻防",
        "适合把本品与竞品的 UGC 反馈放在同一张策略桌上，判断防守点、进攻点与可用传播话术。",
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("<div class='section-caption'>Main Product</div>", unsafe_allow_html=True)
        main_product = st.text_input("本品名称", key="main_product", placeholder="例如：vivo X Fold5")
        if main_product.strip():
            q = compose_query(main_product, "全网口碑")
            render_link_grid(build_search_links(q, ["UGC 社媒", "视频测评"]), compact=True)
        main_input = st.text_area("贴入本品真实语料", height=310, placeholder="粘贴本品评论/测评/用户反馈...")

    with col2:
        st.markdown("<div class='section-caption'>Competitor</div>", unsafe_allow_html=True)
        competitor_product = st.text_input("竞品名称", key="competitor_product", placeholder="例如：OPPO Find N6 / 华为 Mate X 系列")
        if competitor_product.strip():
            q = compose_query(competitor_product, "全网口碑")
            render_link_grid(build_search_links(q, ["UGC 社媒", "视频测评"]), compact=True)
        competitor_input = st.text_area("贴入竞品真实语料", height=310, placeholder="粘贴竞品评论/测评/用户反馈...")

    render_evidence_helper(main_product or competitor_product)

    if st.button("GENERATE COMPETITIVE BRIEF", type="primary", use_container_width=True):
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
