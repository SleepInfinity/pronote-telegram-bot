import hashlib
from pronotepy.dataClasses import Grade, Homework


def get_grade_unique_id(grade: Grade):
    grade_dict = grade.to_dict()
    subject_name = grade_dict["subject"]["name"]
    date = grade_dict["date"].isoformat()
    comment = grade_dict.get("comment", "")
    coefficient = grade_dict.get("coefficient", "")
    out_of = grade_dict.get("out_of", "")
    grade_value = grade_dict.get("grade", "")
    unique_string = (
        f"{subject_name}|{date}|{comment}|{coefficient}|{out_of}|{grade_value}"
    )
    unique_id = hashlib.sha256(unique_string.encode("utf-8")).hexdigest()
    return unique_id


def get_homework_unique_id(homework: Homework):
    homework_dict = homework.to_dict()
    subject_name = homework_dict["subject"]["name"]
    date = homework_dict["date"].isoformat()
    description = homework_dict["description"]
    unique_string = f"{subject_name}|{date}|{description}"
    unique_id = hashlib.sha256(unique_string.encode("utf-8")).hexdigest()
    return unique_id
