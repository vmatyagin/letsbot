import logging
from typing import Dict, List, Optional
from aiogram.types import User, Contact
import db
from enum import Enum

logger = logging.getLogger(__name__)


class PersonStatus(Enum):
    UNSET = "unset"
    ACTIVE = "active"
    MARRIED = "married"
    RELATIONSHIP = "relationship"


PersonStatusLangs: Dict[PersonStatus, str] = {
    PersonStatus.MARRIED: "Женат / замужем",
    PersonStatus.RELATIONSHIP: "В отношениях",
    PersonStatus.ACTIVE: "В активном поиске",
    PersonStatus.UNSET: "Не хочу рассказывать",
}


class Location(Dict):
    id: int
    name: str
    latitude: float
    longitude: float
    user_pk: int


class Person(Dict):
    id: int
    name: str
    username: str
    tg_id: Optional[int]
    location: Optional[Location]
    family_status: PersonStatus
    about: str
    is_admin: bool


def get_user_by_id(id: int | None = None, username: str | None = None) -> Person | None:
    raw_user = None
    cursor = db.get_cursor()

    if id:
        cursor.execute(f"SELECT * FROM person WHERE person.tg_id = {id}")
        data = cursor.fetchall()

        if len(data):
            raw_user = data[0]

    if not raw_user and username:
        cursor.execute(f'SELECT * FROM person WHERE person.username = "{username}"')
        data = cursor.fetchall()

        if len(data):
            raw_user = data[0]

    if not raw_user:
        return

    return {
        "id": raw_user[0],
        "name": raw_user[1],
        "username": raw_user[2],
        "tg_id": raw_user[3],
        "family_status": raw_user[4],
        "about": raw_user[5],
        "is_admin": bool(raw_user[6]),
        "is_activated": bool(raw_user[7]),
    }


def get_user_locations(id: int) -> List[Location]:
    cursor = db.get_cursor()
    cursor.execute(f"SELECT * FROM location WHERE location.user_pk = {id}")
    data = cursor.fetchall()

    locations = list()

    for raw_location in data:
        locations.append(
            {
                "id": raw_location[0],
                "name": raw_location[1],
                "latitude": raw_location[2],
                "longitude": raw_location[3],
            }
        )

    return locations


def get_location_by_id(id: int) -> Location | None:
    cursor = db.get_cursor()
    cursor.execute(f"SELECT * FROM location WHERE location.id = {id}")
    data = cursor.fetchall()

    if not len(data):
        return None

    raw_location = data[0]

    return {
        "id": raw_location[0],
        "name": raw_location[1],
        "latitude": raw_location[2],
        "longitude": raw_location[3],
    }


def delete_location_by_id(id: int) -> None:
    cursor = db.get_cursor()
    try:
        cursor.execute(f"DELETE FROM location WHERE location.id = {id}")
        db.connection.commit()

    except Exception as ex:
        logger.error(f"Ошибка при удалении локации в БД. {ex}")


def update_person(id: int, field: str, value: str) -> list | None:
    cursor = db.get_cursor()
    cursor.execute(f"UPDATE person " f'SET {field} = "{value}" ' f"WHERE id = {id}")

    db.connection.commit()


def insert_person(user: User, is_admin: bool = False):
    cursor = db.get_cursor()

    try:
        name = user.first_name
        if user.last_name:
            name += f" {user.last_name}"

        cursor.execute(
            f"INSERT INTO person(name, username, tg_id, is_admin) "
            f"VALUES "
            f"('{name}', '{user.username}', '{user.id}', '{int(is_admin)}')"
        )
        db.connection.commit()
    except Exception as ex:
        logger.error(f"Ошибка при записи в БД нового пользователя. {ex}")


def insert_person_by_contact(user: Contact):
    cursor = db.get_cursor()

    try:
        name = user.first_name
        if user.last_name:
            name += f" {user.last_name}"

        cursor.execute(
            f"INSERT INTO person(name, tg_id) "
            f"VALUES "
            f"('{name}', '{user.user_id}')"
        )
        db.connection.commit()
    except Exception as ex:
        logger.error(f"Ошибка при записи в БД нового пользователя. {ex}")


def delete_user_locations(user_pk: int):
    cursor = db.get_cursor()
    try:
        cursor.execute(f"DELETE FROM location WHERE location.user_pk = {user_pk}")

        db.connection.commit()

    except Exception as ex:
        logger.error(f"Ошибка при удалении локации в БД. {ex}")


def delete_person(user_pk: int):
    cursor = db.get_cursor()
    try:
        cursor.execute(f"DELETE FROM person WHERE person.pk = {user_pk}")

        db.connection.commit()

    except Exception as ex:
        logger.error(f"Ошибка при удалении person в БД. {ex}")


def insert_location(user_pk: int, name: str, latitude: float, longitude: float):
    cursor = db.get_cursor()

    try:
        cursor.execute(
            f"INSERT INTO location(name, latitude, longitude, user_pk) "
            f"VALUES "
            f"('{name}', '{latitude}', '{longitude}', '{user_pk}')"
        )
        db.connection.commit()

    except Exception as ex:
        logger.error(f"Ошибка при записи в БД локации. {ex}")


def get_full_users():

    cursor = db.get_cursor()

    # locations
    cursor.execute(f"SELECT * FROM location")
    raw_locations = cursor.fetchall()

    locations = dict()

    for raw in raw_locations:
        user_pk = raw[4]
        exists = user_pk in locations

        if exists:
            locations[user_pk].append(
                {
                    "id": raw[0],
                    "name": raw[1],
                    "latitude": raw[2],
                    "longitude": raw[3],
                }
            )
        else:
            locations[user_pk] = [
                {
                    "id": raw[0],
                    "name": raw[1],
                    "latitude": raw[2],
                    "longitude": raw[3],
                }
            ]

    cursor.execute(f"SELECT * FROM person")
    raw_users: list = cursor.fetchall()
    users = list()

    for raw in raw_users:
        users.append(
            {
                "id": raw[0],
                "name": raw[1],
                "username": raw[2],
                "tg_id": raw[3],
                "family_status": raw[4],
                "about": raw[5],
                "is_admin": bool(raw[6]),
                "location": locations.get(raw[0], []),
            }
        )

    return users
