# 🌧️ Rainfall Prediction Model (Grid-Based)

This project implements a **grid-based rainfall prediction system** using **Multiple Linear Regression (Ridge Regression)**.  
The model predicts rainfall by mapping user-selected locations (cities) to predefined spatial grids and using meteorological features to estimate rainfall.

---

## 📌 Project Overview

- **Approach:** Grid-based spatial regression
- **Model Used:** Ridge Regression (Multiple Linear Regression with regularization)
- **Data Format:** `.parquet`
- **Prediction Type:** Inference-based (demo for next 7 days)
- **Geographic Scope:** India (grid-based)

---

## 🧠 Core Idea

Instead of predicting rainfall directly for a city, the system:

1. Maps the city’s latitude & longitude to the **nearest spatial grid**
2. Extracts grid-level meteorological features
3. Predicts rainfall using a trained regression model
4. Generates rainfall estimates for the **next 7 days (demo mode)**

This approach reflects how real-world meteorological systems operate.

---

## 📁 Project Structure

