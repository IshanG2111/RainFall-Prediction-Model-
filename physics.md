# Physics of Satellite-Based Rainfall Prediction

This document explains the meteorological and physical principles governing the rainfall prediction model. The model relies on the relationship between satellite-observed radiative properties and atmospheric thermodynamics.

## 1. Atmospheric Thermodynamics & Instability
Rainfall, particularly convective rainfall, is driven by the instability of the atmosphere.

*   **Land Surface Temperature (LST_K)**: 
    *   **Physics**: Solar heating of the surface warms the air immediately above it, causing it to become less dense and rise (convection).
    *   **Role**: High surface temperatures provide the energy source for storm formation. A large temperature contrast between the hot surface and the cold upper atmosphere triggers strong updrafts.

## 2. Radiative Transfer & Deep Convection
Satellites primarily "see" storms by measuring the radiation emitted by the Earth and clouds.

*   **Outgoing Longwave Radiation (OLR)**:
    *   **Physics**: According to the Stefan-Boltzmann law ($E = \sigma T^4$), the energy radiated is proportional to temperature. Cloud tops are much colder than the Earth's surface.
    *   **Role**: Low OLR values indicate very cold temperatures, meaning the cloud tops are very high in the atmosphere (near the tropopause). High cloud tops are a signature of **Deep Convection**, which is associated with heavy rainfall.
    *   **Relation**: Lower OLR $\rightarrow$ Taller Clouds $\rightarrow$ Stronger Updrafts $\rightarrow$ Heavier Rain.

## 3. Cloud Microphysics
Rain formation depends on what is happening *inside* the cloud—specifically the size and density of water droplets and ice crystals.

*   **Cloud Optical Thickness (COT)**:
    *   **Physics**: Measures the attenuation of light passing through the cloud.
    *   **Role**: Optically "thick" clouds contain a high density of water droplets or ice crystals. Denser clouds have more water available to fall as rain.
*   **Cloud Effective Radius (CER)**:
    *   **Physics**: Represents the weighted average size of the cloud particles.
    *   **Role**: For rain to occur, droplets must grow large enough to overcome updrafts and fall (Collision-Coalescence process). A larger effective radius often indicates that droplets are coalescing into raindrops or snowflakes, signaling the onset of precipitation.

## 4. Moisture Dynamics
A storm needs a continuous supply of moisture to sustain itself.

*   **Upper Tropospheric Humidity (UTH)**:
    *   **Physics**: Detects water vapor in the upper atmosphere using specific IR bands (water vapor channels).
    *   **Role**: High UTH indicates a moist environment that supports cloud longevity. If the upper air is too dry, it can cause cloud tops to evaporate (entrainment), killing the storm.
*   **Wind Speed**:
    *   **Physics**: Advection (horizontal transport) of moisture.
    *   **Role**: Wind brings moisture into the storm system (moisture convergence) and influences the movement/propagation of the rain bands.

## 5. The Hydro-Estimator Method (HEM)
This is a derived physical algorithm used as a baseline.

*   **Physics**: It combines the Infrared (IR) brightness temperature with corrections for moisture, terrain, and atmospheric stability to estimate rain rate.
*   **Role in Model**: It serves as the primary satellite-derived calculation, which our Machine Learning model refines using the other parameters (COT, CER, LST) to correct for false alarms (e.g., cold cirrus clouds that don't produce rain).
