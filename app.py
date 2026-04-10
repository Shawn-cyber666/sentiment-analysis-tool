import streamlit as st
import requests
import datetime
import base64
import re
import urllib.parse

# --- 1. UGC 情报取证入口 (对标 X300U/X9U/Pura90) ---
def get_search_links(keyword):
    enc = urllib.parse.quote(keyword)
    return {
        "🔴 小红书 (痛点挖掘)": f"https://www.xiaohongshu.com/search_result?keyword={enc}%20吐槽",
        "🟡 新浪微博 (舆情翻车)": f"https://s.weibo.com/weibo?q={enc}%20翻车",
        "🎵 抖音 (差评视频)": f"https://www.douyin.com/search/{enc}%20缺点"
    }

# --- 2. 核心分析引擎 (锁定真实语料，彻底杜绝幻觉) ---
def analyze_with_llm(prompt, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    payload = {
        "model": model_name, 
        "messages": [
            {"role": "system", "content": "你是一名严谨的 vivo 产品专家。你必须仅根据提供的语料进行分析，严禁编造任何参数或细节。如果语料中没提到，就写“暂无提及”。"},
            {"role": "user", "content": prompt}
        ], 
        "temperature": 0.0 # 绝对锁定，严禁任何随机发挥
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except Exception:
        return "ERROR: 引擎响应异常，请检查配置。"

# --- 3. 专家级内参渲染 (彻底解决 ||| 乱码与表格缺失) ---
def generate_html_report(text_content, title, mode="single"):
    html_template = """
    <html><head><meta charset="utf-8"><style>
    body { font-family: 'PingFang SC', sans-serif; background: #F4F7FA; padding: 30px; color: #333; }
    .report-card { max-width: 880px; margin: 0 auto; background: #FFF; padding: 40px; border-radius: 2px; border-top: 6px solid #415FFF; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    h1 { text-align: center; font-size: 24px; color: #000; margin-bottom: 5px; }
    .meta { text-align: center; color: #999; font-size: 12px; margin-bottom: 30px; border-bottom: 1px solid #EEE; padding-bottom: 15px; }
    h2 { font-size: 18px; color: #415FFF; margin: 30px 0 15px 0; border-left: 4px solid #415FFF; padding-left: 10px; }
    .quote-box { background: #FFF1F1; border-left: 4px solid #FF3B30; padding: 15px; margin: 15px 0; color: #D00; font-size: 15px; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 13px; }
    th, td { padding: 12px; border: 1px solid #E0E0E0; text-align: left; }
    th { background: #F8F9FB; font-weight: bold; color: #111; }
    .footer { text-align: center; margin-top: 40px; font-size: 11px; color: #BBB; }
    </style></head><body>
    <div class="report-card">
        <h1>{{TITLE}}</h1>
        <div class="meta">vivo 内部保密资料 · 生成日期：{{DATE}}</div>
        {{BODY}}
        <div class="footer">本报告由策略研究中心系统自动解析生成。</div>
    </div></body></html>
    """
    
    # 清洗文本中的干扰符（彻底解决 ||| 问题）
    clean_text = re.sub(r'\|[-: ]+\|', '', text_content) # 移除 Markdown 分隔线
    clean_text = re.sub(r'[*#]', '', clean_text) # 移除多余修饰符
    
    body_html = ""
    lines = clean_text.split('\n')
    in_table = False
    is_quote_section = False

    for line in lines:
        line = line.strip()
        if not line: continue
        
        # 模块识别
        if any(kw in line for kw in ["一、", "二、", "三、", "四、"]):
            if in_table: body_html += "</tbody></table>"; in_table = False
            is_quote_section = "原声" in line or "直击" in line
            body_html += f"<h2>{line}</h2>"
        elif "|" in line:
            # 强化表格行解析
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if len(cells) >= 2:
                row = "<tr>" + "".join([f"<td>{c}</td>" for c in cells]) + "</tr>"
                if not in_table:
                    body_html += "<table><thead>" + row.replace("td>", "th>") + "</thead><tbody>"
                    in_table = True
                else:
                    body_html += row
        else:
            if in_table: body_html += "</tbody></table>"; in_table = False
            if is_quote_section:
                body_html += f"<div class='quote-box'>“{line}”</div>"
            else:
                body_html += f"<p style='margin-bottom:10px;'>{line}</p>"

    if in_table: body_html += "</tbody></table>"
    
    # 最终替换避免语法报错
    res = html_template.replace("{{TITLE}}", title)
    res = res.replace("{{DATE}}", str(datetime.date.today()))
    res = res.replace("{{BODY}}", body_html)
    
    b64 = base64.b64encode(res.encode('utf-8')).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{title}.html" style="text-decoration:none; background:#415FFF; color:white; padding:12px 25px; border-radius:4px; font-weight:bold; display:inline-block;">📥 导出专家级内参 (HTML/PDF)</a>'

# --- 4. 平台交互界面 ---
st.set_page_config(page_title="vivo 终端策略中枢", layout="wide")
st.title("💼 终端产品全维度研判平台")

with st.sidebar:
    st.header("🔑 系统权限")
    api_key = st.text_input("API Key", type="password")
    model_name = st.text_input("模型代号", value="deepseek-v3")
    st.divider()
    mode = st.radio("🛡️ 任务模式", ["单品深度研判 (vivo X300U)", "竞品对比攻防 (X300U vs X9U/Pura90)"])

if mode == "单品深度研判 (vivo X300U)":
    with st.sidebar:
        st.divider()
        st.subheader("📡 UGC 快速取证")
        for name, url in get_search_links("vivo x300u").items():
            st.link_button(name, url, use_container_width=True)

    st.subheader("📑 本品原始语料录入 (vivo X300U)")
    user_input = st.text_area("请贴入真实评论文本：", height=250, placeholder="在此粘贴从社交平台抓取的原始语料...")
    
    if st.button("生成单品深度报告", type="primary"):
        with st.spinner("正在基于真实语料研判..."):
            prompt = f"作为专家，仅根据语料撰写【vivo x300u】研判报告。严禁虚构。结构：一、舆情态势；二、尖锐原声直击（2句原话）；三、问题反馈矩阵（表格：维度|痛点详情|严重程度|改进紧迫性。维度含影像、硬件、系统、价值感）；四、专家建议。语料：{user_input}"
            report = analyze_with_llm(prompt, api_key, model_name)
            st.markdown(report)
            st.markdown(generate_html_report(report, "vivo_X300U_专项研判报告", "single"), unsafe_allow_html=True)

else:
    st.subheader("⚔️ 战略攻防对比阵列")
    col1, col2 = st.columns(2)
    with col1:
        my_prod = "vivo x300u"
        st.info(f"📍 本品核心：{my_prod}")
        for n, u in get_search_links(my_prod).items(): st.link_button(n, u, use_container_width=True)
        my_in = st.text_area("贴入 vivo 负面语料：", height=200)
    with col2:
        comp_prod = "OPPO Find X9U / 华为 Pura 90"
        st.warning(f"📍 对标竞品：{comp_prod}")
        for n, u in get_search_links(comp_prod).items(): st.link_button(n, u, use_container_width=True)
        comp_in = st.text_area("贴入竞品负面语料：", height=200)

    if st.button("启动战略攻防研判", type="primary"):
        with st.spinner("正在构建对比矩阵..."):
            prompt = f"横向对比【{my_prod}】与【{comp_prod}】。严禁虚构。结构：一、舆情分歧点分析；二、典型原声描述（注明机型）；三、战略攻防矩阵（表格：对比维度|{my_prod}现状|竞品现状|攻防建议。维度含影像算法、工业设计、系统稳定性、高端认可度）；四、战术结论。语料：本品-{my_in}，竞品-{comp_in}"
            report = analyze_with_llm(prompt, api_key, model_name)
            st.markdown(report)
            st.markdown(generate_html_report(report, "vivo_vs_竞品攻防报告", "compare"), unsafe_allow_html=True)
