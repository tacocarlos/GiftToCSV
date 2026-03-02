from csv import writer
from argparse import ArgumentParser

from pygiftparser import parser
from pygiftparser.gift import MultipleChoiceRadio, Question, Answer


def get_answer_index(q: Question):
    return list(
        map(lambda o: o.prefix, q.answer.options)  # ty:ignore[unresolved-attribute]
    ).index("=")


def write_csv(file_path, questions: list[Question], delimiter: str, time_limit: int):
    n = 0
    with open(file_path, "w", newline="") as file:
        # how is their template this messed up?
        text = """"Blooket
Import Template",,,,,,,,,,,,,,,,,,,,,,,,,
Question #,Question Text,Answer 1,Answer 2,"Answer 3
(Optional)","Answer 4
(Optional)","Time Limit (sec)
(Max: 300 seconds)","Correct Answer(s)
(Only include Answer #)",,,,,,,,,,,,,,,,,,
"""
        file.write(text)
        file.flush()
        csv = writer(file, delimiter=delimiter)
        for i, q in enumerate(questions):
            # remove prefix to hide the correct answer
            options_text = map(
                lambda o: o.raw_text[1:],
                q.answer.options,  # ty:ignore[unresolved-attribute]
            )
            answer_idx = get_answer_index(q)
            content = [i + 1, q.text, *options_text, time_limit, answer_idx + 1]
            blanks = ["" for _ in range(26 - len(content))]
            csv.writerow(content)
            # csv.writerow([*content, *blanks])
            n += 1
    return n


def load_questions(file_path: str):
    questions = []
    with open(file_path) as file:
        gift = parser.parse(file.read())
        questions = gift.questions
    return questions


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

    return parser.parse_args()


def main():
    args = get_args()
    questions = load_questions(args.gift_path)
    print(f"Found {len(questions)} questions.")
    n_written = write_csv(args.output, questions, args.delimiter, args.time)
    print(f"Wrote {n_written} questions.")


if __name__ == "__main__":
    main()
