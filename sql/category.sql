--:create_categories
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

--:insert_category
INSERT INTO categories (name) VALUES (%s) RETURNING id;

--:get_category_by_name
SELECT id, name FROM categories WHERE name = %s;

--:get_all_categories
SELECT id, name FROM categories;
