## Оновлення

version 0.1.1
- На головну сторінку додано відображення груп юзера
- Дублюючий код з conftest перенесено в utils.py
- Тести для груп
    - TestClient для тестів чату перенесено у фікстуру
- Функцію save_notification перенесено до noti_db
- Для моделі ChatDB змінено назву поля з chat -> title
- Змінено назву таблиці для AdminsOfGroup - moderator -> group
    - Потрібна перевірка міграцій
- Для надсилання собі повідомлення у PrivateManager тепер використовується свій же вебсокет замість PublicManager
- Для видалення групи потрібно її назва замість id

version 0.1.0
- Початок роботи з групами у js
- Додана можливість перенесення рядка у textarea "shift + enter"
- Всі надсилання повідомлень у приватному чаті перенесені до Public менеджера
- Винесені в окремі функції add_count_noti, hide_user_info
- Для delete_group видалено зайвий параметр chat:str

version 0.0.9
- Повідомлення у websocket відправляються у форматі json
- Серверна частина для групових чатів
    - Тести
- Розділення загального чату від особистих у js
- Видалене поле role у юзерів

version 0.0.8
- Оновлення тестів
    - Зв'язок між TestUserDBFriend3|4 створюється по дефолту
- Динамічне оновлення online | offline для юзерів
- Нове поле для MessageDB - sender_username (null=True)
- Додано загальний чат
- Додано Flake8

version 0.0.7
- Додано загальний чат ( html | css )
- Фікс відображення помилок на сторінці логіну
- Допрацювання повідомлень ( всі повідомлення прочитанні = True )

version 0.0.6
- Розділення таблиці NotificationDB на Friend / Message
- Додана модель для token ( Pydantic )
- Тест на перевірку повідомлень додано до test_chat
- В main.html змінні одразу передаються в js
- Покращено опрацювання label
- Відображення кількості не прочитаних повідомлень від кожного юзера
- Отримання списку юзерів для кожної функції перенесено до core/utils

version 0.0.5
- Додано дублювання записів для двох юзерів у таблиці FriendShopDB для спрощення пошуку та взаємодії
- Для моделей ( NotificationDB, FriendRequestDB, FriendshipDB ) змінені поля username -> user_id
- Оновлення chat.js -> спочатку сервер отримує повідомлення, потім розсилає всім вебсокетам

version 0.0.4
- Додані повідомлення ( додати юзера в друзі )
- Logout
- Правки тестів + notification tests
- У файлі user_db замінені HTTPExceptoin на JSONResponse
- Додано websocket для публічного чату ( online/offline - user)

version 0.0.3
- Пошук юзерів
- Розділення тестів для різної бізнес логіки
- Моделі Chat
- Js для блоку "Chat"
- Заготівля для "Notification"
- Додана логіка відхилення "запиту до друзів" - без UI
- Авторизація через JWT токен, який зберігається у Cookie

version 0.0.2
- api (add | accept | delete) friend
    - pytest

version 0.0.1
- api ( login | registration )
    - pytests