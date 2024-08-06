import asyncio
import logging

from aiogram import Bot, types, Dispatcher, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.formatting import Text

from config import token

bot = Bot(token=token)
dp = Dispatcher()
r = open('spravka.txt', encoding='utf-8')
k = r.read()
router = Router(name='main')
dp.include_router(router)


class FSMadm(StatesGroup):
    field = State()
    GS = State()
    NNS = State()
    PS = State()
    defic = State()


volume = {'ВС': [1869.15, 1089.73], 'ВСТР': [1769.55, 1294.96],
          'ЗМБ': [1757.99, 1154.24], 'ЗУ': [1742.21, 1233.39],
          'КИН': [1932.51, 1230.80], 'КУЗ': [1425.51, 1075.96],
          'МБ': [1789.33, 1172.9], 'МАМ': [1913.36, 1186.61],
          'МОСК': [1495.97, 1540.59], 'ОМБ': [1677.84, 1296.46],
          'ПЕТ': [1666.21, 1191.21], 'ПРД': [1500.91, 1351.53],
          'ПРО': [1661.69, 1148.22], 'ЭРГ': [936.61, 1511.51],
          'ПРЗ': [1724.13, 1391.39], 'САЛ': [1163.92, 1304.73],
          'СОР': [1384.81, 1083.14], 'СБ': [1581.45, 1121.26],
          'СУ': [1632.07, 1110.78], 'КУДР': [1845.83, 1097.73],
          'УГ': [1584.56, 1178.26], 'УБ': [1813.36, 1020.92]}

'***************************КНОПКИ****************************'
b1 = KeyboardButton(text='/Расчет')
b2 = KeyboardButton(text='/Справка')
kb_privet = ReplyKeyboardMarkup(keyboard=[[b1], [b2]], resize_keyboard=True)

b3 = KeyboardButton(text='ВС')
b4 = KeyboardButton(text='ВСТР')
b5 = KeyboardButton(text='ЗМБ')
b6 = KeyboardButton(text='ЗУ')
b7 = KeyboardButton(text='КИН')
b8 = KeyboardButton(text='КУЗ')
b9 = KeyboardButton(text='МБ')
b10 = KeyboardButton(text='МАМ')
b11 = KeyboardButton(text='МОСК')
b12 = KeyboardButton(text='ОМБ')

b13 = KeyboardButton(text='ПЕТ')
b14 = KeyboardButton(text='ПРД')
b15 = KeyboardButton(text='ПРО')
b16 = KeyboardButton(text='ЭРГ')
b17 = KeyboardButton(text='ПРЗ')
b18 = KeyboardButton(text='САЛ')
b19 = KeyboardButton(text='СОР')
b20 = KeyboardButton(text='СБ')
b21 = KeyboardButton(text='СУ')
b22 = KeyboardButton(text='КУДР')
b23 = KeyboardButton(text='УГ')
b24 = KeyboardButton(text='УБ')
kb_list = [
    [b15, b24],
    [b3, b4, b5, b6, b7],
    [b8, b9, b10, b11, b12],
    [b13, b14, b16, b17, b18],
    [b19, b20, b21, b22, b23]
]
kb_choose = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True)

defic1 = KeyboardButton(text='Не рассчитывать дефицит')
kb_defic = ReplyKeyboardMarkup(keyboard=[[defic1]], resize_keyboard=True)

'***************************КОМАНДЫ****************************'


@router.message(Command('start'))
async def command_start(message: types.Message):
    await message.answer('Privet', reply_markup=kb_privet)


@router.message(Command('Справка'))
async def command_spravka(message: types.Message):
    await message.answer(k)


# Начало расчета
@router.message(Command('Расчет'))
async def new_calculation(message: types.Message, state: FSMContext):
    await state.set_state(FSMadm.field)
    await message.answer('Введите название месторождения', reply_markup=kb_choose)


# Выход из состояния
@router.message(Command('отмена'))
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer('OK', reply_markup=kb_privet)


# Ловим месторождение и пишем в словарь
@router.message(FSMadm.field)
async def load_field(message: types.Message, state: FSMContext):
    await state.update_data(field=message.text)
    await state.set_state(FSMadm.GS)
    await message.answer('Введите кол-во ГС', reply_markup=ReplyKeyboardRemove())


# Ловим кол-во ГС
@router.message(FSMadm.GS)
async def load_gs(message: types.Message, state: FSMContext):
    await state.update_data(GS=message.text)
    await state.set_state(FSMadm.NNS)
    await message.answer('Введите кол-во ННС')


# Ловим кол-во ННС
@router.message(FSMadm.NNS)
async def load_nns(message: types.Message, state: FSMContext):
    await state.update_data(NNS=message.text)
    await state.set_state(FSMadm.PS)
    await message.answer('Введите кол-во скважин с ПС')


# Ловим кол-во ПС
@router.message(FSMadm.PS)
async def load_ps(message: types.Message, state: FSMContext):
    await state.update_data(PS=message.text)
    await state.set_state(FSMadm.defic)
    await message.answer('Для расчета дефицита введите объем ПНОБ', reply_markup=kb_defic)


# Ловим объем ПНОБ и рассчитывем
@router.message(FSMadm.defic)
async def calculate(message: types.Message, state: FSMContext):
    await state.update_data(defic=message.text)
    data = await state.get_data()
    res = round(2108.63 * data['PS'] + float(volume[str(data['field'])][1]) * data['NNS'] + float(
        volume[str(data['field'])][0]) * (data['GS'] - data['PS']), 2)
    if str(message.text) == 'Не рассчитывать дефицит':
        await message.answer(str('Объем отходов бурения\n' + str(res) + ' куб. м.'), reply_markup=kb_privet)
    else:
        data['defic'] = int(message.text)
        if round(data['defic'] - res, 2) < 0:
            await message.answer(str('Дефицит ПНОБ равен\n' + str(round(data['defic'] - res, 2)) + ' куб. м.'),
                                 reply_markup=kb_privet)
        else:
            await message.answer(
                str('Дефицита нет\n\nЗапас объема:\n' + str(round(data['defic'] - res, 2)) + ' куб. м.'),
                reply_markup=kb_privet)
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
