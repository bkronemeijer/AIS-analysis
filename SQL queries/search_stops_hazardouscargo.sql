-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
--                test method for 1 ship: ship 10				  --
-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

DROP TABLE IF EXISTS testschip_257_result;

CREATE TABLE testschip_257_result AS SELECT * FROM ships
WHERE name='testschip-257'
ORDER BY name, timestamp; 

ALTER TABLE testschip_257_result ADD COLUMN geom_meter geometry;
UPDATE testschip_257_result SET geom_meter = geom;

ALTER TABLE testschip_257_result
	ALTER COLUMN geom_meter TYPE
	geometry(Point, 4978)
	using ST_Transform(geom_meter, 4978);

CREATE INDEX testschip_257_result_geom_idx
	on testschip_257_result
	using GIST(geom_meter);

ALTER TABLE testschip_257_result ADD COLUMN id SERIAL PRIMARY KEY;
ALTER TABLE testschip_257_result ADD COLUMN num_neighbours int;
ALTER TABLE testschip_257_result ADD COLUMN pause int;

-- create a table from temporary table with ship selection (called ships2 in this case) and calculate the 
-- number of other points within a distance (in this case: 3.5 meter)

UPDATE testschip_257_result SET num_neighbours = agg.num_neighbours 
	FROM 
		(SELECT count(b.id) AS num_neighbours, 
			a.id
		FROM testschip_257_result a, testschip_257_result b
		WHERE st_dwithin(a.geom_meter, b.geom_meter, 3.5) 
			AND a.id != b.id 
		GROUP BY a.id) agg
WHERE agg.id = testschip_257_result.id;

-- set 'pause' == 1 if the point has over 8 neighbours
UPDATE testschip_257_result SET pause = 1
WHERE num_neighbours > 8;

-- if 'pause' == null, change null to 0
UPDATE testschip_257_result SET pause = COALESCE(pause, 0);

-- check for trailing points, and set as pause
UPDATE testschip_257_result SET pause = 1
FROM (
	SELECT wl.timestamp, geom, pause -- hoeven er niet per se allemaal in te blijven staan
	FROM
		(SELECT name, timestamp,  geom, pause, lead(pause, 1) OVER (ORDER BY timestamp ASC) AS lead1, 
                                        lead(pause, 2) OVER (ORDER BY timestamp ASC) AS lead2, 
                                        lag(pause, 1) OVER (ORDER BY timestamp ASC) AS lag1, 
                                        lag(pause, 2) OVER (ORDER BY timestamp ASC) AS lag2
		FROM testschip_257_result
		ORDER BY timestamp ASC) AS wl
	WHERE pause = 0 AND lead1 + lead2 + lag1 + lag2 >= 3
) AS wk
WHERE testschip_257_result.timestamp IN (wk.timestamp);

-- -- check for changes in pause and calculate the interval in which a ship either moves or stops
SELECT wl.timestamp, wl.num_neighbours, wl.name, ((lead(timestamp) OVER (ORDER BY timestamp ASC)) - timestamp) AS interval, wl.geom, wl.pause
FROM
	(SELECT name, timestamp, num_neighbours, geom, pause, lag(pause) OVER (ORDER BY timestamp ASC) AS prev_pause,
		lead(pause) OVER (ORDER BY timestamp ASC) AS next_pause
	FROM testschip_257_result
	ORDER BY timestamp ASC) AS wl
WHERE wl.pause IS DISTINCT FROM wl.next_pause
ORDER BY name ASC, wl.timestamp ASC;