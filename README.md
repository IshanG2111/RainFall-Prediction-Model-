# 🌧️ RainFall Prediction ML Model (7-Day Forecast Across India)

A robust, data-driven machine learning pipeline designed to **predict rainfall and weather conditions for the next 7 days** for any location in India.  
Built by our 4-member team using Linear Regression, scientific preprocessing, and a modular ML architecture.

---

## 📌 Project Objective

Weather prediction is one of the most impactful use-cases of machine learning.  
Our model aims to:

- Predict **next 7 days rainfall values** for any selected location in India  
- Use **historical meteorological parameters**  
- Build a **scalable, modular pipeline** suitable for real-world deployment  
- Provide a clear **API/UI-ready prediction structure**

This project reflects an end-to-end ML workflow—from data preprocessing to deployment.

---

# 🧩 Project Architecture


### **1. Data Preprocessing**
- Handling missing values  
- Parsing dates & sorting time series  
- Engineering cyclical date features (sin/cos transformation)  
- Generating lag features (1 to 7 days)  
- 7-day rolling averages  

### **2. ML Model Training**
- Linear Regression for interpretability & baseline accuracy  
- One model per prediction horizon (Day-1 to Day-7)  
- Time-aware train/test split (no data leakage)  
- MAE & RMSE evaluation  

### **3. Prediction Module**
Takes user inputs (weather parameters) and outputs:


### **4. Deployment Ready**
The project includes a structure compatible with:

- Flask/FastAPI backend  
- Streamlit Dashboard  
- GitHub CI/CD workflows  

---


---

# 🚀 Key Features

### ✔️ 7-Day Ahead Forecast  
Predicts rainfall for Day-1 through Day-7 with seven independent regression models.

### ✔️ Modular, Clean Code  
Easy to update, extend or scale to deep learning or LSTM in the future.

### ✔️ Real-World Weather Feature Engineering  
Includes meteorology-grade features:
- Lag features  
- Rolling means  
- Cyclical day encoding  
- Normalization-ready pipeline  

### ✔️ Team Collaboration Ready  
Each module (`src/`, `notebooks/`, `app/`) can be developed independently by different team members.

---

# 📊 Example Preprocessing Workflow

- Convert `date` to datetime format  
- Sort by date  
- Create `day_of_year`, `sin/cos`  
- Generate `rain_mm_lag1` to `rain_mm_lag7`  
- Create rolling window averages  
- Drop missing rows  

---

# 🧠 Modeling Overview

Each “Day-X” forecast has its own model.

Why separate models?

- Reduces error propagation  
- Easy debugging  
- Increased accuracy across horizons  

**Model Used:**  


---

# 📈 Evaluation Metrics

- **MAE (Mean Absolute Error)** → primary metric  
- **RMSE (Root Mean Squared Error)**  
- Baseline comparison using a naïve persistence model  

---

# 🖥️ Tech Stack

- Python  
- Pandas, NumPy  
- Scikit-Learn  
- Joblib  
- Matplotlib / Seaborn  
- Jupyter Notebooks  
- FastAPI / Flask (planned for deployment)

---

# 🤝 Contributors

| Name | Role |
|------|------|
| **Saptarshi Roy** | ML Model Development, Preprocessing Pipeline, GitHub Integration |
| **Ishan Ghosh** | Repository Owner, Architecture Setup |
| **Team Members** | Data Collection, Feature Research, Testing & Documentation |

---

# 🔮 Future Enhancements

- Replace Linear Regression with **LSTM / GRU deep learning models**  
- Live API connected to IMD/NOAA weather data  
- Deploy UI dashboard using **Streamlit**  
- Geo-spatial rainfall mapping across India  

---

# ⭐ Support this project

If you find this repository useful, consider giving it a **star** on GitHub!

---

# 📜 License
This project is for academic and research purposes.
