# Stereo Band Gain Difference Analyzer

[日本語 README](README_ja.md)

**Stereo Band Gain Difference Analyzer** is a Python script for
analyzing level and frequency-response differences between the left and
right channels of stereo audio.

The same DUT (Device Under Test) is recorded in two configurations: a
**normal connection** and a **reversed L/R connection**. The two
measurements are then used to reduce the influence of left/right
differences in the measurement system itself and extract the channel
difference attributable to the DUT.

Version: **1.0.0**\
Author: **Kaneichi-Repair**\
License: **MIT**

> This script is intended to assist in analyzing measurement results.
> Its automatic judgement does not constitute a definitive diagnosis.
> Interpret the results together with the measurement conditions,
> connections, signal level, noise, and equipment used.

## 1. Analysis concept

In a normal stereo measurement, the observed L/R difference includes not
only the DUT but also channel differences in the signal-generation and
recording sides of the measurement system.

This script records the same DUT under two conditions, **normal
connection** and **reversed connection**, and calculates the L-R
difference for each recording.

``` text
Corrected L/R difference = (L-R difference in normal connection - L-R difference in reversed connection) / 2
```

The purpose of this method is to cancel channel differences that remain
on the same measurement-system channels in the normal and reversed
measurements, thereby extracting the L/R difference of the DUT.

The accompanying simulation document intentionally assigns different L/R
gain and EQ characteristics to the signal generator, DUT, and recorder,
and confirms that the corrected result closely reproduces the
characteristics of the DUT alone.

## 2. Main features

-   Analysis of two stereo audio files recorded with normal and reversed
    connections
-   Compensation for measurement-system L/R differences by reversing the
    measurement connections
-   **Band analysis** over 10 bands from 20 Hz to 20 kHz
-   Frequency-by-frequency L/R difference analysis using Welch's method
-   Exclusion of low-signal regions at or below -100 dB from Welch
    evaluation
-   Graph output for Band and Welch analyses
-   Band-analysis results saved in CSV format
-   Summary and automatic judgement saved as text
-   Warning for extreme L/R channel-level asymmetry
-   Simple automatic judgement based on the analysis results
-   Japanese / English display

## 3. Published files

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

`stereo_band_analysis_en.py` and `stereo_band_analysis_ja.py` are
functionally identical. The only difference is the Language setting in
the script.

English version:

``` python
LANG = "en"
```

Japanese version:

``` python
LANG = "ja"
```

This setting changes the language used for console messages, the
Summary, graph titles, and other displayed text.

## 4. Requirements

Python 3 and the following packages are used:

-   NumPy
-   SciPy
-   Matplotlib
-   librosa
-   soundfile

Typical installation:

``` bash
pip install numpy scipy matplotlib librosa soundfile
```

Using a virtual environment (`venv`) is recommended. Python and library
installation/management procedures vary depending on the OS and Python
version, so configure them as appropriate for your environment.

### Fonts for Japanese graphs

The Japanese version automatically selects an available Japanese font
from the following candidates:

-   Yu Gothic / Meiryo --- Windows
-   Hiragino Sans / Hiragino Kaku Gothic ProN --- macOS
-   Noto Sans CJK JP / Noto Sans JP --- Linux and other environments

If none of the candidate Japanese fonts is found, the script displays a
warning and falls back to DejaVu Sans. In that case, Japanese text may
not be displayed correctly.

## 5. Tested environments

Version 1.0.0 was tested on Windows, Linux, and macOS using the same
test audio files, with both the analysis operation and output results
checked.

-   **Windows 11** --- Japanese and English versions tested
-   **Linux Mint / Python 3.12.3** --- Japanese and English versions
    tested
-   **macOS 12 (virtual environment) / Python 3.11.7** --- Japanese and
    English versions tested

The same test signals were analyzed in each environment, and the
numerical results of the Band analysis and Summary were confirmed to
match.

### Linux: note for older CPUs

On older x86 CPUs, recent versions of NumPy and related libraries may
require CPU instruction sets that are not supported, which can cause
runtime errors even if installation succeeds.

On the tested Core 2 Quad Q9450 system, a recent NumPy version produced
an `X86_V2`-related error. Analysis worked with the following version
constraints:

``` bash
pip install "numpy<2" "scipy<1.13"
```

The tested installation resulted in NumPy 1.26.4 / SciPy 1.12.0.

By contrast, on a Core i7-2600 system running Linux Mint / Python
3.12.3, the script ran correctly with the current libraries installed
without version pinning.

### macOS: Python version and dependencies

In the tested macOS 12 virtual environment, Python 3.14 encountered
compatibility issues with some dependencies, so Python 3.11.7 was used.

Example of the tested setup:

``` bash
python3.11 -m venv myenv
source myenv/bin/activate
python --version
pip install --upgrade pip
pip install "numba==0.58.1"
pip install numpy scipy matplotlib librosa soundfile
```

If macOS requests installation of compiler-related tools, install them
and then run the `pip install` command again.

These are examples from the tested environments and do not guarantee
operation with every combination of OS, Python version, and library
versions.

## 6. Input files

Two **stereo audio files** are required: a **normal-connection
recording** and a **reversed-connection recording**. Each input file
must contain two stereo channels.

For measurement use, an uncompressed format such as WAV is recommended.
Audio-file loading follows the formats supported by librosa.

### Normal connection

``` text
Signal Generator
   L → DUT L → Recorder L
   R → DUT R → Recorder R
```

### Reversed connection

Reverse the L/R connections at both the input and output of the DUT so
that each DUT channel is measured through the opposite channel of the
measurement system.

``` text
Signal Generator
   L → DUT R
   R → DUT L

DUT
   L → Recorder R
   R → Recorder L
```

The important point is to **measure each DUT channel through the
opposite channel of the measurement system**.

Between the normal and reversed recordings, keep all measurement
conditions other than the L/R reversal as identical as possible,
including the test signal, recording level, and sample rate.

## 7. Usage

Basic syntax:

``` bash
python stereo_band_analysis_en.py <normal_file> <reversed_file> <output_folder>
```

Example:

``` bash
python stereo_band_analysis_en.py normal.wav reverse.wav result
```

Japanese version:

``` bash
python stereo_band_analysis_ja.py normal.wav reverse.wav result
```

Analysis results are saved in the specified output folder. If the folder
does not exist, it is created automatically.

### Specifying the graph Y-axis range

Use `--yrange` to specify the Y-axis range of the Band-difference and
Welch-difference graphs.

``` bash
python stereo_band_analysis_en.py normal.wav reverse.wav result --yrange -1 1
```

In this example, the Y-axis is set to -1 dB to +1 dB.

## 8. Band analysis

The 20 Hz to 20 kHz range is divided into the following 10 bands:

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

Power is calculated for each band using Welch's method, and the
corrected difference is obtained from the L-R differences of the normal
and reversed recordings. The Welch-analysis `nperseg` value is **4096**.

As a visual guide, the Band-analysis graph uses:

-   **Within ±0.15 dB: green**
-   **±0.15 to ±0.30 dB: yellow**
-   **Beyond ±0.30 dB: no background color**

These are thresholds used by this script for its simple judgement logic.
They are not universal specification limits for all audio equipment.

## 9. Welch analysis

Welch's method is used to calculate the spectra of the normal and
reversed recordings and the corrected L/R difference over the 20 Hz to
20 kHz range.

``` text
d1 = L-R in the normal recording
d2 = L-R in the reversed recording

Corrected Diff = (d1 - d2) / 2
```

### -100 dB signal mask

For Welch-difference evaluation, only frequency regions where the higher
of the L/R signal levels in the normal recording is **above -100 dB**
are evaluated.

Regions with no meaningful signal component or extremely low signal
levels are excluded from the difference evaluation and are not drawn in
the Welch-difference graph.

Therefore, with narrowband signals such as a single sine wave, frequency
regions without signal are excluded from the Welch evaluation. When
analyzing narrowband signals, also refer to the Band-analysis results.

### Uniform-difference detection

If the difference between the maximum and minimum corrected Welch values
within the evaluated region is **less than 0.02 dB**, the result is
treated as a nearly uniform difference across the evaluated region.

In this case, to avoid presenting an arbitrary frequency as a specific
maximum-difference frequency, the red peak marker in the
Welch-difference graph and `Max Diff Freq` in the Summary are omitted.

## 10. Output files

The following files are generated in the specified output folder:

| File | Description |
|---|---|
| `band_levels.csv` | Corrected L/R difference for the 10 bands |
| `diff_by_band.png` | Band-analysis graph |
| `welch_spectra_normal.png` | Welch spectra for the normal recording |
| `welch_spectra_reverse.png` | Welch spectra for the reversed recording |
| `welch_diff.png` | Corrected Welch-difference graph |
| `summary.txt` | Analysis results and simple automatic judgement |

If files with the same names already exist in the specified output folder, they will be overwritten without confirmation.

## 11. ΔDiff and max(diff_welch)

### ΔDiff (Band)

For the 10 Band-analysis values:

``` text
maximum Diff - minimum Diff
```

This value indicates how much the L/R difference changes across the
frequency bands.

### ΔDiff (Welch max)

The Summary label is `ΔDiff (Welch max)`, but the actual value is:

``` text
max(abs(diff_welch))
```

within the evaluated Welch region --- in other words, the **maximum
absolute value of the corrected Welch difference**.

Note that this differs in meaning from Band-analysis `ΔDiff`, which is
the maximum value minus the minimum value.

## 12. Simple automatic judgement

The main thresholds are:

``` text
SAFE = 0.15 dB
WARN = 0.30 dB
```

The Band-analysis `ΔDiff` and the maximum absolute Welch difference are
combined as follows:

  -----------------------------------------------------------------------
  Condition                           Display
  ----------------------------------- -----------------------------------
  Band ΔDiff \< 0.15 dB and Welch max OK: Channel difference is within
  \< 0.15 dB                          measurement tolerance.

  Band ΔDiff \< 0.15 dB and Welch max Warning: Localized peak difference
  ≥ 0.30 dB                           detected.

  Band ΔDiff ≥ 0.30 dB and Welch max  Warning: Overall gain difference
  \< 0.30 dB                          detected.

  Band ΔDiff ≥ 0.30 dB and Welch max  Check required: Possible equipment
  ≥ 0.30 dB                           or measurement problem.

  Intermediate regions not covered    Intermediate condition
  above                               
  -----------------------------------------------------------------------

If the Welch difference is nearly uniform across the evaluated region
and its maximum absolute value is 0.30 dB or greater, it is judged as an
**overall gain difference** rather than a localized peak.

This automatic judgement is intended only as a guide for reviewing the
analysis results. It is not a pass/fail specification for the equipment.

## 13. Channel Check

For the normal recording, the signal energy of the L and R channels is
calculated as:

``` text
Energy Ratio = L / R
```

If the Energy Ratio is **greater than 10** or **less than 0.1**, the
script warns that there is a large channel-level asymmetry.

This is an auxiliary check, separate from the main analysis, intended to
help identify conditions such as an open channel or a major connection
fault.

## 14. Simulation validation

Detailed validation results are included in the following PDFs:

-   [Simulation Test Results
    (English)](docs/simulation_test_results_en.pdf)
-   [シミュレーション検証結果（日本語）](docs/simulation_test_results_ja.pdf)

The validation document assigns different gain/EQ characteristics to the
signal generator, DUT, and recorder and compares the result of:

``` text
(normal connection - reversed connection) / 2
```

with the analysis result of the DUT characteristics alone.

The results confirm that the L/R characteristics assigned to the
measurement system are canceled and that the L/R characteristics
assigned to the DUT are closely reproduced.

The script response was also checked using Python-generated signals and
signals created or processed with WaveGene / Cakewalk SONAR / GClip
under conditions including:

-   Identical L/R signals
-   Gain differences
-   Added THD
-   Added noise
-   Frequency-response differences created with PEQ
-   Frequency-response differences created with a High Shelf Filter
-   1 kHz single-tone signals
-   20 Hz to 20 kHz logarithmic sweeps

The single-tone results are not intended to evaluate broadband DUT
frequency characteristics. They are reference tests used to examine the
judgement logic and signal-mask behavior with narrowband input signals.

See the PDFs for detailed graphs and the corresponding `summary.txt`
results.

## 15. Measurement precautions

The correction method used by this script assumes that the
characteristics of the **measurement system other than the DUT remain
sufficiently stable** between the normal and reversed recordings.

-   Use the same test signal for the normal and reversed recordings
-   Do not change the recording level
-   Do not change the gain or volume settings of the audio interface or
    other measurement equipment
-   Do not change the DUT volume or settings
-   Check cable and connector contact conditions
-   Avoid clipping
-   Maintain sufficient signal-to-noise ratio
-   Avoid changes in the measurement-system condition between the normal
    and reversed recordings

If gain or frequency response changes between the normal and reversed
recordings, those changes will also affect the corrected result.

## 16. What this analysis can and cannot determine

This script primarily analyzes **relative differences between the left
and right channels**.

It is not intended to evaluate changes in frequency response or
distortion that occur equally in both channels as absolute DUT
performance.

Also, even when an L/R difference is detected, the cause is not
necessarily inside the DUT. Changes in connections during measurement,
noise, poor contact, level variation, and other measurement conditions
can also affect the result.

Interpret the Band analysis, Welch analysis, normal/reversed spectra,
and Summary together.

## 17. YouTube tutorial

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

Kaneichi-Repair does not provide individual support for this script,
Python environments, dependency libraries, or environment setup on
individual operating systems.

Users are responsible for managing Python and the required libraries for
their own environments.

## 21. License

This project is released under the **MIT License**.

See `LICENSE` for details.

Copyright (c) 2026 kaneichi-repair
