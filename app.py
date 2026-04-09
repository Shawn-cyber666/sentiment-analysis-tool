import streamlit as st
import requests
import datetime
import base64
import re

# --- 1. 调研工具箱 ---
def get_search_links(keyword):
    return {
        "小红书 (搜涂抹/进灰)": "https://www.xiaohongshu.com/search_result?keyword=" + keyword + "%20%E5%90%8E%E6%82%94",
        "微博 (搜真实翻车)": "https://s.weibo.com/weibo?q=" + keyword + "%20%E7%BF%BB%E8%BD%A6",
        "酷安 (搜系统BUG)": "https://www.coolapk.com/search?q=" + keyword,
        "京东 (搜差评追评)": "https://search.jd.com/Search?keyword=" + keyword + "%20%E5%B7%AE%E8%AF%84"
    }

# --- 2. 纯粹版分析逻辑 (参考模板模块) ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    
    # 指令：强制生成包含表格结构的纯净内容
    prompt = (
        "你是一名专业调研员。请根据提供的评论内容撰写 vivo x300u 调研报告。\n"
        "要求：\n"
        "1. 说话大白话，禁止瞎编，禁止使用 # 或 * 等符号。\n"
        "2. 结构必须严格遵守：一、用户声音概览；二、典型声音描述；三、问题反馈矩阵（表格形式）；四、综合分析总结。\n"
        "3. 在‘问题反馈矩阵’部分，请按【维度 | 关键问题点 | 严重程度 | 舆论趋势】四个列生成表格。\n\n"
        "待处理评论：\n" + comments
    )
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = res.json()['choices'][0]['message']['content']
        # 清洗掉 AI 喜欢乱加的 Markdown 符号
        return re.sub(r'[*#\-\>]', '', content)
    except:
        return "分析调用失败，请检查配置。"

# --- 3. 模板化 HTML 渲染 (支持表格) ---
def get_final_report_link(text_content, target):
    # 使用表格样式优化模板
    html_tpl = """
    <html><head><meta charset="utf-8">
    <style>
        body { font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; padding: 40px; color: #333; line-height: 1.6; background: #fff; }
        .container { max-width: 850px; margin: auto; border: 1px solid #ddd; padding: 50px; box-shadow: 0 0 10px rgba(0,0,0,0.05); }
        h2 { border-bottom: 2px solid #333; padding-bottom: 5px; margin-top: 30px; font-size: 20px; }
        .meta { color: #888; font-size: 13px; margin-bottom: 30px; }
        pre { white-space: pre-wrap; font-family: inherit; font-size: 15px; color: #444; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; }
        th { background: #f8f8f8; border: 1px solid #ccc; padding: 10px; text-align: left; }
        td { border: 1px solid #ccc; padding: 10px; }
        .footer { text-align: center; margin-top: 50px; font-size: 12px; color: #aaa; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
    </head><body>
    <div class="container">
        <div style="font-size: 24px; font-weight: bold; text-align: center;">__TARGET__ 用户负面反馈调研报告</div>
        <div class="meta" style="text-align: center;">生成时间：__DATE__ | 报告属性：内部参考</div>
        <div class="content">__CONTENT__</div>
        <div class="footer">本报告严格基于用户真实评论样本整理生成</div>
    </div>
    </body></html>
    """
    
    # 格式化处理：将 AI 返回的模拟表格文字转换成真正的 HTML 表格
    formatted_content = text_content.replace('\n', '<br>')
    # 简单的正则替换，如果 AI 输出包含 | 符号，尝试转换成 HTML 表格
    if "|" in formatted_content:
        lines = formatted_content.split('<br>')
        new_lines = []
        in_table = False
        for line in lines:
            if "|" in line:
                cells = line.split('|')
                row_html = "<tr>" + "".join(["<td>"+c.strip()+"</td>" for c in cells if c.strip()]) + "</tr>"
                if not in_table:
                    new_lines.append("<table>" + row_html)
                    in_table = True
                else:
                    new_lines.append(row_html)
            else:
                if in_table:
                    new_lines.append("</table>")
                    in_table = False
                new_lines.append(line)
        formatted_content = "<br>".join(new_lines)

    full_html = html_tpl.replace("__TARGET__", target).replace("__DATE__", str(datetime.date.today())).replace("__CONTENT__", formatted_content)
    b64 = base64.b64encode(full_html.encode('utf-8')).decode()
    
    btn = '<a href="data:text/html;base64,' + b64 + '" download="' + target + '_调研报告.html" '
    btn += 'style="text-decoration:none; background-color:#333; color:white; padding:12px 25px; border-radius:4px; font-weight:bold; display:inline-block;">'
    btn += '📥 下载正式版调研报告 (PDF预览)</a>'
    return btn

# --- 4. Streamlit 页面 ---
st.set_page_config(page_title="舆情调研助手", layout="wide")
st.title("📱 vivo x300u 用户评价调研系统")

with st.sidebar:
    st.header("⚙️ 配置")
    api_key = st.text_input("填入 API Key", type="password")
    model_name = st.text_input("模型代号", value="deepseek-v3")
    st.divider()
    st.subheader("第一步：素材搜集")
    target = "vivo x300u"
    links = get_search_links(target)
    for name, url in links.items():
        st.link_button(name, url)

st.subheader("📝 第二步：粘贴真实评价")
user_input = st.text_area("请把搜集到的评论原封不动地粘在这里：", height=350)

if st.button("🚀 生成调研报告", type="primary"):
    if not api_key or len(user_input) < 10:
        st.error("请确保填写了 API Key 且输入了足够的分析样本。")
    else:
        with st.spinner("系统正在按照模板整理数据..."):
            report = analyze_with_llm(user_input, api_key, model_name)
            st.markdown("---")
            st.markdown(report)
            
            st.divider()
            st.markdown(get_final_report_link(report, target), unsafe_allow_html=True)
            st.caption("提示：下载后用浏览器打开，按 Command+P 选择“另存为 PDF”即可。")
