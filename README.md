# 📱 Signal Studio｜终端产品全维度研判平台

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B)
![Multimodal](https://img.shields.io/badge/Multimodal-Text%20%2B%20Image-6C7CFF)
![Export](https://img.shields.io/badge/Export-HTML%20%7C%20Word%20%7C%20PDF%20%7C%20PPT-green)
![License](https://img.shields.io/badge/license-MIT-green)

> 一款面向产品、产品营销、市场与用户研究团队的轻量级产品情报工作台。  
> 输入产品关键词，快速跳转多平台取证；粘贴真实语料或上传图片证据后，自动生成可直接用于内部汇报的产品研判简报。

---

## 1. 项目定位

**Signal Studio｜终端产品全维度研判平台** 是一个围绕「产品舆情取证 → 语料整理 → AI 研判 → 汇报交付」设计的 Streamlit 工具。

它不再绑定单一产品或固定案例，而是支持用户自定义分析对象，例如：

- 手机 / 消费电子产品
- 汽车 / 智能座舱
- 家电 / IoT 产品
- 软件 / App
- 旅游 / 酒店产品
- 其他需要基于 UGC 做快速研判的产品

项目目标是把分散在小红书、微博、抖音、B 站、电商平台和搜索引擎中的用户反馈，转化为结构化、可汇报、可行动的产品策略简报。

---

## 2. 核心能力

### 🔎 便携搜索坞

输入产品关键词后，系统会自动生成多平台搜索入口，帮助快速完成取证。

支持搜索意图：

- 全网口碑
- 吐槽痛点
- 测评体验
- 争议翻车
- 购买建议
- 价格价值感
- 竞品对比

支持平台：

- 小红书
- 微博
- 知乎
- 微信文章
- 抖音
- B 站
- 快手
- 百度
- Google
- 必应
- 京东
- 什么值得买

---

### 🧠 单品深度研判

适用于分析某一款产品的真实用户反馈，包括：

- 用户主要关注点
- 正负面情绪分布
- 高频痛点与潜在风险
- 可放大的卖点和机会
- 产品侧 / 营销侧 / 取证侧建议
- 代表性用户原声
- 信息缺口

---

### ⚔️ 竞品对比攻防

支持将本品与竞品语料放在同一分析框架下进行对比，输出：

- 本品与竞品的核心差异
- 本品需要防守的风险点
- 本品可以主动进攻的机会点
- 传播上应强调和规避的内容
- 下一轮补充取证方向

---

### 🖼️ 图片证据分析

除文字语料外，平台支持上传图片作为分析证据，例如：

- 社媒评论截图
- 测评视频截图
- 电商评价截图
- 产品海报
- 线下物料图
- 表格或数据截图

系统会将图片与文字语料一起传入支持视觉能力的模型进行分析。

> 注意：图片分析需要选择支持视觉输入的模型，例如 `qwen-vl-plus`、`qwen-vl-max`、`Qwen/Qwen2.5-VL-72B-Instruct`、`GPT-4o`、`Gemini Flash` 等。普通文本模型只能处理文字语料。

---

### 📄 多格式报告导出

报告生成后支持多种交付格式：

- HTML：适合浏览器打开和转存 PDF
- Word：适合继续编辑和发送给团队
- PDF：适合正式归档和汇报
- PPT：适合快速生成汇报页
- Markdown：适合二次加工或放入文档系统

同时提供「老板版摘要」复制区，方便直接发微信、飞书或邮件。

---

## 3. 输出报告结构

当前报告更偏向老板可读的内部简报风格，强调少废话、高密度、可执行。

单品研判报告通常包含：

1. 老板先看
2. 用户反馈总览
3. 关键风险
4. 可放大的卖点 / 机会
5. 建议动作
6. 代表性用户原声
7. 信息缺口

竞品攻防报告通常包含：

1. 老板先看
2. 核心对比总览
3. 本品风险点
4. 本品机会点
5. 建议动作
6. 双方代表性用户原声
7. 信息缺口

---

## 4. 技术实现

| 模块 | 技术 |
|---|---|
| 前端界面 | Streamlit |
| API 调用 | Python Requests |
| 语料与报告清洗 | Regex / Markdown Parsing |
| 图片输入 | Base64 Image URL |
| Word 导出 | python-docx |
| PDF 导出 | ReportLab |
| PPT 导出 | python-pptx |
| HTML 报告 | HTML5 + CSS3 |

---

## 5. 支持的模型服务商

当前内置服务商预设：

- 阿里云 DashScope
- OpenRouter
- SiliconFlow

内置模型示例：

- `deepseek-v3`
- `qwen-max`
- `qwen-plus`
- `qwen-vl-plus`
- `qwen-vl-max`
- `deepseek/deepseek-chat-v3-0324:free`
- `openai/gpt-4o-mini`
- `google/gemini-2.5-flash-preview`
- `Qwen/Qwen2.5-VL-72B-Instruct`

> 文本研判可使用普通文本模型；图片证据分析请使用视觉模型。

---

## 6. 快速开始

### 6.1 克隆项目

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 6.2 安装依赖

```bash
pip install streamlit requests python-docx reportlab python-pptx
```

### 6.3 启动应用

```bash
streamlit run signal_studio_multimodal_export.py
```

### 6.4 使用流程

1. 在左侧栏输入 API Key
2. 选择服务商、接口地址和模型代号
3. 在主页面输入产品关键词
4. 使用便携搜索坞打开平台搜索入口
5. 粘贴真实语料，或上传图片证据
6. 生成单品研判报告或竞品攻防报告
7. 导出 HTML / Word / PDF / PPT / Markdown

---

## 7. 使用建议

为了让报告更适合直接汇报，建议输入语料时遵循以下原则：

- 尽量保留用户原话，不要提前润色
- 尽量覆盖多个平台，避免样本过于单一
- 正面、负面、中性反馈都可以放入
- 如果是截图，请确保文字清晰可读
- 不确定的信息不要自行补充，让模型在报告中标注「暂无提及」

---

## 8. 项目边界

本项目强调基于用户提供的真实语料和图片证据进行分析。模型不会自动抓取网页内容，也不会替用户验证外部信息真实性。

为了降低 AI 幻觉风险，Prompt 中设置了严格约束：

- 不编造参数
- 不编造销量
- 不编造发布时间
- 不编造官方动作
- 不编造用户评价
- 信息不足时输出「暂无提及」

---

## 9. 适用场景

- 产品上市前后舆情复盘
- 竞品发布会后快速攻防分析
- 产品经理 / 产品营销经理周报素材整理
- 社媒评论与测评内容归纳
- 老板汇报前的快速策略简报生成
- 实习生 / 分析师的产品情报工作台

---

## 10. License

MIT License
