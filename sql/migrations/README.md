# Database Migration Structure

This directory contains the database migration files for the quiz game application. The migrations are organized in a sequential order and should be applied in the following order:

## Migration Files

1. `000_init.sql` - Initial setup and extensions

   - PostgreSQL extensions setup
   - Schema version tracking

2. `001_user_management.sql` - User-related tables

   - Users
   - User profiles
   - User sessions

3. `002_question_system.sql` - Question management

   - Categories
   - Questions
   - Question choices
   - Tags
   - Question reports

4. `003_game_system.sql` - Game-related tables

   - Game types
   - Games
   - Game participants
   - Game rounds
   - Round answers

5. `004_achievement_system.sql` - Achievement system

   - Achievement categories
   - Achievements
   - User achievements

6. `005_chat_system.sql` - Chat functionality

   - Chat rooms
   - Chat room members
   - Chat messages

7. `006_notification_system.sql` - Notification system

   - Notification types
   - Notifications

8. `007_statistics_and_leaderboards.sql` - Statistics and leaderboards
   - User stats
   - User category stats
   - Leaderboards
   - Top players materialized view

## How to Apply Migrations

To apply these migrations, run them in sequential order using psql or your preferred database management tool:

```bash
# Example using psql
psql -U your_username -d your_database -f sql/migrations/000_init.sql
psql -U your_username -d your_database -f sql/migrations/001_user_management.sql
# ... and so on
```

## Important Notes

1. Each migration file is idempotent (can be run multiple times safely) due to the use of `IF NOT EXISTS` clauses
2. Foreign key constraints ensure referential integrity across tables
3. Appropriate indexes are created for optimizing common queries
4. The materialized view for top players should be refreshed periodically

## Maintenance

To maintain the database:

1. Regularly refresh materialized views:

```sql
REFRESH MATERIALIZED VIEW mv_top_players;
```

2. Monitor index usage:

```sql
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes;
```

3. Update statistics:

```sql
ANALYZE;
```
