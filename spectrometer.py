import numpy as np


class Spectrometer:
    """
    光谱仪物理校准模块
    """

    def __init__(self):
        self.k = 1.0
        self.b = 0.0
        self.r_squared = 0.0
        self.is_calibrated = False

    def calibrate(self, measured_degrees: list, standard_wavelengths: list) -> tuple:
        """
        根据标准波长对测量的度数进行线性拟合校准
        :param measured_degrees: 测量到的光谱仪读数（度数）
        :param standard_wavelengths: 对应的标准波长 (nm)
        :return: (斜率 k, 截距 b, 决定系数 r_squared)
        """
        x = np.array(measured_degrees, dtype=float)
        y = np.array(standard_wavelengths, dtype=float)

        if len(x) != len(y):
            raise ValueError(f"刻度数量({len(x)})与标准波长数量({len(y)})不一致")

        # 一阶多项式拟合 y = k*x + b
        self.k, self.b = np.polyfit(x, y, 1)

        y_pred = self.k * x + self.b
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        self.r_squared = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0

        self.is_calibrated = True
        return self.k, self.b, self.r_squared

    def convert_degrees_to_wavelengths(self, degrees: list) -> list:
        """
        将度数转换为波长
        """
        if not self.is_calibrated:
            raise RuntimeError("光谱仪尚未校准，请先调用 calibrate() 方法！")
        x = np.array(degrees, dtype=float)
        wavelengths = self.k * x + self.b
        return wavelengths.tolist()
