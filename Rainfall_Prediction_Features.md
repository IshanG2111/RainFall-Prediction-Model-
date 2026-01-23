
# 🌦️ Rainfall Prediction Features (Satellite-Derived)

This document describes the key atmospheric and satellite-derived parameters used in the rainfall prediction model, along with their physical interpretation and role in forecasting.

---

## 1. HEM (Hydro-Estimator Method)

**What it is**  
A satellite-derived estimate of rainfall intensity.

**Role**  
This is the **most critical feature**. HEM estimates rainfall using cloud-top temperature. Colder cloud tops generally indicate taller, stronger storm clouds, which are capable of producing heavier rainfall.

**Unit**  
- Millimetres (mm)

---

## 2. LST_K (Land Surface Temperature)

**What it is**  
The temperature of the Earth's ground surface.

**Role**  
Plays a key role in convection. Hot surface temperatures cause air to rise, fueling storm development. A strong contrast between warm land surface temperature and cold cloud-top temperature indicates atmospheric instability.

**Unit**  
- Kelvin (K)  
- Conversion to Celsius:  
  ```
  °C = K − 273.15
  ```

---

## 3. OLR (Outgoing Longwave Radiation)

**What it is**  
The amount of thermal energy radiated from the Earth and cloud tops back into space.

**Role**
- **High OLR** → Clear skies or low, warm clouds (fair weather)
- **Low OLR** → High, cold storm clouds (rainy conditions)

Lower OLR values are strongly associated with deep convection and precipitation.

**Unit**  
- Watts per square meter (W/m²)

---

## 4. UTH (Upper Tropospheric Humidity)

**What it is**  
The moisture content in the upper layers of the atmosphere.

**Role**  
High upper-level humidity supports sustained cloud growth and prevents evaporation of cloud tops. Dry upper air can suppress or weaken storm systems.

**Unit**  
- Percentage (%)

---

## 5. CER (Cloud Effective Radius)

**What it is**  
The average size of water droplets or ice crystals inside a cloud.

**Role**  
Larger droplets or ice crystals have a higher probability of falling as precipitation. Increasing CER often signals rain initiation or intensification.

**Unit**  
- Microns (μm)

---

## 6. COT (Cloud Optical Thickness)

**What it is**  
A measure of how much sunlight a cloud blocks (cloud density).

**Role**  
Thicker clouds (higher COT) contain more condensed water and typically correspond to stronger rainfall potential.

**Unit**  
- Dimensionless (unitless number)

---

## 7. Wind Speed

**What it is**  
The speed of atmospheric air movement.

**Role**  
Indicates moisture transport and storm propagation. Wind helps organize storms, transport humid air, and sustain rainfall systems.

**Unit**  
- Meters per second (m/s)

---

## 🧠 Summary of Model Logic

The model learns combined atmospheric patterns rather than relying on a single parameter.

**Example Interpretation:**
- **Low OLR** → Tall, cold storm clouds  
- **High COT** → Thick, water-laden clouds  
- **High HEM** → Satellite-confirmed rainfall signal  

➡️ **Prediction: Heavy Rainfall**
