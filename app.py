import streamlit as st
import requests
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import datetime

# --- 1. 导航功能：针对 vivo x300u 优化的搜索链接 ---
def get_search_links(keyword):
    # 将关键词编码，确保 URL 正常工作
    return {
        "小红书 (搜算法涂抹/品控)": f"https://www.xiaohongshu.com/search_result?keyword={keyword}%20%E6%B6%82%E6%8A%B9%20%E5%93%81%E6%8E%A7",
        "微博 (搜真实翻车吐槽)": f"https://s.weibo.com/weibo?q={keyword}%20%E7%BF%BB%E8%BD%A6",
        "京东 (搜差评/追评)": f"https://search.jd.com/Search?keyword={keyword}%20%E5%B7%AE%E8%AF%84",
        "酷安 (搜系统BUG/影像退步)": f"https://www.coolapk.com/search?q={keyword}"
    }

# --- 2. PDF 生成逻辑 (极简版) ---
def create_pdf(text_content):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 10) 
    
    y_position = height - 50
    for line in text_content.split('\n'):
        if y_position < 50:
            c.showPage()
            y_position = height - 50
        # 简单处理掉 Markdown 的符号防止渲染问题
        clean_line = line.replace('#', '').replace('*', '').strip()
        c.drawString(50, y_position, clean_line)
        y_position -= 15
        
    c.save()
    buffer.seek(0)
    return buffer

# --- 3. AI 分析引擎 (适配阿里云百炼 DeepSeek) ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    你是一个资深手机行业专家，现在请对人工收集的关于【vivo x300u】的评价进行深度扫描。
    请必须输出以下格式的报告：
    
    一、 用户声音概览
    1
