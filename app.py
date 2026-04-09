import streamlit as st
import requests
import datetime
import base64
import re

# --- 1. 调研工具入口 ---
def get_search_links(keyword):
    return {
        "小红书 (搜深度差评)": f"https://www.xiaohongshu.com/search_result?keyword={keyword}%20%E5%90%8E%E6%82%94",
        "微博 (搜实时翻车)": f"https://s.weibo.com/weibo?q={keyword}%20%E7%BF%BB%E8%BD%A6",
        "酷安 (搜硬件Bug)": f"https://www.coolapk.com/search?q={keyword}",
        "京东 (搜售后追评)": f"https://search.jd.com/Search?keyword={keyword}%20%E5%B7%AE%E8%AF%84"
    }

# --- 2. 专家级深度分析引擎 ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    任务：你是一名拥有15年资历的手机行业高级分析师，负责撰写 vivo x300u 的【高层管理内参】。
    
    严苛要求：
    1. 彻底去AI化：严禁使用任何 Markdown 符号（如 *, #, -, >）。严禁使用“总而言之”、“综上所述”等口水词。
    2. 深度穿透：不要停留在“进灰”、“涂抹”表面。请分析这些问题如何动摇了 vivo 的高端心智，以及在供应链管理上的具体缺失。
    3. 语言风格：专业、冷峻、逻辑严密，直接输出纯文字段落。

    必须包含以下四个维度：
    一、 舆情风险能级评估：判断当前不满情绪对 vivo 高端系列溢价能力的长期损害。
    二、 核心痛点根源溯源：从光学模组封装工艺、底层影像算法逻辑等角度深挖原因。
    三、 典型用户心理画像：还原高端机用户在面对“进灰”等低级品控问题时的真实心理落差。
    四、 战略级对策建议：给出技术迭代、供应链考核及品牌公关的闭环方案。

    待研判样本：
    {comments}
    """
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        raw_text = res.json()['choices'][0]['message']['content']
        # 强制清洗所有 AI 符号
        clean_text = re.sub(r'[*#\-\>]', '', raw_text)
        return clean_text
    except Exception as e:
        return f"深度研判系统调用失败: {str(e)}"

# --- 3. 商务级 HTML 报告模板 ---
def get_professional_html(text_content, target):
    # 注意：CSS 中的 { } 必须写成 {{ }} 才能在 f-string 中正常运行
    html_template = f"""
    <html>
    <head><meta charset="utf-8">
    <style>
        body {{ font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif; line-height: 1.8; color: #1a1a1a; max-width: 900px; margin: 40px auto; padding: 20px; }}
        .header {{ border-bottom: 4px solid #1a3a5f; margin-bottom: 30px; padding-bottom: 10px; text-align: center; }}
        .report-title {{ font-size: 26px; font-weight: bold; color: #1a3a5f; }}
        .meta-info {{ font-size: 14px; color: #666; margin-top: 10px; }}
        .section {{ margin-top: 35px; }}
        .section-h {{ font-size: 20px; font-weight: bold; color: #1a3a5f; border-left: 6px solid #1a3a5f; padding-left: 15px; margin-bottom: 15px; background: #f8f9fa; padding-top: 5px; padding-bottom: 5px; }}
        .text-body {{ font-size: 16px; text-align: justify; white-space: pre-wrap; }}
        .confidential {{ text-align: right; color: #d9534f; font-weight: bold; font-size: 12px; text-transform: uppercase; }}
    </style>
    </head>
    <body>
        <div class="confidential">INTERNAL USE ONLY - CONFIDENTIAL</div>
        <div class="header">
            <div class="report-title">{target} 系列用户核心负面反馈深度研判内参</div>
            <div class="meta-info">报告类别：高端机舆情专项 | 生成时间：{datetime.date.today()}</div>
        </div>
        <div class="text-body">{text_content}</div>
        <div style="margin-top: 60px; text-align: center; font-size: 12px; color: #999;">本分析严格基于所提供的真实样本进行逻辑建模，不代表平台立场。</div>
    </body>
    </html>
    """
    b64 = base64.b64encode(html_template.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{target}_调研内参.html" style="text-decoration:none; background-color:#1a3a5f; color:white; padding:15px 30px; border-radius:4px; font-weight:bold; display:inline-block;">📥 导出高管审阅格式 (专业PDF预览)</a>'

# --- 4. Streamlit 网页前端 ---
st.set_page_config(page_title="手机高端舆情研判", layout="wide")
st.markdown("<style>.main {background-color: #f5f7f9;}</style>", unsafe_allow_html=True)

st.title("💼 手机品牌高端化舆情研判平台
