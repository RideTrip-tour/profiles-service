import phonenumbers
from phonenumbers import NumberParseException


def normalize_phone_number(phone_number: str) -> str:
    """
    Проверяет номер телефона и приводит его к формату E.164.

    Номер должен быть валидным и относиться к одной из поддерживаемых стран.

    :param phone_number: Номер телефона для проверки и нормализации.
    :return: Номер телефона в формате E.164.
    :raises ValueError: Если номер некорректен или страна не поддерживается.
    """
    try:
        phone_parse = phonenumbers.parse(phone_number, None)
    except NumberParseException:
        raise ValueError("Invalid phone number")
    if not phonenumbers.is_valid_number(phone_parse):
        raise ValueError("Invalid phone number")
    return phonenumbers.format_number(phone_parse, phonenumbers.PhoneNumberFormat.E164)
