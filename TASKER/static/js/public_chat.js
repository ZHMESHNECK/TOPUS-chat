// online / offline
document.addEventListener('DOMContentLoaded', connetcToPubChat);
document.addEventListener('DOMContentLoaded', function () {
    clickOnblock(0);
});
// public chat
const PublicmessageHistory = document.querySelector('.pub_messages-content');
const sendPubMes = document.querySelector('.message-box .message-submit')
sendPubMes.addEventListener('click', sendMessagePub);
const pubtextarea = document.getElementById('pub_textarea');


// user_info
/* 
notifications - Object
user - Object
*/
let publicWebSockets = new Map();

// Історія загального чату
async function showPubHistory() {
    let response = await fetch('/chat/get_history_public', {
        method: 'GET',
    });
    let error = document.querySelector('.pub_messages-content .error_chat')
    if (!error.classList.contains('hidden')) {
        error.classList.add('hidden')
    }
    const data = await response.json();

    if (response.status == 200) {
        data.forEach((message) => {
            try {
                username_from_mess = message.sender_username;
                mes_from_user = message.message
            } catch (error) {
                console.log(error);
                return;
            }
            let isFriendMessage = username_from_mess != null && username_from_mess == user['username'];
            let messageSender = isFriendMessage ? 'Ви' : username_from_mess;
            let messageClass = isFriendMessage ? 'pub_msg_self' : 'pub_msg';
            let messageTextClass = isFriendMessage ? 'message message-personal new' : 'message new';
            let messageHTML = `<div class='${messageClass}'><div class='head_pub'>${messageSender}</div><div class='${messageTextClass}'>${mes_from_user}</div></div>`;
            PublicmessageHistory.insertAdjacentHTML('beforeend', messageHTML)
        })
        PublicmessageHistory.scrollTop = PublicmessageHistory.scrollHeight;

    } else {
        if (error.classList.contains('hidden')) {
            error.classList.remove('hidden')
            error.innerHTML = data
        }
    }
}

// Online | Offline
function connetcToPubChat() {
    let pubwebsocket = publicWebSockets.get(user['id']);
    if (!pubwebsocket) {
        showPubHistory();
        pubwebsocket = new WebSocket(`ws://localhost:8000/chat/public_chat/${user['id']}/${user['username']}`);
        publicWebSockets.set(user['id'], pubwebsocket);
        pubwebsocket.onmessage = function (e) {
            handleIncomingMessage(e.data)
        }
    }
    return pubwebsocket
}

// Повідомлення з приватного websocket
function handleIncomingMessage(message) {

    const selectedUserElement = document.querySelector('.info.selected_user');
    let active_friendname_chat, active_friendname_id
    let data = JSON.parse(message)

    if (data.type == 'update_status') {
        let user = document.querySelectorAll(`[data-user-id="${data.user_id}"]`)
        user.forEach(function (el) {
            let element = el.nextElementSibling
            if (data.online) {
                if (element.classList.contains('off')) {
                    element.classList.remove('off')
                    element.classList.add('on')
                    element.innerHTML = 'онлайн'
                }
            } else {
                if (!element.classList.contains('off')) {
                    element.classList.remove('on')
                    element.classList.add('off')
                    element.innerHTML = get_date()
                }
            }
        })
        return;
    }
    if (data.type == 'public') {
        handlePublickIncomingMessage(data)
        return;
    }

    if (selectedUserElement) {
        active_friendname_chat = selectedUserElement.firstElementChild.getAttribute('data-user-name');
        active_friendname_id = selectedUserElement.firstElementChild.getAttribute('data-user-id');
    }

    // Якщо id sender or receiver в active_friendname_id - тоді показуємо повідомлення
    if (active_friendname_id == data.user || data.user == user['id']) {
        let isFriendMessage = data.user != user['id'];
        let messageSender = isFriendMessage ? active_friendname_chat : 'Ви';
        let messageClass = isFriendMessage ? 'friend-with-a-SVAGina' : 'i';
        let messageHTML = `<li class="${messageClass}"><div class="head"><span class="name">${messageSender}</span></div><div class="message">${data.message}</div></li>`;
        messageHistory.insertAdjacentHTML('beforeend', messageHTML);
        messageHistory.scrollTop = messageHistory.scrollHeight;
    } else {
        add_count_noti(data.user, type = 'private')
    }
}

// Надсилання повідомлення до загального чату
function sendMessagePub() {
    const messageText = pubtextarea.value;
    if (messageText.trim().length >= 1) {
        const sendpubWebSocket = connetcToPubChat();
        sendpubWebSocket.send(messageText);
    }
    pubtextarea.value = '';
}

// Текст повідомлення загального чату
pubtextarea.addEventListener('keydown', function (event) {
    if (event.key === 'Enter' && event.shiftKey) {
        event.preventDefault()
        this.value += '\n';
    } else if (event.key === 'Enter') {
        event.preventDefault()
        sendMessagePub()
    }
})

// Повідомлення для загального чату
function handlePublickIncomingMessage(message) {

    let isFriendMessage = message.user != null && message.user == user['username'];
    let messageSender = isFriendMessage ? 'Ви' : message.user;
    let messageClass = isFriendMessage ? 'pub_msg_self' : 'pub_msg';
    let messageTextClass = isFriendMessage ? 'message message-personal new' : 'message new';
    let messageHTML = `<div class='${messageClass}'><div class='head_pub'>${messageSender}</div><div class='${messageTextClass}'>${message.message}</div></div>`;
    PublicmessageHistory.insertAdjacentHTML('beforeend', messageHTML);
    PublicmessageHistory.scrollTop = PublicmessageHistory.scrollHeight;
}
