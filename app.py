import streamlit as st
import requests
import datetime
import base64
import re
import urllib.parse

# --- 1. 专家级 UGC 取证工具 (精准对标 X9U/Pura90) ---
def get_search_links(keyword):
    enc = urllib.parse.quote(keyword)
    return {
        "小红书 (核心痛点搜素)": f"https://www.xiaohongshu.com/search_result?keyword={enc}%20吐槽",
        "新浪微博 (舆情实时翻车)": f"https://s.weibo.com/weibo?q={enc}%20翻车",
        "抖音 (短视频负面反馈)": f"https://www.douyin.com/search/{enc}%20缺点"
    }

# --- 2. 深度分析引擎 (严防幻觉，锁死语料) ---
def analyze_with_llm(prompt, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    payload = {
        "model": model_name, 
        "messages": [
            {"role": "system", "content": "你是一名在 vivo 工作的资深市场营销与产品调研专家。你的报告必须完全基于用户提供的原始语料，严禁虚构任何不存在的细节，语言风格要专业、利落、一针见血。"},
            {"role": "user", "content": prompt}
        ], 
        "temperature": 0.01 # 降低随机性，彻底杜绝虚拟数据
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = res.json()['choices'][0]['message']['content']
        # 移除可能干扰 HTML 的非法 Markdown 符号
        return re.sub(r'[*#\-]', '', content)
    except Exception:
        return "ERROR: 引擎连接中断，请检查 API Key。"

# --- 3. 专家级内参渲染 (修复语法报错，优化视觉体验) ---
def generate_html_report(text_content, title, mode="single"):
    # 使用 Python 的 string.replace 避免 f-string 带来的括号转义报错
    html_template = """
    <html><head><meta charset="utf-8"><style>
    body { font-family: 'Helvetica Neue', 'PingFang SC', sans-serif; background: #F8F9FB; padding: 40px; color: #1D1D1F; }
    .report-card { max-width: 900px; margin: 0 auto; background: #FFF; padding: 60px; border-radius: 4px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-top: 8px solid #415FFF; }
    h1 { text-align: center; font-size: 28px; margin-bottom: 10px; color: #000; }
    .meta { text-align: center; color: #86868b; font-size: 14px; margin-bottom: 50px; border-bottom: 1px solid #F0F0F2; padding-bottom: 20px; }
    h2 { font-size: 20px; color: #415FFF; margin-top: 40px; margin-bottom: 20px; display: flex; align-items: center; }
    h2::before { content: ""; display: inline-block; width: 4px; height: 20px; background: #415FFF; margin-right: 12px; border-radius: 2px; }
    .quote-box { background: #FFF1F1; border-left: 4px solid #FF3B30; padding: 20px; margin: 20px 0; color: #D70010; font-style: italic; font-weight: 500; font-size: 16px; border-radius: 0 8px 8px 0; }
    table { width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 14px; }
    th, td { padding: 16px; text-align: left; border: 1px solid #E5E5E7; line-height: 1.5; }
    th { background: #F5F5F7; color: #1D1D1F; font-weight: 600; }
    .footer { text-align: center; margin-top: 60px; font-size: 12px; color: #86868b; border-top: 1px solid #F0F0F2; padding-top: 20px; }
    </style></head><body>
    <div class="report-card">
        <h1>{{TITLE}}</h1>
        <div class="meta">vivo 内部保密资料 · 报告生成时间：{{DATE}}</div>
        {{BODY}}
        <div class="footer">本报告由策略研究中心自动系统生成，仅供内部决策。</div>
    </div></body></html>
    """
    
    body_html = ""
    lines = text_content.split('\n')
    in_table = False
    is_quote = False

    for line in lines:
        line = line.strip()
        if not line: continue
        
        # 模块识别
        if any(kw in line for kw in ["原声", "吐槽", "原话"]):
            is_quote = True
            if in_table: body_html += "</tbody></table>"; in_table = False
            body_html += f"<h2>{line}</h2>"
        elif any(kw in line for kw in ["一、", "二、", "三、", "四、"]):
            is_quote = False
            if in_table: body_html += "</tbody></table>"; in_table = False
            body_html += f"<h2>{line}</h2>"
        elif "|" in line and not all(c in "| -:" for c in line):
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if len(cells) > 1:
                row = "<tr>" + "".join([f"<td>{c}</td>" for c in cells]) + "</tr>"
                if not in_table:
                    body_html += "<table><thead>" + row.replace("td>", "th>") + "</thead><tbody>"
                    in_table = True
                else:
                    body_html += row
        else:
            if in_table: body_html += "</tbody></table>"; in_table = False
            if is_quote:
                body_html += f"<div class='quote-box'>“{line}”</div>"
            else:
                body_html += f"<p>{line}</p>"
    
    if in_table: body_html += "</tbody></table>"
    
    final_report = html_template.replace("{{TITLE}}", title).replace("{{DATE}}", str(datetime.date.today())).replace("{{BODY}}", body_html)
    b64 = base64.b64encode(final_report.encode('utf-8')).decode()
    btn_style = "background:#415FFF" if mode == "single" else "background:#000"
    
    return f'<a href="data:text/html;base64,{b64}" download="{title}.html" style="text-decoration:none; {btn_style}; color:white; padding:14px 32px; border-radius:6px; font-weight:bold; display:inline-block;">📥 下载专业版 PDF 内参报告</a>'

# --- 4. Streamlit 交互架构 ---
st.set_page_config(page_title="vivo 策略调研中枢", layout="wide")
st.title("💼 终端品牌高端化舆情研判平台")

with st.sidebar:
    st.header("🔑 系统权限")
    api_key = st.text_input("API Key", type="password")
    model_name = st.text_input("LLM Model", value="deepseek-v3")
    st.divider()
    mode = st.radio("📑 研判任务选择", ["单品专项研判 (本品)", "战略对比攻防 (竞品)"])

# 模式一：单品深度研判
if mode == "单品专项研判 (本品)":
    with st.sidebar:
        st.divider()
        target = st.text_input("本品机型", value="vivo x300u")
        st.subheader("📡 UGC 取证入口")
        for name, url in get_search_links(target).items():
            st.link_button(name, url, use_container_width=True)

    st.subheader(f"📑 {target} 原始语料录入")
    user_input = st.text_area("请贴入人工抓取的真实用户评论：", height=250, placeholder="在此粘贴小红书、微博的原始文字...")
    
    if st.button("生成研判报告", type="primary"):
        with st.spinner("专家引擎正在研判..."):
            prompt = f"""
            你现在是 vivo 产品策略专家。请基于以下原始语料，撰写一份关于【{target}】的深度研判报告。
            要求：必须严谨对待语料，严禁使用虚假数据，严禁使用 # 或 *。
            报告结构必须如下：
            一、 核心舆情走势概览（总结当前用户的主要情绪）
            二、 尖锐原声直击（必须摘录语料中杀伤力最强、最真实、最能反映痛点的 2 句原话）
            三、 问题反馈矩阵（必须按此格式输出表格：维度 | 关键痛点详情 | 严重程度 | 改进紧迫性。维度需涵盖：影像表现、硬件品质、系统体验、品牌价值感）
            四、 专家补救建议（针对痛点给出具体的营销或产品优化对策）
            语料内容：{user_input}
            """
            report = analyze_with_llm(prompt, api_key, model_name)
            st.markdown(report)
            st.markdown(generate_html_report(report, f"{target}专项研判报告", "single"), unsafe_allow_html=True)

# 模式二：战略对比攻防
else:
    st.subheader("⚔️ 竞品攻防战略阵列")
    col1, col2 = st.columns(2)
    with col1:
        my_prod = st.text_input("本品定位", value="vivo x300u")
        st.caption("👇 本品情报取证")
        for n, u in get_search_links(my_prod).items(): st.link_button(n, u, use_container_width=True)
        my_in = st.text_area("贴入本品负面评价：", height=200)
    with col2:
        comp_prod = st.text_input("竞品对标", value="OPPO Find X9U / 华为 Pura 90")
        st.caption("👇 竞品情报取证")
        for n, u in get_search_links(comp_prod).items(): st.link_button(n, u, use_container_width=True)
        comp_in = st.text_area("贴入竞品负面评价：", height=200)

    if st.button("启动战略攻防分析", type="primary"):
        with st.spinner("正在构建攻防模型..."):
            prompt = f"""
            你现在是 vivo 竞争战略专家。请对标【{my_prod}】与【{comp_prod}】的舆情态势进行深度对比。
            要求：必须基于提供的真实语料，严禁虚构。
            报告结构：
            一、 双方舆情优劣势定性（分析 vivo 与竞品在用户口中的核心分歧点）
            二、 典型原声描述（分别列出本品和竞品被吐槽最狠的一句话，并标注机型）
            三、 战略攻防矩阵（必须按此格式输出表格：对比维度 | {my_prod}现状 | {comp_prod}现状 | 攻防建议。维度必须包含：影像算法、工业设计、系统稳定性、高端化认可度）
            四、 战术总结建议
            本品语料：{my_in}
            竞品语料：{comp_in}
            """
            report = analyze_with_llm(prompt, api_key, model_name)
            st.markdown(report)
            st.markdown(generate_html_report(report, f"{my_prod}_VS_竞品攻防内参", "compare"), unsafe_allow_html=True)
