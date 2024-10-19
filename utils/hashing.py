import hashlib
from pronotepy.dataClasses import Grade, Homework


def get_grade_unique_id(grade: Grade) -> str:
    subject_name = grade.subject.name
    date = grade.date.isoformat()
    comment = grade.comment
    coefficient = grade.coefficient
    out_of = grade.out_of
    grade_value = grade.grade
    unique_string: str = (
        f"{subject_name}|{date}|{comment}|{coefficient}|{out_of}|{grade_value}"
    )
    unique_id: str = hashlib.sha256(unique_string.encode("utf-8")).hexdigest()
    return unique_id


def get_homework_unique_id(homework: Homework) -> str:
    subject_name = homework.subject.name
    date = homework.date.isoformat()
    description = homework.description
    unique_string: str = f"{subject_name}|{date}|{description}"
    unique_id: str = hashlib.sha256(unique_string.encode("utf-8")).hexdigest()
    return unique_id
