import tkinter as tk
from tkinter import messagebox
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np

# from tools import wavelength_to_rgb


def wavelength_to_rgb(wavelength: float, gamma: float = 0.8) -> tuple[int, int, int]:
    """
    将可见光波长（单位：nm）转换为 0~255 的 RGB 颜色值。

    :param wavelength: 波长值，推荐范围 380~780 nm
    :param gamma: 显示器 Gamma 校正系数，默认 0.8
    :return: (R, G, B) 元组，范围 0~255
    """
    w = float(wavelength)

    # 超出可见光范围返回黑色
    if w < 380 or w > 780:
        return (0, 0, 0)

    # 1. 分段线性映射到 [0, 1]
    if 380 <= w <= 440:
        r = -(w - 440) / (440 - 380)
        g = 0.0
        b = 1.0
    elif 440 <= w <= 490:
        r = 0.0
        g = (w - 440) / (490 - 440)
        b = 1.0
    elif 490 <= w <= 510:
        r = 0.0
        g = 1.0
        b = -(w - 510) / (510 - 490)
    elif 510 <= w <= 580:
        r = (w - 510) / (580 - 510)
        g = 1.0
        b = 0.0
    elif 580 <= w <= 645:
        r = 1.0
        g = -(w - 645) / (645 - 580)
        b = 0.0
    elif 645 <= w <= 780:
        r = 1.0
        g = 0.0
        b = 0.0
    else:
        r = g = b = 0.0

    # 2. 人眼敏感度边缘衰减（380~420nm 与 700~780nm）
    if 380 <= w <= 420:
        factor = 0.3 + 0.7 * (w - 380) / (420 - 380)
    elif 700 <= w <= 780:
        factor = 0.3 + 0.7 * (780 - w) / (780 - 700)
    else:
        factor = 1.0

    # 3. 应用强度衰减与  Gamma 校正
    r = (r * factor) ** gamma
    g = (g * factor) ** gamma
    b = (b * factor) ** gamma

    # 4. 缩放到 0~255 并取整
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def get_inputs_from_popup(
    hints: List[str], title: str = "请输入信息"
) -> Optional[List[str]]:
    """
    弹出窗口，提供多个带提示文本的输入框。
    用于已知数量且有明确标签的数据（如汞灯的7条线）。
    """
    if not hints:
        return []

    root = tk.Tk()
    root.title(title)
    root.resizable(False, False)

    entries = []
    for i, hint in enumerate(hints):
        tk.Label(root, text=hint, font=("Microsoft YaHei", 10)).grid(
            row=i, column=0, padx=10, pady=6, sticky="e"
        )
        entry = tk.Entry(root, font=("Microsoft YaHei", 10), width=25)
        entry.grid(row=i, column=1, padx=10, pady=6)
        entries.append(entry)
        if i == 0:
            entry.focus_set()

    result = None

    def on_ok(event=None):
        nonlocal result
        result = [e.get() for e in entries]
        root.destroy()

    def on_cancel(event=None):
        root.destroy()

    btn_frame = tk.Frame(root)
    btn_frame.grid(row=len(hints), column=0, columnspan=2, pady=12)
    tk.Button(btn_frame, text="确定", command=on_ok, width=8).pack(side="left", padx=10)
    tk.Button(btn_frame, text="取消", command=on_cancel, width=8).pack(
        side="left", padx=10
    )

    root.bind("<Return>", on_ok)
    root.bind("<Escape>", on_cancel)
    root.protocol("WM_DELETE_WINDOW", on_cancel)

    root.mainloop()
    return result


def get_dynamic_inputs_from_popup(
    prompt: str, title: str = "请输入测量数据"
) -> Optional[List[float]]:
    """
    弹出窗口，提供一个大文本框，让用户使用逗号或空格分隔输入不定数量的数据。
    适合用于输入样本测量的读数。
    """
    root = tk.Tk()
    root.title(title)
    root.resizable(False, False)

    tk.Label(root, text=prompt, font=("Microsoft YaHei", 10), justify="left").pack(
        padx=10, pady=10
    )

    entry = tk.Entry(root, font=("Microsoft YaHei", 12), width=50)
    entry.pack(padx=10, pady=5)
    entry.focus_set()

    result = None

    def on_ok(event=None):
        nonlocal result
        text = entry.get().strip()
        if not text:
            messagebox.showwarning("提示", "输入不能为空")
            return

        # 将中文逗号和英文逗号替换为空格后进行分割
        text = text.replace(",", " ").replace("，", " ")
        parts = text.split()

        try:
            result = [float(p) for p in parts]
            root.destroy()
        except ValueError:
            messagebox.showerror(
                "错误", "存在无效数字，请确保仅输入数字并以空格或逗号分隔！"
            )

    def on_cancel(event=None):
        root.destroy()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="确定", command=on_ok, width=8).pack(side="left", padx=10)
    tk.Button(btn_frame, text="取消", command=on_cancel, width=8).pack(
        side="left", padx=10
    )

    root.bind("<Return>", on_ok)
    root.bind("<Escape>", on_cancel)
    root.protocol("WM_DELETE_WINDOW", on_cancel)

    root.mainloop()
    return result


def plot_calibration_curve(
    degrees: list,
    wavelengths: list,
    k: float,
    b: float,
    r_squared: float,
    type: str = "λ-θ",
):
    """绘制校准曲线（散点与拟合直线图）

    Args:
        degrees: 光谱仪角度读数列表
        wavelengths: 标准波长列表
        k: 拟合直线斜率 (λ = kθ + b)
        b: 拟合直线截距
        r_squared: 决定系数
        type: 图表类型 'λ-θ' (波长-角度) 或 'θ-λ' (角度-波长)
    """
    plt.figure(figsize=(8, 5))
    if type == "λ-θ":
        # λ-θ 模式：波长作为y轴，角度作为x轴
        x = np.array(degrees)
        y = np.array(wavelengths)
        x_line = np.linspace(min(x) - 1, max(x) + 1, 100)
        y_line = k * x_line + b

        plt.scatter(x, y, color="blue", s=50, label="Measured Points", zorder=5)
        plt.plot(
            x_line,
            y_line,
            color="red",
            linestyle="--",
            label=f"Fit: λ = {k:.2f}θ + {b:.2f}",
        )

        plt.title(
            f"Calibration: Wavelength vs Angle (R² = {r_squared:.4f})", fontsize=14
        )
        plt.xlabel("Spectrometer Reading (Degrees)", fontsize=12)
        plt.ylabel("Standard Wavelength (nm)", fontsize=12)
    else:
        # θ-λ 模式：角度作为y轴，波长作为x轴
        x = np.array(wavelengths)
        y = np.array(degrees)
        x_line = np.linspace(min(x) - 10, max(x) + 10, 100)
        # θ = (1/k)λ - b/k
        y_line = (1 / k) * x_line - b / k

        plt.scatter(x, y, color="green", s=50, label="Measured Points", zorder=5)
        plt.plot(
            x_line,
            y_line,
            color="orange",
            linestyle="--",
            label=f"Fit: θ = {(1/k):.4f}λ + {(-b/k):.4f}",
        )

        plt.title(
            f"Calibration: Angle vs Wavelength (R² = {r_squared:.4f})", fontsize=14
        )
        plt.xlabel("Standard Wavelength (nm)", fontsize=12)
        plt.ylabel("Spectrometer Reading (Degrees)", fontsize=12)

    plt.legend()
    plt.grid(True, linestyle=":", alpha=0.7)
    plt.tight_layout()
    plt.show()


def plot_comparison_spectrum(
    measured_wls: list,
    reference_wls: list,
    element_name: str,
    title: str = "Spectrum Comparison",
):
    """绘制两个光谱的比对图（上下子图）"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    all_wls = measured_wls + reference_wls
    min_w = min(all_wls) - 30 if all_wls else 380
    max_w = max(all_wls) + 30 if all_wls else 780

    # 可见光背景生成
    vis_x = np.linspace(380, 780, 400)
    vis_rgb = np.array([wavelength_to_rgb(w) for w in vis_x]) / 255.0

    def draw_lines(ax, wls, label_title):
        # 绘制背景
        ax.imshow(
            vis_rgb.reshape(1, -1, 3),
            aspect="auto",
            extent=[380, 780, 0, 0.04],
            alpha=0.3,
            zorder=1,
        )

        for w in wls:
            rgb = wavelength_to_rgb(w)
            color = (
                (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
                if rgb != (0, 0, 0)
                else (0.3, 0.3, 0.3)
            )
            ax.vlines(
                w, 0, 1.0, colors=color, linewidth=2.5, zorder=3, capstyle="round"
            )
            ax.annotate(
                f"{w:.1f}",
                xy=(w, 1.0),
                xytext=(0, 6),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.85, ec="none"),
            )

        ax.set_xlim(min_w, max_w)
        ax.set_ylim(0, 1.3)
        ax.set_title(label_title, fontsize=12)
        ax.set_yticks([])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)

    draw_lines(ax1, measured_wls, "Measured Sample Spectrum")
    draw_lines(ax2, reference_wls, f"Reference Spectrum: {element_name}")

    ax2.set_xlabel("Wavelength (nm)", fontsize=12)
    plt.tight_layout()
    plt.show()
