#!/bin/bash
# Download classic CV paper PDFs

download() {
    local url="$1"
    local filename="$2"
    echo "Downloading $filename..."
    curl -sL -o "$filename" "$url" && echo "  ✓ $filename" || echo "  ✗ FAILED: $filename"
}

# 图像分类主干演进
download "https://proceedings.neurips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf" "01_AlexNet_2012.pdf" &
download "https://arxiv.org/pdf/1409.1556.pdf" "02_VGG_2014.pdf" &
download "https://arxiv.org/pdf/1512.03385.pdf" "03_ResNet_2016.pdf" &
download "https://arxiv.org/pdf/2010.11929.pdf" "04_ViT_2021.pdf" &
download "https://arxiv.org/pdf/2201.03545.pdf" "05_ConvNeXt_2022.pdf" &

# 两阶段检测
download "https://arxiv.org/pdf/1311.2524.pdf" "06_R-CNN_2014.pdf" &
download "https://arxiv.org/pdf/1506.01497.pdf" "07_FasterR-CNN_2016.pdf" &

# 分割经典
download "https://arxiv.org/pdf/1703.06870.pdf" "08_MaskR-CNN_2018.pdf" &
download "https://arxiv.org/pdf/1505.04597.pdf" "09_UNet_2015.pdf" &

wait
echo ""
echo "All downloads complete!"
