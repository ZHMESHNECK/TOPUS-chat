const textarea = document.getElementById('texxt');
textarea.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});


const sendButton = document.querySelector('.write-form .send');
sendButton.addEventListener('click', sendMessage);

function sendMessage() {
    const textarea = document.getElementById('texxt');
    const messageText = textarea.value;
    if (!messageText.trim()) {
        return
    };

    const messageHistory = document.querySelector('.messages');
    const user_message = `<li class="i"><div class="head"><span class="name"> new message</span></div><div class="message">${messageText}</div></li>`;

    messageHistory.insertAdjacentHTML('beforeend', user_message);
    messageHistory.scrollTop = messageHistory.scrollHeight;
    textarea.value = '';
}

const searcharea = document.getElementById('search_chat_req');
searcharea.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        getSearch(event);
    }
});

const searchbutton = document.querySelector('.search input[type="submit"]')
searchbutton.addEventListener('click', getSearch);

searcharea.addEventListener('submit', getSearch);
async function getSearch(e) {
    e.preventDefault()
    let input = searcharea.value;

    if (input.length >= 2) {

        const data = {
            "request": input
        }

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.status == 200) {
                const responseData = await response.json();
                let searchResultsContainer = document.getElementById("searchResults");
                // Очищаємо контейнер перед додаванням нових результатів
                searchResultsContainer.innerHTML = "";

                responseData.forEach(function (result) {
                    let li = document.createElement('li');
                    let divInfo = document.createElement("div");
                    divInfo.className = 'info';

                    let divUser = document.createElement("div");
                    divUser.className = "user";
                    divUser.id = result.id
                    divUser.textContent = result.username;
                    divUser.dataset.userId = result.id;
                    divUser.dataset.userName = result.username;
                    divUser.dataset.userOnline = result.online;
                    divUser.dataset.userLast_seen = result.last_seen;
                    divUser.dataset.userIsFriend = result.is_friend;
                    divInfo.appendChild(divUser);

                    let divStatus = document.createElement("div");
                    divStatus.className = result.online ? "status on" : "status off";
                    divStatus.textContent = result.online ? "онлайн" : result.last_seen;
                    divInfo.appendChild(divStatus);

                    li.appendChild(divInfo);
                    searchResultsContainer.appendChild(li);
                }
                )
                clickOnUser()

            } else {
                const errorData = await response.json();
                console.log(errorData);
                console.log('помилка');
            }
        } catch (error) {
            console.error('Помилка:', error);
        }
    } else {
        let searchResultsContainer = document.getElementById("searchResults");
        // Очищаємо контейнер перед додаванням нових результатів
        searchResultsContainer.innerHTML = "";
    }
}


function clickOnUser() {
    let user = document.querySelectorAll('.info')

    user.forEach(function (element) {
        element.addEventListener('click', function (event) {
            let target = event.target;
            let user_id;
            if (target.classList.contains('status')) {
                user_id = target.previousElementSibling.id
            } else if (target.classList.contains('info')) {
                user_id = target.firstChild.id
            } else {
                user_id = event.target.id
            }
            fetchChatHistory(user_id)
        });
    });
}


async function fetchChatHistory(userId) {

    let errorDiv = document.querySelector('.response_search');
    if (!errorDiv.classList.contains('hidden')) {
        errorDiv.classList.add('hidden');
    }
    try {
        const response = await fetch(`/chat/get_history_chat/${userId}`, {
            method: 'GET',
        });
        const data = await response.json();
        const user = document.getElementById(userId);
        const label_add_friend = document.querySelector('.friendship')

        user_data = {
            user_id: user.dataset.userId,
            user_username: user.dataset.userName,
            user_online: user.dataset.userOnline,
            user_last_seen: user.dataset.userLast_seen,
            user_is_friend: user.dataset.userIsFriend
        }
        const chatContainer = document.getElementById('chat');
        const messageList = chatContainer.querySelector('.messages');
        messageList.innerHTML = '';

        if (user_data['user_is_friend'] == 'true') {
            label_add_friend.classList.add('hidden');
        } else {
            label_add_friend.classList.remove('hidden');
            label_add_friend.lastElementChild.value = user_data['user_username']
        }

        if (!data == null) {
            console.log(data);
        } else {
            document.querySelector('.top .info .name').textContent = user_data['user_username']
            let main_status = document.querySelector('.top .info .count div');

            main_status.className = user_data['user_online'] == 'true' ? "status on" : "status off";
            main_status.textContent = user_data['user_online'] == 'true' ? "онлайн" : user_data['user_last_seen'];

            messageList.innerHTML = '<li class="empty-chat">Історія чату відсутня</li>';
        }
    } catch (error) {
        console.log('error', error)
    }
}


const btn_add_to_friend = document.querySelector('.add-friend-btn')
btn_add_to_friend.addEventListener('click', (e) => sendFriendReq(e))
async function sendFriendReq(e) {
    let friend_username = e.target.value
    try {
        const response = await fetch(`/user/add_friend/${friend_username}`, {
            method: 'GET',
        })
        let responseDiv = document.querySelector('.response_search');
        const data = await response.json();
        if (response.status == 200) {
            console.log(data)
            let okMessageSpan = responseDiv.querySelector('.ok_message');
            okMessageSpan.textContent = data.content;
            responseDiv.classList.remove('hidden');
            btn_add_to_friend.parentNode.classList.add('hidden');
        } else if (response.status == 400) {
            let errorMessageSpan = responseDiv.querySelector('.error_message');
            errorMessageSpan.textContent = data.detail;
            responseDiv.classList.remove('hidden');
            btn_add_to_friend.parentNode.classList.add('hidden');
        }
    } catch (error) {
        console.log('error', error)
    }
}