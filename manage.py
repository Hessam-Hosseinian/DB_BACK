# manage.py

import sys
import os
import json
import random

# اضافه کردن مسیر app برای ایمپورت ماژول‌ها
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

from models.question_model import Question
from models.category_model import Category


def load_questions_from_directory(folder_path):
    count = 0
    file_list = sorted(os.listdir(folder_path))

    for file_name in file_list:
        if file_name.endswith(".json"):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for item in data["results"]:
                try:
                    question_text = item["question"]

                    # جلوگیری از تکرار
                    if Question.exists(question_text):
                        continue

                    category_name = item["category"]
                    difficulty = item["difficulty"]
                    correct = item["correct_answer"]
                    incorrect = item["incorrect_answers"]

                    # ترکیب گزینه‌ها و تعیین پاسخ درست
                    all_choices = incorrect + [correct]
                    random.shuffle(all_choices)
                    correct_letter = "ABCD"[all_choices.index(correct)]

                    # پیدا کردن یا ساخت دسته‌بندی
                    category = Category.find_by_name(category_name)
                    if not category:
                        category = Category(name=category_name)
                        category.save()

                    # ساخت و ذخیره سوال
                    q = Question(
                        text=question_text,
                        choices=all_choices,
                        correct_letter=correct_letter,
                        category_id=category.id,
                        difficulty=difficulty
                    )
                    q.save()
                    count += 1

                except Exception as e:
                    print(f"❌ Error in question: {question_text[:40]}... – {e}")

    print(f"✅ وارد کردن کامل شد. مجموع سوالات جدید: {count}")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "import_questions":
        folder = sys.argv[2]
        if not os.path.isdir(folder):
            print(f"❌ مسیر پوشه پیدا نشد: {folder}")
        else:
            load_questions_from_directory(folder)
    else:
        print("📘 استفاده صحیح:")
        print("  python manage.py import_questions <folder_path>")
