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
| 目标检测 | 15–19 | 如何同时决定「是什么」与「在哪里」？ |
| 图像分割 | 20–22 | 如何将预测从框推进到像素级？ |
| 工程实践 | 23–25 | 如何提升鲁棒性、迁移能力与部署效率？ |
| 前沿实战 | 26–28 | 如何理解预训练、多模态与完整工程系统？ |

## 目录组织

```text
CV-tutorial/
├── docs/                       # GitHub Pages 站点根目录（无需 Node 构建）
│   ├── index.html              # 课程门户：静态章节卡片 + 可选搜索
│   ├── courses.json            # 28 章单一课程清单
│   ├── chapters/               # 01–28 章；01–20 已按深度教程范式精修
│   └── assets/
│       ├── css/site.css        # 站点级设计系统
│       ├── css/article.css     # 长文版式、MathML、移动端和打印
│       └── svg/                # 按知识问题组织的原创独立 SVG
├── scripts/check_site.py       # 静态链接 / SVG / 章节一致性门禁
├── scripts/check_browser.py    # Chromium 1440/768/390/360 响应式浏览器验收
├── tests/test_cv_examples.py   # 06–20 章教学代码断言
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
# 可选：需要 PyTorch 才运行以下单元测试
python3 tests/test_cv_examples.py
# 浏览器 QA 需 playwright 和 chromium
python3 -m pip install playwright
python3 -m playwright install chromium
python3 scripts/check_browser.py
```

避免直接双击 `docs/index.html` 判断所有资源行为：本地文件 URL 与网站 HTTP 路径并不完全等价。

## 批次记录

| 批次 | 内容 | 图解 | 状态 |
| --- | --- | --- | --- |
| 01–05 | 像素、滤波、传统特征、反向传播与 CNN 基础 | 10 张 | 已深化 |
| 06–10 | PyTorch、分类协议、AlexNet、VGG、ResNet | 16 张 | 已深化 |
| 11–15 | ViT、ConvNeXt、训练策略、评估选型、检测基础 | 17 张 | 已深化 |
| 16–20 | R-CNN、Fast/Faster R-CNN、YOLO、SSD、RetinaNet、DETR、分割基础与 U-Net | 21 张 | 已深化 |
| 21–28 | Mask R-CNN、分割前沿、部署与基础模型 | 原课程内容保留 | 等待逐篇复审 |

16–20 章进一步梳理 R-CNN→Fast R-CNN→Faster R-CNN 的共享计算演进，严格区分 RoI Pooling 与后来的 RoIAlign、原始 Faster R-CNN 与 FPN；单阶段与集合预测部分分开说明 YOLOv1 的 7×7×30 输出、SSD300 的 8,732 个 default boxes、RetinaNet 的 Focal Loss 与 DETR 的 Hungarian matching；U-Net 复核 572→388 valid-convolution 几何、中心裁剪、overlap-tile 与原论文加权 softmax loss。证据登记于 docs/evidence/16-20.json。

11–15 章另增加 Vision Transformer token/attention 算术、ConvNeXt 深度卷积成本、AdamW 解耦衰减、Pareto 选型以及 IoU/COCO AP/NMS 的可运行样例。所有性能示例均独立标注为教学构造，并记录参考来源于 `docs/evidence/11-15.json`。

本轮特别区分 AlexNet 2012 年原版与现代 torchvision，VGG-16 原配置与带 BN 变体，以及 ResNet v1、pre-activation v2 与 torchvision v1.5。历史指标只在指定论文/数据/协议下成立。

## 协作约定

- 保留 01–28 章节编号和旧链接兼容入口；更新正文以 `docs/chapters/` 为准。
- 一篇网页应该无需读其它章节也能理解：背景、定义、机制、数学、代码、实验与局限完整闭环。
- 不能编造历史指标、论文结论、模型结构、图像来源或 QA 结果。技术主张在文末注明来源。
- 本项目写作实践参照 [Olah-style-posts](https://github.com/1998x-stack/Olah-style-posts) 的 `olah-style-paper-posts` skill，图示和正文独立原创。
- 贡献者与自动化代理先阅读 [AGENTS.md](AGENTS.md)；PR 请同时执行静态检查、移动端与键盘可访问性验收。

## 许可证与论文资料

代码与教程版权以仓库现有许可证和各文件来源为准。仓库没有显式总 LICENSE 时，**不应推定其为开源许可**；`pdfs/` 中的论文保留原作者版权，不因本仓库整理而改变授权范围。
