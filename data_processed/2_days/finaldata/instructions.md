# Step 5 — FEATURE CHECK + LIGHT EDA (For Shashwat)

**Objective:** Validate that the final merged dataset is physically correct, clean, and ready for ML modeling. This is NOT heavy data science — only sanity checks.

---

## 5.1 Load the Final Dataset
```python
import pandas as pd

df = pd.read_parquet("../data_processed/2_days/finaldata/final_dataset.parquet")
df.head()
```

**Confirm that:**
- Shape ≈ 30,700 × 18
- All expected columns appear (`grid_id`, `rain_mm`, `wind_speed`, `lst_k`, `cer`, `cot`, `uth`, `olr`, `hem`, etc.)

---

## 5.2 Basic Range Checks

### 📌 Expected Physical Ranges

| Variable     | Expected Range                                  |
|--------------|-------------------------------------------------|
| `rain_mm`    | 0–500 mm/day (extreme events rare but possible) |
| `wind_speed` | 0–50 m/s                                        |
| `lst_k`      | 200–330 K (surface & cloud-top temperatures)    |
| `cer`        | 0–60 µm                                         |
| `cot`        | 0–200                                           |
| `uth`        | 0–100 %                                         |
| `olr`        | 100–330 W/m²                                    |
| `hem`        | 0–500+ mm                                       |

### ✔ Run this code:
```
df.describe().T
```

### ✔ What you must verify:

- No negative values (except legitimate ones like minor noise in CER)
- No values outside known physical limits
- LST mostly around 200 K during monsoon (expected)
- CER/COT distributions centered around 2–10, not hundreds
- OLR between 100–300

**If ANY column violates physical limits → flag it.**

---

## 5.3 Null Value Check

**Expected:** 0 missing values, or <1% missing if any remain.
```python
df.isna().sum()
```

**If any non-zero occurs:**
- Report the column
- Report number of missing values
- **DO NOT** attempt imputation (already handled in Step 4)

---

## 5.4 Quick Visual Checks (EDA)

These are sanity-visualizations to confirm feature behavior.

### 5.4.1 Rainfall Distribution (Histogram)
```python
import matplotlib.pyplot as plt

plt.hist(df["rain_mm"], bins=50)
plt.title("Rainfall Distribution (IMC Daily)")
plt.xlabel("rain_mm")
plt.ylabel("frequency")
plt.show()
```

**Expected:**
- Long tail due to extreme rainfall (>100 mm)
- Many values close to 0

This matches tropical rainfall distribution.

---

### 5.4.2 Wind Speed vs Rainfall (Scatter Plot)
```python
plt.scatter(df["wind_speed"], df["rain_mm"], alpha=0.3, s=10)
plt.xlabel("Wind Speed (m/s)")
plt.ylabel("Rainfall (mm)")
plt.title("Wind Speed vs Rainfall")
plt.show()
```

**Interpretation:**
- Weak positive trend is okay
- More scatter = normal
- No strong linear pattern required

---

### 5.4.3 LST vs Rainfall (Scatter Plot)
```python
plt.scatter(df["lst_k"], df["rain_mm"], alpha=0.3, s=10, color='orange')
plt.xlabel("LST (Kelvin)")
plt.ylabel("Rainfall (mm)")
plt.title("LST vs Rainfall")
plt.show()
```

**Expected:**
- Rain clusters when LST is low (200 K) → clouds block surface radiation
- When LST is high (~280–300 K), rainfall should be almost zero

This is a standard monsoon signature.

---

## 5.5 Interpretation Guidelines

**The teammate must confirm:**

✔ **Rainfall behaves like tropical rainfall**
- Many low values
- Tail of extreme rainfall

✔ **Wind speeds increase during high rainfall**  
Expected due to monsoon circulation.

✔ **LST drops during rainfall**  
Because clouds cool the surface and obscure IR measurement.

✔ **CER & COT**  
Should show smooth gradients — no spikes, no negatives.

✔ **OLR lower during rainfall**  
OLR decreases under thick clouds, so low OLR should correlate with rain.

---

## 5.6 Final Output for Step 5

**The teammate must produce:**

**1️⃣ A short report (bullet points) describing:**
- Whether ranges are valid
- Whether missing values exist
- Observations from scatter/histograms

**2️⃣ Screenshots or saved plots for:**
- Rainfall histogram
- Wind vs rainfall
- LST vs rainfall

**3️⃣ A confirmation statement:**

> "Dataset validated for Step 6 — modeling can proceed."