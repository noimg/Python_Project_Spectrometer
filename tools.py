import numpy as np

def calibrate_spectrometer(degrees: list, wavelengths: list = None):
    """
    拟合手制光谱仪刻度（度数）与实际波长的线性转换关系。
    默认使用汞灯可见光区7条标准谱线波长（单位：nm）。
    
    参数:
        degrees (list/array): 光谱仪上读取的刻度值（度数），顺序需与波长一一对应。
        wavelengths (list/array, optional): 对应的标准波长。若为None，则自动使用汞灯默认值。
        
    返回:
        k (float): 线性函数斜率 (nm/度)，表示每增加1度对应的波长变化量。
        b (float): 线性函数截距 (nm)。
        lambda_func (callable): 转换函数，输入度数theta，返回波长 lambda = k*theta + b。
        r_squared (float): 拟合优度 R²，越接近1说明线性近似越好。
    """
    # 汞灯可见光区常用6条易观测谱线标准波长 (单位: nm)
    # 顺序对应: 紫(Violet)、蓝(Blue)、绿(Green)、黄橙1(Y-O 1)、黄橙2(Y-O 2)、橙红(Orange-Red)
    # 注：实际教学中第6条常用弱线 623.4nm 或 690.7nm，此处以 623.4nm 为例，可按需修改
    # 傻逼ai让它给红线了不给红线，还得我自己手加
    default_wavelengths = [404.7, 435.8, 546.1, 577.0, 579.0, 623.4, 690.7]
    
    if wavelengths is None:
        wavelengths = default_wavelengths
        
    # 转换为 numpy 数组以便数学运算
    x = np.array(degrees, dtype=float)
    y = np.array(wavelengths, dtype=float)
    
    if len(x) != len(y):
        raise ValueError(f"刻度值数量({len(x)})与波长数量({len(y)})不匹配，请检查输入顺序。")
        
    # 使用最小二乘法进行一阶多项式拟合（线性拟合）
    # np.polyfit 返回系数从高阶到低阶: [k, b] 对应 y = k*x + b
    k, b = np.polyfit(x, y, 1)
    
    # 计算拟合优度 R² (决定系数)
    y_pred = k * x + b
    ss_res = np.sum((y - y_pred) ** 2)   # 残差平方和
    ss_tot = np.sum((y - np.mean(y)) ** 2) # 总平方和
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
    
    # 封装为可直接调用的波长转换函数
    def degree_to_wavelength(theta):
        """将光谱仪读数(度)转换为实际波长(nm)"""
        return k * theta + b
        
    return k, b, degree_to_wavelength, r_squared




