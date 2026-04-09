import streamlit as st
import requests
import io
import datetime
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- 1. 核心配置：加载字体 ---
def get_pdf_font():
    font_path = "simsun.ttf"  # 必须与 GitHub 中的文件名完全一致（全小写）
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('SimSun', font_path))
            return 'SimSun'
        except:
            return 'Helvetica'
    return 'Helvetica'

# --- 2. 严谨分析：杜绝 AI 瞎编 ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # 强化指令：禁止 AI 提及评论中不存在的事物（如磁吸、增距镜）
    prompt = f"""
    【任务】你现在是一名严谨的 vivo x300u 舆情分析专家。
    【指令】请仅根据下方提供的用户评论进行分析。
    【禁止】严禁提及评论中没有出现过的任何硬件故障、配件（如增距镜）或功能。
    【空缺处理】如果数据中没有提到某个维度，请直接标注“样本未提及”。

    【分析结构】
    一、 用户情绪概览 (仅限数据中存在的槽点)
    二、 典型负面反馈摘录 (必须是原话)
    三、 问题反馈矩阵 (维度 | 具体痛点 | 严重程度 | 趋势)
    四、 专家改进建议 (基于上述事实)

    【待分析评论数据】：
    {comments}
    """
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0  # 将温度设为0，彻底关闭 AI 的“创造力”，让它只说实话
    }
    
    res = requests.post(url, headers=headers, json=payload)
    return res.json()['choices'][0]['message']['content']

# --- 3. PDF 渲染 ---
def create_pdf(text_content):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    font = get_pdf_font()
    c.setFont(font, 10)
    
    y = 800
    for line in text_content.split('\n'):
        if y < 50:
            c.showPage()
            c.setFont(font, 10)
            y = 800
        # 简单过滤 Markdown 符号
        clean_line = line.replace('#', '').replace('*', '').strip()
        c.drawString(50, y, clean_line)
        y -= 18
        
    c.save()
    buffer.seek(0)
    return buffer

# --- 4. 界面设计 ---
st.set_page_config(page_title="vivo x300u 舆情深度分析")
st.title("🛡️ vivo x300u 舆情真实性分析系统")

with st.sidebar:
    st.header("⚙️ 配置中心")
    api_key = st.text_input("阿里云 API Key", type="password")
    # 注意：根据你的图片，模型代号建议改为 deepseek-v3
    model_name = st.text_input("模型代号", value="deepseek-v3") 

st.subheader("📝 录入真实差评")
user_data = st.text_area("请粘贴你搜集到的 vivo x300u 真实评价（AI 将严格基于此内容生成报告）：", height=300)

if st.button("🚀 生成基于事实的报告", type="primary"):
    if not api_key or len(user_data) < 10:
        st.error("请确保填写了 API Key，并粘贴了真实的评论内容。")
    else:
        with st.spinner("正在解析数据，过滤幻觉信息..."):
            report = analyze_with_llm(user_data, api_key, model_name)
            st.markdown(report)
            
            # PDF 下载
            pdf_data = create_pdf(report)
            st.download_button("📥 下载 PDF 报告", pdf_data, "vivo_x300u_Report.pdf", "application/pdf")
