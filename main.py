from csv import writer, reader
from argparse import ArgumentParser

from pygiftparser import parser
from pygiftparser.gift import MultipleChoiceRadio, Question, Answer

from flashcard_generator import FlashCardGenerator
from reportlab.lib.units import cm


def get_answer_index(q: Question):
    return list(
        map(lambda o: o.prefix, q.answer.options)  # ty:ignore[unresolved-attribute]
    ).index("=")

def get_options(q: Question):
    options_text = list(map(
        lambda o: o.raw_text[1:],
        q.answer.options,  # ty:ignore[unresolved-attribute]
    ))
    return options_text


def write_csv(file_path, questions: list[Question], delimiter: str, time_limit: int, template="template.csv"):
    NUM_CHOICES = 4
    n = 0

    rows = []
    with open(template, 'r') as file:
        csv_reader = reader(file)
        rows = [r for r in csv_reader]
    
    if len(rows) == 0:
        raise ValueError("Failed to read template or invalid template")
    
    for i, q in enumerate(questions):
        row_idx = i + 2
        options_text = list(map(
            lambda o: o.raw_text[1:],
            q.answer.options,  # ty:ignore[unresolved-attribute]
        ))
        options_text.extend([''] * (NUM_CHOICES - len(options_text)))

        answer_idx = get_answer_index(q)
        content = [i + 1, q.text, *options_text, time_limit, answer_idx + 1]
        for col, item in enumerate(content):
            rows[row_idx][col] = item
        n += 1


    with open(file_path, "w", newline="") as file:
        csv = writer(file, delimiter=delimiter)
        csv.writerows(rows)
    return n


def load_questions(file_path: str):
    questions = []
    with open(file_path) as file:
        gift = parser.parse(file.read())
        questions = gift.questions
    return questions

def create_flashcards(questions: list[Question]):
    generator = FlashCardGenerator()
    generator.set_filename("flashcards.pdf")
    # generator.set_page_size([8.5, 11])
    generator.set_cards_per_row(3)
    generator.set_card_height(6*cm)
    for i, q in enumerate(questions):
        options = get_options(q)
        correct_idx = get_answer_index(q)
        generator.add_entry(q.text, options[correct_idx], index=str(i+1))
    generator.generate()


def get_args():
    parser = ArgumentParser("GIFT to CSV")
    parser.add_argument(
        "--gift_path", required=True, type=str, help="Path to GIFT file"
    )

    limit_time = lambda x: x if x in range(1, 301) else 300

    parser.add_argument(
        "--output", "-o", type=str, default="blooket.csv", help="Output path for CSV"
    )
    parser.add_argument(
        "--delimiter",
        "-d",
        default=",",
        type=str,
        help="Delimiter for separating values",
    )
    parser.add_argument(
        "--time",
        "-t",
        default=300,
        type=limit_time,
        help="Time Limit (sec) (Max: 300 seconds)",
    )

    parser.add_argument(
        "--template",
        default="template.csv",
        type=str,
        help="Path to template csv"
    )

    parser.add_argument(
        "--flashcard",
        default=False,
        action='store_true',
        help='Additionally generate flashcards'
    )

    return parser.parse_args()


def main():
    args = get_args()
    questions = load_questions(args.gift_path)
    print(f"Found {len(questions)} questions.")
    n_written = write_csv(args.output, questions, args.delimiter, args.time, args.template)
    print(f"Wrote {n_written} questions.")

    if(args.flashcard):
        create_flashcards(questions)
        print("Created flashcards.")


if __name__ == "__main__":
    main()
