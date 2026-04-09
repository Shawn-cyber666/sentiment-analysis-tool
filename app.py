import streamlit as st
import requests
import datetime
import base64
import re

# --- 1. 调研工具入口 ---
def get_search_links(keyword):
    return {
        "小红书 (深度差评)": "https://www.xiaohongshu.com/search_result?keyword=" + keyword + "%20%E5%90%8E%E6%82%94",
        "微博 (实时吐槽)": "https://s.weibo.com/weibo?q=" + keyword + "%20%E7%BF%BB%E8%BD%A6",
        "酷安 (硬件Bug反馈)": "https://www.coolapk.com/search?q=" + keyword,
        "京东 (售后真实评价)": "https://search.jd.com/Search?keyword=" + keyword + "%20%E5%B7%AE%E8%AF%84"
    }

# --- 2. 核心分析逻辑：拒绝幻觉与符号 ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    
    # 使用极致强硬的指令，防止 AI 瞎编
    prompt = (
        "你是一名手机行业资深内参专家。请针对 vivo x300u 的用户评论撰写深度分析报告。\n"
        "要求：\n"
        "1. 禁止脑补：严禁提及评论中没有的内容（如增距镜、磁吸配件等）。\n"
        "2. 深度穿透：分析这些问题如何影响 vivo 的高端品牌心智。\n"
        "3. 纯净文字：禁止使用任何 Markdown 符号（如 #, *, -, >）。\n\n"
        "待分析数据：\n" + comments
    )
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0 # 强制关闭创造力，只说实话
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = res.json()['choices'][0]['message']['content']
        # 强制清理所有残留符号
        return re.sub(r'[*#\-\>]', '', content)
    except Exception as e:
        return "分析系统调用失败，请检查 API Key。"

# --- 3. 稳健的 HTML 生成函数 ---
def get_report_download_link(text_content, target):
    # 彻底避开 f-string 冲突，使用字符串拼接构建专业公文样式
    html_start = """
    <html><head><meta charset="utf-8"><style>
    body { font-family: sans-serif; line-height: 1.8; padding: 40px; color: #1a1a1a; max-width: 800px; margin: auto; }
    .h1 { font-size: 24px; font-weight: bold; border-bottom: 3px solid #1a3a5f; padding-bottom: 10px; text-align: center; color: #1a3a5f; }
    .date { text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }
    .content { white-space: pre-wrap; font-size: 16px; background: #f9f9f9; padding: 20px; border-radius: 5px; }
    </style></head><body>
    <div class="h1">""" + target + """ 舆情研判内参报告</div>
    <div class="date">生成日期：""" + str(datetime.date.today()) + """</div>
    <div class="content">"""
    
    html_end = """</div><p style='text-align:center; font-size:12px; color:#999; margin-top:50px;'>
    提示：下载后用浏览器打开，按 Command + P 选择另存为 PDF 即可获得完美排版报告。</p></body></html>"""
    
    full_html = html_start + text_content + html_end
    b64 = base64.b64encode(full_html.encode('utf-8')).decode()
    
    link = '<a href="data:text/html;base64,' + b64 + '" download="' + target + '_Report.html" '
    link += 'style="text-decoration:none; background-color:#1a3a5f; color:white; padding:12px 25px; border-radius:4px; font-weight:bold;">'
    link += '📥 下载专业调研内参 (防止乱码版)</a>'
    return link

# --- 4. Streamlit 网页前端 ---
st.set_page_config(page_title="vivo x300u 舆情研判")
st.title("💼 vivo x300u 高端舆情专项分析平台")

with st.sidebar:
    st.header("⚙️ 系统配置")
    api_key = st.text_input("API Key", type="password")
    model_name = st.text_input("分析模型", value="deepseek-v3")
    
    st.divider()
    st.subheader("第一步：人工取证")
    links = get_search_links("vivo x300u")
    for name, url in links.items():
        st.link_button(name, url)

st.subheader("📝 第二步：导入待分析样本")
raw_input = st.text_area("请在这里粘贴收集到的差评原话：", height=300)

if st.button("🚀 生成深度研判报告", type="primary"):
    if not api_key or len(raw_input) < 10:
        st.error("请确保 API 配置正确且输入了真实的评论内容。")
    else:
        with st.spinner("系统正在进行语义穿透与风险建模..."):
            final_report = analyze_with_llm(raw_input, api_key, model_name)
            st.markdown("---")
            st.write(final_report)
            
            st.divider()
            # 显示下载链接
            st.markdown(get_report_download_link(final_report, "vivo x300u"), unsafe_allow_html=True)
