from typing import List
from datetime import date
from app.schemas.student import Address, CredentialIn, StudentIn

# students db
students: List[StudentIn] = [
    StudentIn(
        std_id=1023,
        std_name="Kunal",
        std_age=18,
        std_dob=date(2003, 2, 21),
        std_address=Address(city="gsp", state="Punjab", country="India"),
        std_credentials=CredentialIn(
            username="kunal20031023", password="390rjefssc", email="kunal@gmail.com"
        ),
    ),
    StudentIn(
        std_id=1024,
        std_name="Aegon Targaryen",
        std_age=19,
        std_dob=date(2005, 5, 12),
        std_address=Address(
            city="King's Landing", state="Westeros", country="Crownlands"
        ),
        std_credentials=CredentialIn(
            username="aegon_targaryen",
            password="dragonfire123",
            email="aegon@westeros.org",
        ),
    ),
    StudentIn(
        std_id=1025,
        std_name="Jon Snow",
        std_age=18,
        std_dob=date(2007, 8, 3),
        std_address=Address(city="Winterfell", state="North", country="Westeros"),
        std_credentials=CredentialIn(
            username="jon_snow_99",
            password="ghostwolf2024",
            email="jon.snow@thewall.net",
        ),
    ),
]
