import os
import json
import random
from models.question_model import Question

def load_questions_from_directory(folder_path):
    file_list = sorted(os.listdir(folder_path))
    count = 0

    for file_name in file_list:
        if file_name.endswith(".json"):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for item in data["results"]:
                question_text = item["question"]
                category = item["category"]
                difficulty = item["difficulty"]
                correct = item["correct_answer"]
                incorrect = item["incorrect_answers"]

                all_choices = incorrect + [correct]
                random.shuffle(all_choices)

                correct_letter = "ABCD"[all_choices.index(correct)]

                q = Question(
                    text=question_text,
                    choices=all_choices,
                    correct_letter=correct_letter,
                    category=category,
                    difficulty=difficulty
                )

                q.save()
                count += 1

    print(f"✅: {count}")
