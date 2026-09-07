-- PostgreSQL + PostGIS Database Initialization
-- SIH 2026: Urban Flood Nowcasting System (LPU & Phagwara)

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Study Areas
CREATE TABLE IF NOT EXISTS study_areas (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(50) DEFAULT 'India',
    centroid_lat DOUBLE PRECISION NOT NULL,
    centroid_lon DOUBLE PRECISION NOT NULL,
    radius_km DOUBLE PRECISION DEFAULT 3.5,
    boundary_geojson TEXT,
    drainage_mode VARCHAR(50) DEFAULT 'SIMPLIFIED_RUNOFF_LIMITATION',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Weather Observations
CREATE TABLE IF NOT EXISTS weather_observations (
    id SERIAL PRIMARY KEY,
    study_area_id VARCHAR(50) REFERENCES study_areas(id),
    timestamp_utc TIMESTAMPTZ NOT NULL,
    temperature_c DOUBLE PRECISION,
    relative_humidity_pct DOUBLE PRECISION,
    precipitation_mm_h DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    rain_mm DOUBLE PRECISION DEFAULT 0.0,
    wind_speed_kmh DOUBLE PRECISION,
    weather_code INT,
    data_source VARCHAR(100) NOT NULL,
    provenance VARCHAR(30) NOT NULL,
    raw_payload TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_weather_time ON weather_observations(timestamp_utc);

-- Rainfall Forecasts
CREATE TABLE IF NOT EXISTS rainfall_forecasts (
    id SERIAL PRIMARY KEY,
    study_area_id VARCHAR(50) REFERENCES study_areas(id),
    issued_at_utc TIMESTAMPTZ NOT NULL,
    forecast_time_utc TIMESTAMPTZ NOT NULL,
    horizon_hours DOUBLE PRECISION NOT NULL,
    expected_precipitation_mm DOUBLE PRECISION NOT NULL,
    precipitation_probability_pct DOUBLE PRECISION,
    data_source VARCHAR(100) NOT NULL,
    provenance VARCHAR(30) NOT NULL,
    model_name VARCHAR(100) DEFAULT 'Open-Meteo-NWP',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_forecast_time ON rainfall_forecasts(forecast_time_utc);

-- Flood Prediction Runs
CREATE TABLE IF NOT EXISTS flood_prediction_runs (
    id VARCHAR(50) PRIMARY KEY,
    study_area_id VARCHAR(50) REFERENCES study_areas(id),
    run_timestamp_utc TIMESTAMPTZ NOT NULL,
    execution_mode VARCHAR(20) NOT NULL,
    modelling_mode VARCHAR(50) NOT NULL,
    current_rainfall_mm_h DOUBLE PRECISION DEFAULT 0.0,
    forecast_cumulative_6h_mm DOUBLE PRECISION DEFAULT 0.0,
    max_forecast_intensity_mm_h DOUBLE PRECISION DEFAULT 0.0,
    drainage_clogging_fraction DOUBLE PRECISION DEFAULT 0.0,
    max_flood_risk_score DOUBLE PRECISION NOT NULL,
    overall_severity VARCHAR(20) NOT NULL,
    highest_estimated_depth_bracket VARCHAR(30) NOT NULL,
    earliest_time_to_flood VARCHAR(30),
    affected_hotspots_count INT DEFAULT 0,
    confidence_level VARCHAR(20) DEFAULT 'MEDIUM',
    data_sources TEXT,
    model_version VARCHAR(30) DEFAULT '0.1.0-alpha',
    is_simulation BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Flood Hotspots
CREATE TABLE IF NOT EXISTS flood_hotspots (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(50) REFERENCES flood_prediction_runs(id),
    location_name VARCHAR(150) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    elevation_m DOUBLE PRECISION,
    runoff_volume_m3 DOUBLE PRECISION,
    flood_risk_score DOUBLE PRECISION NOT NULL,
    risk_category VARCHAR(20) NOT NULL,
    estimated_depth_bracket VARCHAR(30) NOT NULL,
    estimated_depth_m DOUBLE PRECISION,
    estimated_time_to_flood VARCHAR(30) NOT NULL,
    susceptibility_factors TEXT,
    data_provenance VARCHAR(30) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_hotspots_run ON flood_hotspots(run_id);

-- Ground Truth Validation Events
CREATE TABLE IF NOT EXISTS validation_events (
    id VARCHAR(50) PRIMARY KEY,
    study_area_id VARCHAR(50) NOT NULL,
    event_timestamp_utc TIMESTAMPTZ NOT NULL,
    location_name VARCHAR(150) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    observed_rainfall_24h_mm DOUBLE PRECISION NOT NULL,
    peak_intensity_mm_h DOUBLE PRECISION,
    lead_time_hours DOUBLE PRECISION NOT NULL,
    predicted_risk_score DOUBLE PRECISION NOT NULL,
    predicted_risk_category VARCHAR(30) NOT NULL,
    predicted_depth_bracket VARCHAR(30) NOT NULL,
    predicted_depth_m DOUBLE PRECISION,
    observed_flooded BOOLEAN NOT NULL,
    observed_depth_m DOUBLE PRECISION,
    observed_depth_bracket VARCHAR(30),
    ground_truth_source VARCHAR(200) NOT NULL,
    notes TEXT,
    verified_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_validation_time ON validation_events(event_timestamp_utc);
