"""Seed the 89 LinguaDepth lessons (5 core + 28 per level path).

Every lesson is written as structured data (hook, rule, examples, mistakes,
tip) and rendered to Markdown by ``build_content``. That keeps each entry
compact while still producing the 180–260-word teaching body the frontend
renders through ``react-markdown``.

Quiz-type pairs are assigned per lesson by ``assign_quiz_types``: exactly two
of the three types (objective / theory / oral), cycling through the three
possible pairs so no two consecutive lessons in the same path use the same
pair. Topics that don't fit one type well can override via
``TOPIC_TYPE_OVERRIDES``.

Run from the backend/ directory:
    python seed/seed_lessons.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from models import Lesson, db


# ---------------------------------------------------------------------------
# Content template & quiz-type assignment
# ---------------------------------------------------------------------------

def build_content(title, hook, rule, examples, mistakes, tip):
    """Render a lesson's structured pieces into the required Markdown layout."""
    parts = [f"## {title}", "", hook.strip(), "", "### The Rule", rule.strip(), "", "### Examples"]
    for sentence, note in examples:
        parts.append(f"- **{sentence}** — {note}")
    parts.extend(["", "### Common Mistakes"])
    for wrong, right, why in mistakes:
        parts.append(f"- ❌ {wrong} → ✅ {right} — {why}")
    parts.extend(["", "### Quick Practice Tip", tip.strip(), ""])
    return "\n".join(parts)


def markdown_to_plaintext(md: str) -> str:
    """Strip Markdown syntax down to speech-friendly plain text.

    Kept as a backend mirror of ``utils/markdown.ts`` so the ``lessons.content``
    column always holds something a legacy consumer (or a TTS caller that
    hasn't been updated) can read aloud without spitting out asterisks or
    heading marks. The on-screen render always uses the Markdown source.
    """
    text = re.sub(r"^#{1,6}\s+", "", md, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = text.replace("❌", "").replace("✅", "")
    text = re.sub(r"^[-*]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", ". ", text)
    return text.strip()


QUIZ_TYPE_PAIRS = [
    ["objective", "theory"],
    ["objective", "oral"],
    ["theory", "oral"],
]


def assign_quiz_types(lesson_index: int) -> list:
    """Cycle through the three possible type-pairs across a path.

    Called with a 0-indexed position inside the lesson's own path so that no
    two consecutive lessons in that path share the same pair.
    """
    return list(QUIZ_TYPE_PAIRS[lesson_index % 3])


# Manual overrides for topics that clearly don't suit a given type.
# Written topics with no natural spoken form skip "oral"; skills that live
# entirely in speech skip "theory".
TOPIC_TYPE_OVERRIDES = {
    "punctuation_rules": ["objective", "theory"],
    "advanced_punctuation": ["objective", "theory"],
    "pronunciation_basics": ["objective", "oral"],
    "public_speaking": ["theory", "oral"],
    "phonics": ["objective", "oral"],
}


def quiz_types_for(topic: str, index: int) -> list:
    return TOPIC_TYPE_OVERRIDES.get(topic, assign_quiz_types(index))


# ---------------------------------------------------------------------------
# Lesson bank — 5 core + 28 beginner + 28 intermediate + 28 advanced
# ---------------------------------------------------------------------------

# Each entry: (topic, title, hook, rule, examples, mistakes, tip)
# examples: list of (sentence, note)
# mistakes: list of (wrong, right, why)

CORE_LESSONS = [
    (
        "greetings",
        "Greetings and Introductions",
        "The first words you say shape the whole conversation — a warm greeting opens doors that a cold one keeps shut.",
        "English greetings match the time of day and the level of formality. Use 'Good morning / afternoon / evening' with people you don't know well, and 'Hi' or 'Hey' with friends. Introduce yourself with 'My name is…' or the shorter 'I'm…', and reply to 'How are you?' with a short answer plus the same question back.",
        [
            ("Good morning, my name is Amaka — nice to meet you.", "formal and complete, ideal for lecturers or interviews"),
            ("Hi, I'm Tunde. What about you?", "friendly, invites the other person to speak"),
            ("I'm fine, thank you — and you?", "returns the question so the exchange keeps flowing"),
        ],
        [
            ("How are you? I am fine.", "How are you? I'm fine, thanks — and you?", "one-word replies stall the conversation"),
            ("My name is Amaka Okafor, I am from Lagos, I study medicine.", "My name is Amaka. I'm from Lagos and I study medicine.", "break long introductions into shorter sentences"),
        ],
        "Before you speak, decide: formal or friendly? That single choice picks your greeting, your handshake, and even how loud your voice should be.",
    ),
    (
        "phonics",
        "The English Alphabet and Sounds",
        "English spelling and English sounds don't always match — knowing the sound of each letter is what turns reading into speaking.",
        "There are 26 letters: 5 vowels (a, e, i, o, u) and 21 consonants. Every letter has at least one sound, and some have several — the 'c' in 'cat' sounds like /k/, but the 'c' in 'city' sounds like /s/. Certain letter pairs (sh, ch, th, ph) work together to make new sounds you can't get from either letter alone.",
        [
            ("cat, city — the letter 'c' takes two different sounds", "the vowel that follows decides which sound"),
            ("ship, chip, this — 'sh', 'ch' and 'th' are single sounds", "learn them as pairs, not two letters"),
            ("hat vs late — short and long 'a'", "the silent 'e' at the end lengthens the vowel"),
        ],
        [
            ("Pronouncing 'know' with a hard k-sound.", "Say /noʊ/ — the 'k' is silent.", "some English letters are silent by tradition"),
            ("Reading 'phone' as p-h-one.", "Say /foʊn/ — 'ph' sounds like 'f'.", "letter pairs replace the individual sounds"),
        ],
        "Read every new word out loud once, then twice with the correct stress. Your ear learns faster than your eye.",
    ),
    (
        "sentence_structure",
        "Basic Sentence Structure",
        "Once you can build a clean subject–verb–object sentence, you can say almost anything in English clearly, even with limited vocabulary.",
        "Most English sentences follow the pattern Subject + Verb + Object (SVO). The subject does the action, the verb names the action, and the object receives it. Every complete sentence needs at least a subject and a verb; the object is optional if the verb is complete on its own (e.g. 'She sleeps').",
        [
            ("Ada eats rice.", "Ada = subject, eats = verb, rice = object"),
            ("The students study English.", "plural subject still takes SVO order"),
            ("He sleeps.", "no object needed — 'sleep' is a complete action"),
        ],
        [
            ("Eats Ada rice.", "Ada eats rice.", "the subject comes first, not the verb"),
            ("She happy.", "She is happy.", "you need a verb even when describing"),
        ],
        "If you're stuck, silently label your sentence 'who–did–what'. If any of the three is missing or out of order, fix it before you speak.",
    ),
    (
        "vocabulary_everyday",
        "Common Everyday Vocabulary",
        "You use the same 500 or so words for 80% of daily English — mastering them beats memorising rare ones you'll never say.",
        "Everyday vocabulary clusters by place and purpose: home words (door, chair, kitchen), outside words (market, road, bus), action words (go, come, buy, eat), and time words (today, tomorrow, yesterday). Learn them in short sentences rather than isolated lists so the grammar sticks with the word.",
        [
            ("I go to the market on Saturday.", "combines place, action, and a time word"),
            ("She is eating rice at home.", "action + object + place"),
            ("We take the bus to school every morning.", "action + object + place + time"),
        ],
        [
            ("I go market today.", "I'm going to the market today.", "small words like 'to' and 'the' still matter"),
            ("Yesterday I eat rice.", "Yesterday I ate rice.", "'yesterday' forces past tense"),
        ],
        "Keep a 'word of the day' note on your phone. Use it in three real sentences before bed and it becomes yours.",
    ),
    (
        "questions",
        "Asking and Answering Simple Questions",
        "Good questions keep conversations alive — they show interest and give you time to think while the other person answers.",
        "English questions come in two families. Wh-questions (who, what, where, when, why, how) ask for information. Yes/no questions start with 'do', 'is', 'are', 'can', or 'have' and can be answered with a short reply. Full-sentence answers sound friendlier and give you speaking practice.",
        [
            ("Where do you live?", "'where' asks about place, 'do' matches 'you'"),
            ("When is the lecture?", "'is' agrees with the singular subject 'lecture'"),
            ("Do you like rice? — Yes, I like it very much.", "answer with a full sentence, not just 'yes'"),
        ],
        [
            ("You live where?", "Where do you live?", "put the question word first"),
            ("Yes.", "Yes, I do — it's my favourite.", "expand short answers to keep the conversation open"),
        ],
        "In a new conversation, prepare three 'wh-' questions in advance. You'll never run out of things to ask.",
    ),
]


BEGINNER_LESSONS = [
    (
        "present_simple",
        "Present Simple Tense",
        "The present simple is the tense of routines — the habits, timetables, and facts that make up most of everyday English.",
        "Use the present simple for things you do regularly, general truths, and fixed schedules. With he / she / it, add -s (or -es) to the verb; with I, you, we, they, use the base form. For negatives and questions, use 'do' or 'does' with the base verb.",
        [
            ("I walk to class every morning.", "regular habit — 'every morning' is the clue"),
            ("She studies in the library.", "'she' + verb + s ending"),
            ("Water boils at 100 degrees.", "a general truth, always in present simple"),
        ],
        [
            ("He study every night.", "He studies every night.", "third-person singular needs -s or -es"),
            ("I don't likes tea.", "I don't like tea.", "the -s never appears in negatives with 'do/does'"),
        ],
        "If the sentence contains 'every', 'always', 'usually', or 'never', the present simple is almost always the right choice.",
    ),
    (
        "nouns_pronouns",
        "Nouns and Pronouns",
        "Once you're comfortable swapping nouns for pronouns, your speech stops sounding repetitive and starts sounding natural.",
        "A noun names a person, place, or thing (student, Lagos, phone). A pronoun replaces a noun so you don't repeat it. Subject pronouns (I, you, he, she, it, we, they) do the action; object pronouns (me, you, him, her, it, us, them) receive it.",
        [
            ("Chidi lost his pen.", "'his' replaces the repeated 'Chidi's'"),
            ("I saw them at the library.", "'them' replaces a group already known"),
            ("She gave me the book.", "'me' is the object of 'gave'"),
        ],
        [
            ("Chidi lost Chidi's pen.", "Chidi lost his pen.", "repeated names sound childish"),
            ("Her is my friend.", "She is my friend.", "'her' is an object pronoun, not a subject"),
        ],
        "Read your writing aloud. Anywhere you hear the same name twice in a row, swap the second one for a pronoun.",
    ),
    (
        "adjectives",
        "Adjectives",
        "Adjectives are the colour and detail of English — they turn a flat 'a bag' into a vivid 'a small red bag'.",
        "Adjectives describe nouns. In English they come **before** the noun ('a busy road') or after the verbs 'be', 'seem', 'look' ('The exam is difficult'). When you use more than one, the natural order is opinion → size → colour → origin: 'a lovely small red bag'.",
        [
            ("She wore a beautiful blue dress.", "opinion (beautiful) before colour (blue)"),
            ("The lecture was interesting.", "adjective sits after the verb 'be'"),
            ("They live in a large old house.", "size (large) before age (old)"),
        ],
        [
            ("A dress blue.", "A blue dress.", "adjective comes before the noun, not after"),
            ("It's very fantastic.", "It's fantastic.", "already-strong adjectives don't take 'very'"),
        ],
        "Pick a stronger adjective instead of stacking weak ones — 'exhausted' beats 'very very tired'.",
    ),
    (
        "numbers",
        "Counting and Numbers",
        "Numbers show up every day — in prices, dates, phone digits, exam scores — and confident numbers instantly make you sound more fluent.",
        "Learn 1–20 as separate words. From 21 onwards, use a hyphen between the tens and the ones: twenty-one, thirty-five. For big numbers, group by 'hundred', 'thousand', 'million' with no plural 's' after them.",
        [
            ("thirty-seven, ninety-nine", "hyphens link the two parts"),
            ("two hundred and fifty", "British English adds 'and' before the tens"),
            ("one thousand five hundred", "no 's' — never 'thousands' when counting"),
        ],
        [
            ("Twenty one students.", "Twenty-one students.", "compound numbers take a hyphen"),
            ("Three hundreds naira.", "Three hundred naira.", "hundred/thousand/million never take an 's' after a number"),
        ],
        "Say your matric number, phone number, and today's date out loud in English every morning until the words feel automatic.",
    ),
    (
        "days_months",
        "Days and Months",
        "Names of days and months are simple but easy to muddle — and getting them wrong turns a clear appointment into a missed one.",
        "Days: Monday to Sunday, always capitalised. Months: January to December, always capitalised. Use 'on' with days ('on Friday'), 'in' with months and years ('in March', 'in 2026'), and 'at' with clock times ('at 3 pm').",
        [
            ("My exam is on Friday, the 14th of June.", "'on' with the day, 'of' before the month"),
            ("We usually travel in December.", "'in' with a month"),
            ("Classes start at 8 am on Monday.", "at + time, on + day"),
        ],
        [
            ("I have class on march.", "I have class in March.", "months take 'in', not 'on'; capitalise them"),
            ("My birthday is at Tuesday.", "My birthday is on Tuesday.", "days take 'on', not 'at'"),
        ],
        "Remember the ladder: at → clock time, on → day, in → month or year. Small word, big meaning.",
    ),
    (
        "colours",
        "Colours and Descriptions",
        "Colours are the easiest way to make a description specific — 'a bag' becomes something a listener can actually picture.",
        "Basic colours (red, blue, green, yellow, black, white) go **before** the noun. Add 'light' or 'dark' to specify a shade ('light blue', 'dark green'). When you combine colour with another adjective, opinion comes first: 'a beautiful blue dress'.",
        [
            ("She bought a light green umbrella.", "shade + colour + noun"),
            ("The sky is dark grey today.", "colour appears after 'is'"),
            ("A lovely white shirt.", "opinion (lovely) before colour (white)"),
        ],
        [
            ("A shirt white.", "A white shirt.", "colour comes before the noun"),
            ("The bag is blueish.", "The bag is bluish.", "spelling of the '-ish' shade word drops the 'e'"),
        ],
        "Describe three objects around you right now — one colour word each. Instant vocabulary practice.",
    ),
    (
        "family",
        "Family Vocabulary",
        "Family words let you introduce yourself in a way that feels warm and human, whether you're meeting a classmate or writing an application.",
        "The core family tree: parents (mother, father), siblings (brother, sister), grandparents, aunts, uncles, cousins. Your parents' siblings are aunts and uncles; their children are your cousins. Use 'have' to talk about family members: 'I have two brothers'.",
        [
            ("I have two brothers and one sister.", "use 'have', not 'am having'"),
            ("My aunt lives in Abuja.", "singular subject, third-person -s on the verb"),
            ("They are my cousins.", "'cousin' covers both male and female"),
        ],
        [
            ("I am having three sisters.", "I have three sisters.", "'have' for possession uses simple present, not continuous"),
            ("My father's brother is my nephew.", "My father's brother is my uncle.", "check the relationship direction carefully"),
        ],
        "Draw a quick family tree in English. Labelling each branch fixes the words in your memory better than any list.",
    ),
    (
        "food_drink",
        "Food and Drink Vocabulary",
        "Food is the fastest way into a language — it lets you order confidently, host a guest, or make small talk about lunch.",
        "Group food words by category: staples (rice, beans, bread), proteins (chicken, fish, egg), vegetables and fruit, drinks (water, tea, juice). Use countable / uncountable rules: 'a bottle of water' (uncountable) vs 'three eggs' (countable).",
        [
            ("I would like jollof rice and a bottle of water, please.", "polite order at a restaurant"),
            ("She's making beans for dinner.", "present continuous for a current action"),
            ("Do you drink tea or coffee?", "yes/no question with 'do'"),
        ],
        [
            ("Give me one water.", "Please can I have a bottle of water?", "water is uncountable — use a unit like 'bottle'"),
            ("I'm eating a rice.", "I'm eating rice.", "'rice' is uncountable — no 'a' before it"),
        ],
        "Order at least one meal today entirely in English, even if only mentally rehearsed. Confidence comes from practice, not perfection.",
    ),
    (
        "telling_time",
        "Telling the Time",
        "Being on time is a habit, but *saying* the time confidently is a skill — one that keeps you punctual for lectures, meetings, and calls.",
        "Ask with 'What time is it?'. On the hour: 'It's three o'clock'. At 30 minutes past: 'half past three'. At 15 minutes: 'quarter past' or 'quarter to'. Digital form works too: 'It's 3:45' — 'three forty-five'.",
        [
            ("It's quarter past six.", "6:15 in spoken form"),
            ("The class starts at half past nine.", "9:30 in spoken form"),
            ("It's twenty to eight.", "7:40 — count backwards from the next hour"),
        ],
        [
            ("It's the three o'clock.", "It's three o'clock.", "no 'the' before the time on the hour"),
            ("At 8 hour we start.", "We start at 8 o'clock.", "use 'o'clock', not 'hour', for exact hours"),
        ],
        "Set your phone clock to 12-hour format and read the time aloud every time you glance at it. Free daily practice.",
    ),
    (
        "paragraph_writing",
        "Simple Paragraph Writing",
        "A paragraph is one idea told clearly — master it, and every essay, email, and report you'll ever write gets easier.",
        "A good paragraph has three parts: a **topic sentence** stating the main idea, two or three **supporting sentences** with details or examples, and a **closing sentence** that wraps it up. Keep every sentence tied to the same single idea.",
        [
            ("My favourite subject is biology.", "topic sentence introduces the idea"),
            ("I enjoy the experiments and I like learning about the human body.", "supporting detail with two examples"),
            ("That is why biology feels alive to me.", "closing sentence returns to the main idea"),
        ],
        [
            ("Biology is fun. Football is my hobby. I have a sister.", "Biology is my favourite subject. I enjoy the experiments…", "one paragraph, one idea — not three unrelated ones"),
            ("A paragraph should be one sentence to save time.", "A paragraph should develop the idea in 3–5 sentences.", "single-sentence paragraphs skip the supporting detail"),
        ],
        "Before you write, say the paragraph's main idea in one line. If you can't, you're not ready to write it yet.",
    ),
    (
        "possessives",
        "Possessive Forms",
        "Possessives show ownership — knowing when to add 's' and when to use 'his' or 'her' saves you from awkward, repeated names.",
        "For singular owners, add 's ('Ada's book'). For plural owners ending in 's', add only an apostrophe ('the students' books'). Possessive adjectives (my, your, his, her, its, our, their) come **before** the noun. Possessive pronouns (mine, yours, his, hers, ours, theirs) stand alone.",
        [
            ("This is Ada's phone.", "singular possessor, add 's"),
            ("The teachers' room is upstairs.", "plural possessor already ends in 's'"),
            ("That book is mine.", "possessive pronoun stands alone"),
        ],
        [
            ("The book of Ada.", "Ada's book.", "English prefers 's over 'of' for people"),
            ("This pen is my.", "This pen is mine.", "'my' modifies a noun; alone, use 'mine'"),
        ],
        "Ask yourself: is the possessive followed by a noun? If yes → my/your/his; if no → mine/yours/his.",
    ),
    (
        "prepositions_place",
        "Simple Prepositions of Place",
        "Prepositions of place tell listeners *where* — and the wrong one can send a friend to the wrong room, floor, or city.",
        "Use **in** for enclosed spaces (in the room, in Lagos), **on** for surfaces (on the table, on the wall), and **at** for specific points (at the bus stop, at the door). Direction words like 'under', 'next to', 'between', and 'behind' work with any object.",
        [
            ("The keys are on the table.", "surface → 'on'"),
            ("She lives in Ibadan.", "enclosed area / city → 'in'"),
            ("Meet me at the gate.", "specific point → 'at'"),
        ],
        [
            ("I am at the room.", "I am in the room.", "rooms are enclosed spaces, not points"),
            ("The book is in the table.", "The book is on the table.", "a table's top is a surface, not an enclosure"),
        ],
        "Picture the object first: is it inside, on top, or at a point? The picture chooses the preposition.",
    ),
    (
        "question_words",
        "Question Words (Who / What / Where / When / Why)",
        "The five question words unlock every conversation — they invite the other person to give you real information, not just yes or no.",
        "Each question word asks for a different type of information: **who** (person), **what** (thing / action), **where** (place), **when** (time), **why** (reason), **how** (manner / degree). After the question word, keep normal auxiliary order: Wh + do/does/is/are + subject + verb.",
        [
            ("Who taught this lesson?", "asks about a person"),
            ("Where did you buy that shirt?", "asks about a place"),
            ("Why are you late?", "asks about a reason"),
        ],
        [
            ("You are where?", "Where are you?", "the question word comes first"),
            ("Why you late?", "Why are you late?", "you still need the auxiliary 'are'"),
        ],
        "Answer 'why' questions with 'because' — it forces you to give a full, connected reason instead of a shrug.",
    ),
    (
        "weather",
        "Basic Weather Vocabulary",
        "Weather is the friendliest small-talk topic in every English-speaking culture — a two-line exchange breaks the ice anywhere.",
        "Talk about weather with 'It is + adjective' (It's sunny) or 'It's + verb-ing' (It's raining). Common conditions: sunny, cloudy, windy, rainy, hot, cold, warm, cool. Ask with 'What's the weather like today?'.",
        [
            ("It's very sunny this afternoon.", "'be' + adjective for a state"),
            ("It's raining outside — take an umbrella.", "'be' + verb-ing for an action in progress"),
            ("What's the weather like in Jos?", "the standard question form"),
        ],
        [
            ("Today is rain.", "Today is rainy. / It's raining today.", "use an adjective or a continuous verb, not a noun"),
            ("The weather makes hot.", "The weather is hot.", "'weather' takes 'is', not 'makes'"),
        ],
        "Give a two-line English weather update in your head every morning. It's the easiest daily habit for fluency.",
    ),
    (
        "clothing",
        "Clothing Vocabulary",
        "Clothing words let you describe people, shop confidently, and give directions like 'the man in the red shirt'.",
        "Group clothing words by body area: tops (shirt, blouse, jacket), bottoms (trousers, skirt, shorts), footwear (shoes, sandals, boots), accessories (belt, hat, scarf). Use 'wear' for having clothes on, 'put on' for the action of dressing, and 'take off' for removing.",
        [
            ("She's wearing a blue jacket.", "'wearing' = has it on now"),
            ("I put on my shoes before leaving.", "'put on' = act of dressing"),
            ("He took off his cap indoors.", "'take off' = remove"),
        ],
        [
            ("I am wearing a trouser.", "I'm wearing trousers.", "'trousers' is plural in English"),
            ("She dresses a red shirt.", "She's wearing a red shirt.", "'dress' alone means 'get dressed', not 'wear'"),
        ],
        "Describe what three people around you are wearing, in one sentence each. Instant vocabulary drill.",
    ),
    (
        "body_parts",
        "Body Parts Vocabulary",
        "Body-part vocabulary matters far beyond biology — you need it to see a doctor, describe pain, or follow a workout video.",
        "Learn body parts head-to-toe: head, face, eyes, ears, nose, mouth, neck, shoulder, arm, hand, chest, back, stomach, leg, knee, foot. Some come in pairs and are usually mentioned in the plural: eyes, ears, hands, feet.",
        [
            ("My head hurts.", "singular part, singular verb"),
            ("She has beautiful eyes.", "paired parts stay plural"),
            ("He broke his left arm.", "possessive + adjective + body part"),
        ],
        [
            ("My foots are cold.", "My feet are cold.", "'foot' → 'feet' is irregular"),
            ("I have pain in my body head.", "I have a headache.", "English has dedicated words for common pains"),
        ],
        "Learn 'headache, stomach-ache, toothache, backache' together — one pattern, four words you'll actually need.",
    ),
    (
        "imperatives",
        "Simple Imperatives and Instructions",
        "Imperatives are the shortest sentences in English — perfect for recipes, directions, and any moment you need to be understood immediately.",
        "Use the base form of the verb, with no subject: 'Sit down', 'Turn left', 'Add sugar'. Make it negative with 'Don't' + verb. Add 'please' to soften it into a polite request.",
        [
            ("Please close the door.", "polite imperative with 'please'"),
            ("Don't touch the wire.", "negative imperative for warnings"),
            ("First boil the water, then add the rice.", "sequenced imperatives with 'first' and 'then'"),
        ],
        [
            ("You close the door.", "Close the door, please.", "commands drop the subject"),
            ("No touch that.", "Don't touch that.", "negative imperatives need 'don't', not 'no'"),
        ],
        "Write a short recipe or a set of directions in imperatives only. It's the fastest way to internalise the pattern.",
    ),
    (
        "daily_routines",
        "Describing Daily Routines",
        "Talking about your routine is often the first real conversation you have in English — with a classmate, a host, or a new colleague.",
        "Describe routines in the present simple. Use time markers (in the morning / afternoon / evening, at night) and frequency adverbs (always, usually, often, sometimes, never) placed **before** the main verb.",
        [
            ("I usually wake up at 6 a.m.", "frequency adverb before the verb"),
            ("She goes to class in the morning.", "'in' with parts of the day"),
            ("We never eat late at night.", "'never' before 'eat'"),
        ],
        [
            ("I wake up always at six.", "I always wake up at six.", "frequency adverbs sit before the main verb"),
            ("In night I sleep.", "At night I sleep.", "'night' takes 'at', not 'in'"),
        ],
        "Say your day out loud in seven short sentences. That's a routine — and a full speech at the same time.",
    ),
    (
        "transportation",
        "Transportation Vocabulary",
        "Getting around is one of the most useful early conversations — and it only takes a handful of words to do it confidently.",
        "Common transport words: car, bus, taxi, motorbike, train, plane, bicycle, boat. Use 'by' + transport for the general means ('by bus', 'by car') — but 'on foot' when you walk. For specific vehicles you're inside, say 'in a taxi', 'in the car'; for public transport, 'on the bus / train / plane'.",
        [
            ("I go to work by bus.", "'by' for a general means of transport"),
            ("She's on the train right now.", "'on' for public transport currently in use"),
            ("They came on foot.", "walking gets 'on foot', never 'by foot'"),
        ],
        [
            ("I came with car.", "I came by car.", "means of transport takes 'by'"),
            ("I am in the bus.", "I'm on the bus.", "public transport uses 'on', not 'in'"),
        ],
        "The rule of thumb: your own small vehicle → 'in'; a big shared one → 'on'; walking → 'on foot'.",
    ),
    (
        "shopping",
        "Shopping Vocabulary and Phrases",
        "Shopping in English gives you three real skills at once: asking, bargaining, and paying — all in a few polite phrases.",
        "Ask a price with 'How much is this?' or 'How much are these?'. Ask about size or availability with 'Do you have it in size 40?'. Pay with 'I'll take it' and 'Can I pay by card?'. Say 'thank you' at the end — polite Nigerian and international English both value it.",
        [
            ("How much are the shoes?", "plural noun → 'are'"),
            ("Do you have this in a smaller size?", "polite request about availability"),
            ("Can I pay by card?", "'by card' or 'in cash'"),
        ],
        [
            ("What is the price of this how much?", "How much is this?", "keep the question short and direct"),
            ("I want to pay with cash.", "I'd like to pay in cash.", "'in cash' is the standard phrase"),
        ],
        "Rehearse three shopping lines aloud before you enter the shop. Your future self will sound calm and clear.",
    ),
    (
        "directions",
        "Basic Directions",
        "Giving and following directions is a skill you'll use every trip — a wrong turn wastes time, but a confident phrase saves it.",
        "Give directions with imperatives: 'Go straight', 'Turn left / right', 'Take the second turning'. Use prepositions of place to describe landmarks: 'next to the bank', 'opposite the church', 'between the school and the shop'.",
        [
            ("Go straight for two blocks, then turn right.", "sequenced imperatives"),
            ("The bank is opposite the market.", "landmark description"),
            ("Take the second street on your left.", "'on your left' orients the listener"),
        ],
        [
            ("Turn to the right side.", "Turn right.", "'turn right' is shorter and more natural"),
            ("The shop is in front the bank.", "The shop is in front of the bank.", "always 'in front of', with 'of'"),
        ],
        "When you're being given directions, repeat each step back aloud. It confirms understanding and locks it in.",
    ),
    (
        "home_furniture",
        "Home and Furniture Vocabulary",
        "Home vocabulary lets you describe where you live, invite friends over, and understand a rental listing without guessing.",
        "Learn rooms (bedroom, kitchen, bathroom, living room) and furniture (bed, chair, table, sofa, wardrobe). Use 'there is / there are' to describe what a room contains: 'There is a bed in the bedroom', 'There are two chairs in the kitchen'.",
        [
            ("There is a big sofa in the living room.", "singular subject → 'there is'"),
            ("There are three windows in the bedroom.", "plural subject → 'there are'"),
            ("The kitchen is next to the dining room.", "location using 'next to'"),
        ],
        [
            ("There have a table.", "There is a table.", "existence uses 'there is / are', not 'have'"),
            ("I sit in the sofa.", "I sit on the sofa.", "surfaces take 'on'"),
        ],
        "Sketch your room and label every item in English. Turning vocabulary into a picture doubles what you remember.",
    ),
    (
        "future_going_to",
        "Simple Future Tense: 'going to'",
        "The 'going to' future is how English speakers announce their plans — from tonight's dinner to next year's degree.",
        "Form: subject + am/is/are + going to + base verb. Use it for planned intentions and predictions based on evidence. It's slightly more informal than 'will', which suits promises and spontaneous decisions.",
        [
            ("I'm going to visit my aunt this weekend.", "planned action"),
            ("Look at those clouds — it's going to rain.", "prediction from evidence"),
            ("They're going to buy a new car next month.", "future intention"),
        ],
        [
            ("I going to visit her.", "I'm going to visit her.", "you still need the auxiliary 'am / is / are'"),
            ("She is going to visits her aunt.", "She is going to visit her aunt.", "the main verb stays in base form"),
        ],
        "If you can already picture the plan happening, 'going to' is the right tense.",
    ),
    (
        "likes_dislikes",
        "Likes and Dislikes",
        "Talking about what you like and dislike shows personality — it's the difference between a survey answer and a real conversation.",
        "Verbs for preference: like, love, enjoy, prefer, hate, dislike. After them, use either a noun ('I like tea') or the -ing form ('I like drinking tea'), never the bare infinitive. Ask with 'Do you like…?' — never 'Are you liking?'.",
        [
            ("I love reading in the evenings.", "verb of preference + -ing"),
            ("She prefers coffee to tea.", "'prefer + noun + to + noun'"),
            ("They hate waiting in queues.", "'hate' + -ing"),
        ],
        [
            ("I like to drinking tea.", "I like drinking tea. / I like to drink tea.", "either -ing or 'to' + verb, not both"),
            ("Are you liking mangoes?", "Do you like mangoes?", "'like' is a state verb — simple present, not continuous"),
        ],
        "Pair every preference with a reason: 'because it's…'. It turns a one-word answer into a real conversation.",
    ),
    (
        "health_illness",
        "Basic Health and Illness Vocabulary",
        "Health vocabulary keeps you safe abroad — a doctor understands 'I have a fever' faster than any hand-signal.",
        "Talk about illness with 'I have + illness' (I have a cold, a fever, a cough) or 'I feel + adjective' (I feel dizzy, tired, weak). Common pains use 'a … ache' (headache, stomach-ache, toothache). To describe how long, use 'for' + duration.",
        [
            ("I have a bad headache.", "'have' + 'a' + ache"),
            ("She feels dizzy this morning.", "'feel' + adjective"),
            ("He's had a fever for two days.", "'for' + duration"),
        ],
        [
            ("I am having fever.", "I have a fever.", "state of health uses simple present, not continuous"),
            ("My head is paining me.", "I have a headache. / My head hurts.", "'paining' is regional; standard English uses 'hurt' / 'ache'"),
        ],
        "Learn the pain words in pairs: hurt / ache, feel / have, cold / flu. Pairs stick better than isolated lists.",
    ),
    (
        "hobbies",
        "Hobbies and Free Time",
        "Hobbies are the easiest way to keep a conversation going past introductions — everyone has one, and everyone likes talking about theirs.",
        "Ask 'What do you do in your free time?'. Answer with 'I like / love / enjoy + -ing' or 'I'm into + noun/-ing'. Add frequency ('every weekend') and a short reason ('because it relaxes me') to sound natural.",
        [
            ("I enjoy playing football on weekends.", "'enjoy' + -ing + time phrase"),
            ("She's really into photography.", "'into' + noun, casual and friendly"),
            ("We love hiking because it clears our heads.", "preference + reason"),
        ],
        [
            ("My hobby is play football.", "My hobby is playing football.", "after 'is', use the -ing form"),
            ("I like the football.", "I like football.", "no 'the' with a sport in general"),
        ],
        "Prepare a 30-second answer to 'What do you do for fun?' — one hobby, why you like it, how often. It'll serve you for years.",
    ),
    (
        "simple_comparisons",
        "Simple Comparisons (bigger / smaller)",
        "Comparisons make descriptions specific — 'a big city' is vague, but 'bigger than Ibadan' immediately places it.",
        "For short adjectives, add -er and follow with 'than': 'faster than', 'bigger than'. Adjectives ending in a single vowel + consonant double the consonant ('big → bigger'). Adjectives ending in -y change to -ier ('happy → happier').",
        [
            ("Lagos is bigger than Ibadan.", "short adjective + -er + than"),
            ("This test was easier than the last one.", "-y → -ier"),
            ("My phone is newer than yours.", "possessive pronoun stands alone as second half"),
        ],
        [
            ("Lagos is more bigger than Ibadan.", "Lagos is bigger than Ibadan.", "never use both '-er' and 'more' together"),
            ("She is taller that her brother.", "She is taller than her brother.", "'than', not 'that', in comparisons"),
        ],
        "One syllable → add -er. Three or more → use 'more'. Two syllables → check whether it ends in -y.",
    ),
    (
        "review_beginner",
        "Beginner Review and Consolidation",
        "Reviewing puts your knowledge into a network — and a networked memory is what turns short-term study into long-term skill.",
        "Revisit the beginner path in four blocks: **tenses** (present simple, going-to future), **descriptions** (adjectives, colours, comparisons), **daily life** (routines, likes, hobbies, health), and **communication** (greetings, questions, directions, shopping). Try to link at least one lesson from each block into a single short story about your day.",
        [
            ("I usually wake up at 6, and I'm going to run today.", "present simple + going-to future in one line"),
            ("My friend, who is taller than me, likes swimming.", "comparison + preference"),
            ("Excuse me — how much is this? I'll take it, thanks.", "directions and shopping combined"),
        ],
        [
            ("Skipping revision because 'I already learned it'.", "Doing a 10-minute weekly review.", "review is what stops forgetting; new material adds on top"),
            ("Reading through notes silently.", "Speaking your review aloud.", "your ear teaches your mouth, not your eye"),
        ],
        "Every Sunday, write five sentences about your week that use five different lessons from this path. Review, applied.",
    ),
]


INTERMEDIATE_LESSONS = [
    (
        "present_perfect",
        "Present Perfect Tense",
        "The present perfect is the bridge between past and present — the tense that says 'this happened, and it still matters'.",
        "Form: subject + have/has + past participle. Use it for experiences ('I have visited Ghana'), recent actions with present results ('We've just eaten'), and unfinished periods ('I've lived here for two years'). Don't use it with finished time markers like 'yesterday' — the past simple takes those.",
        [
            ("She has visited three countries.", "life experience — no specific time"),
            ("I have lived here for two years.", "'for' + duration, still true now"),
            ("We've just finished the assignment.", "recent, with present relevance"),
        ],
        [
            ("I have seen him yesterday.", "I saw him yesterday.", "'yesterday' is finished — use past simple"),
            ("She have lived in Abuja.", "She has lived in Abuja.", "third-person singular takes 'has'"),
        ],
        "Ask yourself: is the effect still true now? If yes, use the present perfect; if the moment is closed, use the past simple.",
    ),
    (
        "past_simple",
        "Past Simple Tense",
        "The past simple is the tense of storytelling — the tense you'll use to describe every yesterday, every trip, and every finished event.",
        "Form: regular verbs add -ed ('walked', 'studied'); many common verbs are irregular ('go → went', 'eat → ate'). For negatives and questions, use 'did' + base verb: 'Did you attend?' — 'No, I didn't attend'. Time markers include 'yesterday', 'last week', 'in 2023', 'ago'.",
        [
            ("I wrote the test yesterday.", "irregular verb + finished-time marker"),
            ("Did you attend the lecture?", "'did' + subject + base verb"),
            ("She studied for six hours last night.", "-ied ending for -y verbs"),
        ],
        [
            ("I didn't went to class.", "I didn't go to class.", "after 'did/didn't', use the base form"),
            ("Yesterday I have finished it.", "Yesterday I finished it.", "'yesterday' forbids the present perfect"),
        ],
        "Learn irregular verbs in threes: base, past, past participle (go, went, gone). Threes are the shape you'll need for later tenses too.",
    ),
    (
        "conjunctions",
        "Conjunctions and Linking Words",
        "Linking words are the difference between a list of ideas and a flowing argument — they show your reader how each thought connects.",
        "Basic conjunctions join within a sentence: 'and' adds, 'but' contrasts, 'because' gives a reason, 'so' shows a result. Formal linkers ('however', 'therefore', 'moreover', 'nevertheless') connect whole sentences and often sit after a semicolon or at the start of a new sentence.",
        [
            ("Although it rained, we went out.", "'although' concedes a point"),
            ("The plan was clear; however, the team disagreed.", "formal linker between two sentences"),
            ("She studied hard, so she passed easily.", "'so' shows a result"),
        ],
        [
            ("I like tea. Also I like coffee.", "I like tea and coffee. / I like tea; I also like coffee.", "avoid starting a fragment with 'Also'"),
            ("Because it rained. We stayed home.", "Because it rained, we stayed home.", "'because' clauses need a main clause to attach to"),
        ],
        "Cover your paragraph and read only the linkers aloud. If they don't tell a story on their own, add or fix them.",
    ),
    (
        "reading_comprehension",
        "Reading Comprehension",
        "Reading well isn't about knowing every word — it's about grasping the writer's point and the evidence behind it faster than you read.",
        "Read in three passes: **skim** for the general idea, **scan** for specific information, and **close-read** for detail. Look for the topic sentence (usually first in the paragraph), transition words that signal the argument, and any word repeated across paragraphs — repetition marks the writer's core idea.",
        [
            ("Skim the title, subheadings, and first sentence of each paragraph.", "gives you the map before the journey"),
            ("Underline transition words like 'however', 'therefore', 'in contrast'.", "these mark shifts in the argument"),
            ("Ask: what does the writer want me to believe by the end?", "shifts your focus from words to purpose"),
        ],
        [
            ("Looking up every unknown word before finishing the passage.", "Guessing from context first, then checking a few after.", "stopping breaks your comprehension flow"),
            ("Trusting the first sentence as the answer to every question.", "Checking the whole paragraph — the main idea can appear later.", "sometimes writers build up before stating the point"),
        ],
        "Time yourself: skim for one minute, then explain the passage's point in a single sentence. It's a habit standardised tests reward.",
    ),
    (
        "formal_informal",
        "Formal vs Informal Language",
        "Every conversation lives on a formal–informal scale, and matching the register shows real fluency more than any grammar rule does.",
        "Formal English avoids contractions ('do not' vs 'don't'), slang, and short imperatives; it prefers full sentences, complete titles, and polite indirect requests. Informal English uses contractions, casual vocabulary, and short answers. Match the register to your audience: lecturer → formal, close friend → informal.",
        [
            ("I would like to request an extension.", "formal — 'would like', no contraction"),
            ("Can I get an extra day, please?", "neutral — polite but conversational"),
            ("Hey, mind if I turn it in tomorrow?", "informal — friend-only tone"),
        ],
        [
            ("Yo prof, gimme more time.", "Dear Dr. Adeyemi, I would like to request more time.", "authority relationships need formality"),
            ("It is being wanted that you attend.", "Please attend.", "over-formal, passive constructions sound stiff, not polite"),
        ],
        "Before you send an email, name the register in one word ('formal', 'friendly', 'firm'). It'll shape every sentence you write.",
    ),
    (
        "phrasal_verbs",
        "Phrasal Verbs",
        "Phrasal verbs are the shortcuts everyday English speakers reach for first — knowing them lets you sound natural, not textbook-stiff.",
        "A phrasal verb is a verb + a particle (usually a preposition or adverb) whose combined meaning is often idiomatic: 'give up' (quit), 'look after' (care for), 'run into' (meet by chance). Some are separable ('turn the light off') and some are not ('run into her').",
        [
            ("She gave up smoking last year.", "'give up' = quit"),
            ("Can you look after the baby for an hour?", "'look after' = care for"),
            ("I ran into an old friend at the market.", "'run into' = meet by chance"),
        ],
        [
            ("Turn off it.", "Turn it off. / Turn off the light.", "with pronouns, the particle comes after"),
            ("Give up to smoke.", "Give up smoking.", "after phrasal verbs, use the -ing form"),
        ],
        "Learn phrasal verbs in full sentences with a memorable image. 'Run into' with 'my old teacher at the market' beats it as a list entry.",
    ),
    (
        "email_writing",
        "Writing Emails",
        "A crisp email gets the reply you want — a rambling one gets ignored, no matter how important the message.",
        "Every professional email needs: a specific **subject line**, a **greeting** matched to the recipient, a **first sentence stating your purpose**, a short **body**, and a polite **sign-off**. Keep paragraphs short (two to three lines) and end each email with a clear next step.",
        [
            ("Subject: Request for exam timetable — ENG 202", "specific subject saves the reader's time"),
            ("Dear Dr. Okafor, I am writing to ask about the exam timetable.", "greeting + purpose in one line"),
            ("Yours sincerely, / Best regards, — Ada", "match the sign-off to the greeting"),
        ],
        [
            ("Hey ma, when we go do exam?", "Dear Dr. Okafor, when will the exam take place?", "informal tone for authority is a common mistake"),
            ("Please respond to my email as soon as possible.", "Could you reply by Friday?", "'ASAP' is vague — a specific date is polite and clearer"),
        ],
        "Rule of thumb: if you can't state your purpose in the first sentence, you don't know it well enough to write the email yet.",
    ),
    (
        "expressing_opinions",
        "Expressing Opinions",
        "Sharing your view politely is one of the highest-value skills in English — it's how you contribute to a class, a team, or a debate.",
        "Open with 'In my opinion', 'I believe', 'It seems to me', or 'From my perspective'. Support your view with a reason ('because…', 'the main reason is…'). Disagree respectfully with 'I see your point, but…' or 'That's true, however…'. End by inviting others: 'What do you think?'.",
        [
            ("In my opinion, the new timetable is better because classes start later.", "opinion + reason"),
            ("I see your point, but I'd argue it also raises fees.", "polite disagreement"),
            ("What do you think about this proposal?", "invitation to keep the discussion balanced"),
        ],
        [
            ("You are wrong.", "I see it differently — let me explain why.", "direct contradiction shuts down conversation"),
            ("My opinion is the truth.", "In my opinion / I believe…", "opinion phrases keep the claim humble and open"),
        ],
        "Always pair opinion + reason + example. Three short parts, and you sound structured every time.",
    ),
    (
        "comparatives_superlatives",
        "Comparatives and Superlatives",
        "Comparatives and superlatives sharpen every description — they rank, they contrast, and they make numbers meaningful.",
        "Short adjectives (1 syllable): add -er / -est ('fast → faster → fastest'). Long adjectives (3+ syllables): use 'more' / 'the most' ('more interesting'). Two-syllable adjectives ending in -y take -ier / -iest ('happy → happier → happiest'). Irregulars: good → better → best; bad → worse → worst.",
        [
            ("Kano is the oldest of the three cities.", "superlative for 3+ items"),
            ("This lecture was more interesting than yesterday's.", "long adjective + 'more' + 'than'"),
            ("She is happier now than last year.", "-y → -ier"),
        ],
        [
            ("It is the more best film.", "It is the best film.", "never combine 'more' and '-est' — pick one"),
            ("He is intelligenter.", "He is more intelligent.", "3+ syllable adjectives use 'more', not -er"),
        ],
        "Sort adjectives by syllable count before you compare them — one, two, or three. The syllable count picks the form.",
    ),
    (
        "narrative_writing",
        "Narrative Writing",
        "A good story pulls a reader in — and narrative writing is the skill that turns 'I went out yesterday' into something worth reading.",
        "A narrative has a **setting** (where and when), **characters**, a **problem**, and a **resolution**. Use the past tense to move events forward, and time signals — 'first', 'then', 'suddenly', 'finally' — to guide the reader. Add sensory detail and short dialogue to make scenes vivid.",
        [
            ("On a hot Tuesday afternoon, I was walking home when a stranger stopped me.", "setting + action + tension"),
            ("Suddenly, the lights went out.", "'suddenly' signals a turning point"),
            ("'What are you doing here?' she asked.", "one line of dialogue lifts the scene"),
        ],
        [
            ("I went, I saw, I ate, I came back.", "Show one moment in detail rather than listing five.", "listing kills tension; scenes create it"),
            ("Mixing present and past tense mid-story.", "Pick past simple as your base and stay in it.", "consistent tense keeps the reader oriented"),
        ],
        "Give every story a single vivid sensory detail — a smell, a sound, or a temperature. It's what readers remember.",
    ),
    (
        "past_continuous",
        "Past Continuous Tense",
        "The past continuous captures action in the middle of happening — the tense of 'while' and interrupted moments.",
        "Form: subject + was/were + verb-ing. Use it for actions in progress in the past ('I was studying at 8 p.m.') and for a longer action interrupted by a shorter one in the past simple ('I was reading **when** the phone rang').",
        [
            ("I was reading when the phone rang.", "long action (past continuous) + short interruption (past simple)"),
            ("They were playing football all afternoon.", "extended action in progress"),
            ("What were you doing at midnight?", "question form with 'were'"),
        ],
        [
            ("I was ate when she called.", "I was eating when she called.", "past continuous needs 'was/were' + -ing"),
            ("While I studied, the light went off.", "While I was studying, the light went off.", "'while' usually pairs with the continuous form"),
        ],
        "If you can insert 'in the middle of' before the verb, the past continuous is the natural choice.",
    ),
    (
        "modal_verbs",
        "Modal Verbs (can / could / should / must)",
        "Modal verbs are how English speaks about possibility, ability, permission, and obligation — small words that change a sentence's meaning entirely.",
        "Modals sit before the base verb, never before an -ing or infinitive: 'can go', 'should study', 'must leave'. Each modal has a job: **can** (ability, permission), **could** (past ability, polite request), **should** (advice), **must** (strong obligation), **may / might** (possibility).",
        [
            ("You should rest before the exam.", "'should' = advice"),
            ("Could you close the window, please?", "'could' = polite request"),
            ("Students must submit the form by Friday.", "'must' = strong obligation"),
        ],
        [
            ("You should to rest.", "You should rest.", "no 'to' after a modal"),
            ("She cans swim.", "She can swim.", "modals never take an -s ending"),
        ],
        "Match the modal to the message: soft (could / should), medium (can / may), strong (must). Register lives in the choice.",
    ),
    (
        "reported_speech_basics",
        "Reported Speech Basics",
        "Reported speech is how you tell someone what another person said — and one small tense-shift keeps the whole story honest.",
        "When you report what someone said in the past, shift the tense back by one step: present simple → past simple, present continuous → past continuous, will → would, can → could. Pronouns and time words shift too: 'today' → 'that day', 'here' → 'there'.",
        [
            ("She said, 'I am tired.' → She said she was tired.", "present → past"),
            ("He said, 'I will call you.' → He said he would call me.", "will → would; 'you' → 'me'"),
            ("They said, 'We can help.' → They said they could help.", "can → could"),
        ],
        [
            ("She said she is tired.", "She said she was tired.", "past reporting verb triggers a tense shift back"),
            ("He asked when will I come.", "He asked when I would come.", "reported questions use statement order and a shifted modal"),
        ],
        "Say the direct speech out loud first, then shift the tense back one step. The physical pause helps you catch each shift.",
    ),
    (
        "question_tags",
        "Question Tags",
        "Question tags are the tiny confirmations at the end of a sentence — small clips of grammar that make you sound truly conversational.",
        "Attach an opposite-polarity tag to a statement: positive statement → negative tag ('You're coming, aren't you?'); negative statement → positive tag ('You're not tired, are you?'). Use the same auxiliary and pronoun that the main sentence uses.",
        [
            ("You're coming, aren't you?", "positive statement → negative tag"),
            ("She doesn't like tea, does she?", "negative statement → positive tag"),
            ("They've finished, haven't they?", "present perfect matches with 'haven't'"),
        ],
        [
            ("You are coming, are you?", "You are coming, aren't you?", "the tag must be opposite in polarity"),
            ("She sings well, isn't she?", "She sings well, doesn't she?", "no auxiliary in the main clause → use 'do/does'"),
        ],
        "Rising intonation on the tag → real question; falling intonation → seeking agreement. Same words, different meaning.",
    ),
    (
        "relative_clauses",
        "Relative Clauses (who / which / that)",
        "Relative clauses let you fit two ideas into one clean sentence — the mark of a fluent writer, not just a fluent speaker.",
        "Use **who** for people, **which** for things, and **that** for both in defining clauses. A **defining** clause (no commas) is essential: 'The book **that** I bought'. A **non-defining** clause (with commas) adds extra information: 'My brother, **who** lives in Abuja, called yesterday'.",
        [
            ("The teacher who taught us last term retired.", "defining, about a person"),
            ("The car, which was red, sped past.", "non-defining, adds detail with commas"),
            ("Show me the book that you bought.", "defining, about a thing"),
        ],
        [
            ("The man which came.", "The man who came.", "'which' is for things, not people"),
            ("My brother who lives in Abuja called — comma missing.", "My brother, who lives in Abuja, called.", "extra information takes commas"),
        ],
        "If you can drop the clause without changing the sentence's meaning, use commas. Otherwise, no commas — it defines who or what.",
    ),
    (
        "prefixes_suffixes",
        "Prefixes and Suffixes",
        "Learn a handful of prefixes and suffixes and you multiply your vocabulary — one root word can grow into a small family.",
        "**Prefixes** attach to the front and shift meaning: un- (opposite), re- (again), pre- (before), mis- (wrongly). **Suffixes** attach to the end and often change word class: -ness (noun from adjective), -ly (adverb from adjective), -able (adjective from verb).",
        [
            ("happy → unhappy, happiness, happily", "one root, three word forms"),
            ("read → reread, reader, readable", "prefix + suffix combinations"),
            ("act → actor, action, active, actively", "same root across four word classes"),
        ],
        [
            ("I redo the exercise twice again.", "I redid the exercise. / I did the exercise again.", "'re-' already means 'again' — don't stack it"),
            ("She sang beautiful.", "She sang beautifully.", "adverbs from -y adjectives need -ily / -ly"),
        ],
        "Write a root in the middle of a page and branch out prefixes and suffixes. Word-mapping is faster than word-listing.",
    ),
    (
        "synonyms_antonyms",
        "Synonyms and Antonyms",
        "Synonyms and antonyms give your writing variety and precision — the difference between 'good' and 'good, great, excellent, outstanding'.",
        "**Synonyms** are words with similar meanings ('big' / 'large' / 'huge'). **Antonyms** are opposites ('hot' / 'cold'). Synonyms are rarely perfectly interchangeable — 'thin' and 'skinny' both oppose 'fat', but one sounds neutral and the other rude. Register matters as much as meaning.",
        [
            ("happy — glad, delighted, thrilled", "same idea, rising intensity"),
            ("difficult — hard, tough, challenging", "same idea, different formality"),
            ("start — begin, commence, kick off", "informal → formal → casual"),
        ],
        [
            ("Using 'skinny' in a formal letter.", "Using 'slim' or 'slender' in a formal letter.", "some synonyms carry negative tone"),
            ("Substituting a word without checking it fits the context.", "Read the whole sentence after swapping — does it still sound natural?", "true synonyms are rare; near-synonyms need context checks"),
        ],
        "Learn synonyms in groups of three, ordered by intensity. Small → medium → strong beats a flat, unsorted list.",
    ),
    (
        "giving_advice",
        "Giving Advice",
        "Good advice sounds helpful, not bossy — and English gives you a whole ladder of soft phrases to keep it that way.",
        "Soft advice: 'You could…', 'Maybe you should…', 'It might help to…'. Medium: 'You should…', 'I'd recommend…'. Strong: 'You must…', 'You need to…'. Match the strength to the situation — a friend's minor problem calls for 'you could', a safety issue calls for 'you must'.",
        [
            ("You could try studying earlier in the morning.", "soft suggestion"),
            ("I'd recommend seeing a doctor.", "medium advice, personal"),
            ("You must not skip that medication.", "strong warning"),
        ],
        [
            ("You must to eat more.", "You must eat more.", "no 'to' after 'must'"),
            ("You should study or you fail.", "You should study, or you'll fail.", "conditional consequences need 'will'"),
        ],
        "Before you speak, ask: how urgent is this? The urgency picks the right level of directness.",
    ),
    (
        "job_interview",
        "Job Interview Vocabulary and Phrases",
        "The right phrase in the right moment can turn an interview from a test into a conversation — and that shift is often what wins the offer.",
        "Prepare for classic prompts: 'Tell me about yourself', 'What are your strengths?', 'Where do you see yourself in five years?'. Answer with the **STAR** structure — Situation, Task, Action, Result. Use positive verbs (led, managed, improved, delivered) and end each answer with a takeaway lesson.",
        [
            ("I led a team of five on a research project last year.", "positive verb + specific detail"),
            ("My biggest strength is problem-solving under pressure.", "answers a common prompt cleanly"),
            ("In five years, I see myself leading larger projects in this field.", "future-focused, tied to the role"),
        ],
        [
            ("I don't know, maybe something.", "One-word answers or 'I don't know' end the conversation. Prepare short stories instead.", "interviewers assess how you think, not just what you know"),
            ("I need this job because I need money.", "I'm interested in this role because it matches my skills in…", "focus on what you offer, not what you need"),
        ],
        "Prepare three STAR stories in advance. You can adapt them to almost any interview question you'll ever face.",
    ),
    (
        "telephone_email_etiquette",
        "Telephone and Email Etiquette",
        "Etiquette is invisible when done right — but one missing 'please' or a mistimed call can quietly damage a professional relationship.",
        "**Phone calls**: greet, identify yourself, state the reason within 20 seconds, and close with 'Thank you for your time'. **Emails**: use a specific subject line, a matching greeting, one clear ask per email, and a signature block. Reply within one business day even if only to acknowledge.",
        [
            ("Good morning, this is Ada calling from Uniosun about the internship placement.", "greet + identify + purpose in one line"),
            ("Subject: Follow-up on the report — action needed by Friday", "subject that tells the reader what and when"),
            ("Thanks for your quick reply — I'll have it done today.", "short acknowledgement builds trust"),
        ],
        [
            ("Calling a lecturer at 10 p.m.", "Wait for business hours unless it's urgent.", "timing is part of respect"),
            ("Replying 'ok' with no context.", "Replying 'Got it — I'll send the file by 5 p.m.'", "acknowledgement + next step avoids ambiguity"),
        ],
        "Treat every email as if the recipient is busy — one clear ask, one clear deadline, and a courteous line.",
    ),
    (
        "agree_disagree",
        "Expressing Agreement and Disagreement",
        "Skilled speakers can disagree without offending — and that skill is what turns arguments into productive discussions.",
        "**Agreement**: 'I agree', 'That's a good point', 'Exactly — and…'. **Partial**: 'I see your point, but…', 'To a certain extent, but…'. **Disagreement**: 'I'm afraid I don't agree', 'I see it differently — for me…'. Follow up with a reason so your position sounds thought through, not knee-jerk.",
        [
            ("I completely agree with you on that.", "strong agreement"),
            ("I see your point, but I'd argue the opposite.", "polite partial disagreement"),
            ("I'm afraid I don't agree — here's why…", "firm but polite disagreement"),
        ],
        [
            ("You are wrong.", "I see it differently — for me…", "direct contradiction ends discussion"),
            ("Yes, I agree, but I don't really agree.", "I agree in part, but not on X…", "hedging without a specific point sounds evasive"),
        ],
        "Always follow agreement or disagreement with a reason. 'Yes, because…' or 'No, because…' turns opinion into argument.",
    ),
    (
        "cause_effect",
        "Cause and Effect Language",
        "Cause-and-effect language turns a sequence of events into an explanation — the difference between a story and an argument.",
        "**Cause connectors**: because, since, as, due to, owing to. **Effect connectors**: so, therefore, as a result, consequently, thus. Structural pattern: 'X happened because Y' or 'Y happened, so X'. Formal writing prefers 'therefore', 'consequently'; conversation prefers 'so', 'because'.",
        [
            ("The road was blocked, so we arrived late.", "informal cause-effect with 'so'"),
            ("Owing to the strike, classes were postponed.", "formal cause with 'owing to' + noun"),
            ("Sales dropped; therefore, the price was cut.", "formal effect with 'therefore'"),
        ],
        [
            ("Because it rained. We stayed home.", "Because it rained, we stayed home.", "cause clauses need a main clause attached"),
            ("Due to it rained.", "Due to the rain / Because it rained.", "'due to' takes a noun, not a full clause"),
        ],
        "Say 'so' or 'because' out loud before you commit — one wraps effect, the other wraps cause. Small word, big test.",
    ),
    (
        "complaints",
        "Making Complaints Politely",
        "Politeness in a complaint isn't weakness — it's what gets you a refund faster than shouting ever will.",
        "Structure a polite complaint in four steps: **describe** the problem factually, **explain** the impact, **request** a specific fix, and **thank** the person for their help. Softeners like 'I'm afraid…', 'Unfortunately…', 'I wonder whether…' keep the tone civil.",
        [
            ("I'm afraid the order I received on Monday was damaged.", "'I'm afraid' softens the opening"),
            ("Unfortunately, that made me miss the deadline.", "'unfortunately' explains the impact"),
            ("Could you send a replacement by Friday, please?", "specific request + polite modal"),
        ],
        [
            ("This is unacceptable — I demand my money back!", "I'd appreciate a refund because the item didn't arrive on time.", "aggression stalls resolution"),
            ("Something is wrong with your service.", "The invoice on my account for June is incorrect — it shows £120 instead of £100.", "specific facts get specific action"),
        ],
        "State the fact, name the impact, ask for a fix. Three-line complaints get faster responses than three-page ones.",
    ),
    (
        "charts_trends",
        "Describing Charts and Trends",
        "Describing charts clearly is a superpower in academic and professional writing — a good sentence can replace a whole paragraph of numbers.",
        "Use trend verbs: **rise / increase**, **fall / decrease**, **remain stable**, **fluctuate**, **peak**, **plunge**. Pair each with a matching adverb: 'sharply', 'gradually', 'steadily'. Give the noun-form option too: 'a sharp rise', 'a steady decline'.",
        [
            ("Sales rose sharply in the second quarter.", "verb + adverb + time frame"),
            ("There was a gradual decline over three years.", "noun-form: 'a decline'"),
            ("Prices fluctuated between June and August, then stabilised.", "two trends in one sentence"),
        ],
        [
            ("The graph increases.", "Sales increased by 15% between 2022 and 2024.", "graphs don't move — the data does"),
            ("The line goes up up.", "The line rose steadily throughout 2023.", "prefer a trend verb + adverb to informal repetition"),
        ],
        "Every chart summary needs three things: direction, degree, and time frame. Miss one and the summary is incomplete.",
    ),
    (
        "travel_tourism",
        "Travel and Tourism Vocabulary",
        "Travel English is high-leverage — a handful of specific words is the difference between a smooth trip and a stranded one at the airport.",
        "Group by stage: **before** (book, itinerary, visa, passport), **at the airport** (check-in, boarding pass, luggage, customs), **at the destination** (reception, check-in / out, tourist information), **on the way home** (souvenir, jet lag). Learn each with a full sentence: 'I'd like to check in for my flight to Nairobi'.",
        [
            ("I'd like to check in for my flight to Nairobi, please.", "polite request at the airport"),
            ("Is breakfast included in the room rate?", "common hotel question"),
            ("Could you recommend a good local restaurant?", "friendly opener for local advice"),
        ],
        [
            ("I make check-in.", "I'd like to check in.", "'check in' is the verb; 'check-in' is the noun"),
            ("I have jet lag from too much sleep.", "I have jet lag from crossing time zones.", "jet lag is caused by time zones, not sleep length"),
        ],
        "Rehearse ten travel phrases before every trip. The 90 seconds you spend saves you an hour of stress at the counter.",
    ),
    (
        "social_media_tech",
        "Social Media and Technology Vocabulary",
        "Tech vocabulary changes fast, but a stable core is what lets you follow the news, join a chat, or set up a work tool without help.",
        "Core verbs: post, share, tag, follow, unfollow, block, mute, stream, upload, download, log in, sign up. Nouns: feed, post, story, DM, notification, algorithm, bandwidth, bug. Adjectives: viral, offline, remote, wireless. Combine them naturally: 'I muted the notifications so I could focus'.",
        [
            ("She went viral after posting that video.", "'go viral' as a verb phrase"),
            ("I DMed her about the meeting.", "'DM' as a verb — casual but common"),
            ("The algorithm keeps showing me the same posts.", "'algorithm' in everyday usage"),
        ],
        [
            ("I made post on Facebook.", "I posted on Facebook.", "'post' is the verb — no 'make'"),
            ("Please subscribe my channel.", "Please subscribe to my channel.", "'subscribe' takes 'to'"),
        ],
        "Every time you learn a new tech noun, learn its verb form too. 'Post / to post', 'stream / to stream' — pairs move together.",
    ),
    (
        "formal_letters",
        "Writing Formal Letters",
        "Formal letters still matter — applications, complaints, appeals, official notices — and their structure barely changes across decades.",
        "Full formal letter has: **sender's address** (top right), **date**, **recipient's address** (below, left), **subject / reference line**, **greeting** ('Dear Sir/Madam' or a name), **body** (purpose, details, request), **complimentary close** ('Yours sincerely' if you named them, 'Yours faithfully' if not), and **signature + printed name**.",
        [
            ("Yours sincerely, Ada Okafor", "used when you named the recipient"),
            ("Yours faithfully, Ada Okafor", "used when you wrote 'Dear Sir/Madam'"),
            ("Subject: Application for the position of Research Assistant", "specific subject aids routing"),
        ],
        [
            ("Dear Dr. Okafor, … Yours faithfully.", "Dear Dr. Okafor, … Yours sincerely.", "if you name them, 'sincerely'; if not, 'faithfully'"),
            ("I need this job pls give it to me.", "I would be grateful for the opportunity to be considered for this role.", "formality earns trust; slang loses it"),
        ],
        "Write the whole letter as if it will be printed and signed by hand — even if it won't. That mindset produces the right tone.",
    ),
    (
        "review_intermediate",
        "Intermediate Review and Consolidation",
        "Consolidation is the phase where scattered skills fuse into instinct — the point where you stop translating and start thinking in English.",
        "Revisit intermediate lessons in four bundles: **tenses** (present perfect, past simple, past continuous), **connectors** (linking words, cause–effect), **communication** (formal / informal, opinions, complaints), and **writing** (emails, narratives, reports, letters). Write one short paragraph that draws from each bundle.",
        [
            ("I've just finished a report which explains why sales dropped, so I've emailed it to my supervisor.", "present perfect + relative clause + cause-effect"),
            ("Yesterday, I was writing when the power went out, and I had to restart.", "past continuous + past simple"),
            ("I'd argue that formal emails need a clear subject line, a polite greeting, and one specific request.", "opinion + list + register"),
        ],
        [
            ("Learning many rules but never mixing them.", "Writing one paragraph that uses at least three.", "fluency is the ability to combine"),
            ("Reviewing only what's easy.", "Revisiting the topics you got wrong last time.", "your weak spots are your fastest growth points"),
        ],
        "Every Sunday, pick three intermediate lessons and combine them into one paragraph. Ten minutes; huge compound return.",
    ),
]


ADVANCED_LESSONS = [
    (
        "conditionals",
        "Conditional Sentences",
        "Conditionals let you speak precisely about the possible, the unlikely, and the impossible — the tenses of hypothesis and reasoning.",
        "Four core conditionals: **zero** (general truths — 'If you heat water, it boils'), **first** (real future — 'If it rains, I will stay home'), **second** (unlikely present — 'If I had a car, I would drive'), **third** (unreal past — 'If I had studied, I would have passed'). Match tenses carefully across the two clauses.",
        [
            ("If you heat water, it boils.", "zero conditional — general truth"),
            ("If I had a car, I would drive to campus.", "second — unreal present"),
            ("If I had studied, I would have passed.", "third — unreal past"),
        ],
        [
            ("If I will have time, I will help.", "If I have time, I will help.", "first conditional uses present, not 'will', in the 'if' clause"),
            ("If she would tell me, I would help.", "If she told me, I would help.", "avoid stacking two 'would's in the same conditional"),
        ],
        "Ask: real or unreal? Present or past? Two yes/no questions pick the conditional for you.",
    ),
    (
        "passive_voice",
        "Passive Voice",
        "The passive voice shifts focus from the doer to the deed — essential for objective, formal, and academic writing.",
        "Form: subject + be (in the right tense) + past participle (+ by + agent, when relevant). Use it when the actor is unknown, unimportant, or when you want to emphasise the action or the receiver.",
        [
            ("The results were announced yesterday.", "actor unimportant"),
            ("Antibiotics were discovered in 1928.", "action, not the discoverer, is the point"),
            ("The bill was signed into law by the president.", "actor still matters → keep 'by'"),
        ],
        [
            ("The results was announced.", "The results were announced.", "'be' must agree with the plural subject"),
            ("The book is wrote by her.", "The book is written by her.", "passive needs the past participle, not the past simple"),
        ],
        "Rule of thumb: prefer active in most writing; use passive when the actor is unknown, unimportant, or when the focus belongs on the action.",
    ),
    (
        "academic_vocabulary",
        "Academic Vocabulary",
        "Academic vocabulary isn't about impressing readers — it's about being precise where everyday words are ambiguous.",
        "Replace vague words with precise academic ones: 'demonstrate' > 'show'; 'obtain' > 'get'; 'significant' > 'big'; 'analyse' > 'look at'. Use hedging verbs to signal uncertainty: 'suggests', 'appears to', 'may indicate'. Prefer nominalisation for concision: 'the increase in cases' > 'cases went up more'.",
        [
            ("The data suggest a modest correlation.", "hedging verb 'suggest'"),
            ("Recent studies demonstrate a significant effect.", "precise verb + precise adjective"),
            ("The increase in cases raises questions.", "nominal form is concise"),
        ],
        [
            ("The study shows a lot of a big effect.", "The study demonstrates a substantial effect.", "casual quantifiers dilute academic writing"),
            ("It is 100% proven that…", "The evidence strongly suggests that…", "absolute claims mark inexperienced academic writing"),
        ],
        "Keep a short list of 10 academic verbs and their casual equivalents. Swap one per paragraph and your writing lifts fast.",
    ),
    (
        "argumentative_writing",
        "Argumentative Writing",
        "A good argument doesn't shout — it lines up evidence, anticipates objections, and lets the reader arrive at the conclusion with you.",
        "Structure: **introduction** with a thesis statement, **body paragraphs** each defending one supporting point with evidence, a **counter-argument** paragraph that acknowledges and rebuts the opposing view, and a **conclusion** that restates the thesis and shows why it matters. Use logical connectors: 'consequently', 'nevertheless', 'furthermore'.",
        [
            ("This essay argues that mandatory ICT courses improve graduate employability.", "clear thesis statement"),
            ("Critics argue that this crowds out core subjects; however, the data show only a 4% shift in credit loads.", "acknowledge and rebut"),
            ("Consequently, universities should treat ICT literacy as foundational.", "conclusion with 'consequently'"),
        ],
        [
            ("Presenting only one side of the argument.", "Acknowledge the counter-view before rebutting it.", "one-sided essays read as opinion, not argument"),
            ("Concluding with brand-new evidence.", "Save new evidence for the body; the conclusion synthesises what came before.", "the conclusion is a summary, not a surprise"),
        ],
        "For every claim, ask: what's the evidence, and what would a critic say? Handling both questions turns opinion into argument.",
    ),
    (
        "idioms",
        "Idioms and Expressions",
        "Idioms are fluency shortcuts — one phrase can replace a whole explanation, and native speakers recognise them instantly.",
        "Idioms mean more than the sum of their words. 'Hit the books' means 'study hard'; 'break the ice' means 'start a conversation'; 'once in a blue moon' means 'very rarely'. Learn each idiom with its meaning, register (formal / informal / neutral), and a memorable example sentence.",
        [
            ("Before finals, we all hit the books.", "'hit the books' = study hard"),
            ("Small talk helps break the ice at conferences.", "'break the ice' = start a conversation"),
            ("She only visits once in a blue moon.", "'once in a blue moon' = very rarely"),
        ],
        [
            ("It's raining animals today.", "It's raining cats and dogs.", "idioms don't translate literally"),
            ("Using 'kick the bucket' in a formal email.", "Use 'passed away' instead.", "match the idiom's register to the situation"),
        ],
        "Never use an idiom unless you're sure of its register. A well-chosen idiom lifts a paragraph; a wrong one derails it.",
    ),
    (
        "business_english",
        "Business English",
        "Business English is crisp, courteous, and outcome-focused — designed to move decisions forward without wasting anyone's time.",
        "Key phrases: 'Let's move to the next item', 'Could you clarify…?', 'Let's schedule a follow-up'. Soften requests with 'Would you consider…?'. Open meetings with an agenda and close with action points that name who does what by when.",
        [
            ("Let's schedule a follow-up call for Thursday.", "explicit next step"),
            ("Could you clarify the third bullet on slide four?", "polite, specific request"),
            ("As an action point: Ada will send the revised budget by Friday.", "who / what / when"),
        ],
        [
            ("Sending long, unsigned meeting minutes with no owners.", "End with 'Action points: X will do Y by Z'.", "owners + deadlines are what turn meetings into work"),
            ("Chasing a decision with 'reminder' emails only.", "Reply-all with 'Deciding by Friday will keep the project on track.'", "framing keeps you polite while raising urgency"),
        ],
        "Every meeting ends with three answers: what did we decide, who is doing it, and by when. Without those, you had a chat, not a meeting.",
    ),
    (
        "public_speaking",
        "Public Speaking Techniques",
        "Great speakers don't have magic — they have structure, pace, and rehearsal. Every one of those is learnable in weeks.",
        "Structure: **preview** what you'll say, **say it** in three signposted parts, then **summarise**. Vary pace: slow at key points, faster in bridging sections. Pause after headlines — silence emphasises meaning. Make eye contact across three zones (left, centre, right) so the whole room feels addressed.",
        [
            ("Today I'll cover three things: the problem, our approach, and the result.", "clear preview"),
            ("My second argument is even stronger, because…", "verbal signpost"),
            ("To conclude: we saw a 30% improvement.", "explicit closing"),
        ],
        [
            ("Reading verbatim from your slides.", "Look at the audience; use slides as prompts only.", "reading kills connection"),
            ("Speaking at one flat speed the whole time.", "Slow down for key points; pause after each.", "pace is what emphasis looks like in speech"),
        ],
        "Rehearse the first 30 seconds and last 30 seconds until they're automatic. Confidence at the edges carries the middle.",
    ),
    (
        "critical_analysis",
        "Critical Analysis of Texts",
        "Critical analysis is the difference between reading and thinking — the skill that turns a passage into a claim you can evaluate.",
        "Ask: what is the author's **purpose** (inform / persuade / entertain)? Who is the **audience**? What **evidence** is offered, and how strong is it? What is **omitted**? What **assumptions** does the argument rely on? Only after answering these do you evaluate whether the argument holds.",
        [
            ("The author's purpose is to persuade policymakers, evidenced by policy-focused language throughout.", "identifies purpose from language cues"),
            ("The article cites three studies but omits the largest recent meta-analysis.", "notes what's missing"),
            ("The argument assumes literacy is measured only by test scores — a debatable assumption.", "surfaces a hidden assumption"),
        ],
        [
            ("Summarising the text without evaluating it.", "Distinguish 'this is what it says' from 'this is how strong it is'.", "summary is a prerequisite for analysis, not a substitute"),
            ("Confusing tone with truth.", "A confident tone doesn't make the evidence sound.", "critical readers separate style from substance"),
        ],
        "Write a two-column note as you read: left column = what the text claims, right column = what would need to be true for it to be right.",
    ),
    (
        "reported_speech",
        "Advanced Grammar: Reported Speech",
        "Reported speech is a small piece of grammar that carries big consequences — it's how court reports, news articles, and academic citations preserve accuracy.",
        "Shift tenses back one step after a past reporting verb: present simple → past simple, present continuous → past continuous, present perfect → past perfect, will → would, can → could. Shift pronouns, time words ('today' → 'that day'), and place words ('here' → 'there') consistently. Report questions with 'asked' + statement order; report commands with 'told' + object + infinitive.",
        [
            ("She said, 'I am tired.' → She said she was tired.", "present → past"),
            ("He asked, 'Where do you live?' → He asked where I lived.", "reported question, statement order"),
            ("The teacher told us, 'Submit the assignment.' → The teacher told us to submit the assignment.", "commands use to-infinitive"),
        ],
        [
            ("He asked where did I live.", "He asked where I lived.", "reported questions drop the auxiliary and use statement order"),
            ("She said me she was busy.", "She told me she was busy. / She said she was busy.", "'said' takes no object; 'told' takes one"),
        ],
        "Two speech patterns to keep straight: 'said (to me)' vs 'told me'. Same idea, different grammar.",
    ),
    (
        "professional_writing",
        "Professional Email and Report Writing",
        "Professional documents earn attention through structure — a busy reader should be able to grasp your point in the first ten seconds.",
        "Reports follow the pattern: **title**, **executive summary**, **introduction**, **findings**, **conclusion**, **recommendations**. Use numbered headings, one idea per paragraph, and short sentences. In emails, put the request in the first two lines and details after. Edit ruthlessly: cut hedges, verify names and numbers, and proofread before sending.",
        [
            ("Executive Summary: Sales grew 12% year-on-year, driven mainly by the northern region.", "the whole report in one line"),
            ("Recommendation 1: Reallocate 20% of the marketing budget to online channels.", "numbered, specific, actionable"),
            ("Please review section 3 and reply by Friday.", "email opening — request first, details later"),
        ],
        [
            ("Burying the ask in paragraph four.", "State the request in line 1 or 2.", "readers skim; make skimming enough"),
            ("Long, hedged sentences.", "Short sentences with strong verbs.", "professional writing values clarity over caution"),
        ],
        "Write the executive summary last — but read it first every time you edit. If the summary is wrong, the document is wrong.",
    ),
    (
        "subjunctive",
        "Subjunctive Mood",
        "The subjunctive is small in size but big in signal — it marks wishes, hypotheses, and formal recommendations with a subtle grammatical shift.",
        "Use the base form of the verb (no -s) after verbs of demand, suggestion, or requirement: 'The board **recommend** that she **be** appointed'. In hypothetical 'if I were you' and 'I wish I were…' constructions, use 'were' for all subjects — not 'was'. It's slightly formal, but it makes writing sound precise.",
        [
            ("I wish I were more patient.", "'were' for hypothetical, all subjects"),
            ("The committee insists that the report be revised.", "base form after 'insist that'"),
            ("If I were you, I'd apologise.", "hypothetical + advice"),
        ],
        [
            ("I wish I was there.", "I wish I were there.", "the subjunctive uses 'were' for all subjects in wishes"),
            ("The board suggests that he apologises.", "The board suggests that he apologise.", "after 'suggest that', use the base form"),
        ],
        "Watch for the trigger verbs — demand, insist, recommend, suggest, propose. After 'that', the verb goes back to its base form.",
    ),
    (
        "mixed_conditionals",
        "Advanced Conditionals (Mixed Conditionals)",
        "Mixed conditionals let you talk about how a past hypothetical would change the present, or how a present state would have changed a past outcome.",
        "**Past → present**: 'If I had studied medicine (past), I would be a doctor now (present)'. **Present → past**: 'If I were more careful (present state), I wouldn't have lost my phone (past)'. Combine the tense of each clause according to the time it refers to, not according to a memorised rule.",
        [
            ("If she had taken the job, she would be in Lagos now.", "past unreal → present result"),
            ("If I were fluent in French, I would have applied for that role.", "present state → past unreal"),
            ("If we had left earlier, we wouldn't be stuck in traffic now.", "past → present"),
        ],
        [
            ("If I had studied, I would pass the exam last month.", "If I had studied, I would have passed the exam last month.", "past result needs past-perfect + would have"),
            ("If she was here, she would have helped.", "If she were here, she would have helped.", "hypothetical 'she' takes 'were'"),
        ],
        "Label each clause with a time (past / present) before you match the tense. Mixed conditionals reward planning over instinct.",
    ),
    (
        "nominalisation",
        "Nominalisation in Academic Writing",
        "Nominalisation packs whole clauses into single noun phrases — the trick behind the dense, abstract style of academic writing.",
        "Turn verbs and adjectives into nouns to shift focus from the actor to the concept: 'The government decided quickly' → 'The government's rapid decision'. Nominalisation makes sentences shorter and more objective, but overuse turns writing into a fog. Balance nominal and verbal styles.",
        [
            ("The government's decision was rapid.", "verb 'decided' → noun 'decision'"),
            ("The failure of the project surprised the team.", "'failed' → 'failure' as the sentence subject"),
            ("His refusal to comply led to sanctions.", "verb-phrase → noun-phrase"),
        ],
        [
            ("The problem is because the system failed.", "The problem is the failure of the system.", "avoid a linking-verb + 'because' — nominalise instead"),
            ("Nominalising every verb.", "Balance nominal writing with clear verbs.", "over-nominalisation kills readability"),
        ],
        "If a paragraph reads like a fog, look for stacked nominalisations. Replacing one with a strong verb usually clears the whole passage.",
    ),
    (
        "cohesion",
        "Cohesion and Coherence Devices",
        "Cohesion is what makes paragraphs feel woven together — without it, even good sentences read like a list of unrelated thoughts.",
        "Use four families of devices: **reference** (this, that, these, such) to point back; **substitution** (do so, one) to avoid repeating; **conjunction** (however, in addition, therefore) to signal relationships; and **lexical cohesion** — repeating key nouns or using synonyms to keep the topic in view.",
        [
            ("The policy is controversial. This has drawn public attention.", "'this' refers back to the whole idea"),
            ("Sales grew in the north; in the south, they did so at half the rate.", "'did so' substitutes for 'grew'"),
            ("The trial worked; however, the sample was small.", "conjunction to link contrasting points"),
        ],
        [
            ("Overusing 'this' without a clear referent.", "Add a noun after 'this': 'This trend…', 'This policy…'.", "'this' alone can leave the reader guessing"),
            ("Repeating 'the study' ten times in a paragraph.", "Vary with 'the research', 'the paper', 'the analysis'.", "repetition without variation reads as monotony"),
        ],
        "After you write a paragraph, underline every cohesion word. If a sentence has none linking it to the previous one, the reader will feel the jolt.",
    ),
    (
        "persuasive_rhetoric",
        "Persuasive Rhetoric Techniques",
        "Rhetoric is the ancient art of moving audiences — and even a modern email is more persuasive when you use its three classical appeals.",
        "Aristotle's three appeals still apply: **ethos** (your credibility), **pathos** (the audience's emotion), and **logos** (the logic of your argument). Techniques include the **rule of three** ('quicker, cheaper, safer'), **rhetorical questions** ('Can we really afford to delay?'), and **contrast** ('Not X, but Y').",
        [
            ("Backed by twelve years in the field, I'm confident this plan works.", "ethos — credibility signal"),
            ("Can we really afford to delay?", "rhetorical question invites agreement"),
            ("Not delay — decision.", "contrast for punch"),
        ],
        [
            ("Relying only on emotion.", "Balance pathos with evidence and credibility.", "emotion without logic feels like manipulation"),
            ("Long rhetorical questions.", "Keep them short and pointed.", "one-line rhetorical questions land hardest"),
        ],
        "If a paragraph must persuade, check it against E–P–L. Missing one appeal is a specific fix, not a mystery.",
    ),
    (
        "negotiation",
        "Negotiation Language",
        "Negotiation isn't about winning — it's about finding the answer both sides can live with, and the right phrases keep the door open at every turn.",
        "Open with interests, not positions: 'We're looking for something that keeps the timeline realistic and the budget within range'. Use conditional language to explore options: 'If we could adjust the deadline, we could hold the price'. Bookmark disagreement politely: 'That's a challenge — help me understand your constraint'.",
        [
            ("If we could extend to March, we could keep the current budget.", "conditional trade-off"),
            ("Help me understand what's driving that number.", "opens up the other side's constraints"),
            ("Would you consider a phased delivery instead?", "polite alternative"),
        ],
        [
            ("Take it or leave it.", "Which of these two options works best for you?", "ultimatums close deals; options open them"),
            ("Agreeing to hold and then re-opening later.", "State constraints clearly upfront.", "clarity now saves conflict later"),
        ],
        "Every offer should carry a condition. 'Yes, if…' beats 'No', and keeps you in control of the exchange.",
    ),
    (
        "presenting_data",
        "Presenting Data and Statistics",
        "Statistics without context are noise — presenting them well is what turns numbers into decisions.",
        "Frame every statistic with three things: the **baseline** (compared to what?), the **time frame** (over what period?), and the **implication** (so what?). Prefer clear visuals to dense tables, round smart (12% is more memorable than 12.37%), and lead with the headline, not the method.",
        [
            ("Enrolment rose 22% between 2022 and 2024, driven mainly by the sciences.", "baseline + time frame + implication"),
            ("Only 4 in 10 respondents said the tool was clear — a 15-point drop from last year.", "ratio + comparison"),
            ("Headline: Costs are down 12%. Method (later): based on the last four quarters.", "headline first, method second"),
        ],
        [
            ("Reading a table aloud row by row.", "Highlight the two or three numbers that matter most.", "audiences remember three numbers, not thirty"),
            ("Using precision that isn't real.", "Round to the level of your data's accuracy.", "false precision undermines trust"),
        ],
        "Before a data slide, write the one-sentence takeaway underneath it. If you can't, the slide isn't ready.",
    ),
    (
        "abstracts_summaries",
        "Writing Abstracts and Executive Summaries",
        "The abstract is the most-read piece of any long document — write it as if it's the only paragraph the reader will ever see, because sometimes it is.",
        "An **abstract** (200–300 words) has five parts: background, purpose, method, results, conclusion. An **executive summary** (roughly one page) follows a similar order but adds recommendations. Both must stand alone — the reader shouldn't need to read the full document to understand them.",
        [
            ("This paper investigates X. Using a mixed-methods design, we found Y. The findings suggest Z.", "compressed abstract in three sentences"),
            ("Executive summary: The project succeeded on time and under budget; we recommend scaling to two additional units.", "summary + recommendation"),
            ("Objectives were: (1) X, (2) Y, (3) Z.", "numbered objectives for scannability"),
        ],
        [
            ("Copying the introduction as the abstract.", "Rewrite it from scratch — the abstract is a summary, not a preview.", "introductions preview; abstracts encapsulate"),
            ("Skipping the results in the abstract.", "State the top result explicitly — a % or a finding.", "readers stop reading if the abstract doesn't say what was found"),
        ],
        "Write the abstract last. It's the executive summary of your own writing, and only makes sense once the writing is finished.",
    ),
    (
        "advanced_idioms",
        "Advanced Idioms and Collocations",
        "Advanced idioms and collocations are the invisible glue of native-like English — the phrases that just 'sound right' together.",
        "**Collocations** are words that habitually pair (strong tea, make a decision, take responsibility). **Advanced idioms** carry cultural weight ('the elephant in the room', 'moving the goalposts'). Learn both in context; a wrong verb ('do a decision') marks you as a learner even when the grammar is right.",
        [
            ("The elephant in the room is the missed deadline.", "idiom for the obvious-but-unspoken issue"),
            ("Let's not move the goalposts halfway through.", "idiom for changing the rules unfairly"),
            ("She made a difficult decision under pressure.", "'make' collocates with 'decision', not 'do'"),
        ],
        [
            ("I did a mistake on the report.", "I made a mistake on the report.", "'make', not 'do', for mistakes"),
            ("Using regional idioms in international writing.", "Prefer widely-understood collocations.", "advanced idioms can confuse readers outside their culture"),
        ],
        "Keep a two-column notebook: left column = word, right column = the verbs and adjectives it usually pairs with. That's a working collocation dictionary.",
    ),
    (
        "register_tone",
        "Register and Tone Shifting",
        "Shifting register on demand is a professional superpower — the same message becomes friendly to a colleague, respectful to a client, and firm to a supplier.",
        "Register depends on **audience**, **purpose**, and **channel**. Shift by changing vocabulary (verbs and modals), sentence length (short = firm, longer = polite), and pronouns (we / you / one). Test your draft by imagining reading it aloud in the room the message will be received in.",
        [
            ("I'll get it done today.", "friendly, colleague-to-colleague"),
            ("The item will be delivered by end of day.", "neutral, service-oriented"),
            ("We regret that the delay persists and are actively resolving the underlying cause.", "formal, client-facing"),
        ],
        [
            ("Copy-pasting the same email to different audiences.", "Rewrite the greeting, verb strength, and closing line for each.", "one-size-fits-all messaging misses register"),
            ("Overshooting formality with friends.", "Match warmth to relationship — over-formality reads as distant.", "formality and coldness can look identical if overdone"),
        ],
        "Before you send, name the register in a single word (warm / neutral / firm). If any sentence breaks that word, rewrite it.",
    ),
    (
        "hedging",
        "Hedging Language in Academic Writing",
        "Hedging is how academic writers stay honest — it's the difference between claims that are defensible and claims that are naive.",
        "Hedge with **modal verbs** (may, might, could), **lexical verbs** (suggest, indicate, appear), **adverbs** (possibly, arguably, generally), and **noun phrases** ('there is some evidence that…'). Match the strength of the hedge to the strength of your evidence.",
        [
            ("The data suggest a modest correlation.", "hedge verb 'suggest'"),
            ("This may indicate a link between the two variables.", "'may' + hedge verb doubles the caution"),
            ("It is generally accepted that…", "hedge that acknowledges consensus without overclaiming"),
        ],
        [
            ("The results prove that X causes Y.", "The results suggest that X may contribute to Y.", "correlation is not causation; hedge accordingly"),
            ("Absolute language everywhere.", "Reserve absolute language for genuinely absolute claims.", "hedging conserves your credibility for the claims that matter"),
        ],
        "For every claim, ask: what would I need to say if my strongest evidence went missing tomorrow? That's the hedge to use today.",
    ),
    (
        "debate_counter_argument",
        "Debate and Counter-Argument Structures",
        "The best debaters don't just defend their view — they can steelman the opposing one and still show why theirs is stronger.",
        "Standard debate move: **claim** → **evidence** → **impact** → **counter** → **rebuttal**. When you counter, restate the opposing view fairly ('It's true that…') before rebutting ('however, the recent evidence shows…'). A weak rebuttal to a straw-man argument fools no one.",
        [
            ("Claim: Remote learning improves access. Evidence: enrolment rose 25%. Impact: more inclusive education.", "C–E–I structure"),
            ("It's true that some students struggle without in-person contact; however, hybrid models close that gap.", "acknowledge + rebut"),
            ("The stronger version of the opposing view is that…", "steelmanning language"),
        ],
        [
            ("Attacking the person instead of the argument.", "Attack the argument, respect the person.", "personal attacks lose credibility"),
            ("Ignoring the strongest counter-argument.", "Address the strongest one directly — burying it looks weak.", "the strongest counter is the one your audience is already thinking"),
        ],
        "Steelman before rebutting. If you can state the opposite view better than its supporters, your rebuttal lands harder.",
    ),
    (
        "advanced_punctuation",
        "Advanced Punctuation (semicolons, colons, em-dashes)",
        "Advanced punctuation is the writer's typography — small marks that shape the reader's pace, emphasis, and understanding.",
        "**Semicolons** join two closely related independent clauses ('The project succeeded; the team celebrated'). **Colons** introduce a list, quote, or explanation ('One thing matters: the deadline'). **Em-dashes** (—) mark a sharp break or emphasise an aside ('The plan — flawed as it was — worked').",
        [
            ("The project succeeded; the team celebrated.", "semicolon links two independent clauses"),
            ("One thing matters: the deadline.", "colon introduces an explanation"),
            ("The plan — flawed as it was — worked.", "em-dashes mark an emphatic aside"),
        ],
        [
            ("The project succeeded, the team celebrated.", "The project succeeded; the team celebrated. / The project succeeded, and the team celebrated.", "a comma between two independent clauses is a splice"),
            ("The plan - flawed as it was - worked.", "The plan — flawed as it was — worked.", "hyphens (-) are not em-dashes (—); use the correct mark"),
        ],
        "Use each mark sparingly. One semicolon per paragraph is elegant; five in a row is a signal to rewrite.",
    ),
    (
        "literary_devices",
        "Literary Devices in English Writing",
        "Literary devices give writing rhythm and image — the moves that lift a piece from clear to memorable.",
        "Common devices: **metaphor** (implicit comparison — 'time is money'), **simile** (explicit comparison — 'quiet as a mouse'), **alliteration** (repeated initial sound — 'wild and windy'), **personification** (giving objects human qualities), **irony** (opposite of expectation). Use them sparingly and always in service of meaning.",
        [
            ("Time is money.", "metaphor — no 'like' or 'as'"),
            ("She was as quiet as a mouse.", "simile — explicit comparison"),
            ("The waves whispered along the shore.", "personification"),
        ],
        [
            ("Mixing metaphors: 'That's a hot potato; we need to nip it in the bud.'", "Pick one metaphor and follow it through.", "mixed metaphors distract more than they clarify"),
            ("Overusing devices in professional writing.", "Reserve devices for moments of emphasis.", "in business or academic writing, restraint is a device too"),
        ],
        "If a device doesn't sharpen the meaning, cut it. Ornament without purpose is clutter.",
    ),
    (
        "cross_cultural",
        "Cross-Cultural Communication Nuances",
        "Cross-cultural fluency is more than language — it's understanding what's polite, direct, or offensive in the culture you're writing to.",
        "Communication styles vary along a **direct–indirect** axis (Germans direct, Japanese indirect), a **high-context–low-context** axis (much left unsaid vs. everything spelled out), and a **formal–informal** axis. Adjust openings, silence norms, gift language, and requests to match the culture you're addressing.",
        [
            ("I'd appreciate your input at your convenience.", "polite, indirect — good for high-context cultures"),
            ("Please send the report by Friday.", "direct, low-context — good for German or Dutch business norms"),
            ("Thank you for your continued partnership.", "warm, relationship-oriented opener"),
        ],
        [
            ("Assuming your directness translates as friendliness.", "Ask how the recipient's culture handles requests.", "directness can read as rude in indirect cultures"),
            ("Using humour or idioms untested in the target culture.", "Reserve humour for known contexts.", "idioms and jokes are the fastest way to be misunderstood"),
        ],
        "Before you write, ask: what does polite look like in the recipient's culture? Answer that, then draft.",
    ),
    (
        "advanced_phrasal_verbs",
        "Advanced Phrasal Verbs",
        "Advanced phrasal verbs let you sound completely fluent — a well-placed 'brush up on' beats 'improve your knowledge of' every time.",
        "Advanced examples: **come up with** (produce, invent), **fall through** (fail to happen), **carry out** (perform), **put up with** (tolerate), **pull off** (achieve unexpectedly), **brush up on** (revise). Many are separable ('carry the plan out' / 'carry it out'), and most have a single-verb formal equivalent for academic writing.",
        [
            ("She came up with a brilliant solution.", "'come up with' = produce, invent"),
            ("The deal fell through at the last moment.", "'fall through' = fail to happen"),
            ("We need to brush up on our French before the trip.", "'brush up on' = revise"),
        ],
        [
            ("Using phrasal verbs unchanged in academic writing.", "Replace with single-verb equivalents: 'produced', 'failed'.", "academic register prefers concision"),
            ("Splitting non-separable phrasal verbs.", "Keep 'run into someone' together, not 'run someone into'.", "some phrasal verbs simply won't split"),
        ],
        "For each new advanced phrasal verb, learn one formal single-verb synonym. You'll code-switch effortlessly between registers.",
    ),
    (
        "ambiguity_precision",
        "Ambiguity and Precision in Professional Writing",
        "Ambiguity is what turns a clear request into two people doing two different things — precision is the professional discipline that prevents it.",
        "Precision has three enemies: **vague quantifiers** ('some', 'many'), **unclear referents** ('it', 'this' without a noun), and **loose modifiers** ('only I saw him' vs 'I only saw him'). Fix each by naming the referent, quantifying with numbers or ranges, and placing modifiers directly next to what they modify.",
        [
            ("Send it to the client soon → Send version 3 to Ada Okafor by Friday 5 p.m.", "specific noun + specific person + specific time"),
            ("Only three team members received the update.", "modifier placed correctly"),
            ("The report contains 45 pages, split across four chapters.", "quantified instead of 'many'"),
        ],
        [
            ("Please review it and let me know.", "Please review section 4 of the attached report and reply by Thursday.", "'it' and 'let me know' both need specifics"),
            ("We should improve customer satisfaction.", "We should raise customer satisfaction from 72% to 80% by Q3.", "goal + metric + deadline beats a slogan"),
        ],
        "Before you send, re-read every 'it', 'this', and 'soon'. Each one is a chance for confusion — replace or explain.",
    ),
    (
        "review_advanced",
        "Advanced Review and Consolidation",
        "At advanced level, consolidation means turning strong isolated skills into a mature, adaptable voice — one that shifts register, argues cleanly, and writes with precision.",
        "Revisit advanced content in four bands: **grammar depth** (conditionals, subjunctive, reported speech), **academic style** (nominalisation, hedging, cohesion), **rhetoric and argument** (persuasion, debate, critical analysis), and **professional communication** (business, negotiation, cross-cultural). Rewrite one paragraph from an earlier lesson at higher precision each week.",
        [
            ("Had the policy been reviewed earlier, the delay might have been avoided.", "mixed conditional + hedged claim"),
            ("Nevertheless, the evidence suggests a more nuanced conclusion than the abstract implies.", "hedged rebuttal, formal register"),
            ("This paper argues, and demonstrates through three case studies, that…", "structured, precise, formal"),
        ],
        [
            ("Learning advanced grammar without practising rhetoric.", "Balance form (grammar) with function (argument, register).", "form without function is decoration, not fluency"),
            ("Reviewing by re-reading only.", "Rewrite one old paragraph per week at the new level.", "advanced English is built by rewriting, not re-reading"),
        ],
        "Advanced fluency is a rewriting habit. Take a lesson from the beginner path and rewrite it at advanced level — you'll see your progress in one page.",
    ),
]


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

def _row_from(entry, index):
    topic, title, hook, rule, examples, mistakes, tip = entry
    md = build_content(title, hook, rule, examples, mistakes, tip)
    return {
        "topic": topic,
        "title": title,
        "content_markdown": md,
        "content": markdown_to_plaintext(md),
        "quiz_types": quiz_types_for(topic, index),
    }


def seed(force: bool = False):
    app = create_app()
    with app.app_context():
        existing = Lesson.query.count()
        if existing > 0 and not force:
            print(
                f"Lessons already seeded ({existing} found). "
                "Pass --force to wipe and re-seed."
            )
            return

        if force and existing > 0:
            from models import Question
            Question.query.delete()
            Lesson.query.delete()
            db.session.commit()
            print(f"Wiped {existing} old lessons (and their questions).")

        order = 1
        for i, entry in enumerate(CORE_LESSONS):
            row = _row_from(entry, i)
            db.session.add(
                Lesson(
                    title=row["title"],
                    content=row["content"],
                    content_markdown=row["content_markdown"],
                    estimated_minutes=6,
                    level="beginner",  # core lessons available to all levels
                    topic=row["topic"],
                    path_type="core",
                    order_index=order,
                    quiz_types=json.dumps(row["quiz_types"]),
                )
            )
            order += 1

        for level, bank in (
            ("beginner", BEGINNER_LESSONS),
            ("intermediate", INTERMEDIATE_LESSONS),
            ("advanced", ADVANCED_LESSONS),
        ):
            for i, entry in enumerate(bank):
                row = _row_from(entry, i)
                db.session.add(
                    Lesson(
                        title=row["title"],
                        content=row["content"],
                        content_markdown=row["content_markdown"],
                        estimated_minutes=6,
                        level=level,
                        topic=row["topic"],
                        path_type="level_path",
                        order_index=i + 1,
                        quiz_types=json.dumps(row["quiz_types"]),
                    )
                )

        db.session.commit()
        total = Lesson.query.count()
        print(f"Seeded {total} lessons (expected 89: 5 core + 28 × 3 paths).")


if __name__ == "__main__":
    force = "--force" in sys.argv
    seed(force=force)
