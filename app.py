import streamlit as st
import requests
import datetime
import base64
import re

# --- 1. 调研素材入口 ---
def get_search_links(keyword):
    return {
        "小红书 (看具体槽点)": "https://www.xiaohongshu.com/search_result?keyword=" + keyword + "%20%E5%90%8E%E6%82%94",
        "微博 (看实时反馈)": "https://s.weibo.com/weibo?q=" + keyword + "%20%E7%BF%BB%E8%BD%A6",
        "酷安 (看硬件Bug)": "https://www.coolapk.com/search?q=" + keyword,
        "京东 (看售后差评)": "https://search.jd.com/Search?keyword=" + keyword + "%20%E5%B7%AE%E8%AF%84"
    }

# --- 2. 深度调研逻辑 (说人话 + 严谨格式) ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    
    prompt = (
        "你是一名专业调研员。请根据 vivo x300u 用户评论撰写一份简单的调研总结。\n"
        "要求：\n"
        "1. 用大白话写，别整虚的，禁止瞎编，禁止使用 # 或 * 符号。\n"
        "2. 结构必须包含：一、用户声音概览；二、负面原句摘录；三、问题反馈矩阵（表格）；四、简单总结。\n"
        "3. 表格请严格按：维度 | 关键问题 | 严重程度 | 趋势 这种格式输出，每行一条。\n\n"
        "数据样本：\n" + comments
    )
    
    payload = {
        "model": model_name, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = res.json()['choices'][0]['message']['content']
        return re.sub(r'[*#\-\>]', '', content)
    except:
        return "分析系统调用失败，请检查配置。"

# --- 3. 紧凑版 HTML 模板 (解决空白问题) ---
def get_compact_report_link(text_content, target):
    # 样式中强制设定表格 margin 为 0，并优化间距
    html_tpl = """
    <html><head><meta charset="utf-8">
    <style>
        body { font-family: sans-serif; padding: 30px; color: #333; line-height: 1.5; background: #fff; }
        .report-wrap { max-width: 800px; margin: auto; border: 1px solid #ccc; padding: 40px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
        h2 { border-bottom: 2px solid #444; padding-bottom: 5px; margin: 20px 0 10px 0; font-size: 18px; }
        .info { color: #888; font-size: 12px; margin-bottom: 20px; text-align: center; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 14px; }
        th, td { border: 1px solid #bbb; padding: 8px; text-align: left; }
        th { background: #f2f2f2; }
        .content-area { font-size: 15px; }
    </style>
    </head><body>
    <div class="report-wrap">
        <div style="font-size: 22px; font-weight: bold; text-align: center;">__TARGET__ 用户反馈调研内参</div>
        <div class="info">生成日期：__DATE__ | 内部参考</div>
        <div class="content-area">__CONTENT__</div>
    </div>
    </body></html>
    """
    
    # 核心修复：精准转换表格并剔除多余换行
    lines = text_content.split('\n')
    formatted_html = ""
    in_table = False
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        if "|" in line:
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if not cells: continue
            
            row_html = "<tr>" + "".join(["<td>"+c+"</td>" for c in cells]) + "</tr>"
            if not in_table:
                formatted_html += "<table><thead>" + row_html.replace("td>", "th>") + "</thead><tbody>"
                in_table = True
            else:
                formatted_html += row_html
        else:
            if in_table:
                formatted_html += "</tbody></table>"
                in_table = False
            # 对于标题部分特殊加粗处理
            if line.startswith(('一、', '二、', '三、', '四、')):
                formatted_html += "<h2>" + line + "</h2>"
            else:
                formatted_html += "<div>" + line + "</div>"
    
    if in_table: formatted_html += "
