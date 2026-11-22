# 计算机视觉经典模型教程 · CV Tutorial

> 从像素到视觉理解：28 章中文教程，覆盖图像处理、传统特征、神经网络、主干架构、检测、分割和视觉基础模型。

**在线阅读：** https://1998x-stack.github.io/CV-tutorial/ （以 GitHub Pages 实际发布状态为准）
**直接打开站点源码：** [docs/index.html](docs/index.html) · [课程清单](docs/courses.json) · [写作规范](AGENTS.md)

## 学习路径

| 阶段 | 章节 | 核心问题 |
| --- | --- | --- |
| 视觉基础 | 01–08 | 机器如何表示像素、构造特征并训练识别器？ |
| 主干网络 | 09–12 | CNN 到 ViT 的架构选择源于什么瓶颈？ |
| 训练评估 | 13–14 | 如何设计可比较、可复现的实验？ |
| 目标检测 | 15–18 | 如何同时决定「是什么」与「在哪里」？ |
| 图像分割 | 19–22 | 如何将预测从框推进到像素级？ |
| 工程实践 | 23–25 | 如何提升鲁棒性、迁移能力与部署效率？ |
| 前沿实战 | 26–28 | 如何理解预训练、多模态与完整工程系统？ |

## 目录组织

```text
CV-tutorial/
├── docs/                       # GitHub Pages 站点根目录（无需 Node 构建）
│   ├── index.html              # 课程门户：静态章节卡片 + 可选搜索
│   ├── courses.json            # 28 章单一课程清单
│   ├── chapters/               # 01–28 章；01–05 已按深度教程范式精修
│   └── assets/
│       ├── css/site.css        # 站点级设计系统
│       ├── css/article.css     # 长文版式、MathML、移动端和打印
│       └── svg/                # 按知识问题组织的原创独立 SVG
├── scripts/check_site.py       # 静态链接 / SVG / 章节一致性门禁
├── .github/workflows/          # QA 与 GitHub Pages 部署
├── pdfs/                       # 历史论文资料（不参与本次迁移）
├── AGENTS.md                   # 事实核验和长期维护规范
├── 01.html ... 28.html         # 旧路径兼容跳转
└── index.html                  # 旧首页兼容跳转
```

## 本地预览

无需安装前端依赖。在仓库根目录运行：

```bash
python3 -m http.server 8000
# 浏览 http://localhost:8000/docs/
python3 scripts/check_site.py
```

避免直接双击 `docs/index.html` 判断所有资源行为：本地文件 URL 与网站 HTTP 路径并不完全等价。

## 协作约定

- 保留 01–28 章节编号和旧链接兼容入口；更新正文以 `docs/chapters/` 为准。
- 一篇网页应该无需读其它章节也能理解：背景、定义、机制、数学、代码、实验与局限完整闭环。
- 不能编造历史指标、论文结论、模型结构、图像来源或 QA 结果。技术主张在文末注明来源。
- 本项目写作实践参照 [Olah-style-posts](https://github.com/1998x-stack/Olah-style-posts) 的 `olah-style-paper-posts` skill，图示和正文独立原创。
- 贡献者与自动化代理先阅读 [AGENTS.md](AGENTS.md)；PR 请同时执行静态检查、移动端与键盘可访问性验收。

## 许可证与论文资料

代码与教程版权以仓库现有许可证和各文件来源为准。仓库没有显式总 LICENSE 时，**不应推定其为开源许可**；`pdfs/` 中的论文保留原作者版权，不因本仓库整理而改变授权范围。
