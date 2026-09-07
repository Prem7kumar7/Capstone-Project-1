import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone
from backend.app.config import settings
from backend.app.providers.open_meteo import open_meteo_provider
from backend.app.hydrology.simplified_drainage import evaluate_simplified_drainage_limitation
from backend.app.risk.risk_engine import calculate_flood_risk_score
from backend.app.risk.depth_estimator import estimate_water_depth
from backend.app.risk.time_to_flood import calculate_estimated_time_to_flood
from backend.app.risk.alert_service import generate_alert_advisory
from backend.app.utils.geo import utc_to_ist_str

# Verified Key Observation Points around LPU and NH-44 corridor
VERIFIED_MONITORING_NODES = [
    {
        "id": 1,
        "name": "NH-44 Underpass near LPU Gate 1",
        "latitude": 31.2530,
        "longitude": 75.6985,
        "elevation_m": 233.1,
        "is_depression": True,
        "depression_drop_m": 2.8,
        "slope_deg": 3.2,
        "land_cover_type": "impervious_paved_roof",
        "cn": 98,
        "area_m2": 15000.0,
        "drainage_available": False,
        "notes": "Low-lying underpass; natural topographic depression prone to water accumulation during intense rainfall."
    },
    {
        "id": 2,
        "name": "LPU Main Gate 1 Apron (NH-44 Entry)",
        "latitude": 31.2528,
        "longitude": 75.6990,
        "elevation_m": 236.2,
        "is_depression": False,
        "depression_drop_m": 0.0,
        "slope_deg": 1.2,
        "land_cover_type": "impervious_paved_roof",
        "cn": 98,
        "area_m2": 25000.0,
        "drainage_available": False,
        "notes": "Primary entrance corridor; heavy vehicular movement."
    },
    {
        "id": 3,
        "name": "South Campus Drainage Retention Area",
        "latitude": 31.2480,
        "longitude": 75.7040,
        "elevation_m": 234.8,
        "is_depression": True,
        "depression_drop_m": 1.5,
        "slope_deg": 1.5,
        "land_cover_type": "open_lawns_parks",
        "cn": 69,
        "area_m2": 45000.0,
        "drainage_available": False,
        "notes": "Natural unpaved retention sink absorbing campus runoff."
    },
    {
        "id": 4,
        "name": "Academic Central Plaza (Block 30-38)",
        "latitude": 31.2545,
        "longitude": 75.7038,
        "elevation_m": 239.5,
        "is_depression": False,
        "depression_drop_m": 0.0,
        "slope_deg": 0.6,
        "land_cover_type": "academic_complex",
        "cn": 92,
        "area_m2": 60000.0,
        "drainage_available": False,
        "notes": "Core academic quadrangle on elevated terrain."
    },
    {
        "id": 5,
        "name": "Hostels Residential Zone",
        "latitude": 31.2575,
        "longitude": 75.7060,
        "elevation_m": 237.4,
        "is_depression": False,
        "depression_drop_m": 0.0,
        "slope_deg": 0.8,
        "land_cover_type": "hostel_residential",
        "cn": 79,
        "area_m2": 80000.0,
        "drainage_available": False,
        "notes": "High density residential area with green corridors."
    },
    {
        "id": 6,
        "name": "Gate 2 Access Road (Chaheru Side)",
        "latitude": 31.2595,
        "longitude": 75.7010,
        "elevation_m": 237.8,
        "is_depression": False,
        "depression_drop_m": 0.0,
        "slope_deg": 1.1,
        "land_cover_type": "impervious_paved_roof",
        "cn": 95,
        "area_m2": 20000.0,
        "drainage_available": False,
        "notes": "Northern access road connecting towards Chaheru railway station."
    }
]

async def execute_nowcasting_pipeline(
    is_simulation: bool = False,
    sim_intensity_mm_h: float = 0.0,
    sim_cumulative_mm: float = 0.0,
    sim_clogging_fraction: float = 0.0
) -> Dict[str, Any]:
    """
    Executes the full hydrological and flood-risk nowcasting pipeline.
    Works for both LIVE mode and SIMULATION mode with complete data transparency.
    """
    now_utc = datetime.now(timezone.utc)
    run_id = f"UF-{now_utc.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    if is_simulation:
        intensity_mm_h = sim_intensity_mm_h
        cumulative_6h_mm = sim_cumulative_mm
        max_forecast_mm_h = sim_intensity_mm_h
        clogging = sim_clogging_fraction
        exec_mode = "SIMULATED"
        provenance = "SIMULATED"
        data_sources = ["Simulation Engine (Synthetic Input Parameters)"]
    else:
        # Fetch LIVE data from Open-Meteo
        weather = await open_meteo_provider.get_current_and_forecast()
        intensity_mm_h = weather.get("precipitation_mm_h", 0.0)
        cumulative_6h_mm = weather.get("cumulative_forecast_6h_mm", 0.0)
        max_forecast_mm_h = weather.get("max_forecast_intensity_mm_h", 0.0)
        clogging = 0.0
        exec_mode = "LIVE"
        provenance = "LIVE"
        data_sources = [weather.get("data_source", "Open-Meteo NWP"), "Copernicus DEM", "OpenStreetMap"]

    # Effective intensity to test (current or maximum forecast intensity)
    effective_intensity = max(intensity_mm_h, max_forecast_mm_h * 0.7)

    hotspots = []
    max_risk = 0.0
    highest_depth_bracket = "< 0.10 m"
    earliest_time = "> 6 hours / Low Risk"
    affected_count = 0

    for node in VERIFIED_MONITORING_NODES:
        # 1. Evaluate simplified drainage & runoff
        drain_res = evaluate_simplified_drainage_limitation(
            rainfall_intensity_mm_h=effective_intensity,
            cumulative_rainfall_mm=cumulative_6h_mm,
            cn=node["cn"],
            area_m2=node["area_m2"],
            is_depression=node["is_depression"],
            depression_drop_m=node["depression_drop_m"],
            drainage_clogging_fraction=clogging,
            drainage_available=node["drainage_available"]
        )

        # 2. Calculate Flood Risk Score (0-100)
        impervious_pct = 0.95 if node["cn"] >= 95 else (0.65 if node["cn"] >= 79 else 0.20)
        risk_res = calculate_flood_risk_score(
            forecast_rainfall_intensity_mm_h=effective_intensity,
            cumulative_rainfall_mm=cumulative_6h_mm,
            is_depression=node["is_depression"],
            depression_drop_m=node["depression_drop_m"],
            slope_deg=node["slope_deg"],
            impervious_fraction=impervious_pct,
            drainage_clogging_fraction=clogging,
            drainage_available=node["drainage_available"]
        )
        score = risk_res["flood_risk_score"]
        cat = risk_res["risk_category"]

        # 3. Water Depth bracket (MODEL ESTIMATE)
        depth_res = estimate_water_depth(
            ponding_depth_m=drain_res["estimated_ponding_depth_m"],
            is_depression=node["is_depression"],
            depression_drop_m=node["depression_drop_m"]
        )

        # 4. Estimated Time-to-flood (ESTIMATED)
        time_res = calculate_estimated_time_to_flood(
            rainfall_intensity_mm_h=effective_intensity,
            current_depth_m=depth_res["estimated_depth_m"],
            is_depression=node["is_depression"]
        )

        if score > max_risk:
            max_risk = score
            highest_depth_bracket = depth_res["estimated_depth_bracket"]
            earliest_time = time_res["estimated_time_to_flood"]

        if score >= 40.0:
            affected_count += 1

        hotspots.append({
            "id": node["id"],
            "location_name": node["name"],
            "latitude": node["latitude"],
            "longitude": node["longitude"],
            "elevation_m": node["elevation_m"],
            "flood_risk_score": score,
            "risk_category": cat,
            "estimated_depth_bracket": depth_res["estimated_depth_bracket"],
            "estimated_depth_label": "MODEL ESTIMATE",
            "estimated_time_to_flood": time_res["estimated_time_to_flood"],
            "estimated_time_label": "ESTIMATED",
            "susceptibility_factors": {
                "is_depression": node["is_depression"],
                "slope_deg": node["slope_deg"],
                "land_cover": node["land_cover_type"],
                "curve_number": node["cn"],
                "surcharge_ratio": drain_res["surcharge_ratio"],
                "notes": node["notes"]
            },
            "data_provenance": provenance
        })

    # Overall severity
    if max_risk >= 80.0:
        overall_sev = "EXTREME"
    elif max_risk >= 60.0:
        overall_sev = "HIGH"
    elif max_risk >= 40.0:
        overall_sev = "MODERATE"
    elif max_risk >= 20.0:
        overall_sev = "LOW"
    else:
        overall_sev = "VERY_LOW"

    return {
        "run_id": run_id,
        "study_area_id": settings.DEFAULT_STUDY_AREA_ID,
        "run_timestamp_utc": now_utc.isoformat(),
        "run_timestamp_ist": utc_to_ist_str(now_utc),
        "execution_mode": exec_mode,
        "modelling_mode": "SIMPLIFIED_RUNOFF_LIMITATION",
        "current_rainfall_mm_h": round(intensity_mm_h, 1),
        "forecast_cumulative_6h_mm": round(cumulative_6h_mm, 1),
        "max_forecast_intensity_mm_h": round(max_forecast_mm_h, 1),
        "drainage_clogging_fraction": round(clogging, 2),
        "max_flood_risk_score": round(max_risk, 1),
        "overall_severity": overall_sev,
        "highest_estimated_depth_bracket": highest_depth_bracket,
        "earliest_time_to_flood": earliest_time,
        "affected_hotspots_count": affected_count,
        "confidence_level": "LOW" if not is_simulation and intensity_mm_h == 0 else "MEDIUM",
        "data_sources": data_sources,
        "model_version": "0.1.0-alpha",
        "is_simulation": is_simulation,
        "hotspots": hotspots
    }
