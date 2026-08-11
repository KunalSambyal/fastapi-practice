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
    )
]
