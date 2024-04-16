## Оновлення

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