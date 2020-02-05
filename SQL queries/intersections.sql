CREATE OR REPLACE VIEW track3 AS SELECT 
    ships.name,
    ships.vesseltype,
    ships.hazardouscargo,
    ST_MakeLine(ships.geom ORDER BY timestamp) As geom
FROM ships
WHERE ST_Intersects(ST_SetSRID(
            ST_MakeBox2D(St_MakePoint(5.710553, 52.844946), ST_MakePoint(6.9244598, 53.3310272)), 4326), ships.geom)
	AND ships.timestamp BETWEEN '2019-06-09 00:00:00' AND '2019-06-10 00:00:00'
GROUP BY name, vesseltype, hazardouscargo;

SELECT *
FROM public.track3
WHERE ST_Intersects(ST_SetSRID(ST_MakeLine(ST_MakePoint(6.30850990283755664, 53.24731499263390333), ST_MakePoint(6.30826243889293892, 53.24925663281482002)), 4326), track3.geom)
GROUP BY name, vesseltype, hazardouscargo, geom;