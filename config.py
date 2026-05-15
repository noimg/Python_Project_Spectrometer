# config.py

# 汞灯标准可见光光谱特征波长 (单位: nm)
# Violet, Blue, Green, Yellow-orange(1), Yellow-orange(2), Orange-red, Red
HG_STANDARD_WAVELENGTHS = [404.7, 435.8, 546.1, 577.0, 579.0, 623.4, 690.7]

HG_STANDARD_COLORS = [
    "Violet",
    "Blue",
    "Green",
    "Yellow-orange(1)",
    "Yellow-orange(2)",
    "Orange-red",
    "Red",
]

# 已知元素的特征光谱库 (单位: nm)
KNOWN_ELEMENTS_SPECTRA = {
    "H": [410.2, 434.0, 486.1, 656.3],  # Balmer 系可见光区
    "He": [447.1, 501.6, 587.6, 667.8, 706.5],  # He I 强线
    "Ar": [488.0, 514.6, 696.5, 706.7, 738.4, 750.4, 763.5, 801.5, 811.5],
    "Ne": [
        540.1,
        585.2,
        588.2,
        594.5,
        603.0,
        609.6,
        614.3,
        616.4,
        621.7,
        626.6,
        633.4,
        640.2,
        650.6,
        659.9,
    ],
}
