# 📱 终端产品舆情专项研判系统 (Sentiment Analysis System)

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B)
![License](https://img.shields.io/badge/license-MIT-green)

一个专为硬件终端产品设计的轻量级、零依赖的舆情研判工具。通过结合人工精准取证与大语言模型（LLM）的深度推理能力，一键将全网零散的用户反馈转化为格式规范、高管审阅级别的高清 PDF 研判报告。

## ✨ 核心特性

- **🔗 全网素材一键直达**：内置小红书、微博、酷安、京东等主流社交与电商平台的专属搜索快捷键，一键跳转获取目标产品（如 vivo x300u）的最新真实评价。
- **🧠 灵活的 AI 引擎驱动**：支持自定义输入 API Key 与模型代号（默认接入 DeepSeek-V3 等主流大模型），通过零样本提示（Zero-shot Prompting）进行高精度语义穿透。
- **📊 商务级自动排版引擎**：摒弃了极易报错的云端 PDF 生成库，采用原生 HTML/CSS 引擎渲染，自动将非结构化数据转化为包含“问题反馈矩阵”的专业报表。
- **📥 无损 PDF 导出**：完美兼容 Mac/Windows 浏览器打印引擎，生成报告无乱码、无空白，100% 还原专业咨询公司的交付质感。
- **🔒 隐私与安全**：纯本地运行，API 密钥即用即抛，不记录、不上传任何用户粘贴的原始语料。

## 🚀 快速开始

### 1. 环境准备
确保你的计算机已安装 Python 3.8 或以上版本。克隆本项目后，在终端运行以下命令安装所需依赖：

```bash
git clone [https://github.com/你的用户名/你的仓库名.git](https://github.com/你的用户名/你的仓库名.git)
cd 你的仓库名
pip install -r requirements.txt
