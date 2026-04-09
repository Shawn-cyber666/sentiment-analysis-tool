import streamlit as st
import requests
import datetime
import base64
import re

# --- 1. 调研入口 ---
def get_search_links(keyword):
    return {
        "小红书 (深度差评)": f"https://www.xiaohongshu.com/search_result?keyword={keyword}%20%E5%90%8E%E6%82%94",
        "微博 (实时舆论动态)": f"https://s.weibo.com/weibo?q={keyword}%20%E7%BF%BB%E8%BD%A6",
        "酷安 (极客/硬件Bug)": f"https://www.coolapk.com/search?q={keyword}",
        "京东 (真实售后反馈)": f"https://search.jd.com/Search?keyword={keyword}%20%E5%B7%AE%E8%AF%84"
    }

# --- 2. 深度分析指令 (去AI化) ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    你是一名拥有10年经验的智能硬件舆情内参专家。请针对提供的 vivo x300u 用户评价撰写一份【高层决策内参】。
    
    要求：
    1. 语气专业、冷峻、务实。严禁使用“总而言之”、“综上所述”等AI常用词汇。
    2. 严禁出现任何 Markdown 符号（如 #, *, -, >），请直接用序号或标题段落表达。
    3. 深度要求：不仅要分析表面槽点，要分析这反映了品牌在“高端化进程”或“品控体系”中的什么系统性风险。
    
    报告结构必须包含：
    一、 舆情态势研判（分析当前不满情绪处于哪个爆发阶段，对品牌资产的影响程度）
    二、 核心痛点穿透（从硬件设计瓶颈、软件算法逻辑、售后话术三个层面进行深度复盘）
    三、 典型用户声音还原（选取最具代表性的原话，并附带分析其背后的心理预期落差）
    四、 战略性改进建议（提供可落地的技术路线优化建议及公关对策）
    
    【待分析原始数据】：
    {comments}
    """
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = res.json()['choices'][0]['message']['content']
        # 二次过滤：彻底清除可能残留的符号
        content = re.sub(r'[*#\-\>]', '', content)
        return content
    except Exception as e:
        return f"分析出错: {str(e)}"

# --- 3. 模拟专业公文的 HTML 导出 ---
def get_html_download_link(text_content, target):
    html_content = f"""
    <html>
    <head><meta charset="utf-8">
    <style>
        body {{ font-family: "PingFang SC", "Microsoft YaHei", sans-serif; line-height: 1.8; padding: 50px; color: #2c3e50; max-width: 850px; margin: auto; }}
        .header {{ text-align: center; border-bottom: 3px double #333; margin-bottom: 30px; padding-bottom: 10px; }}
        .title {{ font-size: 28px; font-weight: bold; letter-spacing: 2px; }}
        .meta {{ color: #7f8c8d; font-size: 14px; margin-top: 10px; }}
        .section-title {{ font-size: 20px; font-weight: bold; background: #f2f2f2; padding: 10px 15px; margin-top: 30px; border-left: 5px solid #2c3e50; }}
        .content {{ font-size: 16px; margin: 15px 0; text-align: justify; }}
        .footer {{ margin-top: 50px; font-size: 12px; color: #bdc3c7; text-align: center; border-top: 1px solid #eee; padding-top: 20px; }}
    </style>
    </head>
    <body>
        <div class="header">
            <div class="title">关于 {target} 系列用户负面反馈的专项调研报告</div>
            <div class="meta">报告属性：高层决策内参 | 生成日期：{datetime.date.today()}</div>
        </div>
        <div class="content">{text
