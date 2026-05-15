import numpy as np

from config import KNOWN_ELEMENTS_SPECTRA


def dtw_distance(s1: list, s2: list) -> float:
    """
    计算两个一维序列的 DTW (Dynamic Time Warping) 距离
    序列会被自动排序
    """
    s1, s2 = sorted(s1), sorted(s2)
    n, m = len(s1), len(s2)

    if n == 0 or m == 0:
        return np.inf

    dtw_matrix = np.full((n + 1, m + 1), np.inf)
    dtw_matrix[0, 0] = 0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = abs(s1[i - 1] - s2[j - 1])
            dtw_matrix[i, j] = cost + min(
                dtw_matrix[i - 1, j],  # 插入
                dtw_matrix[i, j - 1],  # 删除
                dtw_matrix[i - 1, j - 1],  # 匹配
            )

    # 为了避免因为参考序列长度不同导致的偏置，可以将距离按路径长度进行标准化
    # 对于基础版直接返回距离也是可以接受的
    return dtw_matrix[n, m]


class SpectrumAnalyzer:
    """
    光谱匹配与分析模块
    """

    def __init__(self, reference_spectra: dict = None):
        self.reference_spectra = reference_spectra or KNOWN_ELEMENTS_SPECTRA

    def match_sample(self, measured_wavelengths: list) -> tuple:
        """
        基于DTW算法，将测量的波长序列与参考光谱进行匹配

        :param measured_wavelengths: 测量到的样本波长列表
        :return: (最匹配的元素名称, 最佳得分/距离, 所有元素的得分字典)
        """
        best_match = None
        min_distance = np.inf
        results = {}

        for element, ref_wls in self.reference_spectra.items():
            dist = dtw_distance(measured_wavelengths, ref_wls)

            # 使用长度标准化来公平对比具有不同谱线数量的元素
            normalized_dist = dist / max(len(measured_wavelengths), len(ref_wls))

            results[element] = normalized_dist

            if normalized_dist < min_distance:
                min_distance = normalized_dist
                best_match = element

        return best_match, min_distance, results
