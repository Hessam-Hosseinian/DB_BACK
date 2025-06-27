# Database Queries

This directory contains commonly used SQL queries for the quiz game application. The queries are organized by functionality into separate files.

## Query Files

1. `user_queries.sql` - User-related operations

   - User authentication and session management
   - Profile updates
   - Achievement tracking
   - User statistics

2. `game_queries.sql` - Game-related operations

   - Game creation and management
   - Round handling
   - Answer submission
   - Game statistics
   - End game processing

3. `question_queries.sql` - Question management

   - Question retrieval with choices
   - Random question selection for games
   - Question creation
   - Question reporting
   - Question statistics
   - Tag-based search

4. `leaderboard_queries.sql` - Leaderboards and statistics
   - Global leaderboard
   - Category-specific leaderboards
   - Daily rankings
   - User ranking history
   - Category statistics
   - Leaderboard refresh logic

## Usage Notes

1. Parameter Placeholders:

   - All queries use numbered parameters ($1, $2, etc.)
   - Parameters should be provided in the correct order and type

2. JSON Aggregation:

   - Many queries use `json_agg` and `json_build_object` for structured results
   - This helps in reducing the number of queries needed in the application

3. Performance Considerations:

   - Queries use appropriate indexes defined in the schema
   - Complex operations use CTEs (Common Table Expressions) for better readability and maintenance
   - Materialized views are used for frequently accessed data

4. Maintenance:

```sql
-- Refresh materialized views regularly
REFRESH MATERIALIZED VIEW mv_top_players;

-- Update table statistics
ANALYZE users, games, questions, leaderboards;

-- Monitor query performance
EXPLAIN ANALYZE <query>;
```

5. Transaction Management:
   - Some operations (like game end processing) should be wrapped in transactions
   - Example:
   ```sql
   BEGIN;
   -- Run game end query
   -- Update user stats
   -- Update leaderboards
   COMMIT;
   ```

## Best Practices

1. Always use parameter binding to prevent SQL injection
2. Wrap complex operations in transactions
3. Consider using EXPLAIN ANALYZE for query optimization
4. Keep indexes updated and monitor their usage
5. Regularly update table statistics for better query planning
