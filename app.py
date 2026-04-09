import streamlit as st
import requests
import datetime
import base64
import re

# --- 1. 调研工具箱 ---
def get_search_links(keyword):
    return {
        "小红书 (深度差评)": "https://www.xiaohongshu.com/search_result?keyword=" + keyword + "%20%E5%90%8E%E6%82%94",
        "微博 (实时反馈)": "https://s.weibo.com/weibo?q=" + keyword + "%20%E7%BF%BB%E8%BD%A6",
        "酷安 (硬件Bug)": "https://www.coolapk.com/search?q=" + keyword,
        "京东 (售后评价)": "https://search.jd.com/Search?keyword=" + keyword + "%20%E5%B7%AE%E8%AF%84"
    }

# --- 2. 纯净版分析逻辑 ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    
    prompt = (
        "你是一名专业调研员。请根据 vivo x300u 用户评论撰写调研总结。\n"
        "要求：\n"
        "1. 用大白话写，禁止瞎编，禁止使用任何 # 或 * 符号。\n"
        "2. 结构：一、用户声音概览；二、典型声音描述；三、问题反馈矩阵（表格）；四、简单总结。\n"
        "3. 表格请按格式：维度 | 关键问题 | 严重程度 | 趋势\n\n"
        "评论数据：\n" + comments
    )
    
    payload = {
        "model": model_name, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = res.json()['choices'][0]['message']['content']
        # 彻底清洗掉 AI 喜欢乱加的 Markdown 符号
        return re.sub(r'[*#\-\>]', '', content)
    except:
        return "分析系统调用失败，请检查配置。"

# --- 3. 稳健的 HTML 渲染逻辑 ---
def get_final_report_link(text_content, target):
    # 采用分段定义，避免长字符串导致的 unterminated string 报错
    html_head = """<html><head><meta charset="utf-8"><style>
    body { font-family: sans-serif; padding: 30px; line-height: 1.6; }
    .wrap { max-width: 800px; margin: auto; border: 1px solid #ddd; padding: 40px; }
    h2 { border-bottom: 2px solid #333; padding-bottom: 5px; margin-top: 25px; }
    table { width: 100%; border-collapse: collapse; margin: 15px 0; }
    th, td { border: 1px solid #ccc; padding: 10px; text-align: left; }
    th { background: #f5f5f5; }
    </style></head><body><div class="wrap">"""
    
    html_title = "<h1 style='text-align:center;'>" + target + " 用户调研报告</h1>"
    html_info = "<p style='text-align:center; color:#888;'>生成时间：" + str(datetime.date.today()) + "</p>"
    
    # 精简高效的表格转换引擎
    lines = text_content.split('\n')
    body_html = ""
    in_table = False
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        if "|" in line:
            cells = [c.strip() for c in line.split('|') if c.strip()]
            row = "<tr>" + "".join(["<td>"+c+"</td>" for c in cells]) + "</tr>"
            if not in_table:
                body_html += "<table>" + row.replace("td>", "th>")
                in_table = True
            else:
                body_html += row
        else:
            if in_table:
                body_html += "</table>"
                in_table = False
            if line.startswith(('一、', '二、', '三、', '四、')):
                body_html += "<h2>" + line + "</h2>"
            else:
                body_html += "<div>" + line + "</div>"
    
    if in_table: body_html += "</table>"
    
    full_html = html_head + html_title + html_info + body_html + "</div></body></html>"
    b64 = base64.b64encode(full_html.encode('utf-8')).decode()
    
    link = '<a href="data:text/html;base64,' + b64 + '" download="' + target + '_Report.html" '
    link += 'style="text-decoration:none; background:#333; color:white; padding:12px 25px; border-radius:4px; font-weight:bold; display:inline-block;">'
    link += '📥 下载正式调研报告</a>'
    return link

# --- 4. Streamlit 界面 ---
st.set_page_config(page_title="调研报告生成器")
st.title("🛡️ vivo x300u 用户反馈整理")

with st.sidebar:
    st.header("配置")
    api_key = st.text_input("填入 API Key", type="password")
    model_name = st.text_input("模型代号", value="deepseek-v3")
    st.divider()
    links = get_search_links("vivo x300u")
    for name, url in links.items():
        st.link_button(name, url)

user_input = st.text_area("请在这里粘贴搜集到的评论原语：", height=300)

if st.button("🚀 生成报告", type="primary"):
    if not api_key or len(user_input) < 10:
        st.error("请检查 API Key 和输入内容。")
    else:
        with st.spinner("正在处理..."):
            report = analyze_with_llm(user_input, api_key, model_name)
            st.markdown("---")
            st.write(report)
            st.divider()
            st.markdown(get_final_report_link(report, "vivo x300u"), unsafe_allow_html=True)
