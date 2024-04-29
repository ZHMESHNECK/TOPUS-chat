const searchResultsContainer = document.getElementById('searchResults');
const messageHistory = document.querySelector('.messages');
const responseDiv = document.querySelector('.response_search');
const friend_group_div = document.querySelector('.list-friends')
// notification
const chat_noti_btn = document.getElementById('radio-2')
const friend_noti_btn = document.getElementById('radio-3')
// private chat
const sendButton = document.querySelector('.write-form .send');
sendButton.addEventListener('click', option);
const textarea = document.getElementById('texxt');
// групи
let status_create_group = false
const create_group_btn = document.querySelector('.create_group')
create_group_btn.addEventListener('click', create_group)
// search
const searcharea = document.getElementById('search_chat_req');
searcharea.addEventListener('submit', getSearch);
const searchbutton = document.querySelector('.search input[type="submit"]')
searchbutton.addEventListener('click', getSearch);
// btn friend request
const btn_add_to_friend = document.querySelector('.add-friend-btn')
btn_add_to_friend.addEventListener('click', (e) => sendFriendReq(e))
const btn_acc_friend = document.querySelector('.accept-friend-btn')
btn_acc_friend.addEventListener('click', (e) => acceptFriendReq(e))
const btn_dec_friend = document.querySelector('.declain-friend-btn')
btn_dec_friend.addEventListener('click', (e) => declainFriendReq(e))
const btn_rem_friend = document.querySelector('.delete-friend-btn')
btn_rem_friend.addEventListener('click', (e) => removeFriend(e))
// label 
let label_send_friend = document.querySelector('.send_friendship')
let label_acc_dec_friend = document.querySelector('.request_friendship')
let label_delete_friend = document.querySelector('.remove_friendship')
let label_user_info = document.querySelector('.top .info')
// user_info
/* 
    notifications - Object
    user - Object
*/

// Відкриті private/загальні websocket
let privateWebSockets = new Map();


// Текст повідомлення приватного чату
textarea.addEventListener('keydown', function (event) {
    if (event.key === 'Enter' && event.shiftKey) {
        event.preventDefault()
        this.value += '\n';
    } else if (event.key === 'Enter') {
        event.preventDefault()
        option()
    }
})

function option() {
    if (!status_create_group) {
        sendMessage()
    } else {
        check_create_group()
    }
}


// Надсилання повідомлення + підключення websocket
function sendMessage() {
    const textarea = document.getElementById('texxt');
    const messageText = textarea.value.trim();

    if (!document.querySelector('.selected_user')) {
        textarea.value = '';
        return;
    }

    if (!messageText) {
        textarea.value = '';
        return;
    }

    let errorMessageSpan = document.querySelector('.error_message');
    let emptyChat = document.querySelector('.empty-chat');
    let friendId = document.querySelector('.selected_user').firstElementChild.attributes.getNamedItem('data-user-id').value;

    if (emptyChat !== null && !emptyChat.classList.contains('hidden')) {
        emptyChat.classList.add('hidden');
    }

    if (!errorMessageSpan.classList.contains('hidden')) {
        errorMessageSpan.textContent = '';
        errorMessageSpan.classList.add('hidden');
    }

    const privateChatWebSocket = connectToPrivCHat(friendId);
    privateChatWebSocket.send(messageText);
    textarea.value = '';
}


// Пошук
async function getSearch(e) {
    e.preventDefault()
    let input = searcharea.value;

    if (input.length >= 2) {
        // Очищаємо контейнер перед додаванням нових результатів
        searchResultsContainer.innerHTML = '';

        const data = {
            'request': input
        }
        try {
            let response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.status == 200) {
                const responseData = await response.json();

                createSearchResults(responseData)
                clickOnblock()

            } else {
                const errorData = await response.json();
                console.log(errorData);
            }
        } catch (error) {
            console.error('Помилка:', error);
        }
    }
}


// Додання нових даних з пошуку 
function clickOnblock() {

    let user = document.querySelectorAll('.info')

    user.forEach(function (element) {
        element.addEventListener('click', function (event) {
            let target = event.target;
            let item_id;
            let selectedElement = target.closest('.info');
            // Якщо обраний блок - юзер 
            if (!selectedElement.classList.contains('info-group')) {

                if (target.classList.contains('status')) {
                    item_id = target.parentElement.firstElementChild.attributes.getNamedItem('data-user-id').value
                } else if (target.classList.contains('info')) {
                    item_id = target.firstElementChild.attributes.getNamedItem('data-user-id').value
                } else if (target.classList.contains('noti_mess')) {
                    item_id = target.previousElementSibling.attributes.getNamedItem('data-user-id').value
                } else {
                    item_id = target.attributes.getNamedItem('data-user-id').value;
                }
            } else {
                if (target.classList.contains('info')) {
                    item_id = target.firstElementChild.attributes.getNamedItem('data-group-id').value
                } else if (target.classList.contains('noti_mess')) {
                    item_id = target.previousElementSibling.attributes.getNamedItem('data-group-id').value
                } else {
                    item_id = target.attributes.getNamedItem('data-group-id').value;
                }
            }

            if (!selectedElement.classList.contains('selected_user')) {
                let previousSelectedUser = document.querySelector('.info.selected_user');
                if (previousSelectedUser) {
                    previousSelectedUser.classList.remove('selected_user');
                }
                selectedElement.classList.add('selected_user');
                if (!selectedElement.classList.contains('info-group')) {
                    fetchChatHistory(item_id)
                    connectToPrivCHat(item_id)
                } else {
                    // //
                    fetchChatGroupHistory(item_id)
                    conectToGroup(item_id)

                }
            }
        });
    });
}

// Підготовка інтерфейсу до відображення історії повідомлень
async function fetchChatHistory(userId) {

    hide_user_info()

    try {
        let response = await fetch(`/chat/get_history_chat/${userId}`, {
            method: 'GET',
        });
        const data = await response.json();
        const friend = document.querySelectorAll(`div[data-user-id="${userId}"]`);

        rm_noti(friend);
        let user_data = show_btn(friend[0])

        show_history(data, user_data)

    } catch (error) {
        console.log('error', error)
    }
}

// Підготовка інтерфейсу до відображення історії повідомлень з групи
async function fetchChatGroupHistory(group_id) {
    hide_user_info()

    try {
        let response = await fetch('/chat/')  /////////////////
    } catch (error) {
        console.log(error)
    }

}


// Генерація історії чату
function show_history(data, user_data) {
    let main_status = document.querySelector('.top .info .count div');
    main_status.className = user_data['online'] == 'true' ? 'status on' : 'status off';
    main_status.textContent = user_data['online'] == 'true' ? 'онлайн' : user_data['last_seen'];
    document.querySelector('.top .info .name').textContent = user_data['username']
    messageHistory.innerHTML = '';

    if (label_user_info.classList.contains('hidden')) {
        label_user_info.classList.remove('hidden')
    }

    if (data.length > 0) {
        data.forEach(function (message) {

            if (message.sender_id == user['id']) {
                let user_message = `<li class="i"><div class="head"><span class="name">Ви</span></div><div class="message">${message.message}</div></li>`;
                messageHistory.insertAdjacentHTML('beforeend', user_message);
            } else {
                let friend_message = `<li class="friend-with-a-SVAGina"><div class="head"><span class="name">${user_data['username']}</span></div><div class="message">${message.message}</div></li>`;
                messageHistory.insertAdjacentHTML('beforeend', friend_message);
            }
        })
        messageHistory.scrollTop = messageHistory.scrollHeight;
    } else {
        messageHistory.innerHTML = '<li class="empty-chat">Історія чату відсутня</li>';
    }
}

// Кнопки взаємодії з користувачем
function show_btn(friend) {

    user_data = {
        id: friend.dataset.userId,
        username: friend.dataset.userName,
        online: friend.dataset.userOnline.toLowerCase(),
        last_seen: friend.dataset.userLast_seen,
        is_friend: friend.dataset.userIsFriend,
        is_send_req: friend.dataset.userSendReq
    }
    if (user_data['is_friend'] == 'true') {
        label_delete_friend.classList.remove('hidden');
        label_delete_friend.lastElementChild.value = user_data['id']
    } else if (user_data['is_friend'] == 'false' && user_data['is_send_req'] == 'true') {
        label_acc_dec_friend.classList.remove('hidden')
        label_acc_dec_friend.children[1].value = user_data['id']
        label_acc_dec_friend.children[2].value = user_data['id']
    } else if (user_data['is_friend'] == 'false' && user_data['is_send_req'] == 'false') {
        label_send_friend.classList.remove('hidden')
        label_send_friend.lastElementChild.value = user_data['id']
    }
    return user_data
}

// Видаляємо не прочитанні повідомлення та віднімаємо їх з головної label
function rm_noti(friend) {

    // Віднімаємо кількість повідомлень з головної label
    if (friend[0].nextElementSibling.classList.contains('noti_mess')) {
        let count_unread_noti;
        count_unread_noti = parseInt(friend[0].nextElementSibling.innerHTML.trim(), 10)
        let label_notific = chat_noti_btn.nextElementSibling.firstElementChild
        let currentCount = parseInt(label_notific.innerHTML.trim(), 10) - count_unread_noti;
        label_notific.innerHTML = currentCount
        // Видаляємо всі notifications у знайдених юзерів
        friend.forEach(noti => {
            noti.nextElementSibling.remove();
        })
    }
}

let friendRequestClicked = false;
let ChatClicked = false;

// Блокуємо надсилання запиту на 1.5 секунди
friend_noti_btn.addEventListener('click', event => {
    if (!friendRequestClicked) {
        showFriendRequest();
        friendRequestClicked = true;
        setTimeout(() => {
            friendRequestClicked = false;
        }, 1500);
    } else {
        event.preventDefault();
    }
});

// Блокуємо надсилання запиту на 1.5 секунди
chat_noti_btn.addEventListener('click', event => {
    if (!ChatClicked) {
        showMessRequest();
        ChatClicked = true;
        setTimeout(() => {
            ChatClicked = false;
        }, 1500);
    } else {
        event.preventDefault();
    }
});


// Запити в друзі
async function showFriendRequest() {

    try {
        let response = await fetch('/noti/friend_req', {
            method: 'GET',
        });

        if (response.status == 200) {
            const data = await response.json()
            // Очищаємо контейнер перед додаванням нових результатів
            searchResultsContainer.innerHTML = '';
            if (data.length > 0) {
                createSearchResults(data, 'friend');
                clickOnblock()
            }
        }
    } catch (error) {
        console.log(error)
    }
}

// Запити нових повідомлень
async function showMessRequest() {

    try {
        let response = await fetch('/noti/mess_noti', {
            method: 'GET',
        });

        if (response.status == 200) {
            const data = await response.json()
            // Очищаємо контейнер перед додаванням нових результатів
            searchResultsContainer.innerHTML = '';
            if (data.length > 0) {
                createSearchResults(data, 'mess');
                clickOnblock()
            }
        }
    } catch (error) {
        console.log(error)
    }

}


// Результат пошуку юзерів
function createSearchResults(responseData, option = null) {
    responseData.forEach(function (result) {
        let li = document.createElement('li');
        if (option == 'friend') {
            li.className = 'friend_req'
        } else if (option == 'mess') {
            li.className = 'mess_req'
        }

        let divInfo = document.createElement('div');
        divInfo.className = 'info';

        let divUser = document.createElement('div');
        divUser.className = 'user';
        divUser.textContent = result.username;
        divUser.dataset.userId = result.id;
        divUser.dataset.userName = result.username;
        divUser.dataset.userOnline = result.online;
        divUser.dataset.userLast_seen = result.last_seen;
        divUser.dataset.userIsFriend = result.is_friend;
        divUser.dataset.userSendReq = result.reque;
        divInfo.appendChild(divUser);

        let divStatus = document.createElement('div');
        divStatus.className = result.online ? 'status on' : 'status off';
        divStatus.textContent = result.online ? 'онлайн' : result.last_seen;

        // Перевіряємо на кількість не прочитаних повідомлень від юзера
        if (result.id in notifications['user_mes']) {
            let divNotiMess = document.createElement('div');
            divNotiMess.className = 'noti_mess';
            divNotiMess.textContent = notifications['user_mes'][result.id];
            divInfo.appendChild(divNotiMess)
        }
        divInfo.appendChild(divStatus);
        li.appendChild(divInfo);
        searchResultsContainer.appendChild(li);
    })
}


// 
function connectToPrivCHat(friend_id) {
    let websocket = privateWebSockets.get(friend_id);
    if (!websocket) {
        websocket = new WebSocket(`ws://localhost:8000/chat/private_chat/${user['id']}/${friend_id}`);

        websocket.onmessage = function (e) {
            handleIncomingMessage(e.data);
        };

        privateWebSockets.set(friend_id, websocket);
    }
    return websocket;
};


// Відправити запит в друзі
async function sendFriendReq(e) {
    let friend_id = e.target.value
    try {
        let response = await fetch(`/user/add_friend/${friend_id}`, {
            method: 'GET',
        })
        const data = await response.json();
        showResponse(response.status, data)
    } catch (error) {
        console.log('error', error)
    }
}

// Прийняти запит в друзі
async function acceptFriendReq(e) {
    let friend_id = e.target.value
    try {
        let response = await fetch(`/user/accept_friend/${friend_id}`, {
            method: 'GET',
        })
        const data = await response.json();
        showResponse(response.status, data)
    } catch (error) {
        console.log('error', error)
    }
}


// Відхилити запит в друзі
async function declainFriendReq(e) {
    let friend_id = e.target.value
    try {
        let response = await fetch(`/user/declain_friend/${friend_id}`, {
            method: 'GET',
        })
        const data = await response.json();
        showResponse(response.status, data, option = 'dec')

    } catch (error) {
        console.log('error', error)
    }
}


// Видалити з друзів
async function removeFriend(e) {
    let friend_id = e.target.value
    try {
        let response = await fetch(`/user/del_friend/${friend_id}`, {
            method: 'DELETE',
        })
        const data = await response.json();
        showResponse(response.status, data, option = 'del')
    } catch (error) {
        console.log('error', error)
    }
}


// Відповідь від сервера
function showResponse(status, data, option = null) {
    let okMessageSpan = responseDiv.querySelector('.ok_message');
    let errorMessageSpan = responseDiv.querySelector('.error_message');
    responseDiv.classList.remove('hidden');
    if (status == 200 || 201) {
        if (!errorMessageSpan.classList.contains('hidden')) {
            errorMessageSpan.classList.add('hidden')
        }
        if (okMessageSpan.classList.contains('hidden')) {
            okMessageSpan.classList.remove('hidden')
        }
        okMessageSpan.textContent = data;

    } else {
        if (!okMessageSpan.classList.contains('hidden')) {
            okMessageSpan.classList.add('hidden')
        }
        errorMessageSpan.textContent = data;
        if (errorMessageSpan.classList.contains('hidden')) {
            errorMessageSpan.classList.remove('hidden')
        }
    }

    if (option == 'del') {
        if (!label_delete_friend.classList.contains('hidden')) {
            label_delete_friend.classList.add('hidden');
        }
    } else if (option == 'dec') {
        if (!label_acc_dec_friend.classList.contains('hidden')) {
            label_acc_dec_friend.classList.add('hidden');
        }
    }

    if (!btn_add_to_friend.parentNode.classList.contains('hidden')) {
        btn_add_to_friend.parentNode.classList.add('hidden')
    }
}


async function logout() {
    let response = await fetch('/logout', {
        method: 'POST'
    });

    if (response.status == 200) {
        location.assign('/auth/login');
    }
    return false
}


function get_date() {
    let currentDate = new Date();
    let day = currentDate.getDate().toString().padStart(2, "0");
    let month = (currentDate.getMonth() + 1).toString().padStart(2, "0");
    let year = currentDate.getFullYear().toString()
    let hours = currentDate.getHours().toString().padStart(2, "0");
    let minutes = currentDate.getMinutes().toString().padStart(2, "0");
    let formattedDate = `${day}-${month}-${year} ${hours}:${minutes}`;
    return formattedDate
}

// Сховати інформацію про юзера
function hide_user_info() {
    // Ховаємо присутні повідомлення response
    if (!responseDiv.classList.contains('hidden')) {
        responseDiv.classList.add('hidden');
    }
    // По дефолту ховаємо кнопки всі кнопки
    if (!label_send_friend.classList.contains('hidden')) {
        label_send_friend.classList.add('hidden')
    }
    if (!label_acc_dec_friend.classList.contains('hidden')) {
        label_acc_dec_friend.classList.add('hidden')
    }
    if (!label_delete_friend.classList.contains('hidden')) {
        label_delete_friend.classList.add('hidden')
    }
    if (!label_user_info.classList.contains('hidden')) {
        label_user_info.classList.add('hidden')
    }
}

// Групи 

// Статус створення групи 
function create_group() {
    hide_user_info()
    messageHistory.innerHTML = '';

    let msg_create_group = document.createElement('span')
    msg_create_group.className = 'msg_create_group'
    msg_create_group.textContent = 'Введіть назву группи'
    responseDiv.appendChild(msg_create_group)
    if (responseDiv.classList.contains('hidden')) {
        responseDiv.classList.remove('hidden')
    }
    status_create_group = true
}

// Перевірка введеної назви
function check_create_group() {
    const textarea = document.getElementById('texxt');
    const messageText = textarea.value.trim();
    let errorMessageSpan = document.querySelector('.error_message');

    if (messageText.length <= 2 || messageText.includes('\n')) {
        errorMessageSpan.textContent = 'Коротка назва або містить символи переносу';
        errorMessageSpan.classList.remove('hidden');
        return;
    }

    if (status_create_group) {
        if (!errorMessageSpan.classList.contains('hidden')) {
            errorMessageSpan.classList.add('hidden')
            errorMessageSpan.textContent = '';
        }
        document.querySelector('.msg_create_group').classList.add('hidden');
        textarea.value = '';
        req_create_group(messageText)
        return;
    }
}

// Запит на створення группи
async function req_create_group(title) {
    try {
        console.log('send')
        let response = await fetch('/chat/create_group', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'title': title })
        });

        const responseData = await response.json();
        showResponse(response.status, responseData.msg)
        response_create_group(title)
        console.log(responseData)
        status_create_group = false;

    } catch (error) {
        console.error('Помилка:', error);
    }
}

// Відображення створенної групи
function response_create_group(title) {
    let divInfoGroup = document.createElement('div');
    let li = document.createElement('li');
    divInfoGroup.className = 'info info-group';

    let divGroup = document.createElement('div');
    divGroup.className = 'user group';
    divGroup.textContent = title;
    divGroup.dataset.groupTitle = title;
    divInfoGroup.appendChild(divGroup);
    li.appendChild(divInfoGroup);

    let firstChild = friend_group_div.children[2];
    friend_group_div.insertBefore(li, firstChild);
    clickOnblock()
}


function add_count_noti(item_id, type = 'private') {
    let noti;

    if (type == 'private') {
        noti = document.querySelectorAll(`[data-user-id="${item_id}"]`)
    } else if (type == 'group') {
        noti = document.querySelectorAll(`[data-group-title="${item_id}"]`) ////
    }

    let label_notific = chat_noti_btn.nextElementSibling.firstElementChild
    let currentCount = parseInt(label_notific.innerHTML.trim(), 10) + 1;
    label_notific.innerHTML = currentCount
    // Обходимо потрібного юзера та додаємо +1 до повідомлення
    noti.forEach(function (el) {
        if (el.nextElementSibling.classList.contains('noti_mess')) {
            let currentCount = parseInt(el.nextElementSibling.innerHTML.trim(), 10) + 1;
            el.nextElementSibling.innerHTML = currentCount
        } else {
            // Якщо наступний елемент відсутній або не має класу 'noti_mess'
            let newElement = document.createElement('div');
            newElement.classList.add('noti_mess');
            newElement.innerHTML = '1'; // Початкове значення лічильника
            el.parentNode.insertBefore(newElement, el.nextSibling);
        }
    })
}