# Stereo Band Gain Difference Analyzer

[English README](README.md)

**Stereo Band Gain Difference Analyzer**
は、ステレオ音声の左右チャンネル間のレベル／周波数特性差を解析する
Python スクリプトです。

同一の測定対象（DUT: Device Under Test）を **正接続** と
**左右を入れ替えた逆接続**
の2通りで録音し、その2つの測定結果から測定系自身が持つ左右差の影響を低減して、DUT由来の左右差を求めます。

Version: **1.0.0**\
Author: **Kaneichi-Repair**\
License: **MIT**

> 本スクリプトは測定結果の解析を補助するためのツールです。表示される判定は診断を確定するものではありません。測定条件、接続、信号レベル、ノイズ、使用機器なども含めて結果を確認してください。

## 1. 解析の考え方

通常のステレオ測定では、得られる左右差に DUT
だけでなく、信号発生側や録音側など測定システム自身の左右特性差も含まれます。

本スクリプトでは、同じ DUT を **正接続** と **逆接続**
の2条件で録音し、各録音から L-R の差を求めます。

``` text
補正後左右差 = (正接続時の L-R差 - 逆接続時の L-R差) / 2
```

この方法により、正接続と逆接続で同じ測定チャンネル側に残る特性差を相殺し、DUT側の左右特性差を抽出することを目的としています。

付属のシミュレーション資料では、信号発生器・DUT・録音器それぞれに意図的な左右特性差を設定し、補正後の結果が
DUT 単独の特性をほぼ再現することを確認しています。

## 2. 主な機能

-   正接続／逆接続の2つのステレオ音声ファイルを解析
-   左右入れ替え測定による測定系の左右差補正
-   20 Hz ～ 20 kHz を10帯域に分割した Band解析
-   Welch法による周波数ごとの左右差解析
-   -100 dB以下の低信号領域をWelch評価から除外
-   Band解析およびWelch解析のグラフ出力
-   CSV形式でBand解析結果を保存
-   テキスト形式のSummaryを保存
-   左右チャンネルの極端なレベル非対称を警告
-   解析結果に基づく簡易判定
-   日本語／英語表示

## 3. 公開ファイル

``` text
stereo_band_analysis_en.py
stereo_band_analysis_ja.py
README.md
README_ja.md
LICENSE

docs/
├─ simulation_test_results_en.pdf
└─ simulation_test_results_ja.pdf
```

`stereo_band_analysis_en.py` と `stereo_band_analysis_ja.py`
は機能的には同一です。違いはスクリプト内の Language setting のみです。

日本語版：

``` python
LANG = "ja"
```

英語版：

``` python
LANG = "en"
```

この設定により、コンソールメッセージ、Summary、グラフタイトルなどの表示言語が切り替わります。

## 4. 必要な環境

Python 3 と以下のパッケージを使用します。

-   NumPy
-   SciPy
-   Matplotlib
-   librosa
-   soundfile

標準的なインストール例：

``` bash
pip install numpy scipy matplotlib librosa soundfile
```

仮想環境（venv）の使用を推奨します。Python本体やライブラリのインストール・管理方法はOSやPythonのバージョンによって異なるため、ご使用の環境に合わせて設定してください。

### 日本語グラフのフォント

日本語版では、環境に存在する日本語フォントを次の候補から自動選択します。

-   Yu Gothic / Meiryo --- Windows
-   Hiragino Sans / Hiragino Kaku Gothic ProN --- macOS
-   Noto Sans CJK JP / Noto Sans JP --- Linux など

候補となる日本語フォントが見つからない場合は警告を表示し、DejaVu Sans
にフォールバックします。この場合、日本語が正しく表示されないことがあります。

## 5. 動作確認環境

Version 1.0.0 は、同じテスト用音声を使用して Windows、Linux、macOS
で解析動作と出力結果を確認しています。

-   **Windows 11** --- 日本語版／英語版とも動作確認
-   **Linux Mint / Python 3.12.3** --- 日本語版／英語版とも動作確認
-   **macOS 12（仮想環境）/ Python 3.11.7** ---
    日本語版／英語版とも動作確認

各環境で同じテスト信号を解析し、Band解析およびSummaryの数値結果が一致することを確認しました。

### Linux：古いCPUでの注意

古いx86
CPUでは、最新のNumPy等が要求するCPU命令セットに対応せず、インストールできても実行時エラーになる場合があります。

検証した Core 2 Quad Q9450 環境では最新NumPyで `X86_V2`
に関するエラーが発生しましたが、次の組み合わせで解析動作を確認しました。

``` bash
pip install "numpy<2" "scipy<1.13"
```

検証時には NumPy 1.26.4 / SciPy 1.12.0 がインストールされました。

一方、Core i7-2600 の Linux Mint / Python 3.12.3
環境では、バージョンを固定しない最新ライブラリ構成で正常動作しました。

### macOS：Pythonバージョンと依存ライブラリ

検証した macOS 12 の仮想環境では、Python 3.14
で一部依存ライブラリの互換性問題が発生したため、Python 3.11.7
を使用しました。

検証時の構築例：

``` bash
python3.11 -m venv myenv
source myenv/bin/activate
python --version
pip install --upgrade pip
pip install "numba==0.58.1"
pip install numpy scipy matplotlib librosa soundfile
```

macOS側からコンパイラ関連ツールのインストールを求められた場合は、それをインストールした後に
`pip install` を再実行することで環境を構築できました。

これらは動作確認時の実例であり、すべてのOS・Python・ライブラリの組み合わせでの動作を保証するものではありません。

## 6. 入力ファイル

解析には **正接続録音** と **逆接続録音**
の2つのステレオ音声ファイルが必要です。入力ファイルは2チャンネルのステレオである必要があります。

WAVなどの非圧縮形式を測定用途では推奨します。音声の読み込みは librosa
が対応する形式に準じます。

### 正接続

``` text
Signal Generator
   L → DUT L → Recorder L
   R → DUT R → Recorder R
```

### 逆接続

DUTを測定システムの反対側チャンネルで測定するよう、DUTの入出力に対する左右接続を入れ替えます。

``` text
Signal Generator
   L → DUT R
   R → DUT L

DUT
   L → Recorder R
   R → Recorder L
```

重要なのは、**DUTの左右チャンネルを測定システムの反対側チャンネルで測定すること**です。

正接続と逆接続では、信号条件、録音レベル、サンプルレートなど、左右入れ替え以外の測定条件を可能な限り同一にしてください。

## 7. 実行方法

基本書式：

``` bash
python stereo_band_analysis_ja.py <正接続ファイル> <逆接続ファイル> <出力フォルダ>
```

例：

``` bash
python stereo_band_analysis_ja.py normal.wav reverse.wav result
```

英語版の場合：

``` bash
python stereo_band_analysis_en.py normal.wav reverse.wav result
```

解析結果は指定した出力フォルダに保存されます。出力フォルダが存在しない場合は自動的に作成されます。

### グラフのY軸範囲を指定する

`--yrange`
オプションでBand差分グラフおよびWelch差分グラフのY軸範囲を指定できます。

``` bash
python stereo_band_analysis_ja.py normal.wav reverse.wav result --yrange -1 1
```

この例ではY軸を -1 dB ～ +1 dB に指定します。

## 8. Band解析

20 Hz ～ 20 kHz を次の10帯域に分割して左右差を解析します。

  Band
  -----------------
  20--40 Hz
  40--80 Hz
  80--160 Hz
  160--315 Hz
  315--630 Hz
  630--1250 Hz
  1250--2500 Hz
  2500--5000 Hz
  5000--10000 Hz
  10000--20000 Hz

各帯域について Welch 法でパワーを求め、正接続と逆接続それぞれの L-R
差から補正後の差分を計算します。Welch解析の `nperseg` は **4096** です。

Band解析グラフでは目安として、

-   **±0.15 dB以内：緑**
-   **±0.15 ～ ±0.30 dB：黄**
-   **±0.30 dB超：背景色なし**

で表示します。

これらは本スクリプト内の簡易判定用しきい値であり、すべてのオーディオ機器に共通する規格値を意味するものではありません。

## 9. Welch解析

Welch法により、20 Hz ～ 20 kHz
の周波数範囲について正接続／逆接続のスペクトルと補正後の左右差を求めます。

``` text
d1 = 正接続の L-R
d2 = 逆接続の L-R

Corrected Diff = (d1 - d2) / 2
```

### -100 dB 信号マスク

Welch差分の評価では、正接続録音のL/Rのうち大きい側の信号レベルが **-100
dBを超える周波数領域**を評価対象とします。

信号成分が存在しない領域や極端に低い領域を差分評価から除外し、その部分はWelch差分グラフにも描画しません。

そのため、単一周波数の正弦波など狭帯域信号では、信号が存在しない周波数領域はWelch評価対象になりません。狭帯域信号を解析する場合はBand解析結果も併せて確認してください。

### 一様な差の検出

Welch評価範囲内の最大値と最小値の差が **0.02
dB未満**の場合、全評価帯域でほぼ一定の差（Uniform
difference）として扱います。

この場合、特定周波数だけを「最大差周波数」として表示することを避けるため、Welch差分グラフの赤いピーク点およびSummaryの
`Max Diff Freq` は表示しません。

## 10. 出力ファイル

指定した出力フォルダに以下を生成します。

  ファイル                      内容
  ----------------------------- -------------------------
  `band_levels.csv`             10帯域の補正後左右差
  `diff_by_band.png`            Band解析グラフ
  `welch_spectra_normal.png`    正接続のWelchスペクトル
  `welch_spectra_reverse.png`   逆接続のWelchスペクトル
  `welch_diff.png`              補正後Welch差分グラフ
  `summary.txt`                 解析結果と簡易判定

## 11. ΔDiff と max(diff_welch)

### ΔDiff (Band)

Band解析10帯域における、

``` text
最大Diff - 最小Diff
```

です。左右差が周波数帯域によってどの程度変化しているかを見るための値です。

### ΔDiff (Welch max)

Summaryでは `ΔDiff (Welch max)`
と表示されますが、実際に出力される値はWelch評価対象内における、

``` text
max(abs(diff_welch))
```

すなわち **補正後Welch差分の絶対値の最大値**です。

Band解析の
`ΔDiff`（最大値－最小値）とは意味が異なる点に注意してください。

## 12. 簡易判定

判定には主に次の値を使用します。

``` text
SAFE = 0.15 dB
WARN = 0.30 dB
```

Band解析の `ΔDiff`
とWelch解析の最大絶対差を組み合わせ、以下のような判定を行います。

  -----------------------------------------------------------------------
  状態                                表示
  ----------------------------------- -----------------------------------
  Band ΔDiff \< 0.15 dB かつ          OK: チャンネル差は測定誤差レベル
  Welch最大差 \< 0.15 dB              

  Band ΔDiff \< 0.15 dB かつ          注意: 局所ピーク差あり
  Welch最大差 ≥ 0.30 dB               

  Band ΔDiff ≥ 0.30 dB かつ           注意: 全体ゲイン差
  Welch最大差 \< 0.30 dB              

  Band ΔDiff ≥ 0.30 dB かつ           要確認:
  Welch最大差 ≥ 0.30 dB               機器または測定条件に問題の可能性

  上記の中間領域                      中間状態
  -----------------------------------------------------------------------

Welch評価範囲がほぼ一様な差で、かつ最大差が 0.30
dB以上の場合は、局所ピークではなく **全体ゲイン差** と判定します。

この判定は解析結果を確認しやすくするための目安です。機器の合否規格そのものではありません。

## 13. Channel Check

正接続録音についてL/Rそれぞれの信号エネルギーを計算し、

``` text
Energy Ratio = L / R
```

を求めます。

Energy Ratio が **10を超える**、または
**0.1未満**の場合、チャンネル間レベルの大きな非対称として警告します。

これは解析結果とは別に、片チャンネルの断線や大きな接続不良などを確認するための補助チェックです。

## 14. シミュレーションによる検証

詳細な検証結果は以下のPDFに収録しています。

-   [シミュレーション検証結果（日本語）](docs/simulation_test_results_ja.pdf)
-   [Simulation Test Results
    (English)](docs/simulation_test_results_en.pdf)

検証資料では、信号発生器、DUT、録音器にそれぞれ異なるゲイン／EQ特性を設定し、

``` text
(正接続 - 逆接続) / 2
```

による補正後の結果とDUT単独特性の解析結果を比較しています。

その結果、測定システム側に設定した左右特性差が相殺され、DUTに設定した左右特性差がほぼ再現されることを確認しています。

また、Python生成信号、および WaveGene / Cakewalk SONAR / GClip
で作成・加工した信号を用いて、次のような条件でスクリプトの応答を確認しています。

-   左右同一信号
-   ゲイン差
-   THD付加
-   ノイズ付加
-   PEQによる周波数特性差
-   High Shelf Filterによる周波数特性差
-   1 kHz単一周波数
-   20 Hz ～ 20 kHzログスイープ

単一周波数による結果は、広帯域のDUT特性を評価するためではなく、狭帯域入力時の判定ロジックや信号マスクの挙動を確認するための参考試験です。

詳細なグラフおよび各 `summary.txt` の結果はPDFを参照してください。

## 15. 測定時の注意

本スクリプトの補正は、正接続と逆接続で
**DUT以外の測定系の特性が十分に安定していること**を前提とします。

-   正接続と逆接続で同じ信号を使用する
-   録音レベルを変更しない
-   Audio Interface等のゲイン／ボリュームを変更しない
-   DUTのボリュームや設定を変更しない
-   ケーブルやコネクタの接触状態を確認する
-   クリッピングを避ける
-   十分なS/N比を確保する
-   正接続と逆接続の間で測定系の状態が変化しないようにする

正接続と逆接続の間でゲインや周波数特性が変化した場合、その変化も補正結果に含まれます。

## 16. 本解析で分かること／分からないこと

本スクリプトが主に解析するのは **左右チャンネル間の相対的な差**です。

したがって、左右両チャンネルに同じように存在する周波数特性の変化や歪みを、絶対的な機器性能として評価するツールではありません。

また、左右差が検出された場合でも、その原因が必ずDUT内部にあるとは限りません。測定中の接続変化、ノイズ、接触不良、レベル変動なども結果に影響します。

Band解析、Welch解析、正接続／逆接続スペクトル、Summaryを総合して判断してください。

## 17. YouTube 解説動画

**Coming soon**

## 18. Version

### 1.0.0

Initial public release.

## 19. Author / Development

Concept, specifications, and validation:

**Kaneichi-Repair**

Source code was generated with AI assistance and subsequently tested and
validated for this project.

## 20. Support

本スクリプト、Python環境、依存ライブラリ、各OSでの環境構築について、Kaneichi-Repairによる個別サポートは行いません。

利用者ご自身の環境に合わせてPythonおよび必要なライブラリを管理してください。

## 21. License

This project is released under the **MIT License**.

See `LICENSE` for details.

Copyright (c) 2026 kaneichi-repair
