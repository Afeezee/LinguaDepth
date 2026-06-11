"""Seed the 35 LinguaDepth lessons.

Run from the backend/ directory:
    python seed/seed_lessons.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from models import Lesson, db

CORE_LESSONS = [
    {
        "title": "Greetings and Introductions",
        "topic": "greetings",
        "quiz_types": ["objective"],
        "content": (
            "When you meet someone, a warm greeting opens the door. Say 'Hello!' or "
            "'Good morning!' and add their name if you know it. To introduce yourself, "
            "say 'My name is...' or simply 'I'm...'. To ask about the other person, "
            "say 'What is your name?' or 'How are you?'. A friendly reply is 'I'm "
            "fine, thank you. And you?'. Practise these and you can start any "
            "conversation with confidence."
        ),
    },
    {
        "title": "The English Alphabet and Sounds",
        "topic": "phonics",
        "quiz_types": ["objective"],
        "content": (
            "English has 26 letters: 5 vowels (a, e, i, o, u) and 21 consonants. "
            "Each letter has a name and one or more sounds — the letter 'c' sounds "
            "like 'k' in 'cat' but like 's' in 'city'. Vowels can be short, like the "
            "'a' in 'hat', or long, like the 'a' in 'late'. Some letters work in "
            "pairs to make new sounds, like 'sh' in 'ship' and 'th' in 'think'. "
            "Listening carefully to these sounds will improve both your speaking "
            "and your spelling."
        ),
    },
    {
        "title": "Basic Sentence Structure",
        "topic": "sentence_structure",
        "quiz_types": ["objective", "theory"],
        "content": (
            "Most English sentences follow one simple pattern: Subject + Verb + "
            "Object. In 'Ada eats rice', Ada is the subject, eats is the verb, and "
            "rice is the object. The subject does the action, and the verb tells us "
            "what the action is. Every complete sentence needs at least a subject "
            "and a verb. Keep this order in mind and your sentences will always be "
            "clear."
        ),
    },
    {
        "title": "Common Everyday Vocabulary",
        "topic": "vocabulary_everyday",
        "quiz_types": ["objective"],
        "content": (
            "Everyday words are the building blocks of conversation. Around the "
            "house you have a 'door', 'window', 'chair', and 'table'. Outside you "
            "see a 'road', 'market', 'school', and 'bus'. Useful action words "
            "include 'go', 'come', 'buy', 'eat', and 'sleep'. Words like 'today', "
            "'tomorrow', and 'yesterday' help you talk about time. Learn a few new "
            "words each day and use them in real sentences."
        ),
    },
    {
        "title": "Asking and Answering Simple Questions",
        "topic": "questions",
        "quiz_types": ["objective", "oral"],
        "content": (
            "Questions in English often begin with question words: who, what, "
            "where, when, why, and how. 'Where do you live?' asks about place; "
            "'When is the lecture?' asks about time. For yes/no questions, start "
            "with 'do', 'is', or 'are' — for example, 'Do you like rice?'. Answer "
            "in a full sentence when you can: 'Yes, I like rice very much.' Asking "
            "good questions keeps a conversation alive."
        ),
    },
]

BEGINNER_LESSONS = [
    {
        "title": "Present Simple Tense",
        "topic": "present_simple",
        "content": (
            "The present simple describes habits and facts. Say 'I walk to class "
            "every day' or 'She studies in the library'. With he, she, or it, add "
            "-s to the verb: 'He plays football'. For negatives, use 'do not' or "
            "'does not': 'I do not eat late at night'. Master this tense and you "
            "can describe your daily life clearly."
        ),
    },
    {
        "title": "Nouns and Pronouns",
        "topic": "nouns_pronouns",
        "content": (
            "Nouns name people, places, and things: 'student', 'Lagos', 'phone'. "
            "Pronouns replace nouns so we do not repeat them: he, she, it, we, "
            "they. Instead of 'Chidi lost Chidi's pen', say 'Chidi lost his pen'. "
            "Subject pronouns (I, you, he) do the action; object pronouns (me, "
            "you, him) receive it. Using pronouns well makes your speech smooth "
            "and natural."
        ),
    },
    {
        "title": "Adjectives",
        "topic": "adjectives",
        "content": (
            "Adjectives describe nouns and make your language colourful. A 'big "
            "market', a 'busy road', a 'kind lecturer' — the adjective comes "
            "before the noun. You can also use adjectives after 'is' or 'are': "
            "'The exam is difficult'. Pile on detail with more than one: 'a small "
            "red bag'. Choose precise adjectives and people will picture exactly "
            "what you mean."
        ),
    },
    {
        "title": "Counting and Numbers",
        "topic": "numbers",
        "content": (
            "Numbers appear everywhere — prices, dates, phone numbers, scores. "
            "Learn one to twenty first, then the tens: thirty, forty, fifty. "
            "Combine them naturally: twenty-one, thirty-five, ninety-nine. For "
            "big numbers, say 'one hundred', 'two thousand', 'a million'. Practise "
            "saying your matric number and phone number aloud in English."
        ),
    },
    {
        "title": "Days and Months",
        "topic": "days_months",
        "content": (
            "The week runs from Monday to Sunday, and weekdays are Monday through "
            "Friday. The twelve months run from January to December. Use 'on' with "
            "days — 'on Tuesday' — and 'in' with months — 'in March'. Dates "
            "combine them: 'My exam is on Friday, the 14th of June'. Knowing these "
            "words helps you plan lectures, deadlines, and meetings."
        ),
    },
    {
        "title": "Colours and Descriptions",
        "topic": "colours",
        "content": (
            "Colours help you describe the world: red, blue, green, yellow, black, "
            "and white. Place the colour before the noun: 'a green bag', 'a white "
            "shirt'. Add 'light' or 'dark' for shades: 'light blue', 'dark green'. "
            "Combine colours with other adjectives: 'a beautiful blue dress'. "
            "Describing things by colour is one of the easiest ways to be specific."
        ),
    },
    {
        "title": "Family Vocabulary",
        "topic": "family",
        "content": (
            "Family words let you talk about the people closest to you. Your "
            "parents are your mother and father; their parents are your "
            "grandparents. Brothers and sisters are siblings, and your parents' "
            "siblings are your uncles and aunts. Their children are your cousins. "
            "Try it: 'I have two brothers and one sister, and my aunt lives in "
            "Abuja.'"
        ),
    },
    {
        "title": "Food and Drink Vocabulary",
        "topic": "food_drink",
        "content": (
            "Talking about food is a daily pleasure. Common words include 'rice', "
            "'beans', 'bread', 'chicken', 'fruit', and 'vegetables'. For drinks, "
            "learn 'water', 'tea', 'juice', and 'soft drink'. Useful verbs are "
            "'cook', 'eat', 'drink', and 'taste'. Order politely: 'I would like "
            "jollof rice and a bottle of water, please.'"
        ),
    },
    {
        "title": "Telling the Time",
        "topic": "telling_time",
        "content": (
            "Ask the time with 'What time is it?'. On the hour, say 'It is three "
            "o'clock'. For thirty minutes past, say 'half past three'; for fifteen "
            "minutes, 'quarter past' or 'quarter to'. You can also read the digits "
            "directly: 'It is 3:45' — 'three forty-five'. Being able to tell time "
            "keeps you punctual for lectures and appointments."
        ),
    },
    {
        "title": "Simple Paragraph Writing",
        "topic": "paragraph_writing",
        "content": (
            "A paragraph is a group of sentences about one idea. Start with a "
            "topic sentence that states the main point. Add two or three "
            "supporting sentences with details or examples. Finish with a closing "
            "sentence that wraps the idea up. Keep sentences short and clear, and "
            "your reader will follow you easily."
        ),
    },
]

INTERMEDIATE_LESSONS = [
    {
        "title": "Present Perfect Tense",
        "topic": "present_perfect",
        "content": (
            "The present perfect connects the past to now: 'I have finished my "
            "assignment'. Form it with 'have' or 'has' plus the past participle. "
            "Use it for experiences — 'She has visited Ghana' — and for recent "
            "actions with present results — 'We have just eaten'. Use 'for' with "
            "durations and 'since' with starting points: 'I have lived here for "
            "two years'. Do not use it with finished time words like 'yesterday'."
        ),
    },
    {
        "title": "Past Simple Tense",
        "topic": "past_simple",
        "content": (
            "The past simple describes completed actions: 'I wrote the test "
            "yesterday'. Regular verbs add -ed ('walked', 'studied'), but many "
            "common verbs are irregular: go → went, eat → ate, see → saw. For "
            "negatives and questions, use 'did' with the base verb: 'Did you "
            "attend the lecture?' — 'No, I did not attend'. Time markers like "
            "'yesterday', 'last week', and 'in 2023' signal this tense."
        ),
    },
    {
        "title": "Conjunctions and Linking Words",
        "topic": "conjunctions",
        "content": (
            "Linking words join ideas smoothly. Use 'and' to add, 'but' to "
            "contrast, and 'because' to give reasons. 'Although' concedes a point: "
            "'Although it rained, we went out'. Words like 'however', 'therefore', "
            "and 'moreover' connect whole sentences in formal writing. Good "
            "linking turns choppy sentences into flowing paragraphs."
        ),
    },
    {
        "title": "Reading Comprehension",
        "topic": "reading_comprehension",
        "content": (
            "Good readers do more than recognise words — they find meaning. First "
            "skim the passage to get the general idea, then read closely for "
            "details. Identify the main idea, usually stated early in each "
            "paragraph. Use context clues to guess unfamiliar words instead of "
            "stopping. Finally, ask yourself what the writer wants you to think "
            "or feel."
        ),
    },
    {
        "title": "Formal vs Informal Language",
        "topic": "formal_informal",
        "content": (
            "English changes with the situation. With friends you might say "
            "'Hey, what's up?', but to a lecturer you write 'Good afternoon, "
            "sir'. Formal language avoids contractions and slang: 'I would like "
            "to request...' instead of 'I wanna ask...'. Informal language is "
            "relaxed and friendly; formal language is respectful and precise. "
            "Choosing the right register shows real skill."
        ),
    },
    {
        "title": "Phrasal Verbs",
        "topic": "phrasal_verbs",
        "content": (
            "A phrasal verb is a verb plus a small word that changes its meaning. "
            "'Give up' means quit; 'look after' means care for; 'run into' means "
            "meet by chance. The particle matters: 'turn on' and 'turn off' are "
            "opposites. Some can be split — 'turn the light off' — while others "
            "cannot. Learn them in full sentences, not as isolated words."
        ),
    },
    {
        "title": "Writing Emails",
        "topic": "email_writing",
        "content": (
            "A clear email has a subject line, a greeting, a body, and a sign-off. "
            "Open formally when writing to staff: 'Dear Dr. Okafor'. State your "
            "purpose in the first sentence: 'I am writing to ask about the exam "
            "timetable'. Keep paragraphs short and end politely: 'Thank you for "
            "your time'. Sign off with 'Yours sincerely' or 'Best regards' and "
            "your full name."
        ),
    },
    {
        "title": "Expressing Opinions",
        "topic": "expressing_opinions",
        "content": (
            "Strong speakers share opinions politely and clearly. Begin with 'In "
            "my opinion', 'I believe', or 'It seems to me'. Support your view "
            "with a reason: 'I think the new timetable is better because classes "
            "start later'. To disagree respectfully, say 'I see your point, but...'. "
            "Asking 'What do you think?' invites others in and keeps discussion "
            "balanced."
        ),
    },
    {
        "title": "Comparatives and Superlatives",
        "topic": "comparatives_superlatives",
        "content": (
            "To compare two things, add -er or use 'more': 'faster', 'more "
            "interesting', followed by 'than'. For three or more, use the "
            "superlative: 'the fastest', 'the most interesting'. Short adjectives "
            "take endings; long ones take 'more' and 'most'. Watch the irregulars: "
            "good → better → best, bad → worse → worst. 'Lagos is bigger than "
            "Enugu, but Kano is the oldest of the three.'"
        ),
    },
    {
        "title": "Narrative Writing",
        "topic": "narrative_writing",
        "content": (
            "A narrative tells a story with a beginning, middle, and end. Set the "
            "scene first: who, where, and when. Use the past tense to move events "
            "forward and time words — 'first', 'then', 'suddenly', 'finally' — to "
            "guide your reader. Add dialogue and sensory detail to bring scenes "
            "alive. End with a resolution or a lesson learned."
        ),
    },
]

ADVANCED_LESSONS = [
    {
        "title": "Conditional Sentences",
        "topic": "conditionals",
        "content": (
            "Conditionals link a condition to a result. The first conditional "
            "handles real future possibilities: 'If it rains, I will stay home'. "
            "The second imagines unlikely presents: 'If I had a car, I would "
            "drive to campus'. The third reflects on unreal pasts: 'If I had "
            "studied, I would have passed'. The zero conditional states general "
            "truths: 'If you heat water, it boils'. Mastering all four lets you "
            "reason and speculate with precision."
        ),
    },
    {
        "title": "Passive Voice",
        "topic": "passive_voice",
        "content": (
            "The passive voice highlights the action rather than the actor: 'The "
            "results were announced yesterday'. Form it with 'be' plus the past "
            "participle, and add 'by' only if the actor matters. It suits formal "
            "and academic writing: 'The experiment was conducted in 2024'. Use it "
            "when the doer is unknown or unimportant. Overuse weakens prose, so "
            "balance it with active sentences."
        ),
    },
    {
        "title": "Academic Vocabulary",
        "topic": "academic_vocabulary",
        "content": (
            "Academic writing relies on a precise register. Prefer 'demonstrate' "
            "to 'show', 'significant' to 'big', and 'obtain' to 'get'. Verbs like "
            "'analyse', 'evaluate', and 'synthesise' describe scholarly thinking. "
            "Hedge claims with 'suggests', 'appears to', or 'may indicate' rather "
            "than absolute statements. A rich academic vocabulary makes your "
            "essays sound authoritative and exact."
        ),
    },
    {
        "title": "Argumentative Writing",
        "topic": "argumentative_writing",
        "content": (
            "An argumentative essay defends a clear thesis with evidence. State "
            "your position in the introduction, then devote each paragraph to one "
            "supporting point backed by examples or data. Acknowledge the "
            "opposing view and rebut it — this strengthens, not weakens, your "
            "case. Use logical connectors: 'consequently', 'nevertheless', "
            "'furthermore'. Conclude by restating the thesis in fresh words and "
            "showing why it matters."
        ),
    },
    {
        "title": "Idioms and Expressions",
        "topic": "idioms",
        "content": (
            "Idioms mean more than their words. To 'hit the books' is to study "
            "hard; to 'break the ice' is to start a conversation; 'once in a blue "
            "moon' means rarely. You cannot translate them literally, so learn "
            "each one with its meaning and a sample sentence. Used well, idioms "
            "make you sound natural and fluent. Used wrongly, they confuse — so "
            "check the context first."
        ),
    },
    {
        "title": "Business English",
        "topic": "business_english",
        "content": (
            "Professional settings demand crisp, courteous language. Open "
            "meetings with agendas — 'Let's move to the first item' — and close "
            "with action points. Useful phrases include 'I'd like to follow up "
            "on...', 'Could you clarify...?', and 'Let's schedule a call'. In "
            "negotiations, soften requests: 'Would you consider...?'. Clear, "
            "polite business English builds trust and gets results."
        ),
    },
    {
        "title": "Public Speaking Techniques",
        "topic": "public_speaking",
        "content": (
            "Great speeches are structured: tell them what you will say, say it, "
            "then tell them what you said. Open with a hook — a question, a "
            "statistic, or a short story. Speak slowly, pause for emphasis, and "
            "make eye contact across the room. Signpost your points: 'Firstly...', "
            "'My second argument...', 'In conclusion...'. Rehearse aloud; "
            "confidence is built through repetition, not luck."
        ),
    },
    {
        "title": "Critical Analysis of Texts",
        "topic": "critical_analysis",
        "content": (
            "Critical reading questions a text instead of merely absorbing it. "
            "Identify the author's purpose, audience, and tone before judging "
            "the argument. Distinguish facts from opinions and evidence from "
            "assertion. Ask what is emphasised, what is omitted, and whose "
            "perspective is missing. Then evaluate: is the evidence sufficient, "
            "the logic sound, the conclusion justified? Writing your analysis "
            "sharpens it further."
        ),
    },
    {
        "title": "Advanced Grammar: Reported Speech",
        "topic": "reported_speech",
        "content": (
            "Reported speech retells what someone said without quoting. Shift "
            "tenses back: 'I am tired' becomes 'She said she was tired'. Pronouns "
            "and time words shift too: 'today' becomes 'that day', 'here' becomes "
            "'there'. Report questions with 'asked' and statement order: 'He "
            "asked where I lived'. Commands use the infinitive: 'She told us to "
            "submit the assignment'. Accurate reporting is essential in essays "
            "and the workplace."
        ),
    },
    {
        "title": "Professional Email and Report Writing",
        "topic": "professional_writing",
        "content": (
            "Professional documents are judged on clarity and structure. Reports "
            "follow a pattern: title, summary, introduction, findings, "
            "conclusion, recommendations. Use headings, numbered points, and one "
            "idea per paragraph. In emails, put the request in the first two "
            "lines and the details after. Edit ruthlessly: cut redundant words, "
            "check names and figures, and proofread before sending. Your writing "
            "is your professional reputation in print."
        ),
    },
]


def seed():
    app = create_app()
    with app.app_context():
        if Lesson.query.count() > 0:
            print(f"Lessons already seeded ({Lesson.query.count()} found). Skipping.")
            return

        order = 1
        for lesson in CORE_LESSONS:
            db.session.add(
                Lesson(
                    title=lesson["title"],
                    content=lesson["content"],
                    level="beginner",  # core lessons are accessible to all levels
                    topic=lesson["topic"],
                    path_type="core",
                    order_index=order,
                    quiz_types=json.dumps(lesson["quiz_types"]),
                )
            )
            order += 1

        for level, lessons in (
            ("beginner", BEGINNER_LESSONS),
            ("intermediate", INTERMEDIATE_LESSONS),
            ("advanced", ADVANCED_LESSONS),
        ):
            for index, lesson in enumerate(lessons, start=1):
                quiz_types = lesson.get("quiz_types", ["objective", "theory"])
                db.session.add(
                    Lesson(
                        title=lesson["title"],
                        content=lesson["content"],
                        level=level,
                        topic=lesson["topic"],
                        path_type="level_path",
                        order_index=index,
                        quiz_types=json.dumps(quiz_types),
                    )
                )

        db.session.commit()
        print(f"Seeded {Lesson.query.count()} lessons.")


if __name__ == "__main__":
    seed()
