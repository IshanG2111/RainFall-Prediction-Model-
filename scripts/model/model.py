import pandas as pd

class PhysicsConstraints:
    """
    Handles physics-based constraints and sanity checks for the Rainfall Model.
    Ref: Physics-Based Rules for Rainfall Prediction (Indian Context)
    """
    
    @staticmethod
    def apply_hard_clamps(df, is_processed=False):
        """
        Apply hard physical clamps to the dataframe.
        Used for both training (data cleaning) and inference (post-processing).
        
        Args:
            df (pd.DataFrame): Dataframe with features (hem, olr, uth, etc.) and 'rain_mm' (if training/cleaning).
            is_processed (bool): If True, assumes input is processed features ready for inference. 
                                 If False, assumes raw data during cleaning.
        """
        # We need specific columns. If they are missing, we skip those rules or warn.
        # Required: olr, uth, wind_speed, lst_k, cer, cot
        # Optional: rain_mm, date/month (for seasonal rules), lat/lon (for spatial rules)
        
        # Working with a copy to avoid SettingWithCopy warnings on slices if any
        df = df.copy()
        
        # --- 1. Warm Rain Fix (OLR) ---
        # Rule: OLR > 260 => Rain = 0
        mask_warm_rain = df['olr'] > 260
        if 'rain_mm' in df.columns:
            df.loc[mask_warm_rain, 'rain_mm'] = 0
            
        # --- 2. Warm Cloud Moisture Check ---
        # Rule: OLR > 200 AND UTH < 40% => Rain <= 5
        mask_warm_dry = (df['olr'] > 200) & (df['uth'] < 40)
        if 'rain_mm' in df.columns:
            df.loc[mask_warm_dry, 'rain_mm'] = df.loc[mask_warm_dry, 'rain_mm'].clip(upper=5)
            
        # --- 3. Haze Filter (Aerosol) ---
        # Rule: COT < 8 => Rain <= 2
        feature_cot = 'cot' if 'cot' in df.columns else None
        if feature_cot:
            mask_haze = df[feature_cot] < 8
            if 'rain_mm' in df.columns:
                df.loc[mask_haze, 'rain_mm'] = df.loc[mask_haze, 'rain_mm'].clip(upper=2)
                
        return df

    @staticmethod
    def get_regime(row):
        """
        Determine the meteorological regime based on OLR, UTH, etc.
        Returns: Str (Regime Name)
        """
        olr = row.get('olr', 300)
        
        if olr > 260:
            return "Clear/Haze"
        elif 220 <= olr <= 260:
            # Check UTH for Shallow Monsoon vs just Warm
            uth = row.get('uth', 0)
            if uth >= 70: 
                return "Shallow Monsoon"
            return "Warm Cloud"
        elif 140 <= olr < 190:
            return "Deep Convection"
        elif olr < 140:
            return "Cyclone/Storm"
        
        return "Transitional"

    @staticmethod
    def apply_post_inference_adjustments(prediction, features):
        """
        Apply sanity checks and adjustments to a single prediction result.
        
        Args:
            prediction (float): The raw predicted rainfall (mm).
            features (dict): The input features used for prediction. 
                             Must include: lat, lon, month, olr, uth, etc.
        
        Returns:
            float: Adjusted rainfall prediction.
            str: Status/Reason for adjustment (optional)
        """
        final_rain = prediction
        reason = "Model Raw"
        
        lat = features.get('latitude', 0)
        lon = features.get('longitude', 0)
        month = features.get('month', 1) 
        olr = features.get('olr', 250)
        uth = features.get('uth', 50)
        features.get('elevation', 0)
        
        # --- Hard Clamps (Redundant safeguard) ---
        if olr > 260:
            return 0.0, "Physical Clamp (OLR > 260)"
            
        if olr > 200 and uth < 40:
            final_rain = min(final_rain, 5.0)
            reason = "Physical Clamp (Warm/Dry)"

        # --- Sanity: Desert Check ---
        # IF Lat > 24°N AND Lon < 73°E (Rajasthan) AND Month != {Jul, Aug}
        is_rajasthan = (lat > 24) and (lon < 73)
        is_monsoon = month in [7, 8]
        if is_rajasthan and not is_monsoon:
            if final_rain > 10:
                final_rain *= 0.1 # Aggressive dampen
                reason = "Desert Sanity Filter"

        # --- Sanity: Winter Dryness ---
        # Month {12, 1} AND Lat > 15°N => Rain <= 20
        if month in [12, 1] and lat > 15:
            if final_rain > 20:
                final_rain = 20.0
                reason = "Winter Dryness Clamp"

        return final_rain, reason