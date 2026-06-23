SELECT p.username, s.kills
FROM player_stats s
JOIN players p ON s.player_id = p.player_id
ORDER BY s.kills DESC
LIMIT 10;
