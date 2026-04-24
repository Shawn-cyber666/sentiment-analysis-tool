import streamlit as st
import requests
import datetime
import base64
import re
import urllib.parse
from html import escape


# --- 1. UGC 情报取证入口：根据用户输入产品名动态生成搜索链路 ---
def get_search_links(keyword: str):
    keyword = keyword.strip()
    enc = urllib.parse.quote(keyword)
    return {
        "🔴 小红书｜痛点/种草/吐槽": f"https://www.xiaohongshu.com/search_result?keyword={enc}%20吐槽%20体验",
        "🟡 微博｜争议/翻车/热议": f"https://s.weibo.com/weibo?q={enc}%20翻车%20争议",
        "🎵 抖音｜短视频差评/体验": f"https://www.douyin.com/search/{enc}%20缺点%20体验",
        "📺 B站｜深度测评/长评": f"https://search.bilibili.com/all?keyword={enc}%20测评",
        "🌐 百度｜全网补充检索": f"https://www.baidu.com/s?wd={enc}%20测评%20口碑%20问题",
    }


# --- 2. 基础工具函数 ---
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


# --- 3. 核心分析引擎：从 vivo 专家改成通用产品策略分析师 ---
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


# --- 4. Prompt 模板：产品名全部由用户输入 ---
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


def build_compare_prompt(main_product: str, competitor_product: str, product_type: str, focus: list[str], main_corpus: str, competitor_corpus: str) -> str:
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


# --- 5. 专家级报告 HTML 导出 ---
def generate_html_report(text_content: str, title: str):
    html_template = """
    <html><head><meta charset="utf-8"><style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #F4F7FA; padding: 30px; color: #222; }
    .report-card { max-width: 920px; margin: 0 auto; background: #FFF; padding: 42px; border-radius: 14px; border-top: 6px solid #415FFF; box-shadow: 0 8px 28px rgba(20,31,70,0.10); }
    h1 { text-align: center; font-size: 25px; color: #111; margin-bottom: 6px; }
    .meta { text-align: center; color: #888; font-size: 12px; margin-bottom: 30px; border-bottom: 1px solid #EEE; padding-bottom: 16px; }
    h2 { font-size: 18px; color: #3154E7; margin: 30px 0 15px 0; border-left: 4px solid #415FFF; padding-left: 10px; }
    .quote-box { background: #FFF5F5; border-left: 4px solid #FF4D4F; padding: 14px 16px; margin: 14px 0; color: #9F1D1D; font-size: 15px; border-radius: 8px; }
    p { line-height: 1.75; margin: 8px 0; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 13px; }
    th, td { padding: 12px; border: 1px solid #E5E8EF; text-align: left; vertical-align: top; }
    th { background: #F6F8FF; font-weight: 700; color: #111; }
    .footer { text-align: center; margin-top: 40px; font-size: 11px; color: #AAA; }
    </style></head><body>
    <div class="report-card">
        <h1>{{TITLE}}</h1>
        <div class="meta">产品策略研判报告 · 生成日期：{{DATE}}</div>
        {{BODY}}
        <div class="footer">本报告由产品研判系统基于用户提供语料自动生成，仅供内部分析参考。</div>
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
    return f'<a href="data:text/html;base64,{b64}" download="{filename}.html" style="text-decoration:none; background:#415FFF; color:white; padding:12px 25px; border-radius:8px; font-weight:bold; display:inline-block;">📥 导出研判报告 HTML/PDF</a>'


# --- 6. Streamlit 页面 ---
st.set_page_config(page_title="终端产品研判平台", layout="wide")

st.title("💼 终端产品全维度研判平台")
st.caption("输入任意产品名 → 自动生成 UGC 取证入口 → 粘贴真实语料 → 生成单品/竞品研判报告")

with st.sidebar:
    st.header("🔑 系统配置")
    api_key = st.text_input("API Key", type="password")
    api_base = st.text_input(
        "接口地址",
        value="https://dashscope.aliyuncs.com/compatible-mode/v1",
        help="需兼容 OpenAI Chat Completions 格式。阿里云 DashScope 可保持默认。",
    )
    model_name = st.text_input("模型代号", value="deepseek-v3")

    st.divider()
    mode = st.radio("🛡️ 任务模式", ["单品深度研判", "竞品对比攻防"])
    product_type = st.selectbox("产品类型", ["手机/消费电子", "汽车/智能座舱", "家电/IOT", "软件/App", "旅游/酒店产品", "其他"])
    focus = st.multiselect(
        "分析重点",
        ["用户痛点", "卖点感知", "价格价值感", "品牌认知", "系统/软件体验", "影像/性能", "外观设计", "渠道/服务", "传播话术"],
        default=["用户痛点", "卖点感知", "价格价值感", "传播话术"],
    )


if mode == "单品深度研判":
    st.subheader("🔎 选择/搜索要分析的产品")
    product_name = st.text_input("产品名称", placeholder="例如：vivo X Fold5、OPPO Find N6、iPhone 17、小米汽车 SU7")

    if product_name.strip():
        st.markdown("#### 📡 UGC 快速取证入口")
        cols = st.columns(5)
        for col, (name, url) in zip(cols, get_search_links(product_name).items()):
            with col:
                st.link_button(name, url, use_container_width=True)
    else:
        st.info("先输入产品名称，系统会自动生成小红书、微博、抖音、B站、百度的搜索入口。")

    st.markdown("#### 📑 原始语料录入")
    user_input = st.text_area(
        "请粘贴真实评论、测评摘录、社媒反馈或客服反馈：",
        height=260,
        placeholder="建议按平台分段粘贴，例如：\n【小红书】……\n【微博】……\n【B站】……",
    )

    if st.button("生成单品深度报告", type="primary", use_container_width=True):
        if is_ready_to_analyze(api_key, product_name, user_input):
            with st.spinner("正在基于真实语料研判..."):
                prompt = build_single_prompt(product_name.strip(), product_type, focus, user_input.strip())
                report = analyze_with_llm(prompt, api_key, model_name, api_base)
                st.markdown(report)
                title = f"{product_name.strip()}_单品深度研判报告"
                st.markdown(generate_html_report(report, title), unsafe_allow_html=True)

else:
    st.subheader("⚔️ 竞品对比攻防阵列")
    col1, col2 = st.columns(2)

    with col1:
        main_product = st.text_input("本品名称", placeholder="例如：vivo X Fold5")
        if main_product.strip():
            st.markdown("##### 本品 UGC 取证")
            for name, url in get_search_links(main_product).items():
                st.link_button(name, url, use_container_width=True)
        main_input = st.text_area("贴入本品真实语料：", height=240, placeholder="粘贴本品评论/测评/用户反馈...")

    with col2:
        competitor_product = st.text_input("竞品名称", placeholder="例如：OPPO Find N6 / 华为 Mate X 系列")
        if competitor_product.strip():
            st.markdown("##### 竞品 UGC 取证")
            for name, url in get_search_links(competitor_product).items():
                st.link_button(name, url, use_container_width=True)
        competitor_input = st.text_area("贴入竞品真实语料：", height=240, placeholder="粘贴竞品评论/测评/用户反馈...")

    if st.button("启动竞品攻防研判", type="primary", use_container_width=True):
        if is_ready_to_analyze(api_key, main_product, competitor_product, main_input, competitor_input):
            with st.spinner("正在构建对比矩阵..."):
                prompt = build_compare_prompt(
                    main_product.strip(),
                    competitor_product.strip(),
                    product_type,
                    focus,
                    main_input.strip(),
                    competitor_input.strip(),
                )
                report = analyze_with_llm(prompt, api_key, model_name, api_base)
                st.markdown(report)
                title = f"{main_product.strip()}_vs_{competitor_product.strip()}_竞品攻防研判报告"
                st.markdown(generate_html_report(report, title), unsafe_allow_html=True)
