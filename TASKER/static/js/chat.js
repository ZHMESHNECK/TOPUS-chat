const searchResultsContainer = document.getElementById('searchResults');
const messageHistory = document.querySelector('.messages');
const responseDiv = document.querySelector('.response_search');
// notification
const chat_noti_btn = document.getElementById('radio-2')
const friend_noti_btn = document.getElementById('radio-3')
// online / offline
document.addEventListener('DOMContentLoaded', connetcToPubChat);
document.addEventListener('DOMContentLoaded', clickOnUser(0));
// private chat
const sendButton = document.querySelector('.write-form .send');
sendButton.addEventListener('click', sendMessage);
const textarea = document.getElementById('texxt');
// public chat
// document.getElementById('public_chat').addEventListener('submit', sendMessage);
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
// user_info
/* 
    notifications - Object
    user - Object
*/

// Відкриті private websocket
let privateWebSockets = new Map();


// Текст повідомлення
textarea.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});


// Надсилання повідомлення + підключення websocket
function sendMessage() {
    let empty_chat = document.querySelector('.empty-chat')
    let friendId = document.querySelector('.selected_user').firstElementChild.attributes.getNamedItem('data-user-id').value
    const messageText = textarea.value;
    if (messageText.trim().length >= 1) {
        // Видаляємо label с порожньою історією
        if (empty_chat !== null && !empty_chat.classList.contains('hidden')) { empty_chat.classList.add('hidden') }

        const privateChatWebSocket = connectToPrivCHat(friendId);
        privateChatWebSocket.send(messageText);
    };

    textarea.value = '';
}


searcharea.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        getSearch(event);
    }
});


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

                createSerachResults(responseData)
                clickOnUser()

            } else {
                const errorData = await response.json();
                console.log(errorData);
                console.log('помилка');
            }
        } catch (error) {
            console.error('Помилка:', error);
        }
    }
}


// Додання нових даних з пошуку 
function clickOnUser() {

    let user = document.querySelectorAll('.info')

    user.forEach(function (element) {
        element.addEventListener('click', function (event) {
            let target = event.target;
            let user_id;
            let selectedElement = target.closest('.info');
            if (target.classList.contains('status')) {
                user_id = target.parentElement.firstElementChild.attributes.getNamedItem('data-user-id').value
            } else if (target.classList.contains('info')) {
                user_id = target.firstElementChild.attributes.getNamedItem('data-user-id').value
            } else if (target.classList.contains('noti_mess')) {
                user_id = target.previousElementSibling.attributes.getNamedItem('data-user-id').value
            } else {
                user_id = target.attributes.getNamedItem('data-user-id').value;
            }

            if (!selectedElement.classList.contains('selected_user')) {
                let previousSelectedUser = document.querySelector('.info.selected_user');
                if (previousSelectedUser) {
                    previousSelectedUser.classList.remove('selected_user');
                }
                selectedElement.classList.add('selected_user');
                fetchChatHistory(user_id)
                connectToPrivCHat(user_id)
            }
        });
    });
}


async function fetchChatHistory(userId) {

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

// Генерація історії чату
function show_history(data, user_data) {
    messageHistory.innerHTML = '';
    if (data.length > 0) {
        data.forEach(function (message) {
            document.querySelector('.top .info .name').textContent = user_data['username']
            let main_status = document.querySelector('.top .info .count div');

            main_status.className = user_data['online'] == 'true' ? 'status on' : 'status off';
            main_status.textContent = user_data['online'] == 'true' ? 'онлайн' : user_data['last_seen'];
            if (message.sender_id == user['id']) {
                let user_message = `<li class="i"><div class="head"><span class="name">Ви</span></div><div class="message">${message.message}</div></li>`;
                messageHistory.insertAdjacentHTML('beforeend', user_message);
            } else {
                let friend_message = `<li class="friend-with-a-SVAGina"><div class="head"><span class="name"> ${user_data['username']}</span></div><div class="message">${message.message}</div></li>`;
                messageHistory.insertAdjacentHTML('beforeend', friend_message);
            }
        })
    } else {
        document.querySelector('.top .info .name').textContent = user_data['username']
        let main_status = document.querySelector('.top .info .count div');

        main_status.className = user_data['online'] == 'true' ? 'status on' : 'status off';
        main_status.textContent = user_data['online'] == 'true' ? 'онлайн' : user_data['last_seen'];

        messageHistory.innerHTML = '<li class="empty-chat">Історія чату відсутня</li>';
    }
    messageHistory.scrollTop = messageHistory.scrollHeight;
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

// Блокуємо надсилання запиту на 2 секунди
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

// Блокуємо надсилання запиту на 2 секунди
chat_noti_btn.addEventListener('click', event => {
    if (!friendRequestClicked) {
        showMessRequest();
        friendRequestClicked = true;
        setTimeout(() => {
            friendRequestClicked = false;
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
                createSerachResults(data, 'friend');
                clickOnUser()
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
                createSerachResults(data, 'mess');
                clickOnUser()
            }
        }
    } catch (error) {
        console.log(error)
    }

}


// Результат пошуку юзерів
function createSerachResults(responseData, option = null) {
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


// function sendPubMessage(e) {
//     e.preventDefault();
//     console.log(e.target)

//     const message = document.getElementById('public_message')
//     console.log(message)
// }


function connetcToPubChat() {
    const pubwebsocket = new WebSocket(`ws://localhost:8000/chat/public_chat?user_id=${user['id']}`)
    pubwebsocket.onmessage = function (e) {
        try {
            let parts = e.data.split(':', 3);
            if (parts[0] == 'private') {
                handleIncomingMessage(parts);
            }
        } catch (error) {
            console.log(error)
        }
    }
}

function connectToPrivCHat(friend_id) {
    let websocket;
    if (privateWebSockets.has(friend_id)) {
        websocket = privateWebSockets.get(friend_id);
    } else {
        websocket = new WebSocket(`ws://localhost:8000/chat/private_chat/${user['id']}/${friend_id}`);

        websocket.onmessage = function (e) {
            try {
                let parts = e.data.split(':', 3);
                if (parts[0] == 'private') {
                    handleIncomingMessage(parts);
                }
            } catch (error) {
                console.log(error)
            }
        };

        privateWebSockets.set(friend_id, websocket);
    }
    return websocket;
};


// Повідомлення з websocket
function handleIncomingMessage(message) {

    const selectedUserElement = document.querySelector('.info.selected_user');
    let active_friendname_chat, active_friendname_id
    let userId_from_mess, mes_from_user;

    if (selectedUserElement) {

        active_friendname_chat = selectedUserElement.firstElementChild.getAttribute('data-user-name');
        active_friendname_id = selectedUserElement.firstElementChild.getAttribute('data-user-id');
    }
    try {
        [_, userId_from_mess, mes_from_user] = message;
    } catch (error) {
        console.log(error);
        return;
    }

    // Якщо id sender or receiver в active_friendname_id - тоді показуємо повідомлення
    if (active_friendname_id == userId_from_mess || userId_from_mess == user['id']) {
        const isFriendMessage = userId_from_mess != null && userId_from_mess != user['id'];
        const messageSender = isFriendMessage ? active_friendname_chat : 'Ви';
        const messageClass = isFriendMessage ? 'friend-with-a-SVAGina' : 'i';
        const messageHTML = `<li class="${messageClass}"><div class="head"><span class="name">${messageSender}</span></div><div class="message">${mes_from_user}</div></li>`;
        messageHistory.insertAdjacentHTML('beforeend', messageHTML);
        messageHistory.scrollTop = messageHistory.scrollHeight;
    } else {
        // Додання кількості не прочитаних повідомлень у label
        let label_notific = chat_noti_btn.nextElementSibling.firstElementChild
        let currentCount = parseInt(label_notific.innerHTML.trim(), 10) + 1;
        label_notific.innerHTML = currentCount

        let user_noti = document.querySelectorAll(`[data-user-id="${userId_from_mess}"]`)

        // Обходимо потрібного юзера та додаємо +1 до повідомлення
        user_noti.forEach(function (user_noti) {
            if (user_noti.nextElementSibling.classList.contains('noti_mess')) {
                let currentCount = parseInt(user_noti.nextElementSibling.innerHTML.trim(), 10) + 1;
                user_noti.nextElementSibling.innerHTML = currentCount
            } else {
                // Якщо наступний елемент відсутній або не має класу 'noti_mess'
                let newElement = document.createElement('div');
                newElement.classList.add('noti_mess');
                newElement.innerHTML = '1'; // Початкове значення лічильника
                user_noti.parentNode.insertBefore(newElement, user_noti.nextSibling);
            }
        })
    }
}

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
        btn_add_to_friend.parentNode.classList.add('hidden');
    } else if (status == 400 || status == 500) {
        if (!okMessageSpan.classList.contains('hidden')) {
            okMessageSpan.classList.add('hidden')
        }
        errorMessageSpan.textContent = data;
        if (errorMessageSpan.classList.contains('hidden')) {
            errorMessageSpan.classList.remove('hidden')
        }
        btn_add_to_friend.parentNode.classList.add('hidden');

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
