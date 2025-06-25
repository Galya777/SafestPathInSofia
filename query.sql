SELECT 
  id, 
  ST_LineMerge(ST_Transform(geom, 4326)) AS geom 
FROM municipality_roads_api
WHERE geom IS NOT NULL;

