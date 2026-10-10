<<<<<<< Updated upstream
=======
<<<<<<< HEAD
from typing import List, Dict, Annotated, Optional
from datetime import datetime
from pydantic import EmailStr   
from schemas.config import basemodel, field, PASSWORD_REGEX
from pydantic_extra_types.phone_numbers import PhoneNumber
from backend.app.models.user import Role
    
class UserBase(basemodel):    
    username : Annotated[
        str, field(
            title = "User's displayed name on MTB",
            min_length = 2,
            max_length = 50,
            description = "**Task:** Receives and validates user's identification name for MTB.\n"
                "**Context:** SignupDetails/username\n"
                "**Profile:** Received by User"
                """**Rules:** Can start with a number or string. \n
                              Can only contain the special charecter: underscore(_). \n
                              Can contain lowercase or uppercase charecters. \n
                              Can contain any formatted combination of special charecters, string(upper or lower) and numbers. \n
                              Compulsary Field\n
                              Min defined length: 2\n
                              Max defined length: 50\n""",
            examples = [["Nichay_21", "pran212av", "suru_21_bhi_21"]],
            pattern = r'^[a-zA-Z0-9_]+$'
        )
    ]
    
    user_email: Annotated[
        EmailStr, field(
            title = "User's registered Email ID for MTB",
            min_length = 12,
            max_length = 50,
            description = """**Task:** Receives and validates the user's registered Email ID for MTB.
                            **Context:** SignupDetails/user_email
                            **Profile:** Received from User
                            **Rules:** Must be a valid email string format.
                                       Can contain lowercase or uppercase characters.
                                       Compulsory Field.
                                       Min defined length: 12.
                                       Max defined length: 50.""",
            examples = [["shashwat7709@gmail.com", "yashraj.yash@gmail.com"]],
            
        )
    ]
    
    phone_no: Annotated[
        PhoneNumber, field(
            title = "User's registered Phone no for MTB",
            min_length = 7,
            max_length = 20,
            description = """**Task:** Receives and validates the user's registered phone number for MTB.
                            **Context:** SignupDetails/phone_no
                            **Profile:** Received from User
                            **Rules:** Must be a valid international phone number format.
                                       Compulsory Field.
                                       Min defined length: 7.
                                       Max defined length: 20."""
        )
    ]
    
    role: Annotated[
        str, field(
            default = Role.CUSTOMER,
            title = "User authorization role for validating operations",
            min_length = 5,
            max_length = 8,
            description = """**Task:** Assigns and validates the user's system authorization role for access control.
                            **Context:** SignupDetails/role
                            **Profile:** System Default / Received from User
                            **Rules:** Defaults to 'CUSTOMER'.
                                       Must be an uppercase string matching authorized roles.
                                       Min defined length: 5.
                                       Max defined length: 8.""",
            examples = [["ADMIN", "CUSTOMER"]],
            
        )
    ]
    
class UserCreate(UserBase):
    password: Annotated[
        str, field(
            title = "User password for MTB",
            exclude = True,
            min_length = 8,
            max_length = 12,
            description = """**Task:** Receives, validates, and safely processes the user password for MTB authentication.
                            **Context:** UserCreate/password
                            **Profile:** Received from User (Securely handled)
                            **Rules:** Compulsory Field.
                                       Excluded from serialization output (hidden from API responses).
                                       Min defined length: 8.
                                       Max defined length: 12.""",
            pattern = PASSWORD_REGEX
        )
    ]

"""class UserUpdate(basemodel):
    username: Optional[str]
    user_email: Optional[str]
    phone_no: Optional[str]
    password: Optional[str]
"""

class UserOut(UserBase):
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        form_attributes = True
=======
>>>>>>> Stashed changes
class UserCreate():
    pass