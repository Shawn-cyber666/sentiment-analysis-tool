import streamlit as st
import requests
import datetime
import base64

# --- 1. 找回消失的调研按钮 (vivo x300u 专属) ---
def get_search_links(keyword):
    return {
        "小红书 (搜涂抹/品控)": f"https://www.xiaohongshu.com/search_result?keyword={keyword}%20%E6%B6%82%E6%8A%B9%20%E5%93%81%E6%8E%A7",
        "微博 (搜真实翻车)": f"https://s.weibo.com/weibo?q={keyword}%20%E7%BF%BB%E8%BD%A6",
        "酷安 (搜算法退步)": f"https://www.coolapk.com/search?q={keyword}",
        "京东 (搜追评/差评)": f"https://search.jd.com/Search?keyword={keyword}%20%E5%B7%AE%E8%AF%84"
    }

# --- 2. 严谨分析逻辑 (拒绝胡编乱造) ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    【绝对指令】你现在是 vivo x300u 舆情分析专家。
    【事实原则】禁止编造！禁止提及任何评论中没出现的硬件（如增距镜、磁吸配件）。
    【逻辑要求】如果用户粘贴的内容为空或无关，请回答“未收到有效差评数据”。
    
    分析结构：
    一、 真实用户情绪概览
    二、 核心问题矩阵 (维度 | 具体痛点 | 严重程度)
    三、 典型差评原话摘录
    四、 针对性改进建议
    
    【待分析原始数据】：
    {comments}
    """
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0  # 极低随机性，保证诚实
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"分析出错: {str(e)}"

# --- 3. 终极 PDF 解决方案：生成 HTML 报告 ---
# 提示：HTML 报告在浏览器打开后，按 Command+P (Mac) 另存为 PDF，绝对不乱码！
def get_html_download_link(text_content, target):
    html_content = f"""
    <html>
    <head><meta charset="utf-8"><style>
    body {{ font-family: sans-serif; line-height: 1.6; padding: 40px; color: #333; }}
    h1 {{ color: #d32f2f; border-bottom: 2px solid #d32f2f; }}
    pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; white-space: pre-wrap; font-size: 14px; }}
    </style></head>
    <body>
    <h1>{target} 舆情分析报告</h1>
    <p>生成日期: {datetime.date.today()}</p>
    <pre>{text_content}</pre>
    <hr>
    <p style="font-size: 12px; color: #888;">提示：在浏览器中按 Command + P，选择“另存为 PDF”即可完成导出。</p>
    </body>
    </html>
    """
    b64 = base64.b64encode(html_content.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{target}_报告.html" style="text-decoration:none; background-color:#ff4b4b; color:white; padding:10px 20px; border-radius:5px;">📥 下载专业格式报告 (防乱码版)</a>'

# --- 4. 界面展示 ---
st.set_page_config(page_title="vivo x300u 舆情助手", layout="wide")
st.title("📱 vivo x300u 真实舆情分析系统")

with st.sidebar:
    st.header("⚙️ 配置参数")
    api_key = st.text_input("阿里云 API Key", type="password")
    model_name = st.text_input("模型代号", value="deepseek-v3")
    
    st.divider()
    st.subheader("第一步：人工取证")
    target = "vivo x300u"
    links = get_search_links(target)
    for name, url in links.items():
        st.link_button(f"🔗 前往{name}", url)

st.subheader("📝 第二步：粘贴你搜集到的真实评价")
user_input = st.text_area("请把差评原封不动地粘贴在这里，AI 将只针对这些内容进行分析：", height=300)

if st.button("🚀 开始生成分析报告", type="primary"):
    if not api_key or len(user_input) < 10:
        st.error("请先输入 API Key 并粘贴真实的评论内容！")
    else:
        with st.spinner("正在根据真实样本构建反馈矩阵..."):
            report_text = analyze_with_llm(user_input, api_key, model_name)
            st.markdown("---")
            st.markdown(report_text)
            
            # 提供下载链接
            st.divider()
            st.markdown(get_html_download_link(report_text, target), unsafe_allow_html=True)
            st.info("💡 为什么是 HTML？因为云端 PDF 库不稳定。下载后用 Mac 浏览器打开，按 Command+P 即可得到完美的 PDF。")
