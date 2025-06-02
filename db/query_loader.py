def load_queries(file_path):
    queries = {}
    current_key = None
    current_lines = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("--:"):
                if current_key and current_lines:
                    queries[current_key] = "\n".join(current_lines).strip()
                current_key = stripped[3:]
                current_lines = []
            elif current_key:
                current_lines.append(line.rstrip())

        if current_key and current_lines:
            queries[current_key] = "\n".join(current_lines).strip()

    return queries
