import streamlit as st
import requests
import datetime
import base64
import re

# --- 1. 调研入口 (找回来的按钮) ---
def get_search_links(keyword):
    return {
        "小红书 (搜涂抹/进灰)": "https://www.xiaohongshu.com/search_result?keyword=" + keyword + "%20%E5%90%8E%E6%82%94",
        "微博 (搜真实翻车)": "https://s.weibo.com/weibo?q=" + keyword + "%20%E7%BF%BB%E8%BD%A6",
        "酷安 (搜系统BUG)": "https://www.coolapk.com/search?q=" + keyword,
        "京东 (搜差评)": "https://search.jd.com/Search?keyword=" + keyword + "%20%E5%B7%AE%E8%AF%84"
    }

# --- 2. 实习生版分析逻辑 (接地气、大白话) ---
def analyze_with_llm(comments, api_key, model_name):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    
    prompt = (
        "你是一名在手机公司工作的实习生。请帮我把这些用户关于 vivo x300u 的评价整理成一份调研总结。\n"
        "要求：\n"
        "1. 说话直接一点，多用大白话，别用太专业的商业词汇。\n"
        "2. 禁止瞎编！别提什么增距镜之类的东西，只说大家都在吐槽的那些事。\n"
        "3. 不要写一堆高大上的建议，我只是个实习生，简单提点改进方向就行。\n\n"
        "报告必须包括这几个部分：\n"
        "一、 用户声音概览（简单说下大家现在情绪怎么样，都在聊什么）\n"
        "二、 问题反馈矩阵（列出大家最不满意的几个点，比如拍照、发热、品控等）\n"
        "三、 负面原句直击（选3-5条骂得最狠、最真实的原话，不用带特殊符号）\n"
        "四、 简单的小建议（作为实习生的个人看法）\n\n"
        "待整理数据：\n" + comments
    )
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = res.json()['choices'][0]['message']['content']
        # 彻底清洗 AI 习惯带的 * 和 # 符号，防止看着太假
        return re.sub(r'[*#\-\>]', '', content)
    except:
        return "分析系统出了点小问题，请检查你的 API Key 是否填对。"

# --- 3. 商务感十足但内容接地气的 HTML 模板 ---
def get_intern_report_link(text_content, target):
    # 使用 replace 方式注入数据，100% 避免大括号冲突导致的报错
    html_tpl = """
    <html><head><meta charset="utf-8">
    <style>
        body { font-family: 'PingFang SC', sans-serif; background: #f0f2f5; padding: 40px; color: #333; }
        .card { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); max-width: 800px; margin: auto; border-top: 6px solid #4a90e2; }
        .tag { background: #4a90e2; color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; display: inline-block; margin-bottom: 15px; }
        .m-title { font-size: 24px; font-weight: bold; color: #1a1a1a; margin-bottom: 5px; }
        .s-info { font-size: 13px; color: #888; margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 15px; }
        .body-text { white-space: pre-wrap; line-height: 1.8; font-size: 15px; color: #444; }
        .footer { text-align: center; margin-top: 30px; font-size: 12px; color: #aaa; }
    </style>
    </head><body>
    <div class="card">
        <div class="tag">实习生调研笔记</div>
        <div class="m-title">关于 __TARGET__ 的用户真实反馈总结</div>
        <div class="s-info">汇报人：实习生 | 整理时间：__DATE__</div>
        <div class="body-text">__CONTENT__</div>
        <div class="footer">注：本内容由 AI 辅助整理自网络真实评价</div>
    </div>
    </body></html>
    """
    
    full_html = html_tpl.replace("__TARGET__", target)
    full_html = full_html.replace("__DATE__", str(datetime.date.today()))
    full_html = full_html.replace("__CONTENT__", text_content)
    
    b64 = base64.b64encode(full_html.encode('utf-8')).decode()
    
    btn = '<a href="data:text/html;base64,' + b64 + '" download="' + target + '_调研笔记.html" '
    btn += 'style="text-decoration:none; background-color:#4a90e2; color:white; padding:12px 25px; border-radius:5px; font-weight:bold; display:inline-block; box-shadow: 0 2px 8px rgba(74,144,226,0.3);">'
    btn += '📥 点击下载 (去浏览器打印 PDF)</a>'
    return btn

# --- 4. Streamlit 页面 ---
st.set_page_config(page_title="实习生调研助手")
st.title("📋 vivo x300u 用户评价整理工具")

with st.sidebar:
    st.header("⚙️ 设置")
    api_key = st.text_input("填入你的 API Key", type="password")
    model_name = st.text_input("模型选择", value="deepseek-v3")
    st.divider()
    st.markdown("### 第一步：找找素材")
    target = "vivo x300u"
    links = get_search_links(target)
    for name, url in links.items():
        st.link_button(name, url)

st.subheader("📝 第二步：把搜集到的评论粘进来")
user_input = st.text_area("把那些吐槽的原话粘贴在这里：", height=300, placeholder="比如：镜头进灰、拍照涂抹严重等...")

if st.button("🚀 开始整理报告", type="primary"):
    if not api_key or len(user_input) < 10:
        st.error("别忘了填 API Key 或者粘贴评论内容。")
    else:
        with st.spinner("正在帮你整理成接地气的总结..."):
            report = analyze_with_llm(user_input, api_key, model_name)
            st.markdown("---")
            # 预览效果
            st.write(report)
            
            st.divider()
            # 导出按钮
            st.markdown(get_intern_report_link(report, target), unsafe_allow_html=True)
            st.caption("提示：下载后打开网页文件，按 Command+P 选“另存为 PDF”就可以发给别人看啦。")
