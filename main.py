import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackContext

# Уровни диалога (состояний) для конечного автомата
SELECT_OIV_MO, SELECT_SYSTEM, DESCRIBE_PROBLEM, GET_CONTACT = range(4)

# Функция для начала диалога
def start(update: Update, _: CallbackContext) -> int:
    user = update.effective_user
    update.message.reply_text(
        f"Здравствуйте, {user.first_name}!\n"
        "С какого ОИВ (органа исполнительной власти) или МО (муниципального образования) вы?\n"
        "Введите название ОИВ или МО:"
    )

    return SELECT_OIV_MO

# Функция для получения ОИВ или МО
def select_oiv_mo(update: Update, _: CallbackContext) -> int:
    # Получаем введенное пользователем ОИВ или МО и сохраняем в user_data
    oiv_mo = update.message.text
    _.user_data['oiv_mo'] = oiv_mo

    # Просим пользователя выбрать систему вопроса из списка
    update.message.reply_text(
        "Отлично! Теперь выберите систему вопроса из списка ниже:",
        reply_markup=ReplyKeyboardMarkup([['Система 1', 'Система 2', 'Система 3', 'Система 4']], resize_keyboard=True, one_time_keyboard=True)
    )

    return SELECT_SYSTEM

# Функция для получения системы вопроса
def select_system(update: Update, _: CallbackContext) -> int:
    # Получаем выбранную систему и сохраняем ее в user_data
    selected_system = update.message.text
    _.user_data['selected_system'] = selected_system

    # Просим пользователя описать проблему
    update.message.reply_text("Отлично! Теперь опишите вашу проблему:", reply_markup=ReplyKeyboardRemove())

    return DESCRIBE_PROBLEM

# Функция для получения описания проблемы
def describe_problem(update: Update, _: CallbackContext) -> int:
    user_data = _.user_data
    text = update.message.text
    user_data['problem'] = text

    # Запрашиваем контактные данные
    update.message.reply_text("Введите ваши контактные данные (ФИО, номер телефона):")
    # не знаю что под контактными данными имелось, впихнула это

    return GET_CONTACT

# Функция для получения контактных данных и создания файла
def get_contact(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    text = update.message.text
    user_data['contact'] = text

    # Создаем файл с данными пользователя
    with open("tech_support_request.txt", "w") as file:
        file.write(f"ОИВ или МО: {user_data['oiv_mo']}\n"
                   f"Система вопроса: {user_data['selected_system']}\n"
                   f"Проблема: {user_data['problem']}\n"
                   f"Контактные данные: {user_data['contact']}")

    # Получаем chat_id технического специалиста, которому хотим отправить файл
    target_chat_id = 642212445  # Заменить на chat_id технического специалиста !!!
    # бот сможет отправлять соо только в том случае, если тех специалист ему отправлял хоть 1 соо

    # Отправляем файл техническому специалисту
    update.message.bot.send_document(chat_id=target_chat_id, document=open("tech_support_request.txt", "rb"))
    update.message.reply_text("Ваш запрос отправлен специалисту техподдержки. Ожидайте ответа.")

    return ConversationHandler.END

# Функция для отмены диалога
def cancel(update: Update, _: CallbackContext) -> int:
    update.message.reply_text("Диалог отменен.")
    return ConversationHandler.END

def main():
    # Включаем логирование для отслеживания ошибок
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # Токен бота, заменить на ваш для удобства
    updater = Updater('6602144802:AAHHKSze7Lt_cPphV0Oc-gs-KgD1SYwU8dA', use_context=True)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_OIV_MO: [MessageHandler(Filters.text & ~Filters.command, select_oiv_mo)],
            SELECT_SYSTEM: [MessageHandler(Filters.regex(r'^(Система 1|Система 2|Система 3|Система 4)$'), select_system)],
            DESCRIBE_PROBLEM: [MessageHandler(Filters.text & ~Filters.command, describe_problem)],
            GET_CONTACT: [MessageHandler(Filters.text & ~Filters.command, get_contact)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl + C в консоли
    updater.idle()

if __name__ == '__main__':
    main()
