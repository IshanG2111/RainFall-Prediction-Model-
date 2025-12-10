# 🌧️ Rainfall Prediction Using INSAT-3DR Satellite Products  
Daily Rainfall Modeling · Multi-Phase Pipeline · Regression-Based Prediction

---

## 📌 Project Overview

This project builds a complete rainfall prediction pipeline using **INSAT-3DR satellite products** from MOSDAC.

All satellite data is converted into **daily features** on a **0.25° × 0.25° India grid**, and then used to train regression models across multiple incremental phases.

The pipeline grows gradually from:

**2 days → 7 days → 15 days → 60–90 days**

ensuring correctness, stability, and accuracy at each step.

---

# 🧭 Project Phases

## 🟦 Phase 0 — Project Foundation
- Create folder structure  
- Set up 0.25° spatial grid plan  
- Decide aggregation rules for each dataset  
- Choose IMC as the target variable  
- Prepare evaluation strategy

## 🟦 Phase 1 — 2-Day Pipeline (Pilot Run)
- Download & organize 2 days of all INSAT datasets  
- Validate raw data  
- Build manifest for all files  
- Build spatial grid (Step 2)  
- Convert half-hourly → daily  
- Merge datasets  
- Train a small regression model  

## 🟩 Phase 2 — 7-Day Pipeline (Early Modeling)
- Process 7 days end-to-end  
- Add lag features & time features  
- Train linear & ridge regressions  
- Generate early diagnostic plots  

## 🟧 Phase 3 — 15-Day Pipeline (Advanced Features)
- Add rolling stats, wind shear, vorticity, divergence  
- Time-based cross-validation  
- Spatial hold-out validation  
- Improve model stability  

## 🟥 Phase 4 — 60–90 Day Final Dataset (Production Model)
- Build the full dataset  
- Train final regression model  
- Deploy backend prediction API  
- Build frontend UI  
- Final reports & evaluation

---