from enum import StrEnum


class Gender(StrEnum):
    MALE = "Мужской"
    FEMALE = "Женский"
    PREFER_NOT_TO_SAY = "Не указывать"


# depricated 18.11.26
# class SkillLevel(StrEnum):
#     BEGINNER = "Новичок"
#     INTERMEDIATE = "Средний"
#     ADVANCED = "Продвинутый"
