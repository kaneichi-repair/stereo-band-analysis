# -----------------------------------------------------------------------------
# Stereo Band Gain Difference Analyzer
# Concept, specifications, and validation by Kaneichi-Repair.
# Source code generated with AI assistance.
# Copyright (c) 2026 Kaneichi-Repair
# Released under the MIT License.
# -----------------------------------------------------------------------------

__author__ = "Kaneichi-Repair"
__copyright__ = "Copyright (c) 2026 Kaneichi-Repair"
__license__ = "MIT"
__version__ = "1.0.0"

import argparse
import os
import numpy as np
import librosa
import matplotlib.pyplot as plt
from matplotlib import font_manager
import csv
from scipy.signal import welch


# ==========================================================
# Language setting
#   "ja" : Japanese
#   "en" : English
# ==========================================================
LANG = "ja"

MSG = {
    "ja": {
        "stereo_error": "入力ファイルはステレオである必要があります。",
        "sample_rate_mismatch": "正接続と逆接続のサンプリング周波数が一致しません。",
        "no_welch_signal": "Welch解析の評価対象である -100 dB を超える有効信号域がありません。Band解析結果は微小信号領域を含む場合があります。",
        "analysis_start": "解析開始...",
        "analysis_band": "帯域別ゲイン差（補正後）解析中...",
        "analysis_complete": "解析完了！",

        "summary_title": "Corrected Gain Difference Analysis",

        "judge": "判定",
        "energy_ratio": "Energy Ratio (L/R)",

        "judge_ok": "OK: チャンネル差は測定誤差レベル",
        "judge_peak": "注意: 局所ピーク差あり（接触不良・共振・ケーブル差の可能性）",
        "judge_gain": "注意: 全体ゲイン差（機器側の可能性）",
        "judge_problem": "要確認: 機器または測定条件に問題の可能性",
        "judge_middle": "中間状態",

        "warning_asymmetry": "警告: チャンネル間レベルに大きな非対称あり（断線・接触不良の可能性）",
        "channel_normal": "チャンネルバランス正常範囲",

        "note1": "※このWelch解析は信号成分が存在する帯域を中心に評価します",
        "note2": "※狭帯域信号（単音など）では、信号が存在しない周波数帯域は評価対象から除外されます",
        "note3": "※帯域外の差分はBand解析結果も併せて確認してください",
        "summary": "--- Summary ---",
        "channel_check": "--- Channel Check ---",
        "delta_band": "ΔDiff (Band)",
        "delta_welch": "ΔDiff (Welch max)",
        "max_diff_freq": "Max Diff Freq",
        "welch_eval_note": "評価対象：信号レベル > -100 dB",
        "uniform_diff": "全評価帯域でほぼ一定の差",

        "csv_band": "Band (Hz)",
        "csv_corrected": "Corrected Diff (dB)",

        "graph_corrected_diff": "補正後差分",
        "graph_left_normal": "左ch（正接続）",
        "graph_right_normal": "右ch（正接続）",
        "graph_left_reverse": "左ch（逆接続）",
        "graph_right_reverse": "右ch（逆接続）",

        "title_band": "帯域別ゲイン差（補正後）",
        "title_welch_normal": "Welchスペクトル（正接続）",
        "title_welch_reverse": "Welchスペクトル（逆接続）",
        "title_welch_diff": "Welchスペクトル差（補正後）",

        "xlabel_freq": "周波数 [Hz]",
        "ylabel_power": "パワー [dB]",
        "ylabel_lr": "L - R [dB]",
        "ylabel_diff": "差分 [dB]",

        "graph_welch_diff": "補正後Welch差分",

        "app_description": "左右入替補正付きチャンネル差解析",
    },

    "en": {
        "stereo_error": "Input file must be stereo.",
        "sample_rate_mismatch": "Sample rates of the normal and reversed files do not match.",
        "no_welch_signal": "No valid signal region above -100 dB was found for Welch analysis.",
        "analysis_start": "Analysis started...",
        "analysis_band": "Analyzing corrected band gain differences...",
        "analysis_complete": "Analysis completed!",

        "summary_title": "Corrected Gain Difference Analysis",

        "judge": "Judgement",
        "energy_ratio": "Energy Ratio (L/R)",

        "judge_ok": "OK: Channel difference is within measurement error.",
        "judge_peak": "Caution: Local peak difference detected (possible contact issue, resonance, or cable difference).",
        "judge_gain": "Caution: Overall gain difference detected (possible DUT issue).",
        "judge_problem": "Check required: Possible equipment or measurement problem.",
        "judge_middle": "Intermediate result.",

        "warning_asymmetry": "Warning: Large channel level asymmetry detected (possible open circuit or poor connection).",
        "channel_normal": "Channel balance is within the normal range.",

        "note1": "This Welch analysis evaluates mainly the frequency regions containing signal energy.",
        "note2": "For narrow-band signals (such as single tones), frequency regions without signal are excluded from the evaluation.",
        "note3": "Please also refer to the band analysis results for differences outside the detected signal region.",
        "summary": "--- Summary ---",
        "channel_check": "--- Channel Check ---",
        "delta_band": "ΔDiff (Band)",
        "delta_welch": "ΔDiff (Welch max)",
        "max_diff_freq": "Max Diff Freq",
        "welch_eval_note": "Evaluated region: Signal > -100 dB",
        "uniform_diff": "Uniform difference detected",

        "csv_band": "Band (Hz)",
        "csv_corrected": "Corrected Diff (dB)",

        "graph_corrected_diff": "Corrected Diff",
        "graph_left_normal": "Left (Normal)",
        "graph_right_normal": "Right (Normal)",
        "graph_left_reverse": "Left (Reverse)",
        "graph_right_reverse": "Right (Reverse)",

        "title_band": "Band-wise Gain Difference (Corrected)",
        "title_welch_normal": "Welch Spectra (Normal)",
        "title_welch_reverse": "Welch Spectra (Reverse)",
        "title_welch_diff": "Welch Spectra Difference (Corrected)",

        "xlabel_freq": "Frequency [Hz]",
        "ylabel_power": "Power [dB]",
        "ylabel_lr": "L - R [dB]",
        "ylabel_diff": "Difference [dB]",

        "graph_welch_diff": "Corrected Welch Diff",

        "app_description": "Stereo Channel Difference Analysis with Channel Swap Compensation",
    }
}

T = MSG.get(LANG, MSG["en"])

# === 帯域設定 ===
BANDS = [
    (20, 40), (40, 80), (80, 160), (160, 315), (315, 630),
    (630, 1250), (1250, 2500), (2500, 5000),
    (5000, 10000), (10000, 20000)
]

FREQ_MIN = 20
FREQ_MAX = 20000

SAFE = 0.15
WARN = 0.30
UNIFORM_THRESHOLD = 0.02

THRESHOLD_DB = -100
ASYM_WARN_RATIO = 10

def band_power(y, sr, band):
    f, Pxx = welch(y, sr, nperseg=4096)
    band_mask = (f >= band[0]) & (f < band[1])
    power = np.mean(Pxx[band_mask]) if np.any(band_mask) else 1e-12
    return 10 * np.log10(power)


def apply_background(ax, ymin, ymax):
    ax.set_ylim(ymin, ymax)
    ax.axhspan(SAFE, WARN, color="yellow", alpha=0.4)
    ax.axhspan(-WARN, -SAFE, color="yellow", alpha=0.4)
    ax.axhspan(-SAFE, SAFE, color="green", alpha=0.25)

def setup_font():
    from matplotlib import rcParams

    if LANG == "ja":
        # Japanese font candidates for Windows / macOS / Linux
        font_candidates = [
            "Yu Gothic",          # Windows
            "Meiryo",             # Windows
            "Hiragino Sans",      # macOS
            "Hiragino Kaku Gothic ProN",  # macOS (older versions)
            "Noto Sans CJK JP",   # Linux
            "Noto Sans JP",       # Linux / other
        ]

        available_fonts = {
            font.name for font in font_manager.fontManager.ttflist
        }

        for font_name in font_candidates:
            if font_name in available_fonts:
                rcParams["font.family"] = font_name
                break
        else:
            rcParams["font.family"] = "DejaVu Sans"
            print(
                "Warning: Japanese font not found. "
                "Japanese text in graphs may not be displayed correctly."
            )

    else:
        rcParams["font.family"] = "DejaVu Sans"

    rcParams["axes.unicode_minus"] = False


def load_stereo(file):
    y, sr = librosa.load(file, sr=None, mono=False)

    if y.ndim != 2 or y.shape[0] != 2:
        raise ValueError(T["stereo_error"])
    return y[0], y[1], sr

def analyze(file_normal, file_reverse, output_dir, yrange=None):

    setup_font()

    print(T["analysis_start"])

    L1, R1, sr1 = load_stereo(file_normal)
    L2, R2, sr2 = load_stereo(file_reverse)

    if sr1 != sr2:
        raise ValueError(
            f'{T["sample_rate_mismatch"]} '
            f'Normal={sr1} Hz, Reverse={sr2} Hz'
        )

    sr = sr1

    # === 非対称検出 ===
    energy_L = np.sum(L1**2)
    energy_R = np.sum(R1**2)
   
    if energy_R == 0:
        asymmetry_ratio = np.inf
    else:
        asymmetry_ratio = energy_L / energy_R

    asymmetry_flag = (asymmetry_ratio > ASYM_WARN_RATIO) or (asymmetry_ratio < 1/ASYM_WARN_RATIO)

    os.makedirs(output_dir, exist_ok=True)

    results = []

    print(T["analysis_band"])

    for band in BANDS:
        pL1 = band_power(L1, sr, band)
        pR1 = band_power(R1, sr, band)
        pL2 = band_power(L2, sr, band)
        pR2 = band_power(R2, sr, band)

        d1 = pL1 - pR1
        d2 = pL2 - pR2

        corrected = (d1 - d2) / 2

        results.append((band, pL1, pR1, pL2, pR2, corrected))

        print(f"{band[0]}-{band[1]} Hz: Corrected Diff={corrected:.3f} dB")

    # === CSV保存 ===（補正結果を出力）
    csv_path = os.path.join(output_dir, "band_levels.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([T["csv_band"], T["csv_corrected"]])
        for band, _, _, _, _, diff in results:
            writer.writerow([f"{band[0]}-{band[1]}", f"{diff:.3f}"])

    # === グラフ（Band）===
    bands = [f"{b[0]}-{b[1]}" for b, *_ in results]
    diffs = [d for *_, d in results]

    fig, ax = plt.subplots(figsize=(10, 5))

    if yrange:
        ymin, ymax = yrange
    else:
        ymin = min(diffs) - 1
        ymax = max(diffs) + 1

    apply_background(ax, ymin, ymax)

    ax.bar(range(len(bands)), diffs, color="skyblue", edgecolor="black")
    ax.plot(range(len(bands)), diffs, marker="o", color="red", linewidth=1, label=T["graph_corrected_diff"])

    ax.axhline(0, color="black", linestyle="--", linewidth=1)

    delta_diff = max(diffs) - min(diffs)

    idx_band = np.argmax(np.abs(diffs))
    band_max = bands[idx_band]
    val_band = diffs[idx_band]

    ax.plot(idx_band, val_band, "ro")
    ax.text(idx_band, val_band,
            f"{band_max}\n{val_band:.2f} dB",
            fontsize=9, ha="center", va="bottom")

    ax.text(0.02, 0.95,
            f"ΔDiff = {delta_diff:.3f} dB",
            transform=ax.transAxes,
            fontsize=11,
            verticalalignment="top",
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"))

    ax.set_xticks(range(len(bands)))
    ax.set_xticklabels(bands, rotation=45)
    ax.set_ylabel(T["ylabel_lr"])
    ax.set_title(T["title_band"])
    ax.legend()
    ax.grid(True, axis="y", linestyle="--", alpha=0.7)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "diff_by_band.png"))
    plt.close()

# === Welchスペクトル（正接続）===
    f, PxxL1 = welch(L1, sr, nperseg=4096)
    _, PxxR1 = welch(R1, sr, nperseg=4096)

    mask = (f >= FREQ_MIN) & (f <= FREQ_MAX)
    f_plot = f[mask]

    Lp1 = 10 * np.log10(PxxL1[mask])
    Rp1 = 10 * np.log10(PxxR1[mask])

    plt.figure(figsize=(10, 6))
    plt.semilogx(f_plot, Lp1, label=T["graph_left_normal"], alpha=0.7)
    plt.semilogx(f_plot, Rp1, label=T["graph_right_normal"], alpha=0.7)
    plt.xlabel(T["xlabel_freq"])
    plt.ylabel(T["ylabel_power"])
    plt.title(T["title_welch_normal"])
    plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "welch_spectra_normal.png"))
    plt.close()

    # === Welchスペクトル（逆接続）===
    f, PxxL2 = welch(L2, sr, nperseg=4096)
    _, PxxR2 = welch(R2, sr, nperseg=4096)

    Lp2 = 10 * np.log10(PxxL2[mask])
    Rp2 = 10 * np.log10(PxxR2[mask])

    plt.figure(figsize=(10, 6))
    plt.semilogx(f_plot, Lp2, label=T["graph_left_reverse"], alpha=0.7)
    plt.semilogx(f_plot, Rp2, label=T["graph_right_reverse"], alpha=0.7)
    plt.xlabel(T["xlabel_freq"])
    plt.ylabel(T["ylabel_power"])
    plt.title(T["title_welch_reverse"])
    plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "welch_spectra_reverse.png"))
    plt.close()

    # === Welch ===
    f, PxxL1 = welch(L1, sr, nperseg=4096)
    _, PxxR1 = welch(R1, sr, nperseg=4096)
    _, PxxL2 = welch(L2, sr, nperseg=4096)
    _, PxxR2 = welch(R2, sr, nperseg=4096)

    # dB変換（フル）
    Lp1_full = 10*np.log10(PxxL1 + 1e-12)
    Rp1_full = 10*np.log10(PxxR1 + 1e-12)

    # 信号存在マスク（両chベース）
    signal_mask = np.maximum(Lp1_full, Rp1_full) > THRESHOLD_DB

    # 周波数範囲
    freq_mask = (f >= FREQ_MIN) & (f <= FREQ_MAX)

    # 表示用
    f_plot = f[freq_mask]

    diff_welch_plot = np.full(f_plot.shape, np.nan)

    # 評価対象
    eval_mask = signal_mask[freq_mask]

    if not np.any(eval_mask):
        raise ValueError(T["no_welch_signal"])

    d1 = (
        10*np.log10(PxxL1[freq_mask] + 1e-12)
        - 10*np.log10(PxxR1[freq_mask] + 1e-12)
    )

    d2 = (
        10*np.log10(PxxL2[freq_mask] + 1e-12)
        - 10*np.log10(PxxR2[freq_mask] + 1e-12)
    )

    diff_tmp = (d1 - d2) / 2

    diff_welch_plot[eval_mask] = diff_tmp[eval_mask]

    # 判定用
    diff_welch = diff_tmp[eval_mask]
    f_eval = f_plot[eval_mask]

    # ---- Uniform difference detection ----
    peak_span = np.max(diff_welch) - np.min(diff_welch)

    uniform_diff = (
        len(diff_welch) > 1
        and peak_span < UNIFORM_THRESHOLD
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    if yrange:
        ymin, ymax = yrange
    else:
        ymin = np.min(diff_welch) - 1
        ymax = np.max(diff_welch) + 1

    apply_background(ax, ymin, ymax)

    ax.semilogx(
        f_plot,
        diff_welch_plot,
        color="purple",
        linewidth=2,
        label=T["graph_welch_diff"],
    )

    ax.set_xlim(FREQ_MIN, FREQ_MAX)

    ax.axhline(0, color="black", linestyle="--", linewidth=1)

    max_welch = np.max(np.abs(diff_welch))

    if not uniform_diff:

        idx_max = np.argmax(np.abs(diff_welch))

        f_max = f_eval[idx_max]
        val_max = diff_welch[idx_max]

        ax.plot(f_max, val_max, "ro")

        ax.text(
            f_max,
            val_max,
            f"{f_max:.0f} Hz\n{val_max:.2f} dB",
            fontsize=9,
            ha="left",
            va="bottom",
        )

    else:

        f_max = None

    ax.text(0.02, 0.95,
            f"ΔDiff = {delta_diff:.3f} dB / max(diff_welch) = {max_welch:.3f} dB",
            transform=ax.transAxes,
            fontsize=11,
            verticalalignment="top",
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"))

    ax.text(
        0.02,
        0.03,
        T["welch_eval_note"],
        transform=ax.transAxes,
        fontsize=9,
        color="gray",
        bbox=dict(
            facecolor="white",
            alpha=0.7,
            edgecolor="none",
        ),
    )
    if uniform_diff:

        ax.text(
            0.02,
            0.08,
            T["uniform_diff"],
            transform=ax.transAxes,
            fontsize=9,
            color="gray",
            bbox=dict(
                facecolor="white",
                alpha=0.7,
                edgecolor="none",
            ),
        )

    ax.set_xlabel(T["xlabel_freq"])
    ax.set_ylabel(T["ylabel_diff"])
    ax.set_title(T["title_welch_diff"])
    ax.legend()
    ax.grid(True, which="both", linestyle="--", alpha=0.7)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "welch_diff.png"))
    plt.close()

    # === 判定 ===
    if uniform_diff and max_welch >= WARN:
        comment = T["judge_gain"]

    elif delta_diff < SAFE and max_welch < SAFE:
        comment = T["judge_ok"]

    elif delta_diff < SAFE and max_welch >= WARN:
        comment = T["judge_peak"]

    elif delta_diff >= WARN and max_welch < WARN:
        comment = T["judge_gain"]

    elif delta_diff >= WARN and max_welch >= WARN:
        comment = T["judge_problem"]

    else:
        comment = T["judge_middle"]

    # === summary ===
    with open(os.path.join(output_dir, "summary.txt"), "w") as f:
        f.write(T["summary_title"] + "\n\n")
        for band, *_ , diff in results:
            f.write(f"{band[0]}-{band[1]} Hz: Diff={diff:.3f} dB\n")

        f.write("\n" + T["summary"] + "\n")
        f.write(f'{T["delta_band"]} = {delta_diff:.3f} dB\n')
        f.write(f'{T["delta_welch"]} = {max_welch:.3f} dB\n')

        if not uniform_diff:
            f.write(f'{T["max_diff_freq"]} = {f_max:.1f} Hz\n')

        f.write(f'{T["judge"]}: {comment}\n')
        f.write("\n" + T["channel_check"] + "\n")
        f.write(f'{T["energy_ratio"]} = {asymmetry_ratio:.2f}\n')

        if asymmetry_flag:
            f.write(T["warning_asymmetry"] + "\n")
        else:
            f.write(T["channel_normal"] + "\n")

        f.write(T["note1"] + "\n")
        f.write(T["note2"] + "\n")
        f.write(T["note3"] + "\n\n")
    print("\n" + T["analysis_complete"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=T["app_description"])
    parser.add_argument("file_normal", type=str)
    parser.add_argument("file_reverse", type=str)
    parser.add_argument("output_dir", type=str)
    parser.add_argument("--yrange", nargs=2, type=float)

    args = parser.parse_args()

    analyze(args.file_normal, args.file_reverse, args.output_dir, args.yrange)