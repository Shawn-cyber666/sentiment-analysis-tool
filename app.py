import streamlit as st
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import datetime

# ==========================================
# 1. 导航功能：生成搜索链接
# ==========================================
def get_search_links(keyword):
    return {
        "小红书 (侧重品控/审美)": f"https://www.xiaohongshu.com/search_result?keyword={keyword}%20%E5%90%8E%E6%82%94",
        "微博 (侧重热点/营销质疑)": f"https://s.weibo.com/weibo?q={keyword}%20%E7%BF%BB%E8%BD%A6",
        "京东 (侧重硬件故障/售后)": f"https://search.jd.com/Search?keyword={keyword}%20%E5%B7%AE%E8%AF%84",
        "酷安 (侧重算法/系统BUG)": f"https://www.coolapk.com/search?q={keyword}"
    }

# ==========================================
# 2. PDF 生成逻辑 (支持中文)
# ==========================================
def create_pdf(text_content):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # 注意：在云端部署时，需要上传一个中文字体文件并在下方引用
    # 暂时使用标准字体，部署时建议添加：pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttf'))
    c.setFont("Helvetica", 12) 
    
    # 简单的分页文本写入
    y_position = height - 50
    lines = text_content.split('\n')
    for line in lines:
        if y_position < 50:
            c.showPage()
            y_position = height - 50
        c.drawString(50, y_position, line)
        y_position -= 15
        
    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
# 3. AI 分析引擎 (阿里云百炼)
# ==========================================
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    你是一个资深舆情专家。请对以下人工收集的原始负面评论进行深度分析。
    
    【待分析内容】：
    {comments}
    
    【输出格式要求】：
    一、 用户声音概览
    1. 情绪占比 (列出 愤怒/失望、质疑、反感等比例及原因)
    2. 核心热议话题 (聚类分析)
    二、 典型声音描述 (提取最尖锐的3-5条原话)
    三、 问题反馈矩阵 (Markdown表格：维度 | 关键问题点 | 严重程度 | 舆论趋势)
    四、 综合分析总结 (1. 舆论阶段判断 2. 补救建议)
    """
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"AI 分析失败: {str(e)}"

# ==========================================
# 4. Streamlit UI 界面
# ==========================================
st.set_page_config(page_title="人机协作舆情分析", layout="wide")

st.title("🛡️ 手机舆情“专家级”分析系统")
st.markdown("---")

# 侧边栏配置
with st.sidebar:
    st.header("🔑 配置 API")
    api_key = st.text_input("阿里云 API Key", type="password")
    model_name = st.text_input("模型代号", value="deepseek-v3")
    
    st.header("🔍 调查对象")
    target = st.text_input("输入分析对象", value="小米14 Ultra")
    
    st.divider()
    st.markdown("### 第一步：人工取证")
    links = get_search_links(target)
    for name, url in links.items():
        st.link_button(f"🔗 进入{name}", url)

# 主界面
st.subheader("📝 第二步：粘贴负面样本")
raw_input = st.text_area("请在下方粘贴你在上述平台发现的负面评价、帖子内容或评论（不限格式）：", height=300)

col1, col2 = st.columns(2)
with col1:
    analyze_btn = st.button("🚀 生成智能分析报告", type="primary", use_container_width=True)

if analyze_btn:
    if not api_key or not raw_input:
        st.warning("⚠️ 请确保 API Key 已填且评论区不为空。")
    else:
        with st.spinner("AI 正在深度解析负面反馈..."):
            report_text = analyze_with_llm(raw_input, api_key, model_name)
            
            st.markdown("### 📊 生成的实时分析报告")
            st.markdown(report_text)
            
            # 生成 PDF 并提供下载
            pdf_data = create_pdf(report_text)
            st.download_button(
                label="📥 下载 PDF 格式报告",
                data=pdf_data,
                file_name=f"{target}_舆情报告_{datetime.date.today()}.pdf",
                mime="application/pdf"
            )

st.divider()
st.caption("提示：人工调查时，建议优先复制带有‘硬件故障’、‘品控’、‘算法退步’等关键词的深度评论。")
