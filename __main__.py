import tkinter as tk
from tkinter import messagebox
from config import HG_STANDARD_COLORS, HG_STANDARD_WAVELENGTHS
from spectrometer import Spectrometer
from analyzer import SpectrumAnalyzer
from visualization import get_inputs_from_popup, get_dynamic_inputs_from_popup, plot_calibration_curve, plot_comparison_spectrum

def main():
    print("=== 手制光谱仪数据可视化分析项目启动 ===")
    
    # 1. 汞灯校准阶段
    print("等待输入汞灯校准数据...")
    hg_hints = [f"{color} (约 {wl} nm):" for color, wl in zip(HG_STANDARD_COLORS, HG_STANDARD_WAVELENGTHS)]
    hg_inputs_str = get_inputs_from_popup(hg_hints, title="第一步：输入汞灯7条可见光谱线读数(度)")
    
    if not hg_inputs_str:
        print("已取消汞灯校准，程序退出。")
        return
        
    try:
        hg_degrees = [float(x) for x in hg_inputs_str]
    except ValueError:
        print("汞灯输入包含无效数字，程序退出。")
        return
        
    # 初始化并执行校准
    spec = Spectrometer()
    # 要不要考虑没看到全部谱线的情况呢……
    try:
        k, b, r_squared = spec.calibrate(hg_degrees, HG_STANDARD_WAVELENGTHS)
    except Exception as e:
        print(f"校准失败: {e}")
        return
        
    print(f"校准成功! \n拟合直线: λ = {k:.4f}θ + {b:.4f}\n决定系数 R² = {r_squared:.4f}")
    plot_calibration_curve(hg_degrees, HG_STANDARD_WAVELENGTHS, k, b, r_squared)
    
    # 2. 样本测量与匹配阶段
    analyzer = SpectrumAnalyzer()
    
    # 循环输入4个样本的数据
    for i in range(1, 5):
        print(f"\n准备测量 样本 {i} ...")
        sample_degrees = get_dynamic_inputs_from_popup(
            prompt=f"请输入 样本 {i} 的所有测量读数(度)\n多个读数请用空格或逗号分隔：", 
            title=f"第二步：样本 {i} 数据输入"
        )
        
        if not sample_degrees:
            print(f"用户取消了 样本 {i} 的输入，跳过...")
            continue
            
        print(f"样本 {i} 输入读数: {sample_degrees}")
        
        # 将度数转为波长
        sample_wls = spec.convert_degrees_to_wavelengths(sample_degrees)
        print(f"样本 {i} 转换波长(nm): {[round(w, 2) for w in sample_wls]}")
        
        # 使用 DTW 算法匹配元素
        best_element, best_dist, all_results = analyzer.match_sample(sample_wls)
        
        print(f"--- 匹配结果 ---")
        for element, dist in all_results.items():
            print(f"  与 {element} 的匹配距离: {dist:.2f}")
        print(f"★ 最优匹配元素: {best_element} (最小距离/匹配度: {best_dist:.2f})")
        
        # 绘制比对光谱图
        plot_comparison_spectrum(
            measured_wls=sample_wls, 
            reference_wls=analyzer.reference_spectra[best_element], 
            element_name=best_element
        )
        
    print("\n所有样本分析完毕，程序结束。")

if __name__ == "__main__":
    main()
