const searchResultsContainer = document.getElementById('searchResults');
const messageHistory = document.querySelector('.messages');
const responseDiv = document.querySelector('.response_search');
// notification
const friend_noti_btn = document.getElementById('radio-3')
const Chat_noti_btn = document.getElementById('radio-2')
// online / offline
document.addEventListener('DOMContentLoaded', connetcToPubChat);
document.addEventListener('DOMContentLoaded', clickOnUser(0));
// private chat
const sendButton = document.querySelector('.write-form .send');
sendButton.addEventListener('click', sendMessage);
const textarea = document.getElementById('texxt');
// public chat
document.getElementById('public_chat').addEventListener('submit', sendMessage);
// search
const searcharea = document.getElementById('search_chat_req');
searcharea.addEventListener('submit', getSearch);
const searchbutton = document.querySelector('.search input[type="submit"]')
searchbutton.addEventListener('click', getSearch);
// btn
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



textarea.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});


function sendMessage() {
    const messageText = textarea.value;
    if (!messageText.trim()) {
        return
    };


    const user_message = `<li class="i"><div class="head"><span class="name"> new message</span></div><div class="message">${messageText}</div></li>`;

    messageHistory.insertAdjacentHTML('beforeend', user_message);
    messageHistory.scrollTop = messageHistory.scrollHeight;
    textarea.value = '';
}


searcharea.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        getSearch(event);
    }
});


async function getSearch(e) {
    e.preventDefault()
    let input = searcharea.value;

    if (input.length >= 2) {

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

                // Очищаємо контейнер перед додаванням нових результатів
                searchResultsContainer.innerHTML = '';

                createSerachResults(responseData)
                clickOnUser(1)

            } else {
                const errorData = await response.json();
                console.log(errorData);
                console.log('помилка');
            }
        } catch (error) {
            console.error('Помилка:', error);
        }
    } else {
        // Очищаємо контейнер перед додаванням нових результатів
        searchResultsContainer.innerHTML = '';
    }
}


// Додання нових данних з пошуку 
function clickOnUser(option) {
    // option:
    // 0 - show friend chat / remove from friend btn
    // 1 - show btn send friend request
    // 2 - accept / declain friend request
    let user = document.querySelectorAll('.info')


    user.forEach(function (element) {
        element.addEventListener('click', function (event) {
            let target = event.target;
            // console.log(option)
            // console.log(target)
            let user_id;
            let selectedElement = target.closest('.info');
            if (target.classList.contains('status')) {
                user_id = target.previousElementSibling.attributes.getNamedItem('data-user-id').value
            } else if (target.classList.contains('info')) {
                user_id = target.firstElementChild.attributes.getNamedItem('data-user-id').value
            } else {
                user_id = target.attributes.getNamedItem('data-user-id').value;
            }

            if (!selectedElement.classList.contains('selected_user')) {
                let previousSelectedUser = document.querySelector('.info.selected_user');
                if (previousSelectedUser) {
                    previousSelectedUser.classList.remove('selected_user');
                }
                selectedElement.classList.add('selected_user');
                fetchChatHistory(user_id, option)

            }
        });
    });
}


async function fetchChatHistory(userId, option) {
    // console.log(userId)
    if (!responseDiv.classList.contains('hidden')) {
        responseDiv.classList.add('hidden');
    }
    try {
        let response = await fetch(`/chat/get_history_chat/${userId}`, {
            method: 'GET',
        });
        const data = await response.json();
        const user = document.querySelector(`div[data-user-id="${userId}"]`);


        user_data = {
            id: user.dataset.userId,
            username: user.dataset.userName,
            online: user.dataset.userOnline,
            last_seen: user.dataset.userLast_seen,
            is_friend: user.dataset.userIsFriend,
            is_send_req: user.dataset.userSendReq
        }
        messageHistory.innerHTML = '';


        // По дефолту ховаємо кнопки "add to friend" та "accept / declain"
        if (!label_send_friend.classList.contains('hidden')) {
            label_send_friend.classList.add('hidden')
        }
        if (!label_acc_dec_friend.classList.contains('hidden')) {
            label_acc_dec_friend.classList.add('hidden')
        }
        if (!label_delete_friend.classList.contains('hidden')) {
            label_delete_friend.classList.add('hidden')
        }
        // console.log(user_data)
        // console.log(option)
        // console.log(user_data['is_friend'])
        // console.log(label_delete_friend)
        if (option == 0) {
            if (label_delete_friend.classList.contains('hidden')) {
                label_delete_friend.classList.remove('hidden');
                label_delete_friend.lastElementChild.value = user_data['username']
            }
        }
        else if (option == 1) {
            if (label_delete_friend.classList.contains('hidden') && user_data['is_friend'] == 'true') {
                label_delete_friend.classList.remove('hidden');
                label_delete_friend.lastElementChild.value = user_data['username']
            }
            else if (label_send_friend.classList.contains('hidden') && user_data['is_send_req'] == 'false') {
                label_send_friend.classList.remove('hidden');
                label_send_friend.lastElementChild.value = user_data['username']
            } else if (user_data['is_send_req'] == 'true') {
                if (label_acc_dec_friend.classList.contains('hidden')) {
                    label_acc_dec_friend.classList.remove('hidden');
                    label_acc_dec_friend.children[1].value = user_data['username']
                    label_acc_dec_friend.children[2].value = user_data['username']
                }
            }
        }
        else if (option == 2) {
            if (label_acc_dec_friend.classList.contains('hidden') && user_data['is_send_req'] == 'true') {
                label_acc_dec_friend.classList.remove('hidden');
                label_acc_dec_friend.children[1].value = user_data['username']
                label_acc_dec_friend.children[2].value = user_data['username']
            }
        }

        if (!data == null) {
            console.log(data);
        } else {
            document.querySelector('.top .info .name').textContent = user_data['username']
            let main_status = document.querySelector('.top .info .count div');

            main_status.className = user_data['online'] == 'true' ? 'status on' : 'status off';
            main_status.textContent = user_data['online'] == 'true' ? 'онлайн' : user_data['last_seen'];

            messageHistory.innerHTML = '<li class="empty-chat">Історія чату відсутня</li>';
        }
    } catch (error) {
        console.log('error', error)
    }
}


let friendRequestClicked = false;

// Блокуемо відправку запиту на 2 секудни
friend_noti_btn.addEventListener('click', event => {
    if (!friendRequestClicked) {
        showFriendRequest();
        friendRequestClicked = true;
        setTimeout(() => {
            friendRequestClicked = false;
        }, 2000);
    }
});


// Запити додати в друзі
async function showFriendRequest() {

    try {
        let response = await fetch('/noti/friend_req', {
            method: 'GET',
        });

        if (response.status == 200) {
            const data = await response.json()
            // Очищаємо контейнер перед додаванням нових результатів
            searchResultsContainer.innerHTML = '';
            createSerachResults(data);
            clickOnUser(2)

        }
    } catch (error) {
        ''
    }

}


// Результат пошуку юзерів
function createSerachResults(responseData) {
    responseData.forEach(function (result) {
        let li = document.createElement('li');
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
        divInfo.appendChild(divStatus);

        li.appendChild(divInfo);
        searchResultsContainer.appendChild(li);
    })
}


function sendPubMessage(e) {
    e.preventDefault();
    console.log(e.target)

    const message = document.getElementById('public_message')
    console.log(message)
}


function connetcToPubChat() {
    let user_id = document.getElementById('user_info').textContent
    const websocket = new WebSocket(`ws://localhost:8000/chat/public_chat?user_id=${user_id}`)
}


async function sendFriendReq(e) {
    let friend_username = e.target.value
    try {
        let response = await fetch(`/user/add_friend/${friend_username}`, {
            method: 'GET',
        })
        const data = await response.json();
        showResponse(response.status, data)
    } catch (error) {
        console.log('error', error)
    }
}


async function acceptFriendReq(e) {
    let friend_username = e.target.value
    try {
        let response = await fetch(`/user/accept_friend/${friend_username}`, {
            method: 'GET',
        })
        const data = await response.json();
        showResponse(response.status, data)
    } catch (error) {
        console.log('error', error)
    }
}


async function declainFriendReq(e) {
    let friend_username = e.target.value
    try {
        let response = await fetch(`/user/declain_friend/${friend_username}`, {
            method: 'GET',
        })
        const data = await response.json();
        showResponse(response.status, data, option = 'dec')

    } catch (error) {
        console.log('error', error)
    }
}


async function removeFriend(e) {
    let friend_username = e.target.value
    try {
        let response = await fetch(`/user/del_friend/${friend_username}`, {
            method: 'DELETE',
        })
        const data = await response.json();
        showResponse(response.status, data, oprion = 'del')
    } catch (error) {
        console.log('error', error)
    }
}


function showResponse(status, data, option = null) {
    let okMessageSpan = responseDiv.querySelector('.ok_message');
    let errorMessageSpan = responseDiv.querySelector('.error_message');
    responseDiv.classList.remove('hidden');
    if (status == 200) {
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
// /// document.getElementById("chatbox").contentWindow.scrollByPages(1);