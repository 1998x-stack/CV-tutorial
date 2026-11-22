#!/usr/bin/env python3
"""Execute the published 01–05 snippets and verify image/gradient contracts.

Install with: python3 -m pip install -r requirements-vision-tests.txt
No external images, model weights, network calls or GUI backend are used.
"""
from contextlib import redirect_stdout
from html.parser import HTMLParser
from io import StringIO
from pathlib import Path
import unittest

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


class Snippets(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_pre = False
        self.in_code = False
        self.current = []
        self.snippets = []

    def handle_starttag(self, tag, attrs):
        if tag == "pre":
            self.in_pre = True
        elif tag == "code" and self.in_pre:
            self.in_code = True
            self.current = []

    def handle_data(self, data):
        if self.in_code:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == "code" and self.in_code:
            self.snippets.append("".join(self.current))
            self.in_code = False
        elif tag == "pre":
            self.in_pre = False


class PublishedExamples(unittest.TestCase):
    def test_every_article_code_block_runs(self):
        count = 0
        for chapter in range(1, 6):
            path = ROOT / "docs" / "chapters" / f"{chapter:02}.html"
            parser = Snippets()
            parser.feed(path.read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(parser.snippets), 2, f"{path}: expected two code examples")
            for index, source in enumerate(parser.snippets, 1):
                self.assertIn("assert ", source, f"{path}: snippet {index} lacks an assertion")
                namespace = {"__name__": "__main__"}
                with redirect_stdout(StringIO()):
                    exec(compile(source, f"{path.name} snippet {index}", "exec"), namespace)
                count += 1
        self.assertGreaterEqual(count, 10)
        print(f"Executed {count} published 01–05 code samples")


class ImageContracts(unittest.TestCase):
    def test_bgr_red_to_gray(self):
        red_bgr = np.array([[[0, 0, 255]]], dtype=np.uint8)
        gray = cv2.cvtColor(red_bgr, cv2.COLOR_BGR2GRAY)
        self.assertEqual(int(gray[0, 0]), 76)

    def test_canny_binary_edges_and_morphological_closing(self):
        image = np.zeros((80, 120), dtype=np.uint8)
        image[20:60, 30:90] = 255
        edges = cv2.Canny(cv2.GaussianBlur(image, (5, 5), 1), 40, 100)
        self.assertEqual(edges.shape, image.shape)
        self.assertEqual(edges.dtype, np.uint8)
        self.assertTrue(set(np.unique(edges)).issubset({0, 255}))
        self.assertGreater(np.count_nonzero(edges), 0)

        mask = np.zeros((7, 7), dtype=np.uint8)
        mask[3, 1:3] = 255
        mask[3, 4:6] = 255
        closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((1, 3), np.uint8))
        self.assertEqual(int(closed[3, 3]), 255)

    def test_numpy_gradient_axis_order(self):
        ramp = np.tile(np.arange(32, dtype=float), (32, 1))
        derivative_rows, derivative_cols = np.gradient(ramp)
        np.testing.assert_allclose(derivative_rows, 0.0)
        np.testing.assert_allclose(derivative_cols, 1.0)

    def test_sift_descriptor_is_present_and_128d(self):
        image = np.zeros((192, 192), dtype=np.uint8)
        for y in range(24, 168, 24):
            for x in range(24, 168, 24):
                cv2.circle(image, (x, y), 5, 255, -1)
                cv2.rectangle(image, (x + 6, y + 6), (x + 13, y + 13), 180, -1)
        keypoints, descriptors = cv2.SIFT_create(nfeatures=256).detectAndCompute(image, None)
        self.assertGreater(len(keypoints), 0)
        self.assertIsNotNone(descriptors)
        self.assertEqual(descriptors.shape, (len(keypoints), 128))

    def test_hog_descriptor_dimension_from_configuration(self):
        image = np.zeros((32, 32), dtype=np.uint8)
        image[:, 16:] = 255
        descriptor = cv2.HOGDescriptor((32, 32), (16, 16), (8, 8), (8, 8), 9)
        features = descriptor.compute(image)
        # 3×3 blocks × 2×2 cells × 9 bins = 324 values.
        self.assertEqual(features.size, 324)

    def test_integral_image_four_corner_query(self):
        image = np.arange(1, 17, dtype=np.int64).reshape(4, 4)
        prefix = image.cumsum(axis=0).cumsum(axis=1)

        def at(x, y):
            return 0 if x < 0 or y < 0 else int(prefix[y, x])

        total = at(3, 2) - at(0, 2) - at(3, 0) + at(0, 0)
        self.assertEqual(total, int(image[1:3, 1:4].sum()))
        self.assertEqual(total, 54)

    def test_multichannel_cross_correlation(self):
        x = np.arange(1, 19, dtype=float).reshape(1, 2, 3, 3)
        weight = np.array([[[[1, 0], [0, -1]],
                            [[1, 0], [0, -1]]]], dtype=float)
        out = np.zeros((1, 1, 2, 2), dtype=float)
        for ci in range(2):
            for row in range(2):
                for col in range(2):
                    out[0, 0, row, col] += np.sum(
                        x[0, ci, row:row+2, col:col+2] * weight[0, ci]
                    )
        self.assertEqual(out.shape, (1, 1, 2, 2))
        np.testing.assert_allclose(out, -8.0)

    def test_convolution_output_size(self):
        def output_size(size, kernel, padding, stride, dilation=1):
            return (size + 2*padding - dilation*(kernel-1) - 1)//stride + 1
        self.assertEqual(output_size(32, 3, 1, 2), 16)
        self.assertEqual(output_size(32, 3, 1, 1), 32)


if __name__ == "__main__":
    print(f"NumPy {np.__version__} | OpenCV {cv2.__version__}")
    unittest.main(verbosity=2)
