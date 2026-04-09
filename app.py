import streamlit as st
import requests
import io
import datetime
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- 1. 搜索链接逻辑 (vivo x300u 专版) ---
def get_search_links(keyword):
    return {
        "小红书 (搜算法/品控)": f"https://www.xiaohongshu.com/search_result?keyword={keyword}%20%E6%B6%82%E6%8A%B9%20%E5%93%81%E6%8E%A7",
        "微博 (搜真实翻车吐槽)": f"https://s.weibo.com/weibo?q={keyword}%20%E7%BF%BB%E8%BD%A6",
        "京东 (搜差评/追评)": f"https://search.jd.com/Search?keyword={keyword}%20%E5%B7%AE%E8%AF%84",
        "酷安 (搜系统BUG/影像退步)": f"https://www.coolapk.com/search?q={keyword}"
    }

# --- 2. 核心：支持中文的 PDF 生成函数 ---
def create_chinese_pdf(text_content):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # 尝试加载上传到 GitHub 的字体
    font_name = "Helvetica" 
    font_path = "simhei.ttf" # 确保你上传的文件名是这个，全小写
    
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('MyChinese', font_path))
            font_name = 'MyChinese'
        except Exception as e:
            st.error(f"字体解析失败: {e}")
    else:
        st.error("⚠️ 报错：根目录找不到 simhei.ttf 文件！请检查 GitHub 上传是否成功。")

    c.setFont(font_name, 11)
    width, height = A4
    y = height - 60
    
    # PDF 绘制逻辑
    c.drawString(200, height - 30, "vivo x300u Public Sentiment Report") 
    
    for line in text_content.split('\n'):
        if y < 50:
            c.showPage()
            c.setFont(font_name, 11)
            y = height - 60
        
        # 简单清洗 Markdown 符号
        clean_line = line.replace('#', '').replace('*', '').replace('-', '•').strip()
        c.drawString(50, y, clean_line)
        y -= 20 # 行间距
        
    c.save()
    buffer.seek(0)
    return buffer

# --- 3. AI 分析引擎 (阿里云百炼) ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt_text = (
        "你是一个资深舆情专家。请对 vivo x300u 的用户真实评价进行多维度扫描。\n"
        "请严格按此结构输出报告：\n"
        "一、 用户声音概览 (占比、核心槽点)\n"
        "二、 典型声音描述 (最尖锐的原话)\n"
        "三、 问题反馈矩阵 (维度|关键问题|严重程度|趋势)\n"
        "四、 综合分析总结 (补救建议)\n\n"
        f"数据内容：\n{comments}"
    )
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.3
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"连接失败: {str(e)}"

# --- 4. 网页界面 ---
st.set_page_config(page_title="vivo x300u 舆情分析", page_icon="📱")
st.title("🛡️ vivo x300u 舆情分析专家系统")

with st.sidebar:
    st.header("🔑 API 配置")
    api_key = st.text_input("阿里云 API Key", type="password")
    model_name = st.text_input("模型代号", value="deepseek-v3")
    
    st.divider()
    target = "vivo x300u"
    st.markdown("### 第一步：人工取证")
    links = get_search_links(target)
    for name, link in links.items():
        st.link_button(f"🔗 前往 {name}", link)

st.subheader("📝 第二步：粘贴负面样本")
raw_input = st.text_area("请将搜集到的真实评价粘贴在此：", height=300)

if st.button("🚀 生成报告并导出 PDF", type="primary"):
    if not api_key or not raw_input:
        st.error("请完善配置信息。")
    else:
        with st.spinner("AI 正在解析数据并渲染中文 PDF..."):
            report = analyze_with_llm(raw_input, api_key, model_name)
            st.markdown("---")
            st.markdown(report)
            
            # 生成 PDF
            pdf_data = create_chinese_pdf(report)
            st.download_button(
                label="📥 下载 PDF 官方报告",
                data=pdf_data,
                file_name=f"{target}_舆情报告.pdf",
                mime="application/pdf"
            )
