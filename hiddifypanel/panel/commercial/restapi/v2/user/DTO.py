from apiflask import Schema
from apiflask.fields import Integer, String, Float, URL, Enum
from apiflask.validators import Length, OneOf
from strenum import StrEnum
from enum import auto
from hiddifypanel.models import Lang


class ProfileDTO(Schema):
    profile_title = String(required=True)
    profile_url = URL(required=True)
    profile_usage_current = Float(required=True)
    profile_usage_total = Float(required=True)
    profile_remaining_days = Integer(required=True)
    profile_reset_days = Integer()
    telegram_bot_url = String()
    telegram_id = Integer()
    admin_message_html = String()
    admin_message_url = URL()
    brand_title = String()
    brand_icon_url = URL()
    doh = URL()
    lang = Enum(Lang,required=True)

class ConfigDTO(Schema):
    name = String(required=True)
    domain = String(required=True)
    link = String(required=True)
    protocol = String(required=True)
    transport = String(required=True)
    security = String(required=True)
    type = String(required=True)

class MtproxyDTO(Schema):
    link = String(required=True)
    title = String(required=True)


class ShortDTO(Schema):
    short = String(required=True)
    full_url = String(required=True)

class UserInfoChangableDTO(Schema):
    language = Enum(Lang,required=False)
    telegram_id = Integer(required=False)