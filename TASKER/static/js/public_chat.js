// online / offline
document.addEventListener('DOMContentLoaded', connetcToPubChat);
document.addEventListener('DOMContentLoaded', clickOnUser(0));
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
    let pubwebsocket;
    if (publicWebSockets.has(user['id'])) {
        pubwebsocket = publicWebSockets.get(user['id']);
    } else {
        showPubHistory();
        pubwebsocket = new WebSocket(`ws://localhost:8000/chat/public_chat/${user['id']}/${user['username']}`);
        publicWebSockets.set(user['id'], pubwebsocket);
        pubwebsocket.onmessage = function (e) {
            try {
                const jsonData = JSON.parse(e.data);
                if (jsonData.type == 'update_status') {
                    let user = document.querySelectorAll(`[data-user-id="${jsonData.user_id}"]`)
                    user.forEach(function (el) {
                        if (jsonData.online) {
                            if (el.nextElementSibling.classList.contains('off')) {
                                el.nextElementSibling.classList.remove('off')
                                el.nextElementSibling.classList.add('on')
                                el.nextElementSibling.innerHTML = 'онлайн'
                            }
                        } else {
                            if (!el.nextElementSibling.classList.contains('off')) {
                                el.nextElementSibling.classList.remove('on')
                                el.nextElementSibling.classList.add('off')
                                el.nextElementSibling.innerHTML = get_date()
                            }
                        }
                    })
                } else if (jsonData.type == 'public') {
                    handlePublickIncomingMessage(jsonData)
                }

            } catch (error) {
                console.log(error)
            }
        };
    }
    return pubwebsocket;
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
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessagePub();
    }
});

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
