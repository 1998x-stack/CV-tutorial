# CV Tutorial · 全站发布验收与后续维护清单

> 目标：28 篇可独立阅读、原始论文依据可追踪、SVG 与 Python 实验可复核的中文计算机视觉课程。此清单是验收协议，不代替 Actions 实际运行结果。

## 章节边界与任务地图

| 章节 | 主要计算问题 | 易混淆的技术边界 | 关键校验 |
| --- | --- | --- | --- |
| 01–05 | 像素、滤波、传统特征、反向传播与卷积 | OpenCV BGR/RGB；核相关与卷积；梯度链式法则 | 至少两幅图、静态资源、章节导航 |
| 06–10 | PyTorch、分类协议、AlexNet、VGG、ResNet | train/eval；原论文与 torchvision 实现 | CPU 片段与形状/梯度断言 |
| 11–15 | ViT、ConvNeXt、训练策略、评估及检测基础 | Transformer 归一化轴；COCO AP vs VOC AP；NMS 类别边界 | 原始公式、AP/IoU 数值复核 |
| 16–20 | 两阶段、单阶段、集合检测与 U-Net | RoIPool vs RoIAlign；YOLOv1 vs 后续；U-Net 572→388 | RPN anchors、SSD boxes、Skip crop 等 |
| 21–25 | 实例/全景分割、SAM、增强、迁移与部署 | Categorical mask 插值；原论文 loss；TensorRT 11 Q/DQ | 几何同步、LoRA 预算与工件条件 |
| 26 | SimCLR、MoCo、DINOv2 与 MAE | 正样本是同源两视图；EMA teacher 不反传；MAE visible-only encoder | NT-Xent 索引、FIFO、停止梯度、75% mask |
| 27 | CLIP、VLM、DDPM/LDM 与 NeRF/3DGS | 图文相似度不是语言生成；扩散噪声损失不是反向采样；2D 与 3D 不等价 | 双向 CE、q(xₜ|x₀)、注意力轴、alpha 渲染 |
| 28 | 数据集到推理服务的完整工程 | Group leakage、预处理与类别 ID、模型 confidence calibration | Group split、CPU toy classifier、abstain、state_dict parity |

## 发布门禁

1. **静态资源**：`python3 scripts/check_site.py`；28 章固定编号、首页 28 张卡片、所有章节 H1 和本地锚点、至少 100 张合法可访问 SVG。
2. **构建兼容**：`python3 scripts/build_pages.py`；根目录旧入口 `01.html`–`28.html` 与 `_site/chapters/*.html` 同时存在。
3. **正文片段**：`python3 tests/test_cv_examples.py`；06–28 章的每个 Python 代码片段在独立 namespace 执行，不下载模型权重。01–05 的第三方依赖示例需在第二轮专项环境审计。
4. **浏览器验收**：`python3 scripts/check_browser.py`；首页 + 28 章，各取 1440、768、390、360 px，共 116 个页面/视口组合。记录溢出、图片尺寸、MathML、脚本报错、键盘、打印和离线行为。
5. **唯一交互检查**：第 26 章 mask ratio slider 默认 75% → 键盘左移到 50% → 再恢复 75%，需要同时更新 aria-live 与可见 token 数量。
6. **发布状态**：PR 的 check/examples/browser 三项均为 success，再 squash merge；Pages workflow 成功后检查默认分支文件，若未做公开浏览器访问，明确记录此限制。

## 证据与专业写作底线

- 原论文定量结果必须注明数据、模型配置、指标和 paper locator；不能把图片中的教学示意数值写成实测 benchmark。
- 原始算法与后续变体独立：DINO 与 DINOv2，MAE 与 Diffusion，CLIP/BLIP/LLaVA，DDPM 与 LDM，NeRF 与 3DGS。
- SVG 配色用于计算语义；每张图 `title`/`desc`/`viewBox`；文字在手机屏幕可读；不可直接复制论文原图。
- 关键引用见 `docs/evidence/`；21–25 和 26–28 已使用逐条证据登记；旧批次保持原有 ledger。
- 不要在文章正文写“本讲义介绍了”“下一篇才讲定义”一类省略上下文的占位句；每篇必须独立成文。

## 后续第二轮建议

优先逐一专项复核 01–05 章第三方 OpenCV/Numpy 示例环境、所有原始论文版本和图形可读性，抽样检查 360/390px 的长公式和独立 SVG 字号，并使用真实浏览器证据做逐章回归。除非有新知识点或事实更正，不要机械增加章节数。
