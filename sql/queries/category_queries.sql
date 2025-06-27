-- Get all categories with their question counts
SELECT c.id, c.name, COUNT(q.id) as question_count
FROM categories c
LEFT JOIN questions q ON c.id = q.category_id
GROUP BY c.id, c.name;

-- Get a specific category by name
SELECT id, name
FROM categories
WHERE name = $1;

-- Insert a new category and return its ID
INSERT INTO categories (name)
VALUES ($1)
RETURNING id;

-- Get category by ID with question count
SELECT c.id, c.name, COUNT(q.id) as question_count
FROM categories c
LEFT JOIN questions q ON c.id = q.category_id
WHERE c.id = $1
GROUP BY c.id, c.name;

-- Update category name
UPDATE categories
SET name = $2
WHERE id = $1
RETURNING id, name;

-- Delete category (if no questions are associated)
DELETE FROM categories
WHERE id = $1 AND NOT EXISTS (
    SELECT 1 FROM questions WHERE category_id = $1
)
RETURNING id; 