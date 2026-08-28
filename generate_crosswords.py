#!/usr/bin/env python3

"""
Daily Mental Health Crossword Generator

Run:
    python generate_crosswords.py

Output:
    puzzles.json

The generated puzzles are validated before being written.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

TARGET_PUZZLES = 365
MAX_ATTEMPTS_PER_PUZZLE = 5000
SEED = 20260828

OUTPUT = Path("puzzles.json")


# ============================================================
# WORD DATA
# ============================================================

# answer, clue
WORDS = [
    ("ABLE", "Having the capacity or confidence to cope"),
    ("ACCEPT", "To acknowledge something without fighting it"),
    ("ACCEPTANCE", "Recognizing thoughts or feelings without judgment"),
    ("ACT", "Acceptance and Commitment Therapy"),
    ("ADHD", "A condition involving attention and impulse regulation"),
    ("AFFECT", "The observable expression of emotion"),
    ("ALONE", "Being by oneself"),
    ("ANGER", "A strong emotional response to perceived wrong"),
    ("ANGST", "A feeling of anxiety or apprehension"),
    ("ANXIETY", "A feeling of worry or unease"),
    ("AWARE", "Conscious of thoughts, feelings, or surroundings"),
    ("AWARENESS", "Recognition of thoughts, feelings, or experiences"),
    ("BAD", "Describing an unpleasant emotional state"),
    ("BALANCE", "A healthy sense of stability"),
    ("BEING", "The state of existing"),
    ("BELIEF", "Something accepted as true"),
    ("BOND", "A connection between people"),
    ("BRAVE", "Showing courage despite fear"),
    ("BURNOUT", "Exhaustion caused by prolonged stress"),
    ("CALM", "A state of reduced agitation"),
    ("CARE", "Attention given to wellbeing"),
    ("CBT", "Cognitive Behavioral Therapy"),
    ("CHANGE", "The process of becoming different"),
    ("CHECK", "To examine or monitor something"),
    ("CHOICE", "An act of selecting between possibilities"),
    ("COPE", "To manage a difficult situation"),
    ("COPING", "Ways of managing stress or difficulty"),
    ("CRISIS", "A period of intense difficulty or danger"),
    ("DBT", "Dialectical Behavior Therapy"),
    ("DEEP", "Extending strongly inward or intensely"),
    ("DENIAL", "Refusal to accept a difficult reality"),
    ("DEPRESS", "To lower mood or emotional energy"),
    ("DEPRESSION", "A mental health condition involving persistent low mood"),
    ("DIAGNOSIS", "Identification of a health condition"),
    ("DISTRESS", "Significant emotional suffering"),
    ("DOUBT", "Uncertainty about something"),
    ("EASE", "Freedom from tension or distress"),
    ("EMOTION", "A feeling or affective state"),
    ("EMPATHY", "Understanding another person's feelings"),
    ("ENERGY", "A person's capacity for activity"),
    ("ERP", "Exposure and Response Prevention"),
    ("ESCAPE", "An attempt to get away from distress"),
    ("EXERCISE", "Physical activity that can support wellbeing"),
    ("EXHAUST", "To use up physical or emotional energy"),
    ("FAIR", "Reasonable and just"),
    ("FEAR", "An emotional response to perceived threat"),
    ("FEEL", "To experience an emotion"),
    ("FEELING", "An emotional experience"),
    ("FOCUS", "Directed attention"),
    ("FORGIVE", "To release resentment toward someone"),
    ("FREE", "Not constrained or trapped"),
    ("FRIEND", "A person who provides companionship and support"),
    ("GAD", "Generalized Anxiety Disorder"),
    ("GRIEF", "The emotional response to loss"),
    ("GROW", "To develop or improve"),
    ("GROWTH", "Positive development or change"),
    ("HABIT", "A repeated behavior or pattern"),
    ("HEAL", "To recover or become healthier"),
    ("HEALTH", "A state of physical or mental wellbeing"),
    ("HELP", "Support provided to someone in need"),
    ("HOPE", "A sense that positive change is possible"),
    ("INNER", "Existing within the mind or self"),
    ("INSIGHT", "A deeper understanding of oneself"),
    ("JOY", "A feeling of great happiness"),
    ("KIND", "Showing consideration and care"),
    ("KINDNESS", "Considerate and compassionate behavior"),
    ("LISTEN", "To pay attention to what someone says"),
    ("LONELY", "Feeling alone or disconnected"),
    ("LOSS", "The experience of something or someone being gone"),
    ("LOVE", "A strong feeling of affection or care"),
    ("MANIA", "A period of unusually elevated or irritable mood"),
    ("MIND", "The part of a person involved in thought"),
    ("MINDFUL", "Attentive to the present moment"),
    ("MINDFULNESS", "Awareness of the present moment without judgment"),
    ("MOOD", "A person's emotional state"),
    ("MOTIVE", "A reason for behavior"),
    ("MOTIVATION", "The drive to act"),
    ("NEED", "Something required for wellbeing"),
    ("NURTURE", "To care for and encourage growth"),
    ("OCD", "Obsessive-Compulsive Disorder"),
    ("OPEN", "Willing to consider or discuss something"),
    ("PANIC", "A sudden surge of intense fear"),
    ("PEACE", "A state of calm or tranquility"),
    ("PHQ", "Patient Health Questionnaire"),
    ("POSITIVE", "Constructive or beneficial"),
    ("PTSD", "Post-Traumatic Stress Disorder"),
    ("QUIET", "A low-stimulation or calm state"),
    ("REST", "Recovery through relaxation or sleep"),
    ("RESET", "A fresh start after stress"),
    ("RESILIENCE", "The ability to recover from difficulty"),
    ("SAFE", "Free from danger or threat"),
    ("SAFETY", "Protection from harm or danger"),
    ("SAD", "Seasonal Affective Disorder"),
    ("SELF", "A person's identity or sense of who they are"),
    ("SHAME", "A painful feeling of negative self-evaluation"),
    ("SLEEP", "An important part of mental wellbeing"),
    ("SMILE", "A facial expression often associated with happiness"),
    ("SOCIAL", "Relating to interaction with others"),
    ("SOLACE", "Comfort during distress or sadness"),
    ("STABLE", "Emotionally steady or balanced"),
    ("STRESS", "A response to challenging demands"),
    ("SUPPORT", "Help provided to someone"),
    ("TALK", "To communicate through speech"),
    ("THERAPY", "Treatment intended to support mental health"),
    ("THINK", "To use the mind to process information"),
    ("TOUGH", "Able to withstand difficulty"),
    ("TRAUMA", "A deeply distressing experience"),
    ("TRUST", "Confidence in another person or process"),
    ("VALID", "Recognized as understandable or legitimate"),
    ("WELL", "In a healthy or satisfactory state"),
    ("WELLBEING", "A state of health, comfort, and happiness"),
    ("WORRY", "Repeated thoughts about possible problems"),
]


# Only 3-5 letter answers are allowed.
WORDS = [
    (answer.upper(), clue)
    for answer, clue in WORDS
    if 3 <= len(answer) <= 5
    and answer.isalpha()
]


WORD_MAP = dict(WORDS)


# ============================================================
# CROSSWORD REPRESENTATION
# ============================================================

@dataclass(frozen=True)
class Slot:
    number: int
    direction: str
    row: int
    col: int
    length: int


@dataclass
class Puzzle:
    grid: list[list[str]]
    across: list[dict]
    down: list[dict]


# ============================================================
# GRID PATTERNS
# ============================================================

# '#' is a block.
# '.' is an open square.
#
# Patterns are deliberately symmetric.
#
# Every run must be >= 3 characters.

PATTERNS = [
    [
        ".....",
        "..#..",
        ".....",
        "..#..",
        ".....",
    ],

    [
        ".....",
        ".#.#.",
        ".....",
        ".#.#.",
        ".....",
    ],

    [
        "..#..",
        ".....",
        ".....",
        ".....",
        "..#..",
    ],

    [
        ".....",
        "#...#",
        ".....",
        "#...#",
        ".....",
    ],
]


# ============================================================
# PATTERN ANALYSIS
# ============================================================

def get_slots(pattern: list[str]) -> list[Slot]:
    starts = []

    for r in range(5):
        for c in range(5):
            if pattern[r][c] == "#":
                continue

            across = (
                (c == 0 or pattern[r][c - 1] == "#")
                and c + 1 < 5
                and pattern[r][c + 1] != "#"
            )

            down = (
                (r == 0 or pattern[r - 1][c] == "#")
                and r + 1 < 5
                and pattern[r + 1][c] != "#"
            )

            if across or down:
                starts.append((r, c))

    starts.sort()

    slots = []
    number = 1

    for r, c in starts:
        across = (
            (c == 0 or pattern[r][c - 1] == "#")
            and c + 1 < 5
            and pattern[r][c + 1] != "#"
        )

        down = (
            (r == 0 or pattern[r - 1][c] == "#")
            and r + 1 < 5
            and pattern[r + 1][c] != "#"
        )

        if across:
            length = 0
            while (
                c + length < 5
                and pattern[r][c + length] != "#"
            ):
                length += 1

            if length < 3:
                raise ValueError("Invalid Across slot")

            slots.append(
                Slot(number, "across", r, c, length)
            )

        if down:
            length = 0
            while (
                r + length < 5
                and pattern[r + length][c] != "#"
            ):
                length += 1

            if length < 3:
                raise ValueError("Invalid Down slot")

            slots.append(
                Slot(number, "down", r, c, length)
            )

        number += 1

    return slots


# ============================================================
# CANDIDATES
# ============================================================

def slot_cells(slot: Slot):
    if slot.direction == "across":
        return [
            (slot.row, slot.col + i)
            for i in range(slot.length)
        ]

    return [
        (slot.row + i, slot.col)
        for i in range(slot.length)
    ]


def candidate_words(
    slot: Slot,
    grid: list[list[str]],
):
    candidates = []

    for word in WORD_MAP:
        if len(word) != slot.length:
            continue

        okay = True

        for i, (r, c) in enumerate(slot_cells(slot)):
            existing = grid[r][c]

            if existing != "." and existing != word[i]:
                okay = False
                break

        if okay:
            candidates.append(word)

    return candidates


# ============================================================
# SOLVER
# ============================================================

def solve(
    pattern: list[str],
    rng: random.Random,
):
    slots = get_slots(pattern)

    across = [
        s for s in slots
        if s.direction == "across"
    ]

    down = [
        s for s in slots
        if s.direction == "down"
    ]

    if len(across) != 5 or len(down) != 5:
        return None

    grid = [
        [
            "#" if pattern[r][c] == "#" else "."
            for c in range(5)
        ]
        for r in range(5)
    ]

    assignment = {}

    def search():
        unfilled = [
            slot for slot in slots
            if slot.number.__str__() + slot.direction
            not in assignment
        ]

        if not unfilled:
            return True

        best = None
        best_candidates = None

        for slot in unfilled:
            candidates = candidate_words(slot, grid)

            if not candidates:
                return False

            if (
                best_candidates is None
                or len(candidates) < len(best_candidates)
            ):
                best = slot
                best_candidates = candidates

        rng.shuffle(best_candidates)

        for word in best_candidates:
            cells = slot_cells(best)

            old = [
                grid[r][c]
                for r, c in cells
            ]

            valid = True

            for i, (r, c) in enumerate(cells):
                if (
                    grid[r][c] != "."
                    and grid[r][c] != word[i]
                ):
                    valid = False
                    break

                grid[r][c] = word[i]

            if not valid:
                for (r, c), value in zip(cells, old):
                    grid[r][c] = value
                continue

            key = str(best.number) + best.direction
            assignment[key] = word

            if search():
                return True

            del assignment[key]

            for (r, c), value in zip(cells, old):
                grid[r][c] = value

        return False

    if not search():
        return None

    return Puzzle(
        grid=grid,
        across=[],
        down=[],
    ), slots, assignment


# ============================================================
# BUILD PUZZLE JSON
# ============================================================

def make_puzzle(
    pattern: list[str],
    rng: random.Random,
):
    result = solve(pattern, rng)

    if result is None:
        return None

    puzzle, slots, assignment = result

    across = []
    down = []

    for slot in slots:
        key = str(slot.number) + slot.direction
        answer = assignment[key]

        item = {
            "number": slot.number,
            "answer": answer,
            "clue": WORD_MAP[answer],
            "row": slot.row,
            "col": slot.col,
            "length": slot.length,
        }

        if slot.direction == "across":
            across.append(item)
        else:
            down.append(item)

    return {
        "grid": [
            "".join(row)
            for row in puzzle.grid
        ],
        "across": across,
        "down": down,
    }


# ============================================================
# VALIDATION
# ============================================================

def validate_puzzle(puzzle: dict):
    grid = puzzle["grid"]

    assert len(grid) == 5

    for row in grid:
        assert len(row) == 5

    assert len(puzzle["across"]) == 5
    assert len(puzzle["down"]) == 5

    for direction in ("across", "down"):
        for entry in puzzle[direction]:

            answer = entry["answer"]

            assert 3 <= len(answer) <= 5
            assert answer.isalpha()
            assert answer in WORD_MAP
            assert entry["clue"] == WORD_MAP[answer]

            cells = []

            if direction == "across":
                for i in range(len(answer)):
                    cells.append(
                        (
                            entry["row"],
                            entry["col"] + i
                        )
                    )
            else:
                for i in range(len(answer)):
                    cells.append(
                        (
                            entry["row"] + i,
                            entry["col"]
                        )
                    )

            for i, (r, c) in enumerate(cells):
                assert 0 <= r < 5
                assert 0 <= c < 5
                assert grid[r][c] == answer[i]

    # Verify numbering.
    starts = {}

    for direction in ("across", "down"):
        for entry in puzzle[direction]:
            key = (
                entry["row"],
                entry["col"]
            )

            starts.setdefault(key, set()).add(
                entry["number"]
            )

    for numbers in starts.values():
        assert len(numbers) == 1

    # Verify crossing consistency.
    for r in range(5):
        for c in range(5):
            letters = []

            for direction in ("across", "down"):
                for entry in puzzle[direction]:
                    if direction == "across":
                        cells = [
                            (entry["row"], entry["col"] + i)
                            for i in range(entry["length"])
                        ]
                    else:
                        cells = [
                            (entry["row"] + i, entry["col"])
                            for i in range(entry["length"])
                        ]

                    if (r, c) in cells:
                        idx = cells.index((r, c))
                        letters.append(entry["answer"][idx])

            if letters:
                assert len(set(letters)) == 1

    return True


# ============================================================
# GENERATION
# ============================================================

def canonical(puzzle):
    return json.dumps(
        puzzle,
        sort_keys=True,
        separators=(",", ":")
    )


def generate():
    rng = random.Random(SEED)

    puzzles = []
    seen = set()

    attempts = 0

    while len(puzzles) < TARGET_PUZZLES:

        attempts += 1

        if attempts > TARGET_PUZZLES * MAX_ATTEMPTS_PER_PUZZLE:
            raise RuntimeError(
                f"Could only generate {len(puzzles)} "
                f"unique puzzles after {attempts} attempts."
            )

        pattern = rng.choice(PATTERNS)

        puzzle = make_puzzle(
            pattern,
            rng
        )

        if puzzle is None:
            continue

        validate_puzzle(puzzle)

        fingerprint = canonical(puzzle)

        if fingerprint in seen:
            continue

        seen.add(fingerprint)
        puzzles.append(puzzle)

        print(
            f"Generated {len(puzzles):3}/{TARGET_PUZZLES}"
        )

    # Final complete validation.
    for index, puzzle in enumerate(puzzles, start=1):
        try:
            validate_puzzle(puzzle)
        except Exception as exc:
            raise RuntimeError(
                f"Puzzle {index} failed validation: {exc}"
            ) from exc

    data = {
        "version": 1,
        "puzzleCount": len(puzzles),
        "generatedBy": "generate_crosswords.py",
        "puzzles": puzzles,
    }

    OUTPUT.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print()
    print("=" * 60)
    print(f"Generated:  {len(puzzles)} puzzles")
    print(f"Validated:  {len(puzzles)} puzzles")
    print(f"Output:     {OUTPUT.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    generate()
