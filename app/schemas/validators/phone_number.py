import re

# Временно отключено, может потребоваться в будущем.
# import phonenumbers
# from phonenumbers import NumberParseException


class InvalidPhoneNumberError(ValueError):
    """Raised when a phone number is invalid."""

    def __init__(self) -> None:
        super().__init__("Invalid phone number")


# Временно отключено, может потребоваться в будущем.
# def normalize_phone_number(phone_number: str) -> str:
#     """
#     Проверяет номер телефона и приводит его к формату E.164.

#     Номер должен быть валидным и относиться к одной из поддерживаемых стран.

#     :param phone_number: Номер телефона для проверки и нормализации.
#     :return: Номер телефона в формате E.164.
#     :raises ValueError: Если номер некорректен или страна не поддерживается.
#     """
#     try:
#         phone_parse = phonenumbers.parse(phone_number, None)
#     except NumberParseException:
#         raise InvalidPhoneNumberError()
#     if not phonenumbers.is_valid_number(phone_parse):
#         raise InvalidPhoneNumberError()
#     return phonenumbers.format_number(phone_parse, phonenumbers.PhoneNumberFormat.E164)


def validate_phone_number(phone_number: str) -> str:
    """Validates a phone number in E.164 format."""
    if not re.fullmatch(r"\+[1-9]\d{6,14}", phone_number, flags=re.ASCII):
        raise InvalidPhoneNumberError()
    return phone_number
