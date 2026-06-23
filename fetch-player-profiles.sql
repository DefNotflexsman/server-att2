SELECT p.username, e.coins, e.gems, s.kills, s.deaths
FROM players p
LEFT JOIN player_economy e ON p.player_id = e.player_id
LEFT JOIN player_stats s ON p.player_id = s.player_id
WHERE p.uuid = UNHEX(REPLACE('40476839-4cb3-48e0-8800-4eb627440b6d', '-', ''));
