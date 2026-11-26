import phonenumbers
from phonenumbers import NumberParseException

ALLOWED_REGION = {"RU", "KZ", "BY"}


class InvalidPhoneNumberError(ValueError):
    """Raised when a phone number is invalid."""

    def __init__(self, message: str = "Invalid phone number") -> None:
        super().__init__(message)


def normalize_phone_number(phone_number: str) -> str:
    """
    Проверяет номер телефона и приводит его к формату E.164.

    Номер должен быть валидным и относиться к одной из поддерживаемых стран.

    :param phone_number: Номер телефона для проверки и нормализации.
    :return: Номер телефона в формате E.164.
    :raises ValueError: Если номер некорректен или страна не поддерживается.
    """
    if not phone_number.startswith("+") or phone_number.count("+") != 1:
        raise InvalidPhoneNumberError()
    try:
        phone_parse = phonenumbers.parse(phone_number, None)
    except NumberParseException:
        raise InvalidPhoneNumberError()
    if (
        not phonenumbers.is_valid_number(phone_parse)
        or phonenumbers.region_code_for_number(phone_parse) not in ALLOWED_REGION
    ):
        raise InvalidPhoneNumberError()
    return phonenumbers.format_number(phone_parse, phonenumbers.PhoneNumberFormat.E164)
