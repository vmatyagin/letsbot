from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    wait_for_location = State()
    wait_for_name = State()
    wait_for_about = State()
    wait_for_status = State()
    wait_for_location_name = State()
