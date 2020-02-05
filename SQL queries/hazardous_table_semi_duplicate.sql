DROP TABLE IF EXISTS testschip_957_result;

CREATE TABLE testschip_957_result AS SELECT * FROM ships
WHERE name='testschip-957'
ORDER BY name, timestamp; 

ALTER TABLE testschip_957_result ADD COLUMN geom_meter geometry;
UPDATE testschip_957_result SET geom_meter = geom;

ALTER TABLE testschip_957_result
	ALTER COLUMN geom_meter TYPE
	geometry(Point, 4978)
	using ST_Transform(geom_meter, 4978);

CREATE INDEX testschip_957_result_geom_idx
	on testschip_957_result
	using GIST(geom_meter);

ALTER TABLE testschip_957_result ADD COLUMN id SERIAL PRIMARY KEY;
ALTER TABLE testschip_957_result ADD COLUMN num_neighbours int;
ALTER TABLE testschip_957_result ADD COLUMN pause int;

-- create a table from temporary table with ship selection (called ships2 in this case) and calculate the 
-- number of other points within a distance (in this case: 3.5 meter)

UPDATE testschip_957_result SET num_neighbours = agg.num_neighbours 
	FROM (
		SELECT count(b.id) as num_neighbours, a.id
		from testschip_957_result a, testschip_957_result b
		where st_dwithin(a.geom_meter, b.geom_meter, 3.5) and a.id != b.id group by a.id)
	agg
where agg.id = testschip_957_result.id;

-- set 'pause' == 1 if the point has over 8 neighbours
UPDATE testschip_957_result SET pause = 1
WHERE num_neighbours > 8;

-- if 'pause' == null, change null to 0
UPDATE testschip_957_result SET pause = COALESCE(pause, 0);

-- check for trailing points, and set as pause
UPDATE testschip_957_result SET pause = 1
FROM (
	SELECT wl.timestamp, geom, pause -- hoeven er niet per se allemaal in te blijven staan
	FROM
		(SELECT name, timestamp,  geom, pause, lead(pause, 1) OVER (ORDER BY timestamp ASC) AS lead1, 
                                        lead(pause, 2) OVER (ORDER BY timestamp ASC) AS lead2, 
                                        lag(pause, 1) OVER (ORDER BY timestamp ASC) AS lag1, 
                                        lag(pause, 2) OVER (ORDER BY timestamp ASC) AS lag2
		FROM testschip_957_result
		ORDER BY timestamp ASC) AS wl
	WHERE pause = 0 AND lead1 + lead2 + lag1 + lag2 >= 3
) AS wk
WHERE testschip_957_result.timestamp IN (wk.timestamp);

UPDATE testschip_957_result SET pause = 0
FROM (
	SELECT wl.timestamp, geom, pause -- hoeven er niet per se allemaal in te blijven staan
	FROM
		(SELECT name, timestamp,  geom, pause, lead(pause, 1) OVER (ORDER BY timestamp ASC) AS lead1, 
                                        lead(pause, 2) OVER (ORDER BY timestamp ASC) AS lead2, 
		 								lead(pause, 3) OVER (ORDER BY timestamp ASC) AS lead3, 
                                        lag(pause, 1) OVER (ORDER BY timestamp ASC) AS lag1, 
                                        lag(pause, 2) OVER (ORDER BY timestamp ASC) AS lag2,
		 								lag(pause, 3) OVER (ORDER BY timestamp ASC) AS lag3
		FROM testschip_957_result
		ORDER BY timestamp ASC) AS wl
	WHERE pause = 1 AND lead1 + lead2 + lead3 + lag1 + lag2 + lag3 <= 2
) AS wk
WHERE testschip_957_result.timestamp IN (wk.timestamp);