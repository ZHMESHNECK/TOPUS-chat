## Оновлення

version 0.0.5
- Додано дублювання записів для двох юзерів у таблиці FriendShopDB для спрощення пошуку та взаемодії
- Для моделей ( NotificationDB, FriendRequestDB, FriendshipDB ) змінені поля username -> user_id
- Оновлення chat.js -> спочатку сервер отримує повідомлення,  потім розсилає всім вебосекам

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