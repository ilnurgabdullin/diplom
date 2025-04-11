document.addEventListener('DOMContentLoaded', function() {
    // Получаем контейнер аккордеона
    const accordionContainer = document.getElementById('goods-accordion');
    
    // Загружаем данные о товарах
    loadGoodsData();
    
    function loadGoodsData() {
      accordionContainer.innerHTML = '<div class="loading">Загрузка данных о продавцах...</div>';
      
      fetch('/profile/get_goods/', {
        method: 'GET',
        credentials: 'include', // Для работы с CookieJWTAuthentication
        headers: {
          'Content-Type': 'application/json',
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Ошибка сети');
        }
        return response.json();
      })
      .then(data => {
        renderAccordion(data.all_goods);
      })
      .catch(error => {
        console.error('Ошибка:', error);
        accordionContainer.innerHTML = '<div class="error">Ошибка загрузки данных: ' + error.message + '</div>';
      });
    }
    
    function renderAccordion(goodsData) {
      // Очищаем контейнер
      accordionContainer.innerHTML = '';
      
      if (!goodsData || goodsData.length === 0) {
        accordionContainer.innerHTML = '<div class="loading">Нет данных о продавцах</div>';
        return;
      }
      
      // Создаем элементы аккордеона для каждого продавца
      goodsData.forEach(seller => {
        const accordionItem = document.createElement('div');
        accordionItem.className = 'accordion-item';
        
        // Заголовок аккордеона
        const accordionHeader = document.createElement('div');
        accordionHeader.className = 'accordion-header';
        accordionHeader.textContent = `${seller.name}${seller.mark ? ' (' + seller.mark + ')' : ''}`;
        
        // Содержимое аккордеона
        const accordionContent = document.createElement('div');
        accordionContent.className = 'accordion-content';
        
        // Таблица с товарами
        const productsTable = document.createElement('table');
            productsTable.className = 'products-table';
            productsTable.innerHTML = `
            <thead>
                <tr>
                <th>Штрихкод</th>
                <th>Название</th>
                <th>Действия</th>
                </tr>
            </thead>
            <tbody>
                ${seller.goods && seller.goods.length > 0 
                ? seller.goods.map(good => `
                    <tr data-good-id="${good.barc}">
                    <td>${good.barc || '-'}</td>
                    <td class="editable-name">${good.name || '-'}</td>
                    <td>
                        <button class="edit-btn">✏️</button>
                        <button class="save-btn" style="display:none">💾</button>
                    </td>
                    </tr>
                `).join('')
                : '<tr><td colspan="3">Нет товаров</td></tr>'
                }
  </tbody>
`;

// Добавляем обработчики для редактирования
productsTable.addEventListener('click', async (event) => {
  const editBtn = event.target.closest('.edit-btn');
  const saveBtn = event.target.closest('.save-btn');
  
  if (editBtn) {
    const row = editBtn.closest('tr');
    const nameCell = row.querySelector('.editable-name');
    const currentName = nameCell.textContent;
    
    // Создаем input для редактирования
    nameCell.innerHTML = `<input type="text" value="${currentName}" class="name-edit-input">`;
    
    // Переключаем видимость кнопок
    editBtn.style.display = 'none';
    row.querySelector('.save-btn').style.display = 'inline-block';
  }
  
  if (saveBtn) {
    const row = saveBtn.closest('tr');
    const goodId = row.dataset.goodId;
    const newName = row.querySelector('.name-edit-input').value;
    
    try {
      // Отправляем запрос на обновление через API
      const response = await fetch('/profile/update_good/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          goodId: goodId,
          newName: newName
        })
      });
      
      if (!response.ok) throw new Error('Ошибка обновления');
      
      // Возвращаем обычный текст после успешного обновления
      const nameCell = row.querySelector('.editable-name');
      nameCell.textContent = newName;
      
      // Переключаем кнопки обратно
      saveBtn.style.display = 'none';
      row.querySelector('.edit-btn').style.display = 'inline-block';
      
    } catch (error) {
      console.error('Ошибка при обновлении:', error);
      alert('Не удалось обновить название товара');
    }
  }
});

        
        // Форма для добавления нового товара
        const addForm = document.createElement('div');
        addForm.className = 'add-product-form';
        addForm.innerHTML = `
          <input type="text" placeholder="Баркод" class="barcode-input">
          <input type="text" placeholder="Название товара" class="name-input">
          <button class="add-btn">Добавить</button>
        `;
        
        // Собираем аккордеон
        accordionContent.appendChild(productsTable);
        accordionContent.appendChild(addForm);
        accordionItem.appendChild(accordionHeader);
        accordionItem.appendChild(accordionContent);
        accordionContainer.appendChild(accordionItem);
        
        // Добавляем обработчик клика на заголовок
        accordionHeader.addEventListener('click', function() {
          const isActive = accordionItem.classList.contains('active');
          accordionItem.classList.toggle('active', !isActive);
        });
        
        // Обработчик для кнопки добавления товара
        addForm.querySelector('.add-btn').addEventListener('click', function(event) {
          addProduct(event, seller.sel_id);
        });
      });
      
    }
    
    function addProduct(event, seller) {
      const form = event.target.closest('.add-product-form');
      const barcode = form.querySelector('.barcode-input').value.trim();
      const name = form.querySelector('.name-input').value.trim();
      
      if (!barcode || !name) {
        alert('Пожалуйста, заполните все поля');
        return;
      }
      
      // Здесь можно добавить запрос на добавление товара
      console.log(`Добавление товара для продавца ${seller}:`, { barcode, name });
      try {
                const response =  fetch('/profile/add_good/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 
                        seller_id : seller,
                        name: name,
                        vendorcode : barcode
                     }),
                    credentials: 'include' 
                });
            } catch (error) {
                console.log(error)
            }
      // Очищаем поля после добавления
      form.querySelector('.barcode-input').value = '';
      form.querySelector('.name-input').value = '';
      loadGoodsData();
    }
    
    // Вспомогательная функция для получения CSRF токена
    
  });