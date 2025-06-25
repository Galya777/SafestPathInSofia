import geopandas as gpd

# 1. Зареждане на пътната мрежа
gdf = gpd.read_file("layer.gpkg")

# 2. Създаване на фиктивен safety cost
def compute_safety_cost(row):
    length = row.geometry.length * 111000  # прибл. м
    if length > 150:
        return length * 3
    elif length > 80:
        return length * 2
    else:
        return length

gdf["safety_cost"] = gdf.apply(compute_safety_cost, axis=1)

# 3. Записване в нов GeoPackage
gdf.to_file("safe_network.gpkg", driver="GPKG")

print("Готово! Мрежата е създадена.")

