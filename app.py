import streamlit as st
import requests
import datetime
import base64
import re

# --- 1. 调研工具箱 (支持动态传参搜竞品) ---
def get_search_links(keyword):
    return {
        "小红书 (搜痛点)": "https://www.xiaohongshu.com/search_result?keyword=" + keyword + "%20%E5%90%8E%E6%82%94",
        "微博 (搜翻车)": "https://s.weibo.com/weibo?q=" + keyword + "%20%E7%BF%BB%E8%BD%A6",
        "酷安 (搜发热/Bug)": "https://www.coolapk.com/search?q=" + keyword,
        "京东 (搜差评)": "https://search.jd.com/Search?keyword=" + keyword + "%20%E5%B7%AE%E8%AF%84"
    }

# --- 2. 核心大模型引擎 (支持单品 & 竞品双模式) ---
def analyze_with_llm(prompt, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    payload = {
        "model": model_name, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = res.json()['choices'][0]['message']['content']
        # 稳健的字符清洗，去除非必要 Markdown
        return re.sub(r'[*#\-\>]', '', content)
    except Exception as e:
        return "分析系统调用失败，请检查 API Key 或网络状态。"

# --- 3. 商务级 HTML 渲染引擎 (保持纯净与美学) ---
def generate_html_report(text_content, title, mode="single"):
    # vivo 蓝核心样式，新增 quote-box 用于高亮最重原声
    html_head = """<html><head><meta charset="utf-8"><style>
    body { font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #F4F6F9; padding: 40px; color: #2C3E50; line-height: 1.6; }
    .report-card { max-width: 850px; margin: 0 auto; background: #FFF; padding: 50px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.05); border-top: 6px solid #415FFF; }
    h1 { text-align: center; font-size: 24px; color: #111; margin-bottom: 5px; }
    .meta { text-align: center; color: #888; font-size: 13px; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid #EEE; }
    h2 { font-size: 18px; color: #415FFF; margin-top: 35px; border-left: 4px solid #415FFF; padding-left: 12px; }
    .quote-box { background: #FFF0F0; border-left: 4px solid #FF4B4B; padding: 15px 20px; margin: 15px 0; color: #D80000; font-weight: 500; border-radius: 0 6px 6px 0; }
    table { width: 100%; border-collapse: separate; border-spacing: 0; margin: 20px 0; border: 1px solid #EAEEF2; border-radius: 8px; overflow: hidden; font-size: 14px; }
    th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #EAEEF2; }
    th { background: #F8FAFC; color: #333; font-weight: bold; }
    tr:last-child td { border-bottom: none; }
    .footer { text-align: center; margin-top: 40px; font-size: 12px; color: #AAA; }
    </style></head><body><div class="report-card">"""
    
    html_title = "<h1>" + title + "</h1>"
    html_info = "<div class='meta'>内部机密 · 生成日期：" + str(datetime.date.today()) + "</div>"
    
    # 智能排版解析器
    lines = text_content.split('\n')
    body_html = ""
    in_table = False
    is_quote_section = False
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # 捕捉“原声直击”模块，自动套用警告样式
        if "原声直击" in line or "尖锐原声" in line:
            is_quote_section = True
            body_html += "<h2>" + line + "</h2>"
            continue
            
        if line.startswith(('一、', '二、', '三、', '四、', '五、')):
            is_quote_section = False # 离开原声模块
            body_html += "<h2>" + line + "</h2>"
            continue
            
        if "|" in line:
            if "---" in line: continue
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if not cells: continue
            row = "<tr>" + "".join(["<td>"+c+"</td>" for c in cells]) + "</tr>"
            if not in_table:
                body_html += "<table>" + row.replace("td>", "th>")
                in_table = True
            else:
                body_html += row
        else:
            if in_table:
                body_html += "</table>"
                in_table = False
            
            # 如果处于原声模块，则使用红色卡片渲染
            if is_quote_section:
                body_html += "<div class='quote-box'>\"" + line + "\"</div>"
            else:
                body_html += "<div style='margin-bottom: 8px;'>" + line + "</div>"
                
    if in_table: body_html += "</table>"
    html_footer = "<div class='footer'>本报告由产品线内参系统自动聚合，仅供决策参考。</div></div></body></html>"
    
    full_html = html_head + html_title + html_info + body_html + html_footer
    b64 = base64.b64encode(full_html.encode('utf-8')).decode()
    
    file_name = title.replace(" ", "_") + ".html"
    btn_color = "#415FFF" if mode == "single" else "#212529"
    
    link = '<a href="data:text/html;base64,' + b64 + '" download="' + file_name + '" '
    link += f'style="text-decoration:none; background:{btn_color}; color:white; padding:12px 28px; border-radius:6px; font-weight:bold; display:inline-block; box-shadow: 0 4px 10px rgba(0,0,0,0.15);"> '
    link += '📥 导出高清 PDF 内参报告</a>'
    return link

# --- 4. Streamlit 界面构建 ---
st.set_page_config(page_title="终端舆情研判平台", page_icon="📱", layout="wide")
st.title("📱 终端产品舆情专项研判系统")

with st.sidebar:
    st.header("⚙️ 引擎配置")
    api_key = st.text_input("API Key", type="password")
    model_name = st.text_input("模型代号", value="deepseek-v3")
    st.divider()
    # 核心升级：模式切换开关
    mode = st.radio("🛡️ 选择研判模式", ["单品深度研判 (本品)", "竞品对比攻防 (横向)"])
    st.divider()
    
    if mode == "单品深度研判 (本品)":
        target = st.text_input("快捷取证机型", value="vivo x300u")
        for name, url in get_search_links(target).items():
            st.link_button(name, url, use_container_width=True)
    else:
        st.caption("提示：在竞品模式下，请分别搜集双方机型的反馈以供对比。")

# --- 模式一：单品深度研判 ---
if mode == "单品深度研判 (本品)":
    st.subheader("📝 单品语料输入舱")
    user_input = st.text_area("请贴入原始用户评价：", height=250)
    
    if st.button("🚀 生成单品研判报告", type="primary"):
        if not api_key or len(user_input) < 10:
            st.error("⚠️ 请检查配置并输入足够的语料。")
        else:
            with st.spinner("正在提取核心痛点..."):
                prompt = (
                    "你是一名内部产品调研员。请根据评论撰写单品反馈总结。\n"
                    "要求大白话，严禁虚构，严禁使用 # 或 * 符号。禁止输出Markdown表格分隔符（如|---|）。\n"
                    "必须按以下四大结构输出：\n"
                    "一、 用户声音概览\n"
                    "二、 尖锐原声直击（挑出最能反映系统/硬件痛点的1-2句用户原话，直接写句子即可）\n"
                    "三、 问题反馈矩阵（必须按此格式输出表格：维度 | 关键问题 | 严重程度 | 趋势。每行一条）\n"
                    "四、 综合总结\n\n数据样本：\n" + user_input
                )
                report = analyze_with_llm(prompt, api_key, model_name)
                st.write(report)
                st.markdown(generate_html_report(report, "单品舆情研判内参", "single"), unsafe_allow_html=True)

# --- 模式二：竞品对比攻防 ---
else:
    st.subheader("⚔️ 竞品攻防输入舱")
    col1, col2 = st.columns(2)
    with col1:
        my_product = st.text_input("本品型号", value="vivo X200")
        my_input = st.text_area("贴入本品负面/核心评价：", height=200)
    with col2:
        comp_product = st.text_input("竞品型号", value="OPPO Find X8 / 华为 Mate")
        comp_input = st.text_area("贴入竞品负面/核心评价：", height=200)

    if st.button("⚡ 生成竞品对比报告", type="primary"):
        if not api_key or len(my_input) < 10 or len(comp_input) < 10:
            st.error("⚠️ 双方语料均需大于 10 个字符才能进行有效对比。")
        else:
            with st.spinner(f"正在建立 {my_product} 与 {comp_product} 的攻防对比模型..."):
                prompt = (
                    f"你是一名高级商业情报分析师。请横向对比【{my_product}】与【{comp_product}】的舆情态势。\n"
                    "要求大白话，专业但通俗，严禁虚构，严禁使用 # 或 * 符号。禁止输出Markdown表格分隔符（如|---|）。\n"
                    "必须按以下四大结构输出：\n"
                    "一、 双方舆情基本盘（对比两者的被吐槽重点差异）\n"
                    "二、 尖锐原声直击（分别列出本品和竞品被骂得最狠的1句原话，标明机型）\n"
                    "三、 竞品攻防矩阵（必须按此格式输出表格：对比维度 | {my_product}现状 | {comp_product}现状 | 攻防建议。每行一条）\n"
                    "四、 战术总结\n\n"
                    f"【{my_product} 数据】：\n" + my_input + "\n\n"
                    f"【{comp_product} 数据】：\n" + comp_input
                )
                report = analyze_with_llm(prompt, api_key, model_name)
                st.write(report)
                report_title = f"{my_product} vs {comp_product} 竞品攻防内参"
                st.markdown(generate_html_report(report, report_title, "compare"), unsafe_allow_html=True)
