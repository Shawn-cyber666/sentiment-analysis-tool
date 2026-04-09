import streamlit as st
import pandas as pd
import requests
import time

# ==========================================
# 1. 数据采集模块
# ==========================================
def fetch_appstore_reviews(app_id, limit=50):
    """抓取 App Store 评论 (公开接口，不分手机品牌)"""
    url = f"https://itunes.apple.com/rss/customerreviews/page=1/id={app_id}/sortby=mostrecent/json"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        entries = data.get('feed', {}).get('entry', [])
        reviews = []
        for entry in entries[1:limit+1]:
            reviews.append({
                "rating": int(entry.get('im:rating', {}).get('label', 0)),
                "text": entry.get('content', {}).get('label', '')
            })
        return pd.DataFrame(reviews)
    except:
        return pd.DataFrame()

# ==========================================
# 2. 核心 AI 分析模块 (适配阿里云百炼)
# ==========================================
def generate_ai_report(text_content, api_key, api_base, model_name):
    prompt = f"""
    你是一个资深舆情分析专家。请根据以下用户评论，严格按照格式输出报告。
    
    【待分析评论】：
    {text_content}
    
    【输出格式要求】：
    一、 用户声音概览
    (包含情绪占比、核心热议话题)
    二、 典型声音描述
    (提取代表性原话)
    三、 问题反馈矩阵
    (Markdown表格：维度 | 关键问题点 | 严重程度 | 舆论趋势)
    四、 综合分析总结
    (给出阶段性判断和改进建议)
    """
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    try:
        res = requests.post(f"{api_base}/chat/completions", headers=headers, json=payload, timeout=60)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
        else:
            return f"AI 分析失败，错误码：{res.status_code}\n错误信息：{res.text}"
    except Exception as e:
        return f"网络异常: {str(e)}"

# ==========================================
# 3. Streamlit 网页界面
# ==========================================
st.set_page_config(page_title="智能舆情分析工具", layout="wide")

st.title("🚀 智能舆情抓取与分析助手")
st.info("适配小米/安卓用户：支持 API 自动抓取 或 手动粘贴评论分析")

with st.sidebar:
    st.header("⚙️ 配置中心")
    api_key = st.text_input("1. 阿里云 API Key", type="password", help="填入你在阿里云百炼申请的 sk- 开头的 Key")
    api_base = st.text_input("2. API Base URL", value="https://dashscope.aliyuncs.com/compatible-mode/v1")
    model_name = st.text_input("3. 模型名称", value="deepseek-v3")
    
    st.divider()
    mode = st.radio("选择数据来源", ["自动抓取 (App Store)", "手动输入 (小米/社媒评论)"])
    
    if mode == "自动抓取 (App Store)":
        app_id = st.text_input("输入 App ID (微信: 414478124)", value="414478124")
    else:
        user_input = st.text_area("粘贴评论内容到这里 (每行一条)", placeholder="例如：这个App太好用了...\n但是物流有点慢...")

    start_btn = st.button("🔥 开始生成智能报告", type="primary")

# --- 执行逻辑 ---
if start_btn:
    if not api_key:
        st.error("请先填入 API Key！")
        st.stop()

    content_to_analyze = ""
    
    if mode == "自动抓取 (App Store)":
        with st.spinner("正在远程抓取数据..."):
            df = fetch_appstore_reviews(app_id)
            if not df.empty:
                st.success(f"抓取成功！获取到 {len(df)} 条评论。")
                content_to_analyze = "\n".join(df['text'].tolist())
            else:
                st.error("抓取失败，请检查 App ID 或稍后再试。")
    else:
        if user_input:
            content_to_analyze = user_input
            st.success("手动数据载入成功！")
        else:
            st.error("请输入评论内容！")

    if content_to_analyze:
        with st.spinner("AI 正在深度思考并生成报告..."):
            report = generate_ai_report(content_to_analyze, api_key, api_base, model_name)
            st.divider()
            st.markdown(report)
            
            # 提供下载
            st.download_button("💾 下载报告", data=report, file_name="舆情报告.md")
