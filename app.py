import streamlit as st
import requests
import datetime
import base64
import re

# --- 1. 调研入口 ---
def get_search_links(keyword):
    return {
        "小红书 (深度差评)": "https://www.xiaohongshu.com/search_result?keyword=" + keyword + "%20%E5%90%8E%E6%82%94",
        "微博 (实时吐槽)": "https://s.weibo.com/weibo?q=" + keyword + "%20%E7%BF%BB%E8%BD%A6",
        "酷安 (硬件Bug反馈)": "https://www.coolapk.com/search?q=" + keyword,
        "京东 (售后真实评价)": "https://search.jd.com/Search?keyword=" + keyword + "%20%E5%B7%AE%E8%AF%84"
    }

# --- 2. 深度专家逻辑：多层级 + 原句模块 ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    
    prompt = (
        "你是一名顶级商业咨询顾问。请针对 vivo x300u 用户评论撰写深度调研报告。\n"
        "要求：\n"
        "1. 严禁使用 #, *, -, > 等符号，直接用中文序号（一、 1. (1)）体现四级深度排版。\n"
        "2. 必须包含【核心负面原句直击】模块，选取3-5条最尖锐的原始评论。\n"
        "3. 深度要求：分析问题背后的品控链路失效、高端心智受损、以及竞品（如小米/华为）的挤压风险。\n"
        "待分析数据：\n" + comments
    )
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = res.json()['choices'][0]['message']['content']
        # 深度清洗符号，确保报告干净
        return re.sub(r'[*#\-\>]', '', content)
    except:
        return "分析调用失败，请检查配置。"

# --- 3. 商务级 HTML 模板 (卡片式布局) ---
def get_ultra_report_link(text_content, target):
    # 彻底隔离大括号冲突，采用分段拼接
    html_header = """
    <html><head><meta charset="utf-8">
    <style>
        body { font-family: 'PingFang SC', sans-serif; background: #f4f7f9; padding: 50px; color: #333; }
        .report-card { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); max-width: 900px; margin: auto; border-top: 8px solid #1a3a5f; }
        .top-tag { color: #d9534f; font-weight: bold; font-size: 12px; letter-spacing: 2px; margin-bottom: 20px; }
        .main-title { font-size: 28px; font-weight: bold; color: #1a3a5f; margin-bottom: 5px; }
        .sub-info { font-size: 14px; color: #999; margin-bottom: 40px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
        .content-box { white-space: pre-wrap; line-height: 2; font-size: 16px; color: #2c3e50; }
        .quote-style { background: #fff5f5; border-left: 5px solid #d9534f; padding: 15px; margin: 20px 0; font-style: italic; }
        .footer { text-align: center; margin-top: 40px; font-size: 12px; color: #bbb; }
    </style>
    </head><body>
    <div class="report-card">
        <div class="top-tag">机密 · 内部传阅</div>
        <div class="main-title">__TARGET__ 舆情深度穿透研判报告</div>
        <div class="sub-info">报告流水号：调研-2026-X | 生成日期：__DATE__</div>
        <div class="content-box">__CONTENT__</div>
        <div class="footer">报告由智能决策分析系统生成，仅供管理层战略决策参考。</div>
    </div>
    </body></html>
    """
    
    # 使用 replace 注入数据，不产生语法歧义
    full_html = html_header.replace("__TARGET__", target)
    full_html = full_html.replace("__DATE__", str(datetime.date.today()))
    full_html = full_html.replace("__CONTENT__", text_content)
    
    b64 = base64.b64encode(full_html.encode('utf-8')).decode()
    
    btn_html = '<a href="data:text/html;base64,' + b64 + '" download="' + target + '_深度分析.html" '
    btn_html += 'style="text-decoration:none; background:linear-gradient(135deg, #1a3a5f 0%, #2c5e8c 100%); color:white; padding:15px 35px; border-radius:30px; font-weight:bold; box-shadow: 0 4px 15px rgba(26,58,95,0.3); display:inline-block;">'
    btn_html += '📥 导出高端商务 PDF 格式报告</a>'
    return btn_html

# --- 4. Streamlit 前端渲染 ---
st.set_page_config(page_title="高端舆情内参", layout="wide")
st.title("🛡️ 手机品牌高端化深度研判平台")

with st.sidebar:
    st.header("🔑 系统凭证")
    api_key = st.text_input("阿里云 Key", type="password")
    model_name = st.text_input("模型代号", value="deepseek-v3")
    st.divider()
    st.subheader("第一步：全网差评透析")
    links = get_search_links("vivo x300u")
    for name, url in links.items():
        st.link_button(name, url)

st.subheader("📝 第二步：输入待研判评论样本")
raw_data = st.text_area("请粘贴 vivo x300u 的差评内容（建议多粘贴几条以提高深度）：", height=350)

if st.button("🚀 启动深度多维建模报告", type="primary"):
    if not api_key or len(raw_data) < 10:
        st.error("请输入 API Key 并粘贴足够的数据。")
    else:
        with st.spinner("正在解析品控链路、品牌资产受损度及用户心理预想..."):
            final_report = analyze_with_llm(raw_data, api_key, model_name)
            
            st.markdown("### 📊 深度研判预览")
            st.info(final_report)
            
            st.divider()
            st.markdown(get_ultra_report_link(final_report, "vivo x300u"), unsafe_allow_html=True)
            st.caption("💡 导出建议：下载后用浏览器打开，按 Command+P 另存为 PDF，效果最佳。")
