import streamlit as st
import pandas as pd
import requests
import json
import time

# ==========================================
# 1. 核心职责说明 (功能概述)
# ==========================================
"""
目标：开发智能舆论抓取分析工具
核心功能：
- 模拟/接口数据采集（针对社媒负面反馈）
- 技能培训：展示从原始文本到结构化矩阵的转化
- 详尽文档：代码内含实现说明
"""

# ==========================================
# 2. 模拟高级采集模块 (Scraper Logic)
# ==========================================
def fetch_ugc_data(keyword):
    """
    模拟从社媒平台（小红书/微博）抓取的原始负面数据。
    在实际生产中，此处可替换为 Webhook 或特定的爬虫 API。
    """
    # 模拟抓取到的关于手机硬件和算法的真实负面声音
    mock_raw_data = [
        f"这代 {keyword} 的硬件品控真是绝了，背板边缘居然有明显突起，手感割裂。",
        f"用了几天 {keyword}，发现影像算法退步明显，长焦涂抹感太重，画面泛白。",
        f"{keyword} 的公关太敏感了，反馈个问题就被说是水军，营销痕迹太重。",
        "万元旗舰居然镜头卡口松动，做工还不如去年的旗舰。",
        "35mm 焦段就是个营销噱头，本质上还是算法暴力锐化，文字边缘描边感太强。"
    ]
    return mock_raw_data

# ==========================================
# 3. 智能分析层 (AI Analysis Engine)
# ==========================================
def run_llm_analysis(raw_texts, api_key, api_base, model_name):
    """
    核心逻辑：通过 LLM 深度提取负面矩阵并按要求格式化
    """
    # 拼接原始评论
    formatted_comments = "\n".join([f"评论{i+1}: {text}" for i, text in enumerate(raw_texts)])
    
    # 严格遵循用户给出的报告模版进行 Prompt 工程
    prompt = f"""
    你是一个资深智能硬件舆情分析专家。请根据以下用户评论，输出一份深度的手机舆情分析报告。
    你必须重点分析【负面评价】，并严格遵守以下格式要求：

    一、 用户声音概览
    1. 情绪占比 (格式：情绪类型 (百分比) 趋势符号：简述原因)
    2. 核心热议话题（新增聚类）

    二、 典型声音描述
    (提取3-4条最尖锐、最具代表性的用户原话)

    三、 问题反馈矩阵（动态更新）
    以 Markdown 表格输出，包含字段：维度、关键问题点、严重程度、舆论趋势

    四、 综合分析总结
    1. 舆论阶段判断
    2. 针对性建议（算法、品控、营销三个维度）

    待分析评论内容：
    {formatted_comments}
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "你是一个能够精准识别手机品控和算法问题的专家，擅长从杂乱评论中提取核心痛点。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1  # 降低随机性，保证报告逻辑严密
    }

    try:
        response = requests.post(f"{api_base}/chat/completions", headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"AI 引擎报告生成失败，请检查配置或网络。详情：{e}"

# ==========================================
# 4. 实现指引与文档 (Implementation Guide)
# ==========================================
def display_guide():
    with st.expander("📘 开发与部署指引 (必读)"):
        st.markdown("""
        ### 实现步骤：
        1. **数据源层**：本程序目前通过模拟函数生成数据。如需对接真实小红书/微博数据，建议使用 `Playwright` 编写自动化脚本。
        2. **API 接入**：由于你使用小米手机及阿里云 API，请在侧边栏正确填写 `sk-xxx`。
        3. **部署**：
            - 将代码提交至 GitHub。
            - 在 Streamlit Cloud 关联仓库。
            - 在云端环境变量中配置 API Key (可选)。
        ### 参数调整：
        - `temperature`: 调低（如 0.1）可使报告格式更稳定。
        - `model_name`: 阿里云百炼请使用 `deepseek-v3` 或 `qwen-max`。
        """)

# ==========================================
# 5. UI 展示层 (Streamlit Dashboard)
# ==========================================
st.set_page_config(page_title="智能舆情分析工具", layout="wide")

st.title("🛡️ 手机产品舆情智能扫描分析引擎")
display_guide()

with st.sidebar:
    st.header("⚙️ 系统配置")
    config_api_key = st.text_input("阿里云 API Key", type="password")
    config_model = st.text_input("模型代号 (Model Name)", value="deepseek-v3")
    config_url = st.text_input("API 接口地址", value="https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    st.divider()
    target_phone = st.text_input("分析目标 (例如：小米14, vivo X200)", value="某品牌旗舰手机")
    
    analyze_btn = st.button("🚀 生成一键分析报告", type="primary")

# 主执行逻辑
if analyze_btn:
    if not config_api_key:
        st.error("请输入 API Key 以启动 LLM 引擎。")
    else:
        # 步骤 1：获取数据
        with st.status("正在检索全网 UGC 数据...", expanded=True) as status:
            st.write("连接数据源接口...")
            raw_data = fetch_ugc_data(target_phone)
            time.sleep(1)
            st.write(f"已发现关于 {target_phone} 的 5 条典型负面样本。")
            
            # 步骤 2：AI 深度分析
            st.write("正在驱动 LLM 进行语义聚类与矩阵提取...")
            final_report = run_llm_analysis(raw_data, config_api_key, config_url, config_model)
            
            status.update(label="报告生成完毕！", state="complete", expanded=False)

        # 步骤 3：渲染报告
        st.divider()
        st.markdown(final_report)
        
        # 步骤 4：一键下载
        st.download_button(
            label="📥 点击下载分析报告 (.md)",
            data=final_report,
            file_name=f"{target_phone}_舆情报告.md",
            mime="text/markdown"
        )
