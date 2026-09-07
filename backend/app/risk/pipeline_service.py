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
# Verified Key Observation Points across all 4 study regions
REGION_MONITORING_NODES: Dict[str, List[Dict[str, Any]]] = {
    "lpu_main_campus": [
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
    ],
    "chaheru": [
        {
            "id": 101,
            "name": "Chaheru Railway Station Underpass",
            "latitude": 31.2612,
            "longitude": 75.6925,
            "elevation_m": 231.8,
            "is_depression": True,
            "depression_drop_m": 2.5,
            "slope_deg": 2.8,
            "land_cover_type": "impervious_paved_roof",
            "cn": 95,
            "area_m2": 18000.0,
            "drainage_available": False,
            "notes": "Low railway underpass prone to immediate water pooling during heavy rainfall."
        },
        {
            "id": 102,
            "name": "NH-44 Chaheru Stream Bridge Low Apron",
            "latitude": 31.2580,
            "longitude": 75.6940,
            "elevation_m": 232.4,
            "is_depression": True,
            "depression_drop_m": 1.8,
            "slope_deg": 2.1,
            "land_cover_type": "impervious_paved_roof",
            "cn": 98,
            "area_m2": 22000.0,
            "drainage_available": False,
            "notes": "Bridge approach corridor over Chaheru natural drainage stream."
        },
        {
            "id": 103,
            "name": "Chaheru Village Junction Road",
            "latitude": 31.2650,
            "longitude": 75.6890,
            "elevation_m": 234.0,
            "is_depression": False,
            "depression_drop_m": 0.0,
            "slope_deg": 0.9,
            "land_cover_type": "hostel_residential",
            "cn": 82,
            "area_m2": 30000.0,
            "drainage_available": False,
            "notes": "Residential and small business street intersection."
        },
        {
            "id": 104,
            "name": "Downstream Agricultural Inundation Fringe",
            "latitude": 31.2460,
            "longitude": 75.6860,
            "elevation_m": 231.2,
            "is_depression": True,
            "depression_drop_m": 1.2,
            "slope_deg": 0.5,
            "land_cover_type": "agricultural_fringe",
            "cn": 72,
            "area_m2": 60000.0,
            "drainage_available": False,
            "notes": "Low-lying cultivated floodplain receiving overflow from Chaheru stream."
        }
    ],
    "phagwara_urban": [
        {
            "id": 201,
            "name": "Chachoki NH-44 Railway Underpass",
            "latitude": 31.2180,
            "longitude": 75.7650,
            "elevation_m": 246.5,
            "is_depression": True,
            "depression_drop_m": 3.0,
            "slope_deg": 3.4,
            "land_cover_type": "impervious_paved_roof",
            "cn": 98,
            "area_m2": 25000.0,
            "drainage_available": False,
            "notes": "Major vehicular underpass connecting Chachoki and Phagwara; recurrent deep waterlogging."
        },
        {
            "id": 202,
            "name": "Satnampura Urban Low Pocket",
            "latitude": 31.2220,
            "longitude": 75.7680,
            "elevation_m": 247.8,
            "is_depression": True,
            "depression_drop_m": 1.6,
            "slope_deg": 1.5,
            "land_cover_type": "hostel_residential",
            "cn": 88,
            "area_m2": 40000.0,
            "drainage_available": False,
            "notes": "Densely populated residential neighborhood with choked roadside drains."
        },
        {
            "id": 203,
            "name": "Phagwara Bus Stand Flyover Underpass",
            "latitude": 31.2240,
            "longitude": 75.7720,
            "elevation_m": 248.2,
            "is_depression": True,
            "depression_drop_m": 2.2,
            "slope_deg": 2.7,
            "land_cover_type": "impervious_paved_roof",
            "cn": 98,
            "area_m2": 20000.0,
            "drainage_available": False,
            "notes": "Bus terminus junction; critical arterial transit bottleneck."
        },
        {
            "id": 204,
            "name": "Phagwara Choe Stormwater Outfall Bank",
            "latitude": 31.2150,
            "longitude": 75.7500,
            "elevation_m": 245.0,
            "is_depression": True,
            "depression_drop_m": 1.4,
            "slope_deg": 1.1,
            "land_cover_type": "open_lawns_parks",
            "cn": 75,
            "area_m2": 55000.0,
            "drainage_available": False,
            "notes": "Open outfall channel discharging municipal storm runoff."
        },
        {
            "id": 205,
            "name": "Model Town High Ground Ridge",
            "latitude": 31.2290,
            "longitude": 75.7810,
            "elevation_m": 252.0,
            "is_depression": False,
            "depression_drop_m": 0.0,
            "slope_deg": 0.8,
            "land_cover_type": "hostel_residential",
            "cn": 78,
            "area_m2": 50000.0,
            "drainage_available": False,
            "notes": "Naturally elevated residential sector with minimal flood susceptibility."
        }
    ],
    "jalandhar_metro": [
        {
            "id": 301,
            "name": "Damoria Railway Bridge Underpass",
            "latitude": 31.3340,
            "longitude": 75.5820,
            "elevation_m": 238.5,
            "is_depression": True,
            "depression_drop_m": 3.2,
            "slope_deg": 3.8,
            "land_cover_type": "impervious_paved_roof",
            "cn": 98,
            "area_m2": 22000.0,
            "drainage_available": False,
            "notes": "Historic underpass notorious for 3-4 feet inundation during intense storms."
        },
        {
            "id": 302,
            "name": "Rama Mandi NH-44 Chowk Depression",
            "latitude": 31.3120,
            "longitude": 75.6150,
            "elevation_m": 240.2,
            "is_depression": True,
            "depression_drop_m": 1.9,
            "slope_deg": 2.0,
            "land_cover_type": "impervious_paved_roof",
            "cn": 98,
            "area_m2": 35000.0,
            "drainage_available": False,
            "notes": "Major commercial and transit roundabout on NH-44 towards Phagwara."
        },
        {
            "id": 303,
            "name": "BMC Chowk Commercial Intersection",
            "latitude": 31.3210,
            "longitude": 75.5840,
            "elevation_m": 242.8,
            "is_depression": False,
            "depression_drop_m": 0.0,
            "slope_deg": 1.0,
            "land_cover_type": "academic_complex",
            "cn": 92,
            "area_m2": 45000.0,
            "drainage_available": False,
            "notes": "Central business district intersection with moderate runoff accumulation."
        },
        {
            "id": 304,
            "name": "Kala Sanghian Outfall Low Point",
            "latitude": 31.3050,
            "longitude": 75.5380,
            "elevation_m": 236.0,
            "is_depression": True,
            "depression_drop_m": 2.1,
            "slope_deg": 1.4,
            "land_cover_type": "open_lawns_parks",
            "cn": 76,
            "area_m2": 65000.0,
            "drainage_available": False,
            "notes": "Confluence point where municipal runoff joins the Kala Sanghian drain."
        },
        {
            "id": 305,
            "name": "Jalandhar Cantt Military Cantonment Ridge",
            "latitude": 31.2950,
            "longitude": 75.6150,
            "elevation_m": 244.5,
            "is_depression": False,
            "depression_drop_m": 0.0,
            "slope_deg": 0.7,
            "land_cover_type": "open_lawns_parks",
            "cn": 68,
            "area_m2": 80000.0,
            "drainage_available": False,
            "notes": "Elevated, well-vegetated cantonment grounds with low runoff coefficients."
        }
    ]
}

async def execute_nowcasting_pipeline(
    study_area_id: str = "lpu_main_campus",
    lead_time_hours: float = 0.0,
    is_simulation: bool = False,
    sim_intensity_mm_h: float = 0.0,
    sim_cumulative_mm: float = 0.0,
    sim_clogging_fraction: float = 0.0
) -> Dict[str, Any]:
    """
    Executes the full hydrological and flood-risk nowcasting pipeline for any study region.
    Supports lead times (0 to 6 hours) with statistical trend projection and full data transparency.
    """
    now_utc = datetime.now(timezone.utc)
    run_id = f"UF-{now_utc.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    active_region_id = study_area_id if study_area_id in REGION_MONITORING_NODES else "lpu_main_campus"
    nodes = REGION_MONITORING_NODES[active_region_id]
    region_info = settings.STUDY_REGIONS.get(active_region_id, settings.STUDY_REGIONS["lpu_main_campus"])

    if is_simulation:
        intensity_mm_h = sim_intensity_mm_h
        cumulative_6h_mm = sim_cumulative_mm
        max_forecast_mm_h = sim_intensity_mm_h
        clogging = sim_clogging_fraction
        exec_mode = "SIMULATED"
        provenance = "SIMULATED"
        data_sources = ["Simulation Engine (Synthetic Input Parameters)"]
    else:
        # Fetch LIVE data from Open-Meteo for the region's centroid
        weather = await open_meteo_provider.get_current_and_forecast(
            lat=region_info["centroid"]["lat"],
            lon=region_info["centroid"]["lon"]
        )
        base_intensity = weather.get("precipitation_mm_h", 0.0)
        hourly = weather.get("hourly_forecast", [])
        cumulative_6h_mm = weather.get("cumulative_forecast_6h_mm", 0.0)
        max_forecast_mm_h = weather.get("max_forecast_intensity_mm_h", 0.0)

        # Apply 0-6h lead time trend projection if lead_time_hours > 0
        if lead_time_hours > 0 and hourly:
            from backend.app.nowcasting.trend import TrendExtrapolationModel
            tm = TrendExtrapolationModel()
            hist = [h.get("precipitation_mm", 0.0) for h in hourly[:3]]
            pred = tm.predict(base_intensity, hist, lead_time_hours)
            intensity_mm_h = pred["projected_intensity_mm_h"]
            exec_mode = f"NOWCAST_PREDICTION_+{int(lead_time_hours*60) if lead_time_hours < 1 else int(lead_time_hours)}{'m' if lead_time_hours < 1 else 'h'}"
            provenance = "FORECAST"
        else:
            intensity_mm_h = base_intensity
            exec_mode = "LIVE"
            provenance = "LIVE"

        clogging = 0.0
        data_sources = [weather.get("data_source", "Open-Meteo NWP"), "Copernicus DEM 30m", "OpenStreetMap"]

    # Effective intensity to test (current or maximum forecast intensity)
    effective_intensity = max(intensity_mm_h, max_forecast_mm_h * 0.7)

    hotspots = []
    max_risk = 0.0
    highest_depth_bracket = "< 0.10 m"
    earliest_time = "> 6 hours / Low Risk"
    affected_count = 0

    for node in nodes:
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
        "study_area_id": active_region_id,
        "study_area_name": region_info["name"],
        "lead_time_hours": lead_time_hours,
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
