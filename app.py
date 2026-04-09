import streamlit as st
import pandas as pd
import requests
import json
import time

# ==========================================
# 1. 真实数据采集 (以苹果 App Store 真实 API 为例)
# ==========================================
def fetch_real_appstore_reviews(app_id, limit=50):
    """
    通过 Apple iTunes RSS 接口获取真实的 App 评论数据。
    """
    url = f"https://itunes.apple.com/rss/customerreviews/page=1/id={app_id}/sortby=mostrecent/json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        entries = data.get('feed', {}).get('entry', [])
        reviews = []
        # 跳过第一个元素，因为通常是App本身的元数据
        for entry in entries[1:limit+1]:
            reviews.append({
                "rating": int(entry.get('im:rating', {}).get('label', 0)),
                "title": entry.get('title', {}).get('label', ''),
                "text": entry.get('content', {}).get('label', '')
            })
        return pd.DataFrame(reviews)
    except Exception as e:
        st.error(f"数据抓取失败: {e}")
        return pd.DataFrame()

# ==========================================
# 2. 真实 AI 分析模块 (生成指定格式报告)
# ==========================================
def generate_custom_report(dataframe, api_key, api_base_url, model_name):
    """
    调用真实的大语言模型 API，按照指定格式生成分析报告。
    """
    # 筛选负面评价 (假设评分 <= 3 为负面)
    negative_df = dataframe[dataframe['rating'] <= 3]
    if negative_df.empty:
        return "没有抓取到足够的负面评价进行分析。"

    # 将负面评论拼接，限制长度防止 token 超出
    comments_text = "\n".join([f"- {row['title']}: {row['text']}" for index, row in negative_df.iterrows()])
    
    prompt = f"""
    你是一个资深的用户体验分析专家和公关专家。请分析以下来自用户的真实负面评论数据。
    请你必须严格按照以下四个模块的格式，输出一篇专业的舆情分析报告，语言要犀利、专业、切中要害。
    
    【参考格式要求如下】
    一、 用户声音概览
    1. 情绪占比 (请根据数据估算各项情绪的占比并列出)
    2. 核心热议话题 (请聚类出最核心的痛点)
    二、 典型声音描述 (提取并精简最具代表性的用户原话)
    三、 问题反馈矩阵 (以Markdown表格形式输出，包含：维度、关键问题点、严重程度、舆论趋势)
    四、 综合分析总结 (给出当前舆论阶段的判断，并给出至少3条具体的补救或改进建议)

    以下是抓取到的真实用户评论：
    {comments_text}
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "你是一个专业的数据分析与舆情监控助手。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3 # 较低的温度保证输出格式稳定
    }

    try:
        response = requests.post(f"{api_base_url}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"AI 分析失败，请检查 API Key 或网络配置。错误详情: {e}"


# ==========================================
# 3. 交互界面 (Streamlit UI)
# ==========================================
st.set_page_config(page_title="智能舆论抓取与分析", layout="wide")

st.title("📊 智能舆情分析工具 (真实数据版)")

with st.sidebar:
    st.header("1. 数据抓取设置")
    # 微信的AppID是 414478124, 淘宝是 387682726
    app_id = st.text_input("输入 App Store 的 App ID (如微信: 414478124)", "414478124") 
    fetch_limit = st.slider("抓取数量", 10, 100, 50)
    
    st.divider()
    st.header("2. AI 模型配置")
    st.markdown("填入兼容 OpenAI 格式的 API 凭证 (如 DeepSeek, Kimi 等)")
    api_base_url = st.text_input("API Base URL", "https://api.deepseek.com/v1")
    api_key = st.text_input("API Key", type="password")
    model_name = st.text_input("Model Name", "deepseek-chat")
    
    start_btn = st.button("一键抓取并生成报告", type="primary")

if start_btn:
    if not api_key:
        st.warning("⚠️ 请在侧边栏填入真实的 API Key 才能进行智能分析！")
        st.stop()

    # 抓取数据
    with st.spinner('正在从 App Store 抓取真实评价...'):
        df = fetch_real_appstore_reviews(app_id, fetch_limit)
        
    if not df.empty:
        st.success(f"成功抓取 {len(df)} 条真实评论！")
        with st.expander("查看原始数据 (重点关注低星评价)"):
            st.dataframe(df)
            
        # AI 分析
        with st.spinner('🤖 AI 正在深度阅读负面评价并生成定制报告...'):
            report_markdown = generate_custom_report(df, api_key, api_base_url, model_name)
            
        # 展示报告
        st.divider()
        st.subheader("📑 智能分析报告")
        st.markdown(report_markdown)
        
        # 下载报告功能
        st.download_button(
            label="⬇️ 一键下载报告 (Markdown格式)",
            data=report_markdown,
            file_name=f"舆情分析报告_{int(time.time())}.md",
            mime="text/markdown"
        )
