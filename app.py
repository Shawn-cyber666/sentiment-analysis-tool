import streamlit as st
import requests
import datetime
import base64
import re
import urllib.parse

# --- 1. 核心 UGC 阵地直达 (精简高效版) ---
def get_search_links(keyword):
    enc = urllib.parse.quote(keyword)
    return {
        "🔴 小红书 (搜痛点)": f"https://www.xiaohongshu.com/search_result?keyword={enc}%20吐槽",
        "🟡 微博 (搜翻车)": f"https://s.weibo.com/weibo?q={enc}%20翻车",
        "🎵 抖音 (搜视频差评)": f"https://www.douyin.com/search/{enc}%20缺点"
    }

# --- 2. 大语言模型底层引擎 ---
def analyze_with_llm(prompt, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    payload = {
        "model": model_name, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = res.json()['choices'][0]['message']['content']
        # 仅清理装饰用 Markdown 符号，保留表格核心管道符
        return re.sub(r'[*#\-\>]', '', content)
    except Exception:
        return "分析系统调用失败，请检查配置。"

# --- 3. 商务内参 PDF 渲染引擎 (高可靠表格解析) ---
def generate_html_report(text_content, title, mode="single"):
    html_head = """<html><head><meta charset="utf-8"><style>
    body { font-family: -apple-system, 'PingFang SC', sans-serif; background: #F4F6F9; padding: 40px; color: #2C3E50; line-height: 1.6; }
    .report-card { max-width: 850px; margin: 0 auto; background: #FFF; padding: 50px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.05); border-top: 6px solid #415FFF; }
    h1 { text-align: center; font-size: 24px; color: #111; margin-bottom: 5px; }
    .meta { text-align: center; color: #888; font-size: 13px; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid #EEE; }
    h2 { font-size: 18px; color: #415FFF; margin-top: 35px; border-left: 4px solid #415FFF; padding-left: 12px; margin-bottom: 15px; }
    .quote-box { background: #FFF0F0; border-left: 4px solid #FF4B4B; padding: 15px 20px; margin: 15px 0; color: #D80000; font-weight: 500; border-radius: 0 6px 6px 0; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; border: 1px solid #EAEEF2; }
    th, td { padding: 14px; text-align: left; border: 1px solid #EAEEF2; vertical-align: top; }
    th { background: #F8FAFC; color: #333; font-weight: bold; white-space: nowrap; }
    .footer { text-align: center; margin-top: 40px; font-size: 12px; color: #AAA; }
    </style></head><body><div class="report-card">"""
    
    html_title = f"<h1>{title}</h1>"
    html_info = f"<div class='meta'>内部机密 · 生成日期：{datetime.date.today()}</div>"
    
    lines = text_content.split('\n')
    body_html = ""
    in_table = False
    is_quote_section = False
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # 模块识别逻辑
        if any(kw in line for kw in ["原声直击", "尖锐原声"]):
            is_quote_section = True
            if in_table: body_html += "</table>"; in_table = False
            body_html += f"<h2>{line}</h2>"
            continue
            
        if line.startswith(('一、', '二、', '三、', '四、', '五、')):
            is_quote_section = False
            if in_table: body_html += "</table>"; in_table = False
            body_html += f"<h2>{line}</h2>"
            continue
            
        # 鲁棒表格解析：只要含有 | 且不全是 - 
        if "|" in line and not all(c in "| -:" for c in line):
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if len(cells) > 1:
                row = "<tr>" + "".join([f"<td>{c}</td>" for c in cells]) + "</tr>"
                if not in_table:
                    body_html += "<table><thead>" + row.replace("td>", "th>") + "</thead><tbody>"
                    in_table = True
                else:
                    body_html += row
                continue

        # 普通文本处理
        if in_table: body_html += "</tbody></table>"; in_table = False
        
        if is_quote_section:
            body_html += f"<div class='quote-box'>“{line}”</div>"
        else:
            body_html += f"<div style='margin-bottom: 8px;'>{line}</div>"
                
    if in_table: body_html += "</tbody></table>"
    html_footer = "<div class='footer'>本报告由产品线内参系统自动聚合。</div></div></body></html>"
    
    full_html = html_head + html_title + html_info + body_html + html_footer
    b64 = base64.b64encode(full_html.encode('utf-8')).decode()
    
    btn_color = "#415FFF" if mode == "single" else "#212529"
    link = f'<a href="data:text/html;base64,{b64}" download="{title}.html" style="text-decoration:none; background:{btn_color}; color:white; padding:12px 28px; border-radius:6px; font-weight:bold; display:inline-block;">📥 导出高清 PDF 内参报告</a>'
    return link

# --- 4. 界面展示 ---
st.set_page_config(page_title="vivo 舆情研判中枢", page_icon="📱", layout="wide")
st.title("📱 终端产品舆情专项研判系统")

with st.sidebar:
    st.header("⚙️ 引擎配置")
    api_key = st.text_input("API Key", type="password")
    model_name = st.text_input("模型代号", value="deepseek-v3")
    st.divider()
    mode = st.radio("🛡️ 选择研判模式", ["单品深度研判 (本品)", "竞品对比攻防 (横向)"])
    
if mode == "单品深度研判 (本品)":
    with st.sidebar:
        st.divider()
        st.subheader("🔗 取证快捷入口")
        target = st.text_input("机型", value="vivo x300u")
        for name, url in get_search_links(target).items():
            st.link_button(name, url, use_container_width=True)
            
    st.subheader("📝 单品语料输入舱")
    user_input = st.text_area("粘贴用户评价：", height=250)
    
    if st.button("🚀 生成研判报告", type="primary"):
        with st.spinner("分析中..."):
            prompt = f"撰写【{target}】研判报告。要求：大白话。一、用户声音概览；二、尖锐原声直击（1-2句原话）；三、问题反馈矩阵（维度|关键问题|严重程度|趋势。包含影像、系统、性能、质感）；四、总结。语料：{user_input}"
            report = analyze_with_llm(prompt, api_key, model_name)
            st.write(report)
            st.markdown(generate_html_report(report, f"{target}_研判报告", "single"), unsafe_allow_html=True)

else:
    st.subheader("⚔️ 竞品攻防阵列")
    col1, col2 = st.columns(2)
    with col1:
        my_prod = st.text_input("本品", value="vivo x300u")
        for n, u in get_search_links(my_prod).items(): st.link_button(n, u, use_container_width=True)
        my_in = st.text_area("本品语料：", height=200)
    with col2:
        comp_prod = st.text_input("竞品", value="OPPO Find X9U / 华为 Pura90")
        for n, u in get_search_links(comp_prod).items(): st.link_button(n, u, use_container_width=True)
        comp_in = st.text_area("竞品语料：", height=200)

    if st.button("⚡ 生成竞品攻防报告", type="primary"):
        with st.spinner("对比建模中..."):
            prompt = (
                f"横向对比【{my_prod}】与【{comp_prod}】。要求：\n"
                f"一、舆情基本盘对比；\n"
                f"二、尖锐原声直击（摘录双方骂得最狠的原话，注明机型）；\n"
                f"三、竞品攻防矩阵（必须严格使用表格格式，包含如下维度：影像能力、系统体验、续航发热、质感设计。行格式：维度 | {my_prod}现状 | {comp_prod}现状 | 攻防建议）；\n"
                f"四、战术总结。\n"
                f"数据：本品-{my_in}，竞品-{comp_in}"
            )
            report = analyze_with_llm(prompt, api_key, model_name)
            st.write(report)
            st.markdown(generate_html_report(report, "竞品对比攻防报告", "compare"), unsafe_allow_html=True)
