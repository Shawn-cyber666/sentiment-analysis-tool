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

# --- 2. 纯净版分析逻辑 (极简、大白话、去符号) ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    
    prompt = (
        "你是一名内部调研专员。请根据用户评论撰写 vivo x300u 的真实反馈总结。\n"
        "要求：\n"
        "1. 语言直白接地气（大白话），严禁虚构，严禁使用 #、* 等 Markdown 符号。\n"
        "2. 结构必须严格为：一、用户声音概览；二、典型声音描述；三、问题反馈矩阵；四、综合总结。\n"
        "3. 在“问题反馈矩阵”部分，按此格式输出：维度 | 关键问题 | 严重程度 | 趋势。每行一条，不要输出任何分隔线（如 |---|）。\n\n"
        "用户原声样本：\n" + comments
    )
    
    payload = {
        "model": model_name, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = res.json()['choices'][0]['message']['content']
        return re.sub(r'[*#\-\>]', '', content)
    except Exception as e:
        return "分析系统调用失败，请检查 API Key 或网络状态。"

# --- 3. 商务级 HTML 渲染 (vivo 视觉风格) ---
def get_final_report_link(text_content, target):
    # 注入 vivo 蓝 (#415FFF) 与现代科技感卡片 UI
    html_head = """<html><head><meta charset="utf-8"><style>
    body { font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #F4F6F9; padding: 40px; color: #2C3E50; line-height: 1.6; }
    .report-card { max-width: 850px; margin: 0 auto; background: #FFF; padding: 50px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.05); border-top: 6px solid #415FFF; }
    h1 { text-align: center; font-size: 24px; color: #111; margin-bottom: 5px; }
    .meta { text-align: center; color: #888; font-size: 13px; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid #EEE; }
    h2 { font-size: 18px; color: #415FFF; margin-top: 35px; border-left: 4px solid #415FFF; padding-left: 12px; }
    table { width: 100%; border-collapse: separate; border-spacing: 0; margin: 20px 0; border: 1px solid #EAEEF2; border-radius: 8px; overflow: hidden; font-size: 14px; }
    th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #EAEEF2; }
    th { background: #F8FAFC; color: #333; font-weight: bold; }
    tr:last-child td { border-bottom: none; }
    .footer { text-align: center; margin-top: 40px; font-size: 12px; color: #AAA; }
    </style></head><body><div class="report-card">"""
    
    html_title = "<h1>" + target + " 用户舆情专项研判</h1>"
    html_info = "<div class='meta'>内部机密 · 生成日期：" + str(datetime.date.today()) + "</div>"
    
    # 极度稳健的表格转换器 (自动忽略 Markdown 干扰)
    lines = text_content.split('\n')
    body_html = ""
    in_table = False
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        if "|" in line:
            if "---" in line: continue # 过滤 AI 可能生成的表头分隔线
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if not cells: continue
            
            row = "<tr>" + "".join(["<td>"+c+"</td>" for c in cells]) + "</tr>"
            if not in_table:
                # 第一行自动作为表头
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
                body_html += "<div style='margin-bottom: 8px;'>" + line + "</div>"
    
    if in_table: body_html += "</table>"
    html_footer = "<div class='footer'>本报告由内部系统自动聚合，结果仅供产品线改进参考。</div>"
    
    full_html = html_head + html_title + html_info + body_html + html_footer + "</div></body></html>"
    b64 = base64.b64encode(full_html.encode('utf-8')).decode()
    
    link = '<a href="data:text/html;base64,' + b64 + '" download="' + target + '_内部研判报告.html" '
    link += 'style="text-decoration:none; background:#415FFF; color:white; padding:12px 28px; border-radius:6px; font-weight:bold; display:inline-block; box-shadow: 0 4px 10px rgba(65,95,255,0.3);"> '
    link += '📥 导出高清 PDF 报告 (无损排版)</a>'
    return link

# --- 4. Streamlit 界面 ---
st.set_page_config(page_title="vivo 内部舆情研判系统", page_icon="📱", layout="wide")
st.title("📱 终端产品真实舆情研判系统")

with st.sidebar:
    st.header("⚙️ 引擎配置")
    api_key = st.text_input("阿里云 API Key", type="password")
    model_name = st.text_input("模型代号", value="deepseek-v3")
    st.divider()
    st.subheader("🔗 全网素材直达")
    links = get_search_links("vivo x300u")
    for name, url in links.items():
        st.link_button(name, url, use_container_width=True)

st.subheader("📝 语料输入舱")
user_input = st.text_area("请贴入原始用户评价（越接地气、越具体的吐槽越好）：", height=300)

if st.button("🚀 开始多维研判", type="primary"):
    if not api_key or len(user_input) < 10:
        st.error("⚠️ 请检查 API Key 是否填写，且评论内容需大于 10 个字符。")
    else:
        with st.spinner("正在提取核心问题并生成结构化表格..."):
            report = analyze_with_llm(user_input, api_key, model_name)
            st.success("研判完成！请预览或直接下载。")
            st.markdown("---")
            st.write(report)
            st.divider()
            st.markdown(get_final_report_link(report, "vivo x300u"), unsafe_allow_html=True)
            st.caption("💡 操作提示：点击下载后，使用 Chrome/Edge 浏览器打开 HTML 文件，按下 `Ctrl+P` (Win) 或 `Cmd+P` (Mac) 即可另存为精美 PDF 发送给团队。")
