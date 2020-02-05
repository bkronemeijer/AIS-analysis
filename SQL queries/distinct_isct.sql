-- create counting line. this example is situated at the lock near Gaarkeuken
CREATE TABLE test_isct (id SERIAL PRIMARY KEY, geom geometry);
INSERT INTO test_isct (id, geom) 
	VALUES ('1', ST_SetSRID(ST_MakeLine(ST_MakePoint(6.30850990283755664, 53.24731499263390333), ST_MakePoint(6.30826243889293892, 53.24925663281482002)), 4326));

-- create view with properties upon which to perform intersection. e.g. based on timestamp and bbox
CREATE OR REPLACE VIEW track4 AS SELECT 
    ships.name,
    ships.vesseltype,
    ships.hazardouscargo,
    ST_MakeLine(ships.geom ORDER BY timestamp) As geom
FROM ships
WHERE ST_Intersects(ST_SetSRID(
            ST_MakeBox2D(St_MakePoint(5.710553, 52.844946), ST_MakePoint(6.9244598, 53.3310272)), 4326), ships.geom)
	AND ships.timestamp BETWEEN '2019-06-09 00:00:00' AND '2019-06-10 00:00:00'
GROUP BY name, vesseltype, hazardouscargo;

-- create table with distinct number of intersections with counting line per ship
DROP TABLE IF EXISTS output_isct_grk_distinct;

CREATE TABLE output_isct_grk_distinct AS
SELECT
	a.name,
    a.geom,
	ST_Intersection(a.geom, b.geom),
	ST_NumGeometries(ST_Intersection(a.geom, b.geom)),
	a.vesseltype
FROM
	track4 as a 
		INNER JOIN 
	test_isct as b
ON
	ST_Intersects(a.geom, b.geom)
GROUP BY
	a.name, a.vesseltype, a.geom, b.geom;