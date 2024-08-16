"""Schemas module."""

from dataclasses import dataclass
import datetime

from src.constants import ADMIN_LOGIN


class BaseParamsMixin:
    """Base parameters for fields."""
    def __init__(self, required: bool | None = None, nullable: bool | None = None):
        self.required = required
        self.nullable = nullable


class BaseDescriptor(BaseParamsMixin):
    """Base descriptor."""

    def __init__(self, required: bool | None = None, nullable: bool | None = None):
        super().__init__(required, nullable)

    def check_field(self, value):
        pass

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        if not self.nullable and value is None:
            raise ValueError
        elif value is not None:
            self.check_field(value)

        setattr(instance, self.name, value)


class CharField(BaseDescriptor):

    def __init__(self, required: bool | None = None, nullable: bool | None = None):
        super().__init__(required, nullable)

    def check_field(self, value):
        if not isinstance(value, str):
            raise ValueError


class EmailField(CharField):

    def __init__(self, required: bool | None = None, nullable: bool | None = None):
        super().__init__(required, nullable)

    def check_field(self, value):
        if not isinstance(value, str) or value.find("@") == -1:
            raise ValueError


class ArgumentsField(BaseDescriptor):

    def __init__(self, required: bool | None = None, nullable: bool | None = None):
        super().__init__(required, nullable)

    def check_field(self, value):
        if not isinstance(value, dict):
            raise ValueError


class PhoneField(BaseDescriptor):

    def __init__(self, required: bool | None = None, nullable: bool | None = None):
        super().__init__(required, nullable)

    def check_field(self, value):
        def check(v: str):
            if len(v) != 11 or not v.startswith("7"):
                raise ValueError

        if isinstance(value, str):
            check(value)
        elif isinstance(value, int):
            check(str(value))
        else:
            raise ValueError


class DateField(BaseDescriptor):

    def __init__(self, required: bool | None = None, nullable: bool | None = None):
        super().__init__(required, nullable)

    def check_field(self, value):
        datetime.datetime.strptime(value, "%d.%m.%Y").date()


class BirthDayField(BaseDescriptor):

    def __init__(self, required: bool | None = None, nullable: bool | None = None):
        super().__init__(required, nullable)

    def check_field(self, value):
        date = datetime.datetime.strptime(value, "%d.%m.%Y").date()

        today = datetime.date.today()
        year_delta = 70
        try:
            lower_date_limit = datetime.date(today.year - year_delta, today.month, today.day)
        except ValueError:
            lower_date_limit = datetime.date(today.year - year_delta, 3, 1)

        if date < lower_date_limit:
            raise ValueError


class GenderField(BaseDescriptor):

    def __init__(self, required: bool | None = None, nullable: bool | None = None):
        super().__init__(required, nullable)

    def check_field(self, value):
        if value not in (0, 1, 2):
            raise ValueError


class ClientIDsField(BaseDescriptor):

    def __init__(self, required: bool | None = None, nullable: bool | None = None):
        super().__init__(required, nullable)

    def check_field(self, value):
        if not isinstance(value, list) or not value:
            raise ValueError

        for item in value:
            if not isinstance(item, int):
                raise ValueError


@dataclass
class ClientsInterestsRequest:
    client_ids: list[int] | None = ClientIDsField(required=True, nullable=False)
    date: datetime.date | str | None = DateField(required=False, nullable=True)


@dataclass
class OnlineScoreRequest:
    first_name: str | None = CharField(required=False, nullable=True)
    last_name: str | None = CharField(required=False, nullable=True)
    email: str | None = EmailField(required=False, nullable=True)
    phone: str | int | None = PhoneField(required=False, nullable=True)
    birthday: datetime.date | str | None = BirthDayField(required=False, nullable=True)
    gender: int | None = GenderField(required=False, nullable=True)


@dataclass
class MethodRequest:
    account: str = CharField(required=False, nullable=True)
    login: str = CharField(required=True, nullable=True)
    token: str = CharField(required=True, nullable=True)
    arguments: dict = ArgumentsField(required=True, nullable=True)
    method: str = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN
