import uuid
from dataclasses import dataclass, field
from typing import Dict

from common.dynamo import Dynamodb
from common.utils import Utils
from models.user_dynamo.errors import UserNotFoundError, IncorrectPasswordError, InvalidEmailError, \
    UserAlreadyRegisteredError


@dataclass
class User:
    table: str = field(init=False, default="Users")
    email: str
    password: str
    _id: str = field(default_factory=lambda: uuid.uuid4().hex)

    @classmethod
    def save_to_dynamo(cls, item):
        user_table = Dynamodb(cls.table)
        user_table.insert(item)

    @classmethod
    def find_by_email(cls, email: str) -> "User":
        try:
            user_table = Dynamodb(cls.table)
            users = user_table.find_by_hash_key("email",email)
            return cls(**users[0])
        except IndexError:
            raise UserNotFoundError('A user with this e-mail was not found.')

    @classmethod
    def is_login_valid(cls, email: str, password: str) -> bool:
        """
        This method verifies that an e-mail/password combo (as sent by the site forms) is valid or not.
        Checks that the e-mail exists, and that the password associated to that e-mail is correct.
        :param email: The user's email
        :param password: The password
        :return: True if valid, an exception otherwise
        """
        user = cls.find_by_email(email)

        if not Utils.check_hashed_password(password, user.password):
            # Tell the user that their password is wrong
            raise IncorrectPasswordError("Your password was wrong.")

        return True

    @classmethod
    def register_user(cls, email: str, password: str) -> bool:
        """
        This method registers a user using e-mail and password.
        :param email: user's e-mail (might be invalid)
        :param password: password
        :return: True if registered successfully, or False otherwise (exceptions can also be raised)
        """
        if not Utils.email_is_valid(email):
            raise InvalidEmailError("The e-mail does not have the right format.")

        try:
            cls.find_by_email(email)
            raise UserAlreadyRegisteredError("The e-mail you used to register already exists.")
        except UserNotFoundError:
            user = User(email, Utils.hash_password(password))
            User.save_to_dynamo(user.json())

        return True

    def json(self) -> Dict:
        return {
            "_id": self._id,
            "email": self.email,
            "password": self.password
        }
