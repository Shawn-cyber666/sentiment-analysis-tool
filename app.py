import streamlit as st
import requests
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import datetime

# --- 1. 导航功能：生成搜索链接 ---
def get_search_links(keyword):
    return {
        "小红书 (搜品控/黑料)": f"https://www.xiaohongshu.com/search_result?keyword={keyword}%20%E9%99%B7%E9%B1%BC",
        "微博 (搜实时吐槽)": f"https://s.weibo.com/weibo?q={keyword}%20%E7%BF%BB%E8%BD%A6",
        "京东 (搜追评/差评)": f"https://search.jd.com/Search?keyword={keyword}",
        "酷安 (搜数码硬核Bug)": f"https://www.coolapk.com/search?q={keyword}"
    }

# --- 2. PDF 生成逻辑 (由于云端默认无中文字体，此处做了容错处理) ---
def create_pdf(text_content):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 10) # 默认字体，如需中文请按下方提示操作
    
    y_position = height - 50
    # 简单的自动换行逻辑
    for line in text_content.split('\n'):
        if y_position < 50:
            c.showPage()
            y_position = height - 50
        # 针对报告格式做简单处理
        c.drawString(50, y_position, line.strip())
        y_position -= 15
        
    c.save()
    buffer.seek(0)
    return buffer

# --- 3. AI 分析引擎 (适配阿里云百炼) ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    你是一个手机行业舆情专家。请根据以下人工收集的评价，输出专业分析报告。
    要求格式：
    一、 用户声音概览 (占比、核心槽点)
    二、 典型声音描述 (原话)
    三、 问题反馈矩阵 (维度|关键问题|严重程度|趋势)
    四、 综合分析总结 (阶段判断、改进建议)
    
    待分析内容：
    {comments}
    """
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
        else:
            return f"AI 响应错误 ({res.status_code}): {res.text}"
    except Exception as e:
        return f"连接失败: {str(e)}"

# --- 4. 网页界面 ---
st.set_page_config(page_title="手机舆情专家分析系统", layout="wide")

st.title("🛡️ 手机舆情“人机协作”分析工具")
st.markdown("> **操作流程：** 点击侧边栏链接去搜集评论 -> 粘贴到中间框 -> 点击分析并生成PDF")

with st.sidebar:
    st.header("🔑 API 配置")
    api_key = st.text_input("阿里云 API Key", type="password")
    model_name = st.text_input("模型代号", value="deepseek-v3")
    
    st.header("🔍 目标产品")
    target = st.text_input("手机型号", value="小米14 Ultra")
    
    st.divider()
    st.markdown("### 第一步：人工取证")
    links = get_search_links(target)
    for name, url in links.items():
        st.link_button(f"🔗 前往 {name}", url)

st.subheader("📝 第二步：粘贴收集到的负面样本")
raw_input = st.text_area("请把你在社交平台看到的不满评价、帖子内容全部粘贴在这里（支持多行）：", height=350)

if st.button("🚀 生成智能分析报告", type="primary"):
    if not api_key or not raw_input:
        st.error("请确保填写了 API Key 和 评论内容。")
    else:
        with st.spinner("AI 专家正在深度解析中..."):
            report_text = analyze_with_llm(raw_input, api_key, model_name)
            st.markdown("---")
            st.markdown(report_text)
            
            # 生成 PDF
            pdf_data = create_pdf(report_text)
            st.download_button(
                label="📥 下载 PDF 格式分析报告",
                data=pdf_data,
                file_name=f"{target}_舆情报告_{datetime.date.today()}.pdf",
                mime="application/pdf"
            )

st.divider()
st.caption("提示：如需在 PDF 中完美显示中文，请在 GitHub 中上传 simsun.ttf 字体并在代码中配置。")
