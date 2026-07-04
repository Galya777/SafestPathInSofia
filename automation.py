import geopandas as gpd
import numpy as np
import random

# Гео данни - пътна мрежа на София
gdf = gpd.read_file("layer.gpkg")

# Оптимизиране за маршрутиране
gdf = gdf.rename(columns={'id': 'road_id'})

def estimate_night_safety(row):
    """
    Оценка за нощна безопасност на пътя.
    Фактори: дължина, тип улица (грубо оценка), разстояние до обществен транспорт
    """
    length_km = row.geometry.length * 0.01  # Приблизително в km
    
    # Базова цена - по-къси пътища са по-добри
    base_cost = max(1, length_km * 10)
    
    # Имитирана оценка за фонари (различаваме по ID)
    # Вярно би се използвало осветление със свързана база
    lighting_score = random.uniform(0.5, 1.0)
    
    # Имитирана оценка за обществен транспорт близост
    transit_score = random.uniform(0.7, 1.5)
    
    # Имитирана оценка за интензивност на движение нощем
    traffic_night_score = random.uniform(0.8, 1.2)
    
    # Имитирана оценка за разположение (център vs периферия)
    # Центърът обикновено има по-много осветление и камери
    centrality_score = 1 / (1 + np.exp(-0.5 * (row.road_id % 10 - 5)))
    
    safety_cost = base_cost * (2 - lighting_score) * transit_score * (2 - traffic_night_score) * (2 - centrality_score)
    
    return round(safety_cost, 2), lighting_score, transit_score

def calculate_safety_metrics(gdf):
    """Изчислява комплексна безопасност за всяко парче път"""
    results = gdf.apply(estimate_night_safety, axis=1, result_type='expand')
    results.columns = ['safety_cost', 'lighting_score', 'transit_score']
    
    gdf['safety_cost'] = results['safety_cost']
    gdf['lighting_score'] = results['lighting_score']
    gdf['transit_score'] = results['transit_score']
    gdf['risk_level'] = gdf['safety_cost'].apply(
        lambda x: 'low' if x < 5 else ('medium' if x < 10 else 'high')
    )
    
    return gdf

gdf = calculate_safety_metrics(gdf)

# Експорт за QGIS процесинг
gdf.to_file("safe_network.gpkg", driver="GPKG", index=False)

# Създаване на резултатен GeoJSON с обогаче̊дени данни
def create_route_geojson(gdf, output_path='route_night_safe.geojson'):
    """Създава GeoJSON файл с маршрутиране с данни за безопасност"""
    features = []
    for idx, row in gdf.iterrows():
        feature = {
            "type": "Feature",
            "properties": {
                "road_id": int(row['road_id']),
                "safety_cost": float(row['safety_cost']),
                "risk_level": row['risk_level'],
                "length_m": round(float(row.geometry.length * 111000), 2)
            },
            "geometry": row.geometry.__geo_interface__
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}}
    }
    
    import json
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    
    return output_path

output_file = create_route_geojson(gdf)
print(f"Готово! Мрежата е създадена в {output_file}")
print(f"Общо сегменти: {len(gdf)}")
print(f"Средна цена за безопасност: {gdf['safety_cost'].mean():.2f}")
print(f"Разпределение по риск: {gdf['risk_level'].value_counts().to_dict()}")

