const pathSegments = window.location.pathname.split('/').filter(Boolean);
const selectionId = pathSegments[pathSegments.length - 1];
async function fetchData(n) {
    const url = `/profile/fbs_supplies/${selectionId}`;
    console.log(url)
    const resultList = document.getElementById('resultList');
    
    
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Ошибка при загрузке данных');
        }
    
        const data = await response.json();
        resultList.innerHTML = '';
    
        if (data.supplies.length == 0) {
            const li = document.createElement('p');
            li.textContent = 'Нет поставок';
            li.classList.toggle('elem');
            resultList.appendChild(li);
        } else {
            if (n != 0){
                d = data.supplies.slice(0, n)
            } else {
                console.log('нет N')
                d = data.supplies
            }
            d.forEach(item => {
                const li = document.createElement('li');
                li.className = 'list-item';
                
                li.innerHTML = `
                <details>
                <summary>${item.name}   ${item.id}</summary>
                <div class="details-content" data-id="${item.id}">
                <div class="loading-message" id="${item.id}-message">Загрузка данных...</div>
                </div>
                </details>
                `;
                
                const details = li.querySelector('details');
                details.addEventListener('toggle', async (event) => {
                    if (event.target.open) {
                        const loadingMessage = details.querySelector('.loading-message');
                            
                        try {
                            // Ждем ответа от API
                            await getSelectionList(item.id);
                            
                            const loadMess = document.getElementById(`${item.id}-message`);
                            loadMess.innerHTML =`
                            <div><a class="extra-text" target="_blank" href="/profile/stikers/${item.id}">/profile/stikers/${item.id}</a></div>
                            <div><a class="extra-text" target="_blank" href="/profile/supplies/${item.id}">/profile/supplies/${item.id}</a></div>`
                            // После успешной загрузки скрываем сообщение о загрузке
                            // loadingMessage.style.display = 'none';
                            
                        } catch (error) {
                            console.error('Ошибка при загрузке данных:', error);
                            loadingMessage.textContent = 'Ошибка при загрузке данных';
                        }
                    }
                });
                
                resultList.appendChild(li);
            });
        }
    } catch (error) {
        console.error('Ошибка:', error);
        resultList.innerHTML = '<li>Ошибка при загрузке данных</li>';
    }
}
    async function getSelectionList(id) {
        const response = await fetch('/profile/get_podbor_list/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                supply: id,
                seller: selectionId
            }),
            credentials: 'include' 
        });
        
        if (!response.ok) {
            throw new Error('Ошибка при загрузке данных');
        }
        
        // Здесь можно обработать ответ и добавить данные в details
        const data = await response.json();
        // Например, добавить данные в соответствующий details
        // document.querySelector(`.details-content[data-id="${id}"]`).innerHTML += ...
        
        return data;
    }
    document.getElementById('fetchButton').addEventListener('click', ()=>fetchData(0));
        try {
            fetchData(10);
        } catch {
            ;
        }