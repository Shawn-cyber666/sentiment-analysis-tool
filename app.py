import streamlit as st
import requests
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import datetime

# --- 1. 搜索链接逻辑 ---
def get_search_links(keyword):
    return {
        "小红书 (搜算法涂抹/品控)": f"https://www.xiaohongshu.com/search_result?keyword={keyword}%20%E6%B6%82%E6%8A%B9%20%E5%93%81%E6%8E%A7",
        "微博 (搜真实翻车吐槽)": f"https://s.weibo.com/weibo?q={keyword}%20%E7%BF%BB%E8%BD%A6",
        "京东 (搜差评/追评)": f"https://search.jd.com/Search?keyword={keyword}%20%E5%B7%AE%E8%AF%84",
        "酷安 (搜系统BUG/影像退步)": f"https://www.coolapk.com/search?q={keyword}"
    }

# --- 2. 简易 PDF 生成 (规避字符冲突) ---
def create_pdf(text_content):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica", 10)
    y = 800
    for line in text_content.split('\n'):
        if y < 50:
            c.showPage()
            y = 800
        # 移除可能导致渲染错误的字符
        safe_line = line.replace('#', '').replace('*', '').strip()
        c.drawString(50, y, safe_line)
        y -= 15
    c.save()
    buffer.seek(0)
    return buffer

# --- 3. AI 分析引擎 (阿里云百炼专版) ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # 修复：确保 Prompt 引号闭合，且逻辑清晰
    prompt_text = (
        "你是一个数码博主和舆情专家。请对以下关于 vivo x300u 的负面评价进行分析。\n"
        "请严格按此结构输出：\n"
        "一、 用户声音概览 (占比、核心槽点)\n"
        "二、 典型声音描述 (原话摘录)\n"
        "三、 问题反馈矩阵 (表格格式：维度 | 问题 | 严重程度 | 趋势)\n"
        "四、 综合分析总结 (改进建议)\n\n"
        f"待分析评论：\n{comments}"
    )
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.2
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
        else:
            return f"错误：{res.text}"
    except Exception as e:
        return f"连接失败: {str(e)}"

# --- 4. Streamlit 网页布局 ---
st.set_page_config(page_title="vivo x300u 舆情助手", layout="wide")
st.title("📱 vivo x300u 舆情“人机协作”分析工具")

with st.sidebar:
    st.header("🔑 配置 API")
    api_key = st.text_input("阿里云 API Key", type="password")
    # 截图显示你用的是 deepseek，请确认是 v3 还是 r1
    model_name = st.text_input("模型代号", value="deepseek-v3")
    
    st.divider()
    target = st.text_input("监测目标", value="vivo x300u")
    st.markdown("### 第一步：人工调研")
    links = get_search_links(target)
    for name, link in links.items():
        st.link_button(f"🔗 前往 {name}", link)

st.subheader("📝 第二步：粘贴负面样本")
raw_input = st.text_area("请粘贴收集到的差评：", height=300, placeholder="例如：长焦算法太暴力了...")

if st.button("🚀 生成深度分析报告", type="primary"):
    if not api_key or not raw_input:
        st.error("请确保 API Key 和评论区都已经填写。")
    else:
        with st.spinner("AI 正在解析 vivo x300u 的反馈矩阵..."):
            report = analyze_with_llm(raw_input, api_key, model_name)
            st.markdown("---")
            st.markdown(report)
            
            # PDF 导出
            pdf_data = create_pdf(report)
            st.download_button("📥 下载 PDF 报告", pdf_data, f"{target}_report.pdf", "application/pdf")
