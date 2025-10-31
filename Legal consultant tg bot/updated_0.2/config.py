import os
import logging
from enum import Enum # Для использования перечислений для состояний
from dotenv import load_dotenv # Добавляем импорт для загрузки переменных окружения

# Загружаем переменные окружения из файла .env в начале выполнения скрипта
load_dotenv()

# --- Конфигурация приложения ---
class Config:
    """
    Класс для хранения всех конфигурационных параметров приложения.
    Параметры считываются из переменных окружения (файла .env).
    """
    # Токены и ключи API
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Лимиты использования функций бота
    DAILY_QUESTION_LIMIT = 10
    DAILY_DOCUMENT_LIMIT = 10
    
    # Настройки OpenAI
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', "gpt-4o-mini") # Предпочтительная модель AI, читаем из env
    
    # Настройки базы данных
    DB_NAME = os.getenv('DB_NAME', "multilang_bot.db") # Имя БД, читаем из env
    
    # Карта для уровней логирования из строк в объекты logging
    LOG_LEVEL_MAP = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }

class BotState(Enum):
    """
    Перечисление (Enum) для управления состояниями ConversationHandler.
    Использование Enum делает код более читабельным, безопасным и менее подверженным ошибкам,
    чем использование магических чисел (например, SELECTING_LANG = 0).
    """
    SELECTING_LANG = 1          # Выбор языка
    SELECTING_ACTION = 2        # Выбор основного действия в меню
    ASKING_QUESTION = 3         # Задавание вопроса AI
    ANALYZING_DOC = 4           # Анализ документа AI
    EDITING_DOC = 5             # Редактирование документа AI
    AWAITING_CONTACT = 6        # Ожидание контакта пользователя

    # --- Состояния для создания адвокатского запроса ---
    AWAIT_LEGAL_FORM = 7
    AWAIT_BUREAU_NAME = 8
    AWAIT_LEGAL_ADDRESS = 9
    AWAIT_MAILING_ADDRESS = 10
    AWAIT_ADVOCATE_NAME = 11
    AWAIT_ADVOCATE_PHONE = 12
    AWAIT_ADVOCATE_EMAIL = 13
    AWAIT_CERTIFICATE_DETAILS = 14
    AWAIT_CERTIFICATE_ISSUER = 15
    AWAIT_ORDER_DETAILS = 16
    AWAIT_CLIENT_TYPE = 17
    AWAIT_CLIENT_PHYSICAL_NAME = 18
    AWAIT_CLIENT_PHYSICAL_ADDRESS = 19
    AWAIT_CLIENT_LEGAL_NAME = 20
    AWAIT_CLIENT_LEGAL_EDRPOU = 21
    AWAIT_CLIENT_LEGAL_ADDRESS = 22
    AWAIT_CONTRACT_DETAILS = 23
    AWAIT_LEGAL_AID_SUBJECT = 24
    AWAIT_RECIPIENT_DETAILS = 25
    AWAIT_OUTGOING_NUMBER = 26
    AWAIT_REQUEST_BODY = 27

    # --- Состояния для создания договора ---
    CREATE_CONTRACT_START = 28 # Начальная точка для диалога создания договора
    AWAIT_CONTRACT_NUMBER_DATE = 29
    CONFIRM_CLIENT_DATA = 30
    AWAIT_CLIENT_NAME = 31 # Используется для имени клиента, ФИО и других текстовых полей
    AWAIT_CLIENT_POSITION = 32
    AWAIT_CLIENT_BASIS = 33
    CONFIRM_ADVOCATE_DATA = 34
    AWAIT_ADVOCATE_FIO = 35
    AWAIT_ADVOCATE_CERTIFICATE_SERIES = 36
    AWAIT_ADVOCATE_CERTIFICATE_NUMBER = 37
    AWAIT_ADVOCATE_CERTIFICATE_ISSUER = 38
    AWAIT_ADVOCATE_CERTIFICATE_ISSUER_DATE_NUMBER = 39 # Комбинированное поле для даты и номера решения
    SELECT_PAYMENT_TYPE = 40
    AWAIT_FIXED_AMOUNT = 41
    AWAIT_FIXED_PAYMENT_ORDER = 42
    AWAIT_HOURLY_RATE = 43
    AWAIT_HOURLY_ACCOUNTING = 44
    AWAIT_HOURLY_PAYMENT_PERIOD = 45
    AWAIT_PERCENTAGE_VALUE = 46
    AWAIT_PERCENTAGE_BASE = 47
    AWAIT_PERCENTAGE_CONDITION = 48
    AWAIT_COMBINED_DESCRIPTION = 49
    AWAIT_CONTRACT_END_DATE = 50
    AWAIT_ADVOCATE_LOCATION = 51
    AWAIT_CLIENT_EDRPOU = 52
    AWAIT_CLIENT_LOCATION = 53

class Translations:
    """
    Класс для управления всеми текстовыми строками бота на разных языках.
    Обеспечивает легкий доступ к переводам и механизм fallback.
    """
    LANGUAGES = {'uk': "Українська", 'en': "English", 'de': "Deutsch"}
    TEXTS = {
        'uk': {
            # --- ОБЩИЕ ТЕКСТЫ ---
            "welcome_choose_lang": "👋 Вітаю! Будь ласка, оберіть мову:",
            "welcome": "🏛️ <b>Вітаю! Я — консультант Бандуль, ваш персональний AI Юрист.</b>\n\nГотовий допомогти вам розібратися в правових нюансах, проаналізувати документи та сформулювати професійні запити.\n\n<b>Мої можливості:</b>\n• Відповіді на юридичні питання\n• Аналіз та редагування документів\n• Формування адвокатських запитів\n• Генерація договору\n\n⚠️ <b>Важливо:</b> Мої відповіді мають інформаційний характер. Для прийняття важливих рішень звертайтесь до кваліфікованих юристів.\n\nОберіть дію:",
            "main_menu": "🏛️ <b>AI Юрист</b>\n\nОберіть дію:",
            "prompt_use_buttons": "Будь ласка, використовуйте кнопки нижче, щоб обрати дію.",
            "back_btn": "◀️ Назад", "cancel_btn": "❌ Скасувати", "info_btn": "ℹ️ Інформація", "confirm_btn": "✅ Підтвердити", "edit_btn": "✏️ Редагувати",
            "limit_reached": "⛔ Ви досягли денного ліміту на цю операцію. Спробуйте знову завтра.",
            "processing_query": "⏳ Аналізую ваш запит...", "processing_doc": "⏳ Оброблюю документ...",
            "error_generic": "❌ Сталася помилка. Спробуйте пізніше.", "error_invalid_input": "❌ Некоректне введення. Будь ласка, спробуйте ще раз.",
            "ai_response_footer": "⚠️ <b>Важливо:</b> Це інформаційна консультація. Для прийняття юридичних рішень обов'язково проконсультуйтесь з кваліфікованим юристом.",
            "info_text": "ℹ️ <b>Інформація про бота</b>\n\n<b>Ваші ліміти на сьогодні:</b>\n• Питання: {q_count}/{q_limit}\n• Документи: {d_count}/{d_limit}\n\n⚠️ <b>Відмова від відповідальності:</b> Відповіді мають інформаційний характер і не є юридичною консультацією.",
            "share_contact_btn": "📱 Поділитися номером", "contact_received": "✅ Дякую! Ваш номер телефону збережено.",
            "contact_request": "Будь ласка, натисніть кнопку нижче, щоб поділитися вашим контактом для кращого зв'язку.",
            "back_to_menu_message": "Добре, повертаємось до головного меню...",
            "ask_question_btn": "❓ Поставити питання", "analyze_doc_btn": "📄 Аналізувати документ", "edit_doc_btn": "✏️ Редагувати документ",
            "ask_question_prompt": "❓ <b>Поставте ваше юридичне питання</b>\n\nЗалишилось питань сьогодні: <b>{remaining}</b>\n\nОпишіть вашу ситуацію детально. Просто напишіть ваше питання у наступному повідомленні:",
            "analyze_doc_prompt": "📄 <b>Аналіз документа</b>\n\nЗалишилось обробок сьогодні: <b>{remaining}</b>\n\nНадішліть документ для аналізу (.txt, .docx, .pdf).",
            "edit_doc_prompt": "✏️ <b>Редагування документа</b>\n\nЗалишилось обробок сьогодні: <b>{remaining}</b>\n\nНадішліть документ та вкажіть у підписі до файлу, що саме потрібно змінити.",
            "doc_result_header": "📄 <b>Результат обробки документа:</b>",
            "error_file_format": "❌ Непідтримуваний формат. Використовуйте .txt, .docx, .pdf.",
            "error_file_size": "❌ Файл завеликий (макс. 20 МБ).",
            "error_file_extract": "❌ Не вдалося вилучити текст з документа. Перевірте, чи файл не пошкоджений та містить текст.",
            
            # --- АДВОКАТСКИЙ ЗАПРОС ---
            "create_request_btn": "📝 Сформулювати адвокатський запит",
            "request_start": "✍️ Розпочинаємо. Крок 1: <b>Оберіть форму адвокатської діяльності:</b>",
            "legal_form_self": "Самозайнята особа", "legal_form_fop": "ФОП", "legal_form_bureau": "Адвокатське бюро", "legal_form_union": "Адвокатське об'єднання",
            "prompt_bureau_name": "Введіть повну <b>назву адвокатського бюро / об'єднання</b>:",
            "prompt_legal_address": "Крок 2: Введіть <b>юридичну адресу</b> (місцезнаходження):",
            "prompt_mailing_address": "Крок 3: Введіть <b>адресу для листування</b>:", "same_as_legal_btn": "Така сама, як юридична",
            "prompt_advocate_name": "Крок 4: Введіть <b>ПІБ адвоката</b>:",
            "prompt_advocate_phone": "Крок 5: Введіть <b>контактний телефон</b>:", "prompt_advocate_email": "Крок 6: Введіть <b>електронну пошту</b>:",
            "prompt_certificate_details": "Крок 7: Введіть <b>серію та номер свідоцтва</b>:", "prompt_certificate_issuer": "Крок 8: Введіть, <b>ким і коли видане свідоцтво</b>:",
            "prompt_order_details": "Крок 9: Введіть <b>серію, номер та дату ордера</b>:",
            "prompt_client_type": "Крок 10: <b>Оберіть тип клієнта</b>:", "client_type_physical": "Фізична особа", "client_type_legal": "Юридична особа",
            "prompt_client_physical_name": "Клієнт (Фіз. особа): Введіть <b>ПІБ</b>:", "prompt_client_physical_address": "Клієнт (Фіз. особа): Введіть <b>адресу реєстрації</b>:",
            "prompt_client_legal_name": "Клієнт (Юр. особа): Введіть <b>повну назву</b>:", "prompt_client_legal_edrpou": "Клієнт (Юр. особа): Введіть <b>код ЄДРПОУ</b>:", "prompt_client_legal_address": "Клієнт (Юр. особа): Введіть <b>юридичну адресу</b>:",
            "prompt_contract_details": "Крок 11: Введіть <b>номер та дату договору</b> про правову допомогу:", "prompt_legal_aid_subject": "Крок 12: Коротко опишіть <b>предмет правової допомоги</b>:",
            "prompt_recipient_details": "Крок 13: Введіть дані <b>отримувача</b> (Посада, ПІБ, Назва організації, адреса).",
            "prompt_outgoing_number": "Крок 14: Введіть <b>вихідний номер запиту</b> (або /skip, щоб пропустити):", "prompt_request_body": "Фінальний крок: Введіть <b>текст вашого запиту</b> (пункти 'ПРОШУ НАДАТИ...'):",
            "request_generating": "⏳ Дякую! Генерую фінальний документ... Це може зайняти до хвилини.",
            "request_generation_complete": "✅ <b>Адвокатський запит згенеровано!</b> Надсилаю його у файлі `.docx`.", "request_cancelled": "Дію скасовано. Повертаюся в головне меню.",

            # --- ЗАГОЛОВКИ ДЛЯ AI ПРОМПТА АДВОКАТСКОГО ЗАПИТУ (важно, чтобы AI их понимал!) ---
            "prompt_header_recipient": "Отримувач",
            "prompt_header_sender": "Відправник",
            "prompt_header_form": "Форма адвокатської діяльності",
            "prompt_header_bureau": "Назва бюро / об'єднання",
            "prompt_header_advocate_name": "ПІБ адвоката",
            "prompt_header_phone": "Телефон",
            "prompt_header_email": "Email",
            "prompt_header_address": "Адреса",
            "prompt_header_certificate": "Свідоцтво",
            "prompt_header_order": "Ордер",
            "prompt_header_client": "Клієнт",
            "prompt_header_client_type_phys": "Фізична особа",
            "prompt_header_client_type_legal": "Юридична особа",
            "prompt_header_basis": "Підстава",
            "prompt_header_contract": "Договір про правову допомогу",
            "prompt_header_subject": "Предмет правової допомоги",
            "prompt_header_request_details": "Деталі запиту",
            "prompt_header_number": "Вихідний номер",
            "prompt_header_date": "Дата",
            "prompt_header_body": "Текст запиту",
            "prompt_header_liability": "Відповідальність", # Заголовок для пункта об ответственности


            # --- AI ПРОМПТЫ ---
            "ai_system_prompt_general": "Ти — професійний юридичний AI-асистент. Надавай детальні, добре структуровані відповіді на юридичні питання. Завжди відповідай наступною мовою: {lang_name}.",
            "ai_system_prompt_document": "Ти — професійний юридичний AI-асистент, що спеціалізується на аналізі та редагуванні документів. Чітко дотримуйся інструкцій користувача. Завжди відповідай наступною мовою: {lang_name}.",
            "ai_system_prompt_advocate_request_uk": """Ти — висококваліфікований український юрист-асистент. Твоє завдання — згенерувати повний, юридично грамотний текст адвокатського запиту на основі наданих даних. Дотримуйся офіційно-ділового стилю. Структуруй документ: шапка (адресат, відправник), назва, преамбула (з посиланням на ст. 20, 24 ЗУ «Про адвокатуру та адвокатську діяльність» та договір), прохальна частина.
ОБОВ'ЯЗКОВО після прохальної частини додай блок про відповідальність за ненадання відповіді, який тобі надано.
В кінці додай перелік додатків, вкажи поточну дату та залиш місце для підпису адвоката.""",
            "advocate_request_liability_clause_uk": "Окремо звертаю Вашу увагу, що відповідно до ч. 2 ст. 24 Закону України «Про адвокатуру та адвокатську діяльність», орган державної влади, орган місцевого самоврядування, їх посадові та службові особи, керівники підприємств, установ, організацій, громадських об’єднань, яким направлено адвокатський запит, зобов’язані не пізніше п’яти робочих днів з дня отримання запиту надати адвокату відповідну інформацію, копії документів. У разі якщо адвокатський запит стосується надання значного обсягу інформації або потребує пошуку інформації серед значної кількості даних, строк розгляду адвокатського запиту може бути продовжено до двадцяти робочих днів з обґрунтуванням причин такого продовження.\n\nЗа неправомірну відмову в наданні інформації на адвокатський запит, несвоєчасне або неповне надання інформації, надання інформації, що не відповідає дійсності, встановлена адміністративна відповідальність за статтею 212-3 Кодексу України про адміністративні правопорушення.",

            # --- НОВЫЕ ТЕКСТЫ ДЛЯ ДОГОВОРА ---
            "create_contract_btn": "📝 Сформувати договір",
            "contract_header": "ДОГОВІР ПРО НАДАННЯ ПРАВОВОЇ ДОПОМОГИ", # Без звёздочек, так как Docx не использует их напрямую
            "contract_start_intro": "Будь ласка, введіть основні дані договору:",

            "prompt_contract_number_date": "*1. НОМЕР І ДАТА:*\n\nВведіть номер договору та дату його укладення у форматі: `Номер ДД.ММ.РРРР`\nНаприклад: `123 01.01.2024`",
            "contract_date_header_template": "м. Київ                                                «{day}» {month} {year} року",
            "contract_generating": "⏳ Генерую документ договору...",
            "contract_generation_complete": "✅ <b>Договір згенеровано!</b> Надсилаю його у файлі `.docx`.",

            "contract_client_details_header": "2. СТОРОНИ ДОГОВОРУ: НАСТРОЙКА СТОРОНИ: КЛІЄНТ",
            "confirm_client_data_prompt": "_Будь ласка, підтвердіть або змініть дані КЛІЄНТА:_\nНазва: <b>{name}</b>\nПосада керівника: <b>{position}</b>\nПІБ керівника: <b>{fio}</b>\nПідстава дії: <b>{basis}</b>",
            "edit_client_name_btn": "Змінити назву Клієнта",
            "edit_client_position_btn": "Змінити посаду керівника",
            "edit_client_fio_btn": "Змінити ПІБ керівника",
            "edit_client_basis_btn": "Змінити підставу дії",
            "prompt_client_name": "Введіть повну назву КЛІЄНТА:",
            "prompt_client_position": "Введіть посаду керівника КЛІЄНТА:",
            "prompt_client_fio": "Введіть ПІБ керівника КЛІЄНТА:",
            "prompt_client_basis": "Введіть підставу дії керівника КЛІЄНТА:",

            "contract_advocate_details_header": "НАСТРОЙКА СТОРОНИ: АДВОКАТ",
            "confirm_advocate_data_prompt": "_Будь ласка, підтвердіть або змініть дані АДВОКАТА:_\nПІБ: <b>{fio}</b>\nСерія Свідоцтва: <b>{cert_series}</b>\nНомер Свідоцтва: <b>{cert_number}</b>\nКим видано: <b>{cert_issuer}</b>\nДата рішення: <b>{decision_date}</b>\nНомер рішення: <b>{decision_number}</b>",
            "edit_advocate_fio_btn": "Змінити ПІБ Адвоката",
            "edit_advocate_cert_series_btn": "Змінити серію свідоцтва",
            "edit_advocate_cert_number_btn": "Змінити номер свідоцтва",
            "edit_advocate_cert_issuer_btn": "Змінити ким видано",
            "edit_advocate_decision_date_btn": "Змінити дату та номер рішення", # Changed for clarity that it's a combined field
            "prompt_advocate_fio": "Введіть ПІБ АДВОКАТА:",
            "prompt_advocate_cert_series": "Введіть серію Свідоцтва про право на заняття адвокатською діяльністю (наприклад, `ВН`):",
            "prompt_advocate_cert_number": "Введіть номер Свідоцтва (наприклад, `000237`):",
            "prompt_advocate_cert_issuer": "Введіть орган видачі Свідоцтва (наприклад, `Ради адвокатів Вінницької області`):",
            "prompt_advocate_decision_date_number": "Введіть дату та номер рішення про видачу Свідоцтва (наприклад, `21.03.2018 №3`):",

            "contract_section_1_header": "1. ПРЕДМЕТ ДОГОВОРУ",
            "contract_section_2_header": "2. ОБОВ’ЯЗКИ ТА ПРАВА СТОРІН",
            "contract_section_2_options": "Оберіть, що хочете переглянути або змінити:",
            "advocate_duties_btn": "Обов'язки Адвоката (2.1)",
            "client_duties_btn": "Обов'язки Клієнта (2.2)",
            "advocate_rights_btn": "Права Адвоката (2.3)",
            "client_rights_btn": "Права Клієнта (2.4)",
            # Тексты разделов 2.1 - 2.4 перенесены сюда из DocxGenerator для упрощения изменений
            "section_2_content_2_1": "<b>2.1. ОБОВ’ЯЗКИ АДВОКАТА</b>\n\n<b>2.1. АДВОКАТ, на підставі звернення КЛІЄНТА, приймає на себе зобов’язання з надання наступної правової допомоги:</b>\n- перевіряє на відповідність вимогам українського законодавства внутрішніх документів КЛІЄНТА, надає допомогу КЛІЄНТУ при підготовці та правильному оформленні вказаних документів;\n- приймає участь в підготовці та юридичному оформленні різного роду договорів, що укладаються КЛІЄНТОМ з юридичними особами, підприємцями та громадянами, надає допомогу в організації контролю за виконанням зазначених договорів, слідкує за застосуванням передбачених законом та договором санкцій по відношенню до контрагентів, які не виконують договірні зобов’язання;\n- представляє у встановленому порядку інтереси КЛІЄНТА в господарських судах, судах загальної юрисдикції, адміністративних судах, а також в інших органах під час розгляду правових спорів;\n- узагальнює та аналізує: практику розгляду судових та інших справ; спільно з іншими підрозділами КЛІЄНТА результати розгляду претензій; практику укладення та виконання договорів; надає КЛІЄНТУ пропозиції щодо усунення виявлених недоліків;\n- надає консультації, висновки, довідки з правових питань, що виникають у КЛІЄНТА в процесі здійснення діяльності;\n- зберігає адвокатську таємницю, предметом якої є питання, пов’язані з наданням правової допомоги, згідно з умовами цього Договору, а також документація (договори, бухгалтерська і податкова звітність, інші документи).",
            "section_2_content_2_2": "<b>2.2. ОБОВ’ЯЗКИ КЛІЄНТА</b>\n\n<b>2.2. КЛІЄНТ зобов’язаний:</b>\n- повідомити АДВОКАТА про всі вжиті заходи, що стосуються справи;\n- інформувати АДВОКАТА про всі відомі обставини, які можуть мати суттєве значення для прийняття та виконання АДВОКАТА доручення відповідно до цього Договору;\n- вчасно забезпечувати АДВОКАТА всім необхідним для виконання його доручень, передбачених цим Договором, в тому числі документами в необхідній кількості екземплярів, внутрішніми нормативними актами, які регулюють діяльність КЛІЄНТА, у випадку необхідності робочим місцем, транспортними засобами;\n- при вирішенні спорів КЛІЄНТА з іншими підприємствами, установами, організаціями та фізичними особами, органами державної влади та місцевого самоврядування, їх посадовими та службовими особами, оперативно надавати повну та достовірну інформацію, що необхідна для врегулювання відповідного спору;\n- не вимагати виконання дій, що виходять за межі професійних прав і обов’язків АДВОКАТА;\n- на вимогу АДВОКАТА надавати документи, що стосуються виконання доручення;\n- інформувати АДВОКАТА про зміну місцезнаходження, адреси електронної пошти, номерів телефонів та факсу;\n- відшкодовувати АДВОКАТУ фактичні витрати, необхідні для виконання Договору;\n- своєчасно та в повному обсязі оплачувати вартість отриманих послуг за Договором.",
            "section_2_content_2_3": "<b>2.3. ПРАВА АДВОКАТА</b>\n\n<b>2.3. АДВОКАТ має право:</b>\n- звертатися з адвокатськими запитами, у тому числі щодо отримання копій документів, до органів державної влади, органів місцевого самоврядування, їх посадових і службових осіб, підприємств, установ, організацій, громадських об’єднань, а також до фізичних осіб;\n- представляти і захищати права, свободи та інтереси Клієнта у суді, органах державної влади та органах місцевого самоврядування, на підприємствах, в установах, організаціях незалежно від форми власності, громадських об’єднаннях, перед громадянами, посадовими і службовими особами, до повноважень яких належить вирішення відповідних питань;\n- знайомитися з матеріалами справи, робити з них витяги, знімати копії з документів, долучених до справи, одержувати копії рішень, ухвал, брати участь у судових засіданнях, подавати докази, брати участь у дослідженні доказів, задавати питання іншим особам, які беруть участь у справі, а також свідкам, експертам, спеціалістам, заявляти клопотання та відводи, давати усні та письмові пояснення судові, подавати свої доводи, міркування щодо питань, які виникають під час судового розгляду, і заперечення проти клопотань, доводів і міркувань інших осіб, знайомитися з журналом судового засідання, знімати з нього копії та подавати письмові зауваження з приводу його неправильності чи неповноти, прослуховувати запис фіксування судового засідання технічними засобами, робити з нього копії, подавати письмові зауваження з приводу його неправильності чи неповноти, оскаржувати рішення і ухвали суду, користуватися іншими процесуальними правами, встановленими законом;\n- ознайомлюватися на підприємствах, в установах і організаціях з необхідними для виконання Договору документами та матеріалами, крім тих, що містять інформацію з обмеженим доступом;\n- складати заяви, скарги, клопотання, інші правові документи, та подавати їх у встановленому законом порядку;\n- застосовувати технічні засоби, у тому числі для копіювання матеріалів справи, в якій АДВОКАТ здійснює захист, представництво або надає інші види правової допомоги, фіксувати процесуальні дії, в яких він бере участь, а також хід судового засідання в порядку, передбаченому законом;\n- посвідчувати копії документів у справах, які веде АДВОКАТ, крім випадків, якщо законом установлено інший обов’язковий спосіб посвідчення копій документів;\n- одержувати письмові висновки фахівців, експертів з питань, що потребують спеціальних знань;\n- користуватися іншими правами, передбаченими Законом України „Про адвокатуру та адвокатську діяльність” та іншими законами;\n- направляти КЛІЄНТУ повідомлення засобами: смс–розсилок; поштового зв’язку; електронної пошти; телефонного та/або факсимільного зв’язку.\n\n<b>АДВОКАТ може достроково розірвати угоду з КЛІЄНТОМ і відмовитися від надання послуг без складання будь-яких додаткових угод за наявності однієї з наступних підстав:</b>\n- якщо КЛІЄНТ грубо порушує обов’язки, взяті ним на себе згідно з даним Договором, а саме, відмовляється від сплати гонорару частково або в повному обсязі;\n- КЛІЄНТ, незважаючи на роз’яснення АДВОКАТА, наполягає на досягненні результату, який АДВОКАТОМ не може бути виконаний з об’єктивних причин;\n- належне виконання доручення стає неможливим через дії КЛІЄНТА, що вчиняються ним всупереч порадам АДВОКАТА;\n- КЛІЄНТ не погоджується погашати фактичні видатки або оплачувати роботу АДВОКАТА у разі суттєвого збільшення обсягу його роботи;\n- фізичний або психологічний стан АДВОКАТА позбавляє його можливості належним чином продовжувати виконання Договору;\n- наявні будь-які факти або обставини, які роблять представництво АДВОКАТОМ інтересів КЛІЄНТА незаконним або неетичним, та в інших випадках, передбачених законодавством.",
            "section_2_content_2_4": "<b>2.4. ПРАВА КЛІЄНТА</b>\n\n<b>2.4. КЛІЄНТ має право:</b>\n- на будь-якій стадії виконання Договору отримувати від АДВОКАТА інформацію про хід виконання доручення;\n- давати АДВОКАТУ усні або письмові вказівки щодо виконання доручення відповідно до цього Договору;\n- отримувати від АДВОКАТА усні відомості про хід виконання доручення у порядку та на умовах, встановлених цим Договором;\n- отримувати від АДВОКАТА юридичні консультації з питань наявності фактичних і правових підстав щодо виконання доручення, практики застосування відповідного законодавства, можливості та правових наслідків досягнення бажаного для Клієнта результату;\n- розірвати договір з АДВОКАТОМ в односторонньому порядку, письмово повідомивши про це АДВОКАТА за 10 днів, рекомендованим листом з повідомленням про вручення або вручається АДВОКАТУ особисто.",
            
            "contract_section_3_header": "3. ОПЛАТА ТА ПОРЯДОК ЗДІЙСНЕННЯ РОЗРАХУНКІВ",
            "prompt_payment_type": "Будь ласка, виберіть, який тип оплати ви хочете вказати в договорі:",
            "payment_type_free_btn": "Безкоштовно (безоплатна основа)",
            "payment_type_fixed_btn": "Фіксований гонорар",
            "payment_type_hourly_btn": "Погодинна оплата",
            "payment_type_percentage_btn": "Відсоток від виграшу/результату",
            "payment_type_combined_btn": "Комбінована система",

            "payment_type_free_text": "<b>3. ОПЛАТА ТА ПОРЯДОК ЗДІЙСНЕННЯ РОЗРАХУНКІВ</b>\n<b>3.1. Надання АДВОКАТОМ правової допомоги КЛІЄНТУ здійснюється на безоплатній основі.</b>",

            "prompt_fixed_amount": "Будь ласка, введіть суму фіксованого гонорару в гривнях. Наприклад: `15000`",
            "prompt_fixed_payment_order": "Відмінно! Як ви хочете вказати порядок оплати? (наприклад, '100% передоплата', '50% передоплата, 50% по завершенні', 'щомісячно')",
            "payment_type_fixed_text": "<b>3. ОПЛАТА ТА ПОРЯДОК ЗДІЙСНЕННЯ РОЗРАХУНКІВ</b>\n<b>3.1. За надання правової допомоги КЛІЄНТ сплачує АДВОКАТУ фіксований гонорар у розмірі {amount} грн ({amount_words} гривень).</b>\n<b>3.2. Порядок оплати: {payment_order}</b>\n<b>3.3. КЛІЄНТ відшкодовує АДВОКАТУ фактичні витрати, необхідні для виконання Договору (наприклад, поштові витрати, оплата держмита, вартість проїзду тощо) за наявності підтверджуючих документів.</b>",

            "prompt_hourly_rate": "Будь ласка, введіть вартість однієї години роботи Адвоката в гривнях. Наприклад: `800`",
            "prompt_hourly_accounting": "Як буде оформлятися облік часу? (наприклад, 'акти виконаних робіт щомісячно', 'табель обліку часу')",
            "prompt_hourly_payment_period": "З якою періодичністю буде здійснюватися оплата та протягом скількох банківських днів? (наприклад, 'щомісячно протягом 5 банківських днів з дати підписання акту наданих послуг')",
            "payment_type_hourly_text": "<b>3. ОПЛАТА ТА ПОРЯДОК ЗДІЙСНЕННЯ РОЗРАХУНКІВ</b>\n<b>3.1. За надання правової допомоги КЛІЄНТ сплачує АДВОКАТУ гонорар виходячи з погодинної ставки у розмірі {rate} грн/год ({rate_words} гривень за годину).</b>\n<b>3.2. Облік наданих послуг та відпрацьованого часу здійснюється за {accounting} та оформлюється Сторонами шляхом підписання актів наданих послуг.</b>\n<b>3.3. Оплата здійснюється {payment_period}</b>\n<b>3.4. КЛІЄНТ відшкодовує АДВОКАТУ фактичні витрати, необхідні для виконання Договору (наприклад, поштові витрати, оплата держмита, вартість проїзду тощо) за наявності підтверджуючих документів.</b>",

            "prompt_percentage_value": "Будь ласка, введіть відсоток від суми виграшу/отриманого результату. Наприклад: `10`",
            "prompt_percentage_base": "Яка буде база для розрахунку цього відсотка? (наприклад, 'від фактично стягнутої суми', 'від зекономленої суми')",
            "prompt_percentage_condition": "Яка умова оплати? (наприклад, 'після фактичного отримання коштів', 'після набрання рішенням законної сили')",
            "payment_type_percentage_text": "<b>3. ОПЛАТА ТА ПОРЯДОК ЗДІЙСНЕННЯ РОЗРАХУНКІВ</b>\n<b>3.1. За надання правової допомоги КЛІЄНТ сплачує АДВОКАТУ гонорар у розмірі {percentage}% від {base} після {condition}</b>\n<b>3.2. КЛІЄНТ відшкодовує АДВОКАТУ фактичні витрати, необхідні для виконання Договору (наприклад, поштові витрати, оплата держмита, вартість проїзду тощо) за наявності підтверджуючих документів.</b>",

            "prompt_combined_description": "Будь ласка, докладно опишіть комбіновану систему оплати (наприклад, 'Фіксований гонорар 5000 грн + 5% від суми виграшу', або 'Погодинна оплата 600 грн/год + премія за успішне завершення справи').",
            "payment_type_combined_text": "<b>3. ОПЛАТА ТА ПОРЯДОК ЗДІЙСНЕННЯ РОЗРАХУНКІВ</b>\n<b>3.1. За надання правової допомоги КЛІЄНТ сплачує АДВОКАТУ гонорар у відповідності до наступної комбінованої системи: {description}</b>\n<b>3.2. КЛІЄНТ відшкодовує АДВОКАТУ фактичні витрати, необхідні для виконання Договору (наприклад, поштові витрати, оплата держмита, вартість проїзду тощо) за наявності підтверджуючих документів.</b>",

            "contract_section_4_header": "4. КОНФІДЕНЦІЙНІСТЬ ТА АДВОКАТСЬКА ТАЄМНИЦЯ",
            "contract_section_5_header": "5. ФОРС-МАЖОР",
            "contract_section_6_header": "6. СТРОК ДІЇ ДОГОВОРУ",
            "prompt_contract_end_date": "Будь ласка, введіть кінцеву дату дії договору. (наприклад, `31.12.2024`)",
            "contract_section_7_header": "7. ЗМІНА УМОВ ДАНОГО ДОГОВОРУ",
            "contract_section_8_header": "8. ІНШІ УМОВИ",
            "contract_section_9_header": "9. РЕКВІЗИТИ ТА ПІДПИСИ СТОРІН",
            "prompt_advocate_location": "Введіть місцезнаходження АДВОКАТА:",
            "prompt_client_edrpou": "Введіть ЄДРПОУ КЛІЄНТА:",
            "prompt_client_location": "Введіть місцезнаходження КЛІЄНТА:",

        },
        'en': {
            # --- General texts ---
            "welcome_choose_lang": "👋 Hello! Please choose your language:",
            "welcome": "🏛️ <b>Welcome! I am Bandul Consultant, your personal AI Lawyer.</b>\n\nReady to help you understand legal nuances, analyze documents, draft professional requests, and generate contracts.\n\n<b>My capabilities:</b>\n• Answers to legal questions\n• Document analysis and editing\n• Drafting formal requests\n• Contract generation\n\n⚠️ <b>Important:</b> My answers are for informational purposes only. For critical decisions, please consult a qualified lawyer.\n\nChoose an action:",
            "main_menu": "🏛️ <b>AI Lawyer</b>\n\nChoose an action:",
            "prompt_use_buttons": "Please use the buttons below to select an action.",
            "back_btn": "◀️ Back", "cancel_btn": "❌ Cancel", "info_btn": "ℹ️ Info", "confirm_btn": "✅ Confirm", "edit_btn": "✏️ Edit",
            "limit_reached": "⛔ You have reached the daily limit for this operation. Please try again tomorrow.",
            "processing_query": "⏳ Analyzing your request...", "processing_doc": "⏳ Processing document...",
            "error_generic": "❌ An error occurred. Please try again later.", "error_invalid_input": "❌ Invalid input. Please try again.",
            "ai_response_footer": "⚠️ <b>Important:</b> This is an informational consultation. For legal decisions, always consult a qualified lawyer.",
            "info_text": "ℹ️ <b>Bot Information</b>\n\n<b>Your daily limits:</b>\n• Questions: {q_count}/{q_limit}\n• Documents: {d_count}/{d_limit}\n\n⚠️ <b>Disclaimer:</b> Answers are for informational purposes only and do not constitute legal advice.",
            "share_contact_btn": "📱 Share Contact", "contact_received": "✅ Thank you! Your phone number has been saved.",
            "contact_request": "Please press the button below to share your contact for better communication.",
            "back_to_menu_message": "Okay, returning to the main menu...",
            "ask_question_btn": "❓ Ask a Question", "analyze_doc_btn": "📄 Analyze Document", "edit_doc_btn": "✏️ Edit Document",
            "ask_question_prompt": "❓ <b>Ask your legal question</b>\n\nQuestions remaining today: <b>{remaining}</b>\n\nDescribe your situation in detail. Just type your question in the next message:",
            "analyze_doc_prompt": "📄 <b>Document Analysis</b>\n\nProcessed remaining today: <b>{remaining}</b>\n\nSend a document for analysis (.txt, .docx, .pdf).",
            "edit_doc_prompt": "✏️ <b>Document Editing</b>\n\nProcessed remaining today: <b>{remaining}</b>\n\nSend the document and specify in the file caption what needs to be changed.",
            "doc_result_header": "📄 <b>Document Processing Result:</b>",
            "error_file_format": "❌ Unsupported format. Please use .txt, .docx, .pdf.",
            "error_file_size": "❌ File is too large (max. 20 MB).",
            "error_file_extract": "❌ Failed to extract text from document. Please check if the file is not corrupted and contains text.",
            
            # --- Advocate Request ---
            "create_request_btn": "📝 Draft Formal Request",
            "request_start": "✍️ Let's start. Step 1: <b>Choose the form of legal activity:</b>",
            "legal_form_self": "Self-employed", "legal_form_fop": "Sole Proprietor", "legal_form_bureau": "Law Firm (Bureau)", "legal_form_union": "Law Firm (Association)",
            "prompt_bureau_name": "Enter the full <b>name of the law firm / association</b>:",
            "prompt_legal_address": "Step 2: Enter the <b>legal address</b> (location):",
            "prompt_mailing_address": "Step 3: Enter the <b>mailing address</b>:", "same_as_legal_btn": "Same as legal",
            "prompt_advocate_name": "Step 4: Enter <b>Advocate's Full Name</b>:",
            "prompt_advocate_phone": "Step 5: Enter <b>contact phone number</b>:", "prompt_advocate_email": "Step 6: Enter <b>email address</b>:",
            "prompt_certificate_details": "Step 7: Enter <b>certificate series and number</b>:", "prompt_certificate_issuer": "Step 8: Enter <b>who and when the certificate was issued by</b>:",
            "prompt_order_details": "Step 9: Enter <b>order series, number, and date</b>:",
            "prompt_client_type": "Step 10: <b>Select client type</b>:", "client_type_physical": "Individual", "client_type_legal": "Legal Entity",
            "prompt_client_physical_name": "Client (Individual): Enter <b>Full Name</b>:", "prompt_client_physical_address": "Client (Individual): Enter <b>registration address</b>:",
            "prompt_client_legal_name": "Client (Legal Entity): Enter <b>full name</b>:", "prompt_client_legal_edrpou": "Client (Legal Entity): Enter <b>EDRPOU code</b>:", "prompt_client_legal_address": "Client (Legal Entity): Enter <b>legal address</b>:",
            "prompt_contract_details": "Step 11: Enter <b>number and date of legal aid agreement</b>:", "prompt_legal_aid_subject": "Step 12: Briefly describe the <b>subject of legal aid</b>:",
            "prompt_recipient_details": "Step 13: Enter <b>recipient details</b> (Position, Full Name, Organization Name, address).",
            "prompt_outgoing_number": "Step 14: Enter <b>outgoing request number</b> (or /skip to skip):", "prompt_request_body": "Final step: Enter the <b>text of your request</b> (points 'I REQUEST TO PROVIDE...'):",
            "request_generating": "⏳ Thank you! Generating the final document... This may take up to a minute.",
            "request_generation_complete": "✅ <b>Advocate Request generated!</b> Sending it as a `.docx` file.", "request_cancelled": "Action canceled. Returning to main menu.",

            # --- HEADERS FOR AI PROMPT ADVOCATE REQUEST (important for AI understanding) ---
            "prompt_header_recipient": "Recipient",
            "prompt_header_sender": "Sender",
            "prompt_header_form": "Form of legal activity",
            "prompt_header_bureau": "Law Firm Name",
            "prompt_header_advocate_name": "Advocate's Full Name",
            "prompt_header_phone": "Phone",
            "prompt_header_email": "Email",
            "prompt_header_address": "Address",
            "prompt_header_certificate": "Certificate",
            "prompt_header_order": "Order",
            "prompt_header_client": "Client",
            "prompt_header_client_type_phys": "Individual",
            "prompt_header_client_type_legal": "Legal Entity",
            "prompt_header_basis": "Basis",
            "prompt_header_contract": "Legal Aid Agreement",
            "prompt_header_subject": "Subject of Legal Aid",
            "prompt_header_request_details": "Request Details",
            "prompt_header_number": "Outgoing Number",
            "prompt_header_date": "Date",
            "prompt_header_body": "Request Body",
            "prompt_header_liability": "Liability",

            "ai_system_prompt_general": "You are a professional legal AI assistant. Provide detailed, well-structured answers to legal questions. Always respond in the following language: {lang_name}.",
            "ai_system_prompt_document": "You are a professional legal AI assistant specializing in document analysis and editing. Follow the user's instructions precisely. Always respond in the following language: {lang_name}.",
            "ai_system_prompt_advocate_request_en": """You are a highly qualified Ukrainian legal assistant. Your task is to generate a complete, legally sound text of an advocate's request based on the provided data. Adhere to a formal business style. Structure the document: header (addressee, sender), title, preamble (referencing Articles 20, 24 of the Law of Ukraine "On Advocacy and Advocacy Activities" and the agreement), and the request part.
MANDATORY after the request part, add the block on responsibility for not providing a response, which is provided to you.
At the end, add a list of appendices, indicate the current date, and leave space for the advocate's signature.""",
            "advocate_request_liability_clause_en": """Separately, I draw your attention to the fact that, in accordance with Part 2 of Article 24 of the Law of Ukraine "On Advocacy and Advocacy Activities," a state authority, local self-government body, their officials, heads of enterprises, institutions, organizations, public associations, to whom an advocate's request is sent, are obliged to provide the advocate with the relevant information, copies of documents no later than five working days from the date of receipt of the request. If the advocate's request relates to the provision of a significant amount of information or requires searching for information among a significant amount of data, the period for reviewing the advocate's request may be extended to twenty working days with a justification of the reasons for such extension.\n\nAdministrative liability for unlawful refusal to provide information in response to an advocate's request, untimely or incomplete provision of information, provision of information that does not correspond to reality, is established by Article 212-3 of the Code of Ukraine on Administrative Offenses.""",
            
            # --- Contract texts (simplified for EN as example, for full support would need translation for each) ---
            "create_contract_btn": "📝 Generate Contract",
            "confirm_btn": "✅ Confirm", "edit_btn": "✏️ Edit",
            "error_invalid_input": "❌ Invalid input. Please try again.",

            "contract_header": "AGREEMENT FOR LEGAL ASSISTANCE",
            "contract_start_intro": "Please enter the main contract details:",
            "prompt_contract_number_date": "*1. NUMBER AND DATE:*\n\nEnter the contract number and date of signing in format: `Number DD.MM.YYYY`\nExample: `123 01.01.2024`",
            "contract_date_header_template": "Kyiv                                                «{day}» {month} {year}",
            "contract_generating": "⏳ Generating contract document...",
            "contract_generation_complete": "✅ <b>Contract generated!</b> Sending it as a `.docx` file.",

            "contract_client_details_header": "2. CONTRACTING PARTIES: CLIENT SETTINGS:",
            "confirm_client_data_prompt": "_Please confirm or modify CLIENT data:_\nName: <b>{name}</b>\nHead's position: <b>{position}</b>\nHead's Full Name: <b>{fio}</b>\nBasis of action: <b>{basis}</b>",
            "edit_client_name_btn": "Change Client Name",
            "edit_client_position_btn": "Change Head's Position",
            "edit_client_fio_btn": "Change Head's Full Name",
            "edit_client_basis_btn": "Change Basis of Action",
            "prompt_client_name": "Enter full CLIENT name:",
            "prompt_client_position": "Enter CLIENT Head's position:",
            "prompt_client_fio": "Enter CLIENT Head's Full Name:",
            "prompt_client_basis": "Enter basis of action for CLIENT Head:",

            "contract_advocate_details_header": "ADVOCATE SETTINGS:",
            "confirm_advocate_data_prompt": "_Please confirm or modify ADVOCATE data:_\nFull Name: <b>{fio}</b>\nCertificate Series: <b>{cert_series}</b>\nCertificate Number: <b>{cert_number}</b>\nIssued by: <b>{cert_issuer}</b>\nDecision Date: <b>{decision_date}</b>\nDecision Number: <b>{decision_number}</b>",
            "edit_advocate_fio_btn": "Change Advocate FIO",
            "edit_advocate_cert_series_btn": "Change Certificate Series",
            "edit_advocate_cert_number_btn": "Change Certificate Number",
            "edit_advocate_cert_issuer_btn": "Change Issuer",
            "edit_advocate_decision_date_btn": "Change Decision Date/Number", 
            "prompt_advocate_fio": "Enter ADVOCATE Full Name:",
            "prompt_advocate_cert_series": "Enter Certificate Series (e.g., `VN`):",
            "prompt_advocate_cert_number": "Enter Certificate Number (e.g., `000237`):",
            "prompt_advocate_cert_issuer": "Enter Certificate Issuer (e.g., `Vinnytsia Region Bar Council`):",
            "prompt_advocate_decision_date_number": "Enter Decision Date and Number (e.g., `21.03.2018 №3`):",

            "contract_section_1_header": "1. SUBJECT OF THE AGREEMENT",
            "contract_section_2_header": "2. OBLIGATIONS AND RIGHTS OF THE PARTIES",
            "contract_section_2_options": "Select what you want to view or change:",
            "advocate_duties_btn": "Advocate's Duties (2.1)",
            "client_duties_btn": "Client's Duties (2.2)",
            "advocate_rights_btn": "Advocate's Rights (2.3)",
            "client_rights_btn": "Client's Rights (2.4)",
            "section_2_content_2_1": "<b>2.1. ADVOCATE'S DUTIES</b>\n\n<b>2.1. The ADVOCATE, based on the CLIENT's request, undertakes to provide the following legal assistance:</b>\n- checks the CLIENT's internal documents for compliance with Ukrainian legislation, assists the CLIENT in preparing and properly formulating the specified documents;\n- participates in the preparation and legal formulating of various types of agreements concluded by the CLIENT with legal entities, entrepreneurs, and citizens, assists in organizing control over the execution of these agreements, monitors the application of sanctions provided by law and the agreement against counterparties who fail to fulfill contractual obligations;\n- represents in the prescribed manner the interests of the CLIENT in commercial courts, general jurisdiction courts, administrative courts, and other bodies during the consideration of legal disputes;\n- generalizes and analyzes: the practice of considering court and other cases; jointly with other CLIENT departments, the results of claims consideration; the practice of concluding and executing agreements; provides the CLIENT with proposals for eliminating identified shortcomings;\n- provides consultations, opinions, certificates on legal issues that arise for the CLIENT in the course of business;\n- keeps attorney-client privilege, which is the subject of issues related to the provision of legal assistance, in accordance with the terms of this Agreement, as well as documentation (agreements, accounting and tax reports, other documents).",
            "section_2_content_2_2": "<b>2.2. CLIENT'S DUTIES</b>\n\n<b>2.2. The CLIENT undertakes to:</b>\n- inform the ADVOCATE of all measures taken related to the case;\n- inform the ADVOCATE of all known circumstances that may be significant for the ADVOCATE's acceptance and fulfillment of the assignment under this Agreement;\n- timely provide the ADVOCATE with everything necessary to fulfill his assignments under this Agreement, including documents in the required number of copies, internal regulations governing the CLIENT's activities, and if necessary, a workplace, vehicles;\n- when resolving disputes between the CLIENT and other enterprises, institutions, organizations and individuals, state authorities and local self-government bodies, their officials, promptly provide full and reliable information necessary for resolving the respective dispute;\n- not demand actions that go beyond the professional rights and duties of the ADVOCATE;\n- at the request of the ADVOCATE, provide documents related to the fulfillment of the assignment;\n- inform the ADVOCATE about changes in location, email address, phone and fax numbers;\n- reimburse the ADVOCATE for actual expenses necessary for the performance of the Agreement (e.g., postal expenses, state duty, travel costs, etc.);\n- timely and fully pay for the received services under the Agreement.",
            "section_2_content_2_3": "<b>2.3. ADVOCATE'S RIGHTS</b>\n\n<b>2.3. The ADVOCATE has the right to:</b>\n- submit advocate's requests, including for obtaining copies of documents, to state authorities, local self-government bodies, their officials, enterprises, institutions, organizations, public associations, and individuals;\n- represent and protect the rights, freedoms, and interests of the Client in court, state authorities and local self-government bodies, enterprises, institutions, organizations of all forms of ownership, public associations, before citizens, officials who are authorized to resolve relevant issues;\n- familiarize himself with case materials, make excerpts from them, take copies of documents attached to the case, receive copies of decisions, rulings, participate in court sessions, submit evidence, participate in the examination of evidence, ask questions to other persons participating in the case, as well as witnesses, experts, specialists, make petitions and challenges, give oral and written explanations to the court, present arguments, opinions on issues arising during the trial, and objections to petitions, arguments, and opinions of other persons, familiarize himself with the minutes of the court session, take copies of them and submit written comments on their incorrectness or incompleteness, listen to the recording of the court session by technical means, make copies of them, submit written comments on their incorrectness or incompleteness, appeal court decisions and rulings, exercise other procedural rights established by law;\n- familiarize himself with the necessary documents and materials at enterprises, institutions, and organizations for the performance of the Agreement, except for those containing restricted access information;\n- prepare statements, complaints, petitions, other legal documents, and submit them in the manner prescribed by law;\n- use technical means, including for copying case materials in which the ADVOCATE carries out protection, representation, or provides other types of legal assistance, record procedural actions in which he participates, as well as the course of the court session in the manner prescribed by law;\n- certify copies of documents in cases handled by the ADVOCATE, except when the law establishes another mandatory method of certifying copies of documents;\n- receive written opinions from specialists, experts on issues requiring special knowledge;\n- exercise other rights provided for by the Law of Ukraine \"On Advocacy and Advocacy Activities\" and other laws;\n- send messages to the CLIENT by: SMS mailings; postal mail; email; telephone and/or fax.\n\n<b>The ADVOCATE may prematurely terminate the agreement with the CLIENT and refuse to provide services without drawing up any additional agreements if one of the following grounds exists:</b>\n- if the CLIENT grossly violates the obligations assumed by him under this Agreement, namely, refuses to pay the fee partially or in full;\n- the CLIENT, despite the ADVOCATE's explanations, insists on achieving a result that cannot be performed by the ADVOCATE due to objective reasons;\n- proper execution of the assignment becomes impossible due to the CLIENT's actions taken contrary to the ADVOCATE's advice;\n- the CLIENT does not agree to reimburse actual expenses or pay for the ADVOCATE's work in case of a significant increase in the scope of his work;\n- the ADVOCATE's physical or psychological condition prevents him from properly continuing the performance of the Agreement;\n- there are any facts or circumstances that make the ADVOCATE's representation of the CLIENT's interests illegal or unethical, and in other cases provided by law.",
            "section_2_content_2_4": "<b>2.4. CLIENT'S RIGHTS</b>\n\n<b>2.4. The CLIENT has the right to:</b>\n- at any stage of the Agreement's performance, receive information from the ADVOCATE about the progress of the assignment;\n- give the ADVOCATE oral or written instructions regarding the performance of the assignment in accordance with this Agreement;\n- receive oral information from the ADVOCATE about the progress of the assignment in the manner and on the terms established by this Agreement;\n- receive legal consultations from the ADVOCATE on the factual and legal grounds for performing the assignment, the practice of applying relevant legislation, the possibility and legal consequences of achieving the desired result for the Client;\n- unilaterally terminate the agreement with the ADVOCATE by notifying the ADVOCATE in writing 10 days in advance, by registered mail with delivery notification or handed to the ADVOCATE personally.",
            
            "contract_section_3_header": "3. PAYMENT AND CALCULATION",
            "prompt_payment_type": "Please select the payment type for the contract:",
            "payment_type_free_btn": "Free of charge",
            "payment_type_fixed_btn": "Fixed fee",
            "payment_type_hourly_btn": "Hourly rate",
            "payment_type_percentage_btn": "Percentage of win/result",
            "payment_type_combined_btn": "Combined system",

            "payment_type_free_text": "<b>3. PAYMENT AND CALCULATION</b>\n<b>3.1. Legal assistance is provided free of charge.</b>",

            "prompt_fixed_amount": "Please enter the fixed fee amount in UAH. Example: `15000`",
            "prompt_fixed_payment_order": "Great! How do you want to specify the payment order? (e.g., '100% prepayment', '50% prepayment, 50% upon completion', 'monthly')",
            "payment_type_fixed_text": "<b>3. PAYMENT AND CALCULATION</b>\n<b>3.1. For legal assistance, the CLIENT pays the ADVOCATE a fixed fee of {amount} UAH ({amount_words} hryvnias).</b>\n<b>3.2. Payment order: {payment_order}</b>\n<b>3.3. The CLIENT reimburses the ADVOCATE for actual expenses necessary for the performance of the Agreement (e.g., postal expenses, state duty, travel costs, etc.) upon presentation of supporting documents.</b>",

            "prompt_hourly_rate": "Please enter the hourly rate of the Advocate in UAH. Example: `800`",
            "prompt_hourly_accounting": "How will time tracking be documented? (e.g., 'monthly acts of completed work', 'time sheet')",
            "prompt_hourly_payment_period": "What will be the payment frequency and within how many banking days? (e.g., 'monthly within 5 banking days from the date of signing the act of rendered services')",
            "payment_type_hourly_text": "<b>3. PAYMENT AND CALCULATION</b>\n<b>3.1. For legal assistance, the CLIENT pays the ADVOCATE a fee based on an hourly rate of {rate} UAH/hour ({rate_words} hryvnias per hour).</b>\n<b>3.2. The accounting of rendered services and worked hours is carried out according to {accounting} and is formalized by the Parties by signing acts of rendered services.</b>\n<b>3.3. Payment is made {payment_period}</b>\n<b>3.4. The CLIENT reimburses the ADVOCATE for actual expenses necessary for the performance of the Agreement (e.g., postal expenses, state duty, state fees, travel costs, etc.) upon presentation of supporting documents.</b>",

            "prompt_percentage_value": "Please enter the percentage of the winning amount/result. Example: `10`",
            "prompt_percentage_base": "What will be the basis for calculating this percentage? (e.g., 'from the actually recovered amount', 'from the saved amount')",
            "prompt_percentage_condition": "What is the payment condition? (e.g., 'after actual receipt of funds', 'after the decision becomes legally binding')",
            "payment_type_percentage_text": "<b>3. PAYMENT AND CALCULATION</b>\n<b>3.1. For legal assistance, the CLIENT pays the ADVOCATE a fee of {percentage}% of {base} after {condition}</b>\n<b>3.2. The CLIENT reimburses the ADVOCATE for actual expenses necessary for the performance of the Agreement (e.g., postal expenses, state duty, travel costs, etc.) upon presentation of supporting documents.</b>",

            "prompt_combined_description": "Please describe the combined payment system in detail (e.g., 'Fixed fee of 5000 UAH + 5% of the winning amount', or 'Hourly rate of 600 UAH/hour + bonus for successful case completion').",
            "payment_type_combined_text": "<b>3. PAYMENT AND CALCULATION</b>\n<b>3.1. For legal assistance, the CLIENT pays the ADVOCATE a fee in accordance with the following combined system: {description}</b>\n<b>3.2. The CLIENT reimburses the ADVOCATE for actual expenses necessary for the performance of the Agreement (e.g., postal expenses, state duty, travel costs, etc.) upon presentation of supporting documents.</b>",

            "contract_section_4_header": "4. CONFIDENTIALITY AND ATTORNEY-CLIENT PRIVILEGE",
            "contract_section_5_header": "5. FORCE MAJEURE",
            "contract_section_6_header": "6. TERM OF THE AGREEMENT",
            "prompt_contract_end_date": "Please enter the end date of the agreement. (e.g., `31.12.2024`)",
            "contract_section_7_header": "7. AMENDMENT OF THIS AGREEMENT",
            "contract_section_8_header": "8. OTHER TERMS",
            "contract_section_9_header": "9. REQUISITES AND SIGNATURES OF THE PARTIES",
            "prompt_advocate_location": "Enter ADVOCATE's location:",
            "prompt_client_edrpou": "Enter CLIENT's EDRPOU code:",
            "prompt_client_location": "Enter CLIENT's location:",
        },
        'de': {
            # --- General texts ---
            "welcome_choose_lang": "👋 Hallo! Bitte wählen Sie Ihre Sprache:",
            "welcome": "🏛️ <b>Willkommen! Ich bin Bandul Berater, Ihr persönlicher KI-Anwalt.</b>\n\nBereit, Ihnen zu helfen, rechtliche Nuancen zu verstehen, Dokumente zu analysieren, professionelle Anfragen zu formulieren und Verträge zu erstellen.\n\n<b>Meine Fähigkeiten:</b>\n• Antworten auf rechtliche Fragen\n• Dokumentenanalyse und -bearbeitung\n• Erstellung von formellen Anfragen\n• Vertragserstellung\n\n⚠️ <b>Wichtig:</b> Meine Antworten dienen nur zu Informationszwecken. Für wichtige Entscheidungen wenden Sie sich bitte an einen qualifizierten Anwalt.\n\nWählen Sie eine Aktion:",
            "main_menu": "🏛️ <b>KI-Anwalt</b>\n\nWählen Sie eine Aktion:",
            "prompt_use_buttons": "Bitte verwenden Sie die Schaltflächen unten, um eine Aktion auszuwählen.",
            "back_btn": "◀️ Zurück", "cancel_btn": "❌ Abbrechen", "info_btn": "ℹ️ Information", "confirm_btn": "✅ Bestätigen", "edit_btn": "✏️ Bearbeiten",
            "limit_reached": "⛔ Sie haben das Tageslimit für diesen Vorgang erreicht. Bitte versuchen Sie es morgen erneut.",
            "processing_query": "⏳ Analysiere Ihre Anfrage...", "processing_doc": "⏳ Verarbeite Dokument...",
            "error_generic": "❌ Es ist ein Fehler aufgetreten. Bitte versuchen Sie es später erneut.", "error_invalid_input": "❌ Ungültige Eingabe. Bitte versuchen Sie es erneut.",
            "ai_response_footer": "⚠️ <b>Wichtig:</b> Dies ist eine Informationskonsultation. Für rechtliche Entscheidungen konsultieren Sie unbedingt einen qualifizierten Anwalt.",
            "info_text": "ℹ️ <b>Informationen zum Bot</b>\n\n<b>Ihre Tageslimits:</b>\n• Fragen: {q_count}/{q_limit}\n• Dokumente: {d_count}/{d_limit}\n\n⚠️ <b>Haftungsausschluss:</b> Die Antworten dienen nur zu Informationszwecken und stellen keine Rechtsberatung dar.",
            "share_contact_btn": "📱 Kontakt teilen", "contact_received": "✅ Danke! Ihre Telefonnummer wurde gespeichert.",
            "contact_request": "Bitte drücken Sie die Schaltfläche unten, um Ihren Kontakt für eine bessere Kommunikation zu teilen.",
            "back_to_menu_message": "Okay, zurück zum Hauptmenü...",
            "ask_question_btn": "❓ Frage stellen", "analyze_doc_btn": "📄 Dokument analysieren", "edit_doc_btn": "✏️ Dokument bearbeiten",
            "ask_question_prompt": "❓ <b>Stellen Sie Ihre Rechtsfrage</b>\n\nVerbleibende Fragen heute: <b>{remaining}</b>\n\nBeschreiben Sie Ihre Situation ausführlich. Geben Sie einfach Ihre Frage in der nächsten Nachricht ein:",
            "analyze_doc_prompt": "📄 <b>Dokumentenanalyse</b>\n\nVerbleibende Verarbeitungen heute: <b>{remaining}</b>\n\nSenden Sie ein Dokument zur Analyse (.txt, .docx, .pdf).",
            "edit_doc_prompt": "✏️ <b>Dokumentenbearbeitung</b>\n\nVerbleibende Verarbeitungen heute: <b>{remaining}</b>\n\nSenden Sie das Dokument und geben Sie in der Dateibeschreibung an, was geändert werden soll.",
            "doc_result_header": "📄 <b>Ergebnis der Dokumentenverarbeitung:</b>",
            "error_file_format": "❌ Nicht unterstütztes Format. Bitte verwenden Sie .txt, .docx, .pdf.",
            "error_file_size": "❌ Datei zu groß (max. 20 MB).",
            "error_file_extract": "❌ Text konnte nicht aus dem Dokument extrahiert werden. Überprüfen Sie, ob die Datei nicht beschädigt ist und Text enthält.",
            
            # --- Advocate Request ---
            "create_request_btn": "📝 Formelle Anfrage erstellen",
            "request_start": "✍️ Beginnen wir. Schritt 1: <b>Wählen Sie die Form der Anwaltstätigkeit:</b>",
            "legal_form_self": "Selbstständig", "legal_form_fop": "Einzelunternehmer", "legal_form_bureau": "Anwaltskanzlei (Büro)", "legal_form_union": "Anwaltskanzlei (Vereinigung)",
            "prompt_bureau_name": "Geben Sie den vollständigen <b>Namen der Anwaltskanzlei / -vereinigung</b> ein:",
            "prompt_legal_address": "Schritt 2: Geben Sie die <b>juristische Adresse</b> (Standort) ein:",
            "prompt_mailing_address": "Schritt 3: Geben Sie die <b>Postanschrift</b> ein:", "same_as_legal_btn": "Gleich wie juristische Adresse",
            "prompt_advocate_name": "Schritt 4: Geben Sie den <b>vollständigen Namen des Anwalts</b> ein:",
            "prompt_advocate_phone": "Schritt 5: Geben Sie die <b>Telefonnummer</b> ein:", "prompt_advocate_email": "Schritt 6: Geben Sie die <b>E-Mail-Adresse</b> ein:",
            "prompt_certificate_details": "Schritt 7: Geben Sie die <b>Seriennummer und Nummer des Zertifikats</b> ein:", "prompt_certificate_issuer": "Schritt 8: Geben Sie an, <b>wer und wann das Zertifikat ausgestellt wurde</b>:",
            "prompt_order_details": "Schritt 9: Geben Sie <b>Seriennummer, Nummer und Datum des Auftrags</b> ein:",
            "prompt_client_type": "Schritt 10: <b>Wählen Sie den Kundentyp</b>:", "client_type_physical": "Einzelperson", "client_type_legal": "Juristische Person",
            "prompt_client_physical_name": "Kunde (Einzelperson): Geben Sie den <b>vollständigen Namen</b> ein:", "prompt_client_physical_address": "Kunde (Einzelperson): Geben Sie die <b>Registrierungsadresse</b> ein:",
            "prompt_client_legal_name": "Kunde (Juristische Person): Geben Sie den <b>vollständigen Namen</b> ein:", "prompt_client_legal_edrpou": "Kunde (Juristische Person): Geben Sie den <b>EDRPOU-Code</b> ein:", "prompt_client_legal_address": "Kunde (Juristische Person): Geben Sie die <b>juristische Adresse</b> ein:",
            "prompt_contract_details": "Schritt 11: Geben Sie <b>Nummer und Datum des Rechtsbeistandsvertrags</b> ein:", "prompt_legal_aid_subject": "Schritt 12: Beschreiben Sie kurz den <b>Gegenstand des Rechtsbeistands</b>:",
            "prompt_recipient_details": "Schritt 13: Geben Sie die <b>Empfängerdetails</b> ein (Position, Vollständiger Name, Name der Organisation, Adresse).",
            "prompt_outgoing_number": "Schritt 14: Geben Sie die <b>ausgehende Anfragenummer</b> ein (oder /skip zum Überspringen):", "prompt_request_body": "Letzter Schritt: Geben Sie den <b>Text Ihrer Anfrage</b> ein (Punkte 'BITTE GEBEN SIE AN...'):",
            "request_generating": "⏳ Vielen Dank! Erstelle das endgültige Dokument... Dies kann bis zu einer Minute dauern.",
            "request_generation_complete": "✅ <b>Anwaltsanfrage erstellt!</b> Sende sie als `.docx`-Datei.", "request_cancelled": "Aktion abgebrochen. Zurück zum Hauptmenü.",

            # --- HEADERS FÜR AI PROMPT ANWALTSANFRAGE (важно, чтобы AI их понимал!) ---
            "prompt_header_recipient": "Empfänger",
            "prompt_header_sender": "Absender",
            "prompt_header_form": "Form der Anwaltstätigkeit",
            "prompt_header_bureau": "Name der Kanzlei",
            "prompt_header_advocate_name": "Vollständiger Name des Anwalts",
            "prompt_header_phone": "Telefon",
            "prompt_header_email": "E-Mail",
            "prompt_header_address": "Adresse",
            "prompt_header_certificate": "Zertifikat",
            "prompt_header_order": "Auftrag",
            "prompt_header_client": "Kunde",
            "prompt_header_client_type_phys": "Einzelperson",
            "prompt_header_client_type_legal": "Juristische Person",
            "prompt_header_basis": "Grundlage",
            "prompt_header_contract": "Rechtsbeistandsvertrag",
            "prompt_header_subject": "Gegenstand des Rechtsbeistands",
            "prompt_header_request_details": "Anfragedetails",
            "prompt_header_number": "Ausgehende Nummer",
            "prompt_header_date": "Datum",
            "prompt_header_body": "Anfragetext",
            "prompt_header_liability": "Haftung",

            "ai_system_prompt_general": "Sie sind ein professioneller juristischer KI-Assistent. Geben Sie detaillierte, gut strukturierte Antworten auf Rechtsfragen. Antworten Sie immer in der folgenden Sprache: {lang_name}.",
            "ai_system_prompt_document": "Sie sind ein professioneller juristischer KI-Assistent, der sich auf die Analyse und Bearbeitung von Dokumenten spezialisiert hat. Befolgen Sie die Anweisungen des Benutzers genau. Antworten Sie immer in der folgenden Sprache: {lang_name}.",
            "ai_system_prompt_advocate_request_de": """Sie sind ein hochqualifizierter ukrainischer Rechtsassistent. Ihre Aufgabe ist es, einen vollständigen, rechtlich korrekten Text einer Anwaltsanfrage basierend auf den bereitgestellten Daten zu erstellen. Halten Sie sich an einen förmlichen Geschäftsstil. Strukturieren Sie das Dokument: Kopfzeile (Empfänger, Absender), Titel, Präambel (unter Bezugnahme auf Artikel 20, 24 des Gesetzes der Ukraine "Über die Anwaltschaft und die Anwaltstätigkeit" und die Vereinbarung) und den Anfrageteil.
OBLIGATORISCH nach dem Anfrageteil fügen Sie den Ihnen zur Verfügung gestellten Block zur Verantwortung für die Nichtbeantwortung hinzu.
Am Ende fügen Sie eine Liste der Anhänge hinzu, geben das aktuelle Datum an und lassen Platz für die Unterschrift des Anwalts.""",
            "advocate_request_liability_clause_de": """Gesondert weise ich Sie darauf hin, dass gemäß Teil 2 von Artikel 24 des Gesetzes der Ukraine „Über die Anwaltschaft und die Anwaltstätigkeit“ ein staatliches Organ, ein Organ der lokalen Selbstverwaltung, deren Beamte und Bedienstete, Leiter von Unternehmen, Einrichtungen, Organisationen, öffentlichen Vereinigungen, an die eine Anwaltsanfrage gerichtet wurde, verpflichtet sind, dem Anwalt die entsprechenden Informationen und Kopien von Dokumenten spätestens innerhalb von fünf Arbeitstagen ab dem Datum des Erhalts der Anfrage zur Verfügung zu stellen. Falls die Anwaltsanfrage die Bereitstellung eines erheblichen Informationsumfangs betrifft oder die Suche nach Informationen in einer großen Datenmenge erfordert, kann die Bearbeitungsfrist der Anwaltsanfrage auf zwanzig Arbeitstage verlängert werden, unter Angabe der Gründe für diese Verlängerung.
Für eine rechtswidrige Weigerung, Informationen auf eine Anwaltsanfrage hin zu erteilen, für die verspätete oder unvollständige Bereitstellung von Informationen oder für die Bereitstellung von Informationen, die der Realität nicht entsprechen, ist gemäß Artikel 212-3 des ukrainischen Ordnungswidrigkeitengesetzes eine administrative Haftung vorgesehen.""",

            "create_contract_btn": "📝 Vertrag erstellen",
            "confirm_btn": "✅ Bestätigen", "edit_btn": "✏️ Bearbeiten",
            "error_invalid_input": "❌ Ungültige Eingabe. Bitte versuchen Sie es erneut.",

            "contract_header": "VERTRAG ÜBER RECHTSBEISTAND",
            "contract_start_intro": "Bitte geben Sie die wichtigsten Vertragsdaten ein:",
            "prompt_contract_number_date": "*1. NUMMER UND DATUM:*\n\nGeben Sie die Vertragsnummer und das Datum des Vertragsabschlusses im Format ein: `Nummer TT.MM.JJJJ`\nBeispiel: `123 01.01.2024`",
            "contract_date_header_template": "Kiew                                                «{day}» {month} {year}",
            "contract_generating": "⏳ Erstelle Vertragsdokument...",
            "contract_generation_complete": "✅ <b>Vertrag erstellt!</b> Sende ihn als `.docx`-Datei.",

            "contract_client_details_header": "2. VERTRAGSPARTEIEN: MANDANTEN-EINSTELLUNGEN:",
            "confirm_client_data_prompt": "_Bitte bestätigen oder ändern Sie die MANDANTEN-Daten:_\nName: <b>{name}</b>\nPosition des Leiters: <b>{position}</b>\nName des Leiters: <b>{fio}</b>\nGrundlage der Handlung: <b>{basis}</b>",
            "edit_client_name_btn": "Mandantenname ändern",
            "edit_client_position_btn": "Position des Leiters ändern",
            "edit_client_fio_btn": "Name des Leiters ändern",
            "edit_client_basis_btn": "Grundlage der Handlung ändern",
            "prompt_client_name": "Geben Sie den vollständigen MANDANTEN-Namen ein:",
            "prompt_client_position": "Geben Sie die Position des MANDANTEN-Leiters ein:",
            "prompt_client_fio": "Geben Sie den vollständigen Namen des MANDANTEN-Leiters ein:",
            "prompt_client_basis": "Geben Sie die Grundlage der Handlung des MANDANTEN-Leiters ein:",

            "contract_advocate_details_header": "ANWALTS-EINSTELLUNGEN:",
            "confirm_advocate_data_prompt": "_Bitte bestätigen oder ändern Sie die ANWALTS-Daten:_\nName: <b>{fio}</b>\nZulassungsserie: <b>{cert_series}</b>\nZulassungsnummer: <b>{cert_number}</b>\nAusgestellt von: <b>{cert_issuer}</b>\nBeschlussdatum: <b>{decision_date}</b>\nBeschlussnummer: <b>{decision_number}</b>",
            "edit_advocate_fio_btn": "Anwaltsnamen ändern",
            "edit_advocate_cert_series_btn": "Zulassungsserie ändern",
            "edit_advocate_cert_number_btn": "Zulassungsnummer ändern",
            "edit_advocate_cert_issuer_btn": "Aussteller ändern",
            "edit_advocate_decision_date_btn": "Beschlussdatum/Nummer ändern",
            "prompt_advocate_fio": "Geben Sie den vollständigen Namen des ANWALTS ein:",
            "prompt_advocate_cert_series": "Geben Sie die Zulassungsserie ein (z.B. `VN`):",
            "prompt_advocate_cert_number": "Geben Sie die Zulassungsnummer ein (z.B. `000237`):",
            "prompt_advocate_cert_issuer": "Geben Sie die ausstellende Behörde ein (z.B. `Anwaltskammer Region Winnyzja`):",
            "prompt_advocate_decision_date_number": "Geben Sie das Datum und die Nummer des Beschlusses ein (z.B. `21.03.2018 №3`):",

            "contract_section_1_header": "1. VERTRAGSGEGENSTAND",
            "contract_section_2_header": "2. PFLICHTEN UND RECHTE DER PARTEIEN",
            "contract_section_2_options": "Wählen Sie, was Sie ansehen oder ändern möchten:",
            "advocate_duties_btn": "Pflichten des Anwalts (2.1)",
            "client_duties_btn": "Pflichten des Mandanten (2.2)",
            "advocate_rights_btn": "Rechte des Anwalts (2.3)",
            "client_rights_btn": "Rechte des Mandanten (2.4)",
            "section_2_content_2_1": "<b>2.1. PFLICHTEN DES ANWALTS</b>\n\n<b>2.1. Der ANWALT verpflichtet sich auf Antrag des MANDANTEN, die folgende Rechtsberatung zu erbringen:</b>\n- prüft die internen Dokumente des MANDANTEN auf Einhaltung der ukrainischen Gesetzgebung, unterstützt den MANDANTEN bei der Vorbereitung und ordnungsgemäßen Ausfertigung der angegebenen Dokumente;\n- beteiligt sich an der Vorbereitung und rechtlichen Ausfertigung verschiedener Vertragsarten, die der MANDANT mit juristischen Personen, Unternehmern und Bürgern abschließt, unterstützt bei der Organisation der Kontrolle über die Erfüllung dieser Verträge, überwacht die Anwendung der gesetzlich und vertraglich vorgesehenen Sanktionen gegenüber Vertragspartnern, die ihre vertraglichen Verpflichtungen nicht erfüllen;\n- vertritt in der vorgeschriebenen Weise die Interessen des MANDANTEN vor Wirtschaftsgerichten, Gerichten der allgemeinen Gerichtsbarkeit, Verwaltungsgerichten sowie anderen Behörden bei der Behandlung von Rechtsstreitigkeiten;\n- fasst zusammen und analysiert: die Praxis der Behandlung von Gerichts- und anderen Angelegenheiten; gemeinsam mit anderen Abteilungen des MANDANTEN die Ergebnisse der Bearbeitung von Ansprüchen; die Praxis des Abschlusses und der Erfüllung von Verträgen; unterbreitet dem MANDANTEN Vorschläge zur Beseitigung festgestellter Mängel;\n- erteilt Rechtsberatungen, Gutachten und Auskünfte zu Rechtsfragen, die dem MANDANTEN im Rahmen seiner Tätigkeit entstehen;\n- wahrt das Anwaltsgeheimnis, dessen Gegenstand Fragen im Zusammenhang mit der Erbringung von Rechtsberatung gemäß den Bestimmungen dieses Vertrags sowie Dokumentation (Verträge, Buchhaltungs- und Steuerunterlagen, andere Dokumente) sind.",
            "section_2_content_2_2": "<b>2.2. PFLICHTEN DES MANDANTEN</b>\n\n<b>2.2. Der MANDANT verpflichtet sich:</b>\n- den ANWALT über alle ergriffenen Maßnahmen in Bezug auf den Fall zu informieren;\n- den ANWALT über alle ihm bekannten Umstände zu informieren, die für die Annahme und Ausführung des Auftrags durch den ANWALT gemäß diesem Vertrag von wesentlicher Bedeutung sein könnten;\n- den ANWALT rechtzeitig mit allem Notwendigen für die Ausführung seiner in diesem Vertrag vorgesehenen Aufträge zu versorgen, einschließlich Dokumenten in der erforderlichen Anzahl von Exemplaren, internen Normativakten, die die Tätigkeit des MANDANTEN regeln, gegebenenfalls mit einem Arbeitsplatz, Transportmitteln;\n- bei der Beilegung von Streitigkeiten des MANDANTEN mit anderen Unternehmen, Institutionen, Organisationen und natürlichen Personen, staatlichen Behörden und lokalen Selbstverwaltungsbehörden, deren Amtsträgern und Bediensteten, unverzüglich vollständige und wahrheitsgemäße Informationen zu liefern, die zur Beilegung des jeweiligen Streits erforderlich sind;\n- keine Handlungen zu verlangen, die über die beruflichen Rechte und Pflichten des ANWALTS hinausgehen;\n- auf Verlangen des ANWALTS Dokumente zur Verfügung zu stellen, die die Ausführung des Auftrags betreffen;\n- den ANWALT über Änderungen des Standorts, der E-Mail-Adresse, der Telefon- und Faxnummern zu informieren;\n- dem ANWALT die tatsächlichen Ausgaben zu erstatten, die für die Erfüllung des Vertrags erforderlich sind (z.B. Portokosten, Gerichtsgebühren, Fahrtkosten usw.), gegen Vorlage entsprechender Belege;\n- die Kosten der erhaltenen Dienstleistungen gemäß dem Vertrag pünktlich und in vollem Umfang zu bezahlen.",
            "section_2_content_2_3": "<b>2.3. RECHTE DES ANWALTS</b>\n\n<b>2.3. Der ANWALT hat das Recht:</b>\n- Anwaltsanfragen, einschließlich solcher zur Erlangung von Dokumentenkopien, an staatliche Behörden, lokale Selbstverwaltungsorgane, deren Amtsträger und Bedienstete, Unternehmen, Institutionen, Organisationen, öffentliche Vereinigungen sowie an natürliche Personen zu richten;\n- Rechte, Freiheiten und Interessen des Mandanten vor Gericht, bei staatlichen Behörden und lokalen Selbstverwaltungsorganen, in Unternehmen, Institutionen, Organisationen unabhängig von der Eigentumsform, öffentlichen Vereinigungen, gegenüber Bürgern, Amtsträgern, deren Befugnisse die Klärung entsprechender Fragen umfassen, zu vertreten und zu verteidigen;\n- sich mit den Gerichtsakten vertraut zu machen, Auszüge daraus anzufertigen, Kopien von zu den Akten genommenen Dokumenten anzufertigen, Kopien von Urteilen, Beschlüssen zu erhalten, an Gerichtsverhandlungen teilzunehmen, Beweismittel vorzulegen, an der Beweisaufnahme teilzunehmen, Fragen an andere am Verfahren beteiligte Personen sowie an Zeugen, Sachverständige, Spezialisten zu stellen, Anträge und Ablehnungen zu stellen, dem Gericht mündliche und schriftliche Erläuterungen zu geben, seine Argumente und Überlegungen zu Fragen, die während des Gerichtsverfahrens aufkommen, sowie Einwendungen gegen Anträge, Argumente und Überlegungen anderer Personen vorzubringen, sich mit dem Protokoll der Gerichtsverhandlung vertraut zu machen, Kopien davon anzufertigen und schriftliche Bemerkungen zu dessen Unrichtigkeit oder Unvollständigkeit einzureichen, die Aufzeichnung der Gerichtsverhandlung mit technischen Mitteln anzuhören, Kopien davon anzufertigen, schriftliche Bemerkungen zu deren Unrichtigkeit oder Unvollständigkeit einzureichen, Gerichtsurteile und -beschlüsse anzufechten, andere gesetzlich festgelegte Prozessrechte auszuüben;\n- sich in Unternehmen, Institutionen und Organisationen mit den für die Vertragserfüllung erforderlichen Dokumenten und Materialien vertraut zu machen, ausgenommen solche, die Informationen mit eingeschränktem Zugang enthalten;\n- Erklärungen, Beschwerden, Anträge, andere rechtliche Dokumente zu erstellen und diese im gesetzlich vorgeschriebenen Verfahren einzureichen;\n- technische Mittel zu verwenden, einschließlich zur Kopie von Aktenmaterialien in Fällen, in denen der ANWALT die Verteidigung, Vertretung oder andere Arten der Rechtsbeistand leistet, prozessuale Handlungen, an denen er teilnimmt, sowie den Verlauf der Gerichtsverhandlung in der gesetzlich vorgesehenen Weise zu protokollieren;\n- Kopien von Dokumenten in Fällen, die der ANWALT führt, zu beglaubigen, außer in Fällen, in denen das Gesetz eine andere obligatorische Art der Beglaubigung von Dokumentenkopien vorschreibt;\n- schriftliche Gutachten von Fachleuten, Experten zu Fragen, die besondere Kenntnisse erfordern;\n- andere Rechte auszuüben, die im Gesetz der Ukraine „Über die Anwaltschaft und die Anwaltstätigkeit“ und anderen Gesetzen vorgesehen sind;\n- dem MANDANTEN Benachrichtigungen übermitteln mittels: SMS-Massenversand; Postdienst; E-Mail; Telefon- und/oder Faxverbindung.\n\n<b>Der ANWALT kann den Vertrag mit dem MANDANTEN vorzeitig kündigen und die Erbringung von Dienstleistungen ohne zusätzliche Vereinbarungen verweigern, wenn einer der folgenden Gründe vorliegt:</b>\n- wenn der MANDANT die gemäß diesem Vertrag übernommenen Pflichten grob verletzt, insbesondere die Zahlung des Honorars ganz oder teilweise verweigert;\n- der MANDANT trotz der Erläuterungen des ANWALTS darauf besteht, ein Ergebnis zu erzielen, das der ANWALT nicht erbringen kann;\n- die ordnungsgemäße Ausführung des Auftrags aufgrund von Handlungen des MANDANTEN unmöglich wird, die dieser entgegen den Ratschlägen des ANWALTS vornimmt;\n- der MANDANT sich weigert, tatsächliche Ausgaben zu erstatten oder die Arbeit des ANWALTS bei einer erheblichen Erhöhung des Arbeitsumfangs zu bezahlen;\n- der physische oder psychische Zustand des ANWALTS ihn daran hindert, die Vertragserfüllung ordnungsgemäß fortzusetzen;\n- es Fakten oder Umstände gibt, die die Vertretung der Interessen des MANDANTEN durch den ANWALT rechtswidrig oder unethisch machen, und in anderen gesetzlich vorgesehenen Fällen.",
            "section_2_content_2_4": "<b>2.4. RECHTE DES MANDANTEN</b>\n\n<b>2.4. Der MANDANT hat das Recht:</b>\n- in jeder Phase der Vertragserfüllung Informationen vom ANWALT über den Fortschritt des Auftrags zu erhalten;\n- dem ANWALT mündliche oder schriftliche Anweisungen bezüglich der Ausführung des Auftrags gemäß diesem Vertrag zu erteilen;\n- vom ANWALT mündliche Informationen über den Fortschritt des Auftrags in der in diesem Vertrag festgelegten Reihenfolge und zu den Bedingungen zu erhalten;\n- vom ANWALT rechtliche Konsultationen zu Fragen der tatsächlichen und rechtlichen Grundlagen für die Ausführung des Auftrags, zur Praxis der Anwendung einschlägiger Gesetze, zur Möglichkeit und den rechtlichen Folgen der Erzielung des für den MANDANTEN gewünschten Ergebnisses zu erhalten;\n- den Vertrag mit dem ANWALT einseitig zu kündigen, indem er den ANWALT schriftlich 10 Tage im Voraus per Einschreiben mit Zustellnachweis oder persönlich an den ANWALT übergibt.",
            
            "contract_section_3_header": "3. ZAHLUNG UND ABRECHNUNG",
            "prompt_payment_type": "Bitte wählen Sie die Zahlungsart für den Vertrag:",
            "payment_type_free_btn": "Kostenlos",
            "payment_type_fixed_btn": "Pauschalhonorar",
            "payment_type_hourly_btn": "Stundensatz",
            "payment_type_percentage_btn": "Prozentsatz vom Gewinn/Ergebnis",
            "payment_type_combined_btn": "Kombiniertes System",

            "payment_type_free_text": "<b>3. ZAHLUNG UND ABRECHNUNG</b>\n<b>3.1. Die Rechtsberatung erfolgt kostenlos.</b>",

            "prompt_fixed_amount": "Bitte geben Sie den Festbetrag des Honorars in UAH ein. Beispiel: `15000`",
            "prompt_fixed_payment_order": "Großartig! Wie möchten Sie die Zahlungsmodalitäten angeben? (z.B. '100% Vorauszahlung', '50% Vorauszahlung, 50% nach Fertigstellung', 'monatlich')",
            "payment_type_fixed_text": "<b>3. ZAHLUNG UND ABRECHNUNG</b>\n<b>3.1. Für die Rechtsberatung zahlt der MANDANT dem ANWALT ein Pauschalhonorar in Höhe von {amount} UAH ({amount_words} Griwna).</b>\n<b>3.2. Zahlungsmodalitäten: {payment_order}</b>\n<b>3.3. Der MANDANT erstattet dem ANWALT die tatsächlich erforderlichen Ausgaben für die Vertragserfüllung (z.B. Portokosten, Gerichtsgebühren, Fahrtkosten etc.) gegen Vorlage entsprechender Belege.</b>",

            "prompt_hourly_rate": "Bitte geben Sie den Stundensatz des Anwalts in UAH ein. Beispiel: `800`",
            "prompt_hourly_accounting": "Wie wird die Zeiterfassung erfolgen? (z.B. 'monatliche Leistungsnachweise', 'Stundenzettel')",
            "prompt_hourly_payment_period": "Wie oft erfolgt die Zahlung und innerhalb wie vieler Bankarbeitstage? (z.B. 'monatlich innerhalb von 5 Bankarbeitstagen ab Unterzeichnung des Leistungsnachweises')",
            "payment_type_hourly_text": "<b>3. ZAHLUNG UND ABRECHNUNG</b>\n<b>3.1. Für die Rechtsberatung zahlt der MANDANT dem ANWALT ein Honorar auf Basis eines Stundensatzes von {rate} UAH/Stunde ({rate_words} Griwna pro Stunde).</b>\n<b>3.2. Die Erfassung der erbrachten Leistungen und der Arbeitszeit erfolgt gemäß {accounting} und wird von den Parteien durch Unterzeichnung von Leistungsnachweisen formalisiert.</b>\n<b>3.3. Die Zahlung erfolgt {payment_period}</b>\n<b>3.4. Der MANDANT erstattet dem ANWALT die tatsächlich erforderlichen Ausgaben für die Vertragserfüllung (z.B. Portokosten, Gerichtsgebühren, Fahrtkosten etc.) gegen Vorlage entsprechender Belege.</b>",

            "prompt_percentage_value": "Bitte geben Sie den Prozentsatz des Gewinnbetrags/Ergebnisses ein. Beispiel: `10`",
            "prompt_percentage_base": "Was ist die Berechnungsgrundlage für diesen Prozentsatz? (z.B. 'vom tatsächlich eingezogenen Betrag', 'vom eingesparten Betrag')",
            "prompt_percentage_condition": "Was ist die Zahlungsbedingung? (z.B. 'nach tatsächlichem Geldeingang', 'nach Rechtskraft der Entscheidung')",
            "payment_type_percentage_text": "<b>3. ZAHLUNG UND ABRECHNUNG</b>\n<b>3.1. Für die Rechtsberatung zahlt der MANDANT dem ANWALT ein Honorar in Höhe von {percentage}% von {base} nach {condition}</b>\n<b>3.2. Der MANDANT erstattet dem ANWALT die tatsächlich erforderlichen Ausgaben für die Vertragserfüllung (z.B. Portokosten, Gerichtsgebühren, Fahrtkosten etc.) gegen Vorlage entsprechender Belege.</b>",

            "prompt_combined_description": "Bitte beschreiben Sie das kombinierte Zahlungssystem detailliert (z.B. 'Pauschalhonorar von 5000 UAH + 5% des Gewinnbetrags' oder 'Stundensatz von 600 UAH/Stunde + Prämie für den erfolgreichen Abschluss des Falls').",
            "payment_type_combined_text": "<b>3. ZAHLUNG UND ABRECHNUNG</b>\n<b>3.1. Für die Rechtsberatung zahlt der MANDANT dem ANWALT ein Honorar gemäß dem folgenden kombinierten System: {description}</b>\n<b>3.2. Der MANDANT erstattet dem ANWALT die tatsächlich erforderlichen Ausgaben für die Vertragserfüllung (z.B. Portokosten, Gerichtsgebühren, Fahrtkosten etc.) gegen Vorlage entsprechender Belege.</b>",

            "contract_section_4_header": "4. VERTRAULICHKEIT UND ANWALTSGEHEIMNIS",
            "contract_section_5_header": "5. HÖHERE GEWALT",
            "contract_section_6_header": "6. VERTRAGSLAUFZEIT",
            "prompt_contract_end_date": "Bitte geben Sie das Enddatum des Vertrags ein. (z.B. `31.12.2024`)",
            "contract_section_7_header": "7. ÄNDERUNG DIESES VERTRAGES",
            "contract_section_8_header": "8. SONSTIGE BESTIMMUNGEN",
            "contract_section_9_header": "9. ANGABEN UND UNTERSCHRIFTEN DER PARTEIEN",
            "prompt_advocate_location": "Geben Sie den Standort des ANWALTS ein:",
            "prompt_client_edrpou": "Geben Sie die EDRPOU-Nummer des MANDANTEN ein:",
            "prompt_client_location": "Geben Sie den Standort des MANDANTEN ein:",
        },
    }

    @classmethod
    def get_text(cls, lang_code: str, key: str, **kwargs) -> str:
        """
        Получает текстовую строку по ключу для указанного языка.
        Использует fallback: сначала пытается найти текст для lang_code,
        затем для 'en', затем для 'uk'.
        """
        # Попытка получить текст для выбранного языка
        lang_texts = cls.TEXTS.get(lang_code, cls.TEXTS['uk'])
        text = lang_texts.get(key)
        
        # Fallback к английскому, если нет в выбранном языке
        if text is None:
            lang_texts = cls.TEXTS['en']
            text = lang_texts.get(key)
            
        # Fallback к украинскому, если нет и в английском
        if text is None:
            lang_texts = cls.TEXTS['uk']
            text = lang_texts.get(key)

        # Если текст все равно не найден, возвращаем сам ключ, чтобы было видно, что что-то не так
        if text is None:
            logging.warning(f"Missing translation key: '{key}' for language '{lang_code}'.")
            return key
            
        # Форматирование текста с помощью переданных аргументов
        return text.format(**kwargs) if kwargs else text

# --- Начальная настройка логирования ---
def setup_logging():
    """
    Настраивает базовое логирование для всего приложения.
    Уровень логирования определяется переменной окружения LOG_LEVEL.
    """
    log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_level = Config.LOG_LEVEL_MAP.get(log_level_str, logging.INFO)
    
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=log_level
    )
    # Возвращаем логгер для этого модуля, его можно импортировать в других местах.
    # Это гарантирует, что все части приложения будут использовать одинаково настроенный логгер.
    return logging.getLogger(__name__)

# Примечание: logger инициализируется здесь, но основное приложение
# вызывает setup_logging() в main.py, чтобы убедиться, что он настроен
# до того, как другие модули начнут использовать logging.getLogger(__name__).
# Тем не менее, иметь здесь logger = logging.getLogger(__name__) - хорошая практика
# для отладки самого config.py
# logger = logging.getLogger(__name__) # Закомментировано, так как `main.py` вызывает setup_logging()