-- CREATE OR REPLACE VIEW ship10MOVE2 AS SELECT COUNT(*)
-- FROM public.ship10
-- WHERE (ST_Intersects(ST_Buffer (geom, 10), geom));

--ALTER TABLE ship10test ADD COLUMN num_neighbors int;

--ALTER TABLE ship10test ADD COLUMN id SERIAL PRIMARY KEY;

--ALTER TABLE ship10test ADD COLUMN geom_meter geometry;
--UPDATE ship10test SET geom_meter = geom;
--ALTER TABLE ship10test 
	--ALTER COLUMN geom_meter TYPE
	--geometry(Point, 4978)
	--using ST_Transform(geom_meter, 4978);


-- CREATE INDEX ship10test_geom_idx
-- 	on ship10test
-- 	using GIST(geom_meter);

ALTER TABLE ship10test DROP COLUMN num_neighbors;
ALTER TABLE ship10test DROP COLUMN pauze;

ALTER TABLE ship10test ADD COLUMN num_neighbors int;
ALTER TABLE ship10test ADD COLUMN pauze int;

UPDATE ship10test SET num_neighbors = agg.num_neighbors 
	FROM (
		SELECT count(b.id) as num_neighbors, a.id
		from ship10test a, ship10test b
		where st_dwithin(a.geom_meter, b.geom_meter, 3.5) and a.id != b.id group by a.id)
	agg
where agg.id =ship10test.id;

--ALTER TABLE ship10test ADD COLUMN pauze int;

UPDATE ship10test SET pauze = 1
WHERE num_neighbors > 6;

-- -- change NULL to 0
-- UPDATE ship10test SET pauze = COALESCE(pauze, 0);