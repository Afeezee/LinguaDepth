"""Seed a small set of handwritten sample questions for development.

Use this when you don't have a GROQ_API_KEY yet — it gives every lesson
enough objective questions to run quizzes and the placement test.
For production content, use seed_questions.py (LLM-generated).

Run from the backend/ directory:
    python seed/seed_sample_questions.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from models import Lesson, Question, db

# Generic but valid English questions, parameterised lightly by level
SAMPLES = {
    "beginner": [
        ("Which word is a greeting?", ["Hello", "Table", "Run", "Blue"], "Hello",
         "'Hello' is the most common English greeting."),
        ("Choose the correct sentence.",
         ["She go to school.", "She goes to school.", "She going school.", "She gone to school."],
         "She goes to school.",
         "With 'she', the present simple verb takes -s: 'goes'."),
        ("What is the plural of 'book'?", ["bookes", "books", "bookies", "book"],
         "books", "Most English nouns form the plural by adding -s."),
        ("Which word is a colour?", ["Run", "Green", "Sing", "Door"], "Green",
         "'Green' names a colour; the others are actions or objects."),
        ("Complete: 'I ___ a student.'", ["is", "are", "am", "be"], "am",
         "Use 'am' with 'I': 'I am a student.'"),
    ],
    "intermediate": [
        ("Choose the present perfect sentence.",
         ["I have finished my work.", "I finish my work.", "I finishing my work.", "I will finish my work."],
         "I have finished my work.",
         "The present perfect uses 'have/has' + past participle."),
        ("Which linking word shows contrast?", ["And", "But", "Because", "So"], "But",
         "'But' contrasts two ideas; 'because' gives a reason."),
        ("What does the phrasal verb 'give up' mean?",
         ["To donate", "To quit", "To lift", "To arrive"], "To quit",
         "'Give up' means to stop trying or to quit."),
        ("Choose the correct comparative: 'Lagos is ___ than Enugu.'",
         ["big", "bigger", "biggest", "more big"], "bigger",
         "Short adjectives form the comparative with -er plus 'than'."),
        ("Which is the most formal?",
         ["Hey, what's up?", "Yo!", "Good afternoon, sir.", "How far?"],
         "Good afternoon, sir.",
         "Formal greetings avoid slang and show respect."),
    ],
    "advanced": [
        ("Identify the passive sentence.",
         ["The results were announced.", "They announced the results.",
          "We announce results.", "Announcing the results now."],
         "The results were announced.",
         "The passive uses 'be' + past participle and hides the actor."),
        ("Choose the third conditional.",
         ["If I study, I pass.", "If I studied, I would pass.",
          "If I had studied, I would have passed.", "If I study, I will pass."],
         "If I had studied, I would have passed.",
         "The third conditional reflects on an unreal past."),
        ("What does 'once in a blue moon' mean?",
         ["Very often", "Rarely", "At night", "Monthly"], "Rarely",
         "This idiom describes something that happens very rarely."),
        ("Report this speech: 'I am tired,' she said.",
         ["She said she is tired.", "She said she was tired.",
          "She says she was tired.", "She said I am tired."],
         "She said she was tired.",
         "Reported speech shifts the tense back: 'am' becomes 'was'."),
        ("Which verb is most academic?", ["Show", "Get", "Demonstrate", "Put"],
         "Demonstrate",
         "'Demonstrate' belongs to the formal academic register."),
    ],
}

DIFFICULTIES = ["easy", "easy", "medium", "medium", "hard"]


def seed():
    app = create_app()
    with app.app_context():
        if Question.query.count() > 0:
            print(f"Questions already exist ({Question.query.count()}). Skipping.")
            return

        count = 0
        for lesson in Lesson.query.all():
            for (text, options, answer, explanation), difficulty in zip(
                SAMPLES[lesson.level], DIFFICULTIES
            ):
                db.session.add(
                    Question(
                        lesson_id=lesson.id,
                        type="objective",
                        difficulty=difficulty,
                        level=lesson.level,
                        question_text=text,
                        options=json.dumps(options),
                        correct_answer=answer,
                        explanation=explanation,
                    )
                )
                count += 1
        db.session.commit()
        print(f"Seeded {count} sample questions across {Lesson.query.count()} lessons.")


if __name__ == "__main__":
    seed()
