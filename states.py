from aiogram.fsm.state import State, StatesGroup


class RegState(StatesGroup):
    name = State()
    sex = State()
    age = State()


class Chatting(StatesGroup):
    msg = State()


class NameState(StatesGroup):
    name = State()


class AgeState(StatesGroup):
    age = State()


class SexState(StatesGroup):
    sex = State()


class Search(StatesGroup):
    searching = State()


class Bug(StatesGroup):
    bug = State()


class Idea(StatesGroup):
    idea = State()

