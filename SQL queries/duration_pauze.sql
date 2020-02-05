-- UPDATE ship10test SET pauze = COALESCE(pauze, 0);

-- -- outputs the amount of time a stop/move takes
SELECT wl.timestamp, ((lead(timestamp) OVER (ORDER BY timestamp ASC)) - timestamp) AS interval, wl.geom, wl.pauze
FROM
	(SELECT timestamp, geom, pauze, lag(pauze) OVER (ORDER BY timestamp ASC) AS prev_pauze,
		lead(pauze) OVER (ORDER BY timestamp ASC) AS next_pauze
	FROM ship10test
	ORDER BY timestamp ASC) AS wl
WHERE wl.pauze IS DISTINCT FROM wl.next_pauze
ORDER BY wl.timestamp ASC;

-- -- fill pauze gaps
UPDATE ship10test SET pauze = 1
FROM (
	SELECT wl.timestamp, geom, pauze -- hoeven er niet per se allemaal in te blijven staan
	FROM
		(SELECT timestamp,  geom, pauze, lead(pauze, 1) OVER (ORDER BY timestamp ASC) AS lead1, 
                                        lead(pauze, 2) OVER (ORDER BY timestamp ASC) AS lead2, 
                                        lag(pauze, 1) OVER (ORDER BY timestamp ASC) AS lag1, 
                                        lag(pauze, 2) OVER (ORDER BY timestamp ASC) AS lag2
		FROM ship10test
		ORDER BY timestamp ASC) AS wl
	WHERE pauze = 0 AND lead1 + lead2 + lag1 + lag2 = 4
) AS wk
WHERE ship10test.timestamp IN (wk.timestamp);