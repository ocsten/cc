import re
from dataclasses import dataclass, field
from typing import Optional, Tuple

@dataclass
class CardData:
    number: str
    month: str
    year: str
    cvv: str
    bin: str = field(init=False)
    valid_luhn: bool = field(init=False)
    
    def __post_init__(self):
        self.bin = self.number[:6] if len(self.number) >= 6 else ""
        self.valid_luhn = self._check_luhn()
    
    def _check_luhn(self) -> bool:
        digits = [int(d) for d in self.number if d.isdigit()]
        if len(digits) < 13:
            return False
        checksum = 0
        reverse_digits = digits[::-1]
        for i, digit in enumerate(reverse_digits):
            if i % 2 == 1:
                doubled = digit * 2
                checksum += doubled - 9 if doubled > 9 else doubled
            else:
                checksum += digit
        return checksum % 10 == 0

def parse_card(card_str: str) -> Optional[CardData]:
    numbers = re.findall(r'\d+', card_str)
    if len(numbers) < 4:
        return None
    ccn, mm, yy, cvv = numbers[0], numbers[1], numbers[2], numbers[3]
    if len(ccn) < 13 or len(ccn) > 19:
        return None
    if not mm.isdigit() or int(mm) < 1 or int(mm) > 12:
        return None
    if not yy.isdigit() or len(yy) not in [2, 4]:
        return None
    if not cvv.isdigit() or len(cvv) not in [3, 4]:
        return None
    return CardData(number=ccn, month=mm, year=yy, cvv=cvv)

def validate_card(card: CardData) -> Tuple[bool, str]:
    if len(card.number) < 13 or len(card.number) > 19:
        return False, "Invalid card number length"
    if int(card.month) < 1 or int(card.month) > 12:
        return False, "Invalid month"
    if len(card.year) not in [2, 4]:
        return False, "Invalid year"
    if len(card.cvv) not in [3, 4]:
        return False, "Invalid CVV"
    if not card.valid_luhn:
        return False, "Luhn checksum failed"
    return True, "Valid card"
