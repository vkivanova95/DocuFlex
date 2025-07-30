from django.core.exceptions import ValidationError


def validate_eik_only_digits(value):
    if not value.isdigit():
        raise ValidationError("ЕИК трябва да съдържа само цифри.")


def validate_represented_together(data):
    represented_together = data.get("represented_together")
    representative1 = data.get("representative1")
    representative2 = data.get("representative2")

    if represented_together:
        if not representative2:
            raise ValidationError(
                {
                    "representative2": "Трябва да въведете двама представляващи при отметка 'съвместно представителство'."
                }
            )

        if (
            representative1
            and representative2
            and representative1.strip() == representative2.strip()
        ):
            raise ValidationError(
                {"representative2": "Трябва да въведете двама различни представляващи."}
            )

    else:
        if representative2:
            raise ValidationError(
                {
                    "representative2": "Ако не е избрано 'съвместно представителство', не трябва да има втори представляващ."
                }
            )
