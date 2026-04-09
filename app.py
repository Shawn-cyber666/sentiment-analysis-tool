import streamlit as st
import requests
import io
import datetime
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- 1. 搜索链接 (vivo x300u) ---
def get_search_links(keyword):
    return {
        "小红书 (搜涂抹/品控)": f"https://www.xiaohongshu.com/search_result?keyword={keyword}%20%E6%B6%82%E6%8A%B9%20%E5%93%81%E6%8E%A7",
        "微博 (搜真实翻车)": f"https://s.weibo.com/weibo?q={keyword}%20%E7%BF%BB%E8%BD%A6",
        "酷安 (搜算法退步)": f"https://www.coolapk.com/search?q={keyword}"
    }

# --- 2. 增强版 PDF 生成 (自动适配 SimSun 字体) ---
def create_chinese_pdf(text_content):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    font_name = "Helvetica" 
    # 这里修改为和你截图一致的文件名（全小写更稳妥）
    font_path = "simsun.ttf" 
    
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('ZhongWen', font_path))
            font_name = 'ZhongWen'
        except Exception as e:
            st.error(f"字体加载失败。请确保上传了真实的 TTF 文件。错误详情: {e}")
    else:
        st.warning(f"警告：未在根目录找到 {font_path}，PDF 将使用英文显示（中文会乱码）。")

    c.setFont(font_name, 11)
    y = 800
    for line in text_content.split('\n'):
        if y < 50:
            c.showPage()
            c.setFont(font_name, 11)
            y = 800
        # 基础清洗，防止非法字符中断渲染
        clean_line = line.replace('#', '').replace('*', '').strip()
        c.drawString(50, y, clean_line)
        y -= 20
    c.save()
    buffer.seek(0)
    return buffer

# --- 3. 强制事实分析逻辑 ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # 极高强度的约束指令
    prompt_text = f"""
    【强制指令】
    你是一个严谨的数码质检专家。当前分析对象是：vivo x300u。
    
    【禁止行为】
    1. 绝对禁止编造任何不在下方“原始评论”中出现的功能。
    2. 如果评论中没有提到硬件品控、影像算法等，对应部分请直接回复“样本不足，无法得出结论”。
    3. 严禁出现“增距镜”、“磁吸配件”等本产品不具备或评论未提及的内容。
    
    【报告结构】
    一、 真实声音概览 (仅总结原始数据)
    二、 典型吐槽摘录 (必须是原文)
    三、 负面反馈矩阵 (维度 | 问题详情 | 严重等级)
    四、 针对性补救建议
    
    【原始评论数据开始】
    {comments}
    【原始评论数据结束】
    """
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.0  # 强制 AI 放弃创造力，只做数据搬运和分类
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"API 分析失败: {str(e)}"

# --- 4. 界面展示 ---
st.set_page_config(page_title="vivo x300u 真实分析助手")
st.title("📱 vivo x300u 舆情实证分析工具")

with st.sidebar:
    st.header("⚙️ 配置中心")
    api_key = st.text_input("阿里云 API Key", type="password")
    # 注意：阿里云百炼中 DeepSeek 的正确代号通常是 deepseek-v3
    model_name = st.text_input("模型代号", value="deepseek-v3")
    
    st.divider()
    st.markdown("### 第一步：获取真实数据")
    links = get_search_links("vivo x300u")
    for name, link in links.items():
        st.link_button(f"🔗 前往{name}", link)

st.subheader("📝 第二步：在此输入你观察到的真实评价")
raw_input = st.text_area("请务必粘贴你在各平台看到的真实吐槽（建议3条以上）：", height=300)

if st.button("🚀 生成基于事实的报告", type="primary"):
    if not api_key or len(raw_input) < 5:
        st.error("请输入 API Key 并提供有效的评论数据。")
    else:
        with st.spinner("AI 正在严格核对原始数据..."):
            report = analyze_with_llm(raw_input, api_key, model_name)
            st.markdown("---")
            st.markdown(report)
            
            pdf_data = create_chinese_pdf(report)
            st.download_button("📥 下载 PDF 报告", pdf_data, "x300u_fact_report.pdf", "application/pdf")
