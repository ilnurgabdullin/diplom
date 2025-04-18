async function fetchStorage() {
        try {
            let response = await fetch('/profile/get_my_storages', {
                method: 'GET',
                headers: {'Content-Type': 'application/json'},
                credentials: 'include' 
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            let data = await response.json();
            let list = document.getElementById('storages-list');
            
            if (!list) {
                console.error("Ошибка: Элемент #storages-list не найден");
                return;
            }

            list.innerHTML = ""; 
            
            data.storages.forEach((storage, index) => {
                let li = document.createElement('li');
                li.className = "storage-item";
                
                let accordionId1 = `accordion-${index}-1`;
                let accordionId2 = `accordion-${index}-2`;
                let collapseId1 = `collapse-${index}-1`;
                let collapseId2 = `collapse-${index}-2`;
                
                li.innerHTML = `
                <div class="my-3 p-3 bg-body rounded shadow-sm">
                    <h6 class="border-bottom pb-2 mb-0">${storage.name}</h6>
                    
                    <!-- Первый аккордеон -->
                    <div class="accordion" id="${accordionId1}">
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                                    data-bs-target="#${collapseId1}" aria-expanded="false" aria-controls="${collapseId1}">
                                    Информация о складе
                                </button>
                            </h2>
                            <div id="${collapseId1}" class="accordion-collapse collapse" data-bs-parent="#${accordionId1}">
                                <div class="accordion-body first-accordion-content">
                                    <div class="text-center text-muted py-2">
                                        <div class="spinner-border spinner-border-sm" role="status">
                                            <span class="visually-hidden">Загрузка...</span>
                                        </div>
                                        Загрузка данных...
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Второй аккордеон -->
                    <div class="accordion mt-3" id="${accordionId2}">
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                                    data-bs-target="#${collapseId2}" aria-expanded="false" aria-controls="${collapseId2}">
                                    Управление складом
                                </button>
                            </h2>
                            <div id="${collapseId2}" class="accordion-collapse collapse" data-bs-parent="#${accordionId2}">
                                <div class="accordion-body">
                                    <!-- Форма создания ячейки -->
                                    <div class="card-body">
                                        <form class="create-cell-form" data-storage-id="${storage.id}">
                                            <div class="mb-3">
                                                <label for="cell-name-${index}" class="form-label">Код ячейки</label>
                                                <input type="text" class="form-control" id="cell-name-${index}" name="name" required>
                                            </div>
                                            <div class="mb-3">
                                                <label class="form-label">Склад</label>
                                                <input type="text" class="form-control" value="${storage.name}" readonly>
                                                <input type="hidden" name="wrh" value="${storage.id}">
                                            </div>
                                            <div class="mb-3">
                                                <label for="cell-description-${index}" class="form-label">Описание</label>
                                                <textarea class="form-control" id="cell-description-${index}" name="address" rows="2"></textarea>
                                            </div>
                                            <button type="submit" class="btn btn-primary">Создать ячейку</button>
                                            <div class="response-message mt-3"></div>
                                        </form>
                                    </div>
                                    
                                    <hr>
                                    
                                    <!-- Дополнительные действия -->
                                    <div class="form-container">
                                        <h6 class="mb-3">Действия со складом</h6>
                                        <form class="storage-actions-form" data-storage-id="${storage.id}">
                                            <div class="mb-3">
                                                <div class="form-check">
                                                    <input class="form-check-input" type="checkbox" id="notifications-${index}">
                                                    <label class="form-check-label" for="notifications-${index}">
                                                        Получать уведомления
                                                    </label>
                                                </div>
                                            </div>
                                            <div class="d-flex gap-2">
                                                <button type="button" class="btn btn-outline-secondary btn-sm storage-archive">
                                                    Архивировать
                                                </button>
                                                <button type="button" class="btn btn-outline-danger btn-sm storage-delete">
                                                    Удалить
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`;
                
                list.appendChild(li);
                
                fillFirstAccordion(li.querySelector('.first-accordion-content'), storage);
                setupFormHandlers(li, storage.id);
            });
        } catch (error) {
            console.error("Ошибка загрузки данных:", error);
            let list = document.getElementById('storages-list');
            if (list) {
                list.innerHTML = `
                    <div class="alert alert-danger" role="alert">
                        Произошла ошибка при загрузке данных. Пожалуйста, попробуйте позже.
                    </div>`;
            }
        }
    }

    async function fillFirstAccordion(container, storage) {
        if (!container) return;
        
        try {
            let response = await fetch(`/profile/get_cells/?wrh=${storage.id}`, {
                method: 'GET',
                headers: {'Content-Type': 'application/json'},
                credentials: 'include' 
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            let cellsData = await response.json();
            container.innerHTML = '';
            
            // Загружаем список всех товаров для выпадающего списка
            let allProducts = await fetchProducts();
            
            cellsData.cells.forEach(cell => {
                const productsHtml = cell.products.length > 0 
                    ? `<div class="mt-3">
                          <h6 class="text-muted small">Товары в ячейке:</h6>
                          <div class="list-group list-group-flush">
                              ${cell.products.map(product => `
                                  <div class="list-group-item py-2">
                                      <div class="d-flex justify-content-between align-items-center">
                                          <div>
                                              <strong>${product.name}</strong>
                                              <div class="text-muted small">Арт: ${product.article}</div>
                                          </div>
                                          <div>
                                              <span class="badge bg-primary rounded-pill">${product.quantity} шт.</span>
                                          </div>
                                      </div>
                                  </div>
                              `).join('')}
                          </div>
                       </div>`
                    : '<div class="text-muted mt-2 small">В ячейке нет товаров</div>';
    
                const itemHtml = `
                    <div class="d-flex text-body-secondary pt-3">
                        <svg class="bd-placeholder-img flex-shrink-0 me-2 rounded" width="32" height="32" 
                            xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Placeholder: 32x32" 
                            preserveAspectRatio="xMidYMid slice" focusable="false">
                            <title>${cell.cell_code}</title>
                            <rect width="100%" height="100%" fill="#${Array.from(cell.cell_code).reduce((hash, char) => {
                                const updated = (hash << 5) - hash + char.charCodeAt(0);
                                return updated & updated;
                            }, 5381).toString(16).padStart(6, '0').slice(-6)}"></rect>
                            <text x="40%" y="50%" fill="#ffffff" dy=".3em" font-size="12">${cell.cell_code.substring(0, 1)}</text>
                        </svg>
                        <div class="pb-3 mb-0 small lh-sm border-bottom w-100">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <strong class="d-block text-gray-dark">${cell.cell_code}</strong>
                                    ${cell.description || ''}
                                </div>
                                <div class="cell-actions">
                                    <button type="button"  
                                        class="delete-cell-btn"
                                        data-cell-id="${cell.id}" 
                                        data-storage-id="${storage.id}">
                                        Удалить ячейку
                                    </button>
                                    <button class="btn btn-sm btn-outline-primary add-product-btn" type="button" 
                                        data-bs-toggle="modal" data-bs-target="#addProductModal"
                                        data-cell-id="${cell.id}" 
                                        data-storage-id="${storage.id}">
                                        Добавить товар
                                    </button>
                                </div>
                            </div>
                            ${productsHtml}
                        </div>
                    </div>`;
                container.insertAdjacentHTML('beforeend', itemHtml);
            });
    
            // Создаем модальное окно для добавления товара (если ещё не создано)
            if (!document.getElementById('addProductModal')) {
                const modalHtml = `
                    <div class="modal fade" id="addProductModal" tabindex="-1" aria-labelledby="addProductModalLabel" aria-hidden="true">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="addProductModalLabel">Добавить товар в ячейку</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <form id="addProductForm">
                                        <input type="hidden" id="modalCellId" name="cell_id">
                                        <input type="hidden" id="modalStorageId" name="storage_id">
                                        <div class="mb-3">
                                            <label for="productSelect" class="form-label">Выберите товар</label>
                                            <select class="form-select" id="productSelect" required>
                                                <option value="" selected disabled>Выберите товар</option>
                                                ${allProducts.map(product => `
                                                    <option value="${product.barcode}">${product.name}</option>
                                                `).join('')}
                                            </select>
                                        </div>
                                        <div class="mb-3">
                                            <label for="productQuantity" class="form-label">Количество</label>
                                            <input type="number" class="form-control" id="productQuantity" value="1" min="1" required>
                                        </div>
                                    </form>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
                                    <button type="button" class="btn btn-primary" id="submitAddProduct">Добавить</button>
                                </div>
                            </div>
                        </div>
                    </div>`;
                document.body.insertAdjacentHTML('beforeend', modalHtml);
    
                // Обработчики для модального окна
                document.querySelectorAll('.add-product-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        document.getElementById('modalCellId').value = this.getAttribute('data-cell-id');
                        document.getElementById('modalStorageId').value = this.getAttribute('data-storage-id');
                    });
                });
                document.querySelectorAll('.delete-cell-btn').forEach(btn => {
                    btn.addEventListener('click', async function() {
                        try {
                            const response = await fetch(`/profile/delete/${this.getAttribute('data-cell-id')}/`, {
                              method: 'DELETE',
                              headers: {
                                'Content-Type': 'application/json',
                              },
                            });
                        
                            if (!response.ok) {
                              throw new Error('Ошибка при удалении');
                            }
                        
                            const data = await response.json();
                            console.log('Успешно удалено:', data);
                            return data;
                          } catch (error) {
                            console.error('Ошибка:', error);
                            throw error;
                          }
                    });
                });
    
                document.getElementById('submitAddProduct').addEventListener('click', async function() {
                    const cellId = document.getElementById('modalCellId').value;
                    const storageId = document.getElementById('modalStorageId').value;
                    const barcode = document.getElementById('productSelect').value;
                    const quantity = document.getElementById('productQuantity').value;
                    
                    if (!barcode) {
                        alert('Пожалуйста, выберите товар');
                        return;
                    }
    
                    try {
                        const response = await fetch('/profile/add_product_to_cell/', {
                            method: 'POST',
                            credentials: 'include',
                            headers: {
                                // 'X-CSRFToken': getCookie('csrftoken'),
                                'Accept': 'application/json',
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                wrh_id: storageId,
                                cell_id: cellId,
                                barcode: barcode,
                                quantity: quantity
                            })
                        });
    
                        if (!response.ok) {
                            const error = await response.json();
                            throw new Error(error.error || 'Неизвестная ошибка');
                        }
    
                        const data = await response.json();
                        alert(`Товар успешно добавлен в ячейку!`);
                        
                        // Закрываем модальное окно и обновляем данные
                        const modal = bootstrap.Modal.getInstance(document.getElementById('addProductModal'));
                        modal.hide();
                        fetchStorage(); // Обновляем весь список
                        
                    } catch (error) {
                        console.error('Ошибка:', error);
                        alert(`Ошибка: ${error.message}`);
                    }
                });
            }
            
        } catch (error) {
            console.error("Ошибка загрузки данных ячеек:", error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    Ошибка загрузки данных ячеек. Пожалуйста, попробуйте позже.
                </div>`;
        }
    }

    
async function fetchProducts() {
    try {
        const response = await fetch('/profile/get_goods/', {
            method: 'GET',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        // Собираем все товары из всех поставщиков в один массив
        let allProducts = [];
        console.log(data);
        data.all_goods.forEach(supplier => {
            supplier.goods.forEach(product => {
                console.log(product);
                allProducts.push({
                    name: `${supplier.mark}-${product.name}(${product.barc})`,
                    barcode: product.barc,
                    supplier: supplier.mark
                });
            });
        });
        return allProducts;
    } catch (error) {
        console.error("Ошибка загрузки товаров:", error);
        return [];
    }
}


function setupFormHandlers(container, storageId) {
        // Обработчик формы создания ячейки
        const createCellForm = container.querySelector('.create-cell-form');
        if (createCellForm) {
            createCellForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                const responseMessage = this.querySelector('.response-message');
                
                try {
                    const response = await fetch('/profile/create_cell/', {
                        method: 'POST',
                        credentials: 'include',
                        headers: {
                            // 'X-CSRFToken': getCookie('csrftoken'),
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            name: formData.get('name'),
                            wrh: formData.get('wrh'),
                            address: formData.get('address')
                        })
                    });

                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.error || 'Неизвестная ошибка');
                    }

                    const data = await response.json();
                    responseMessage.innerHTML = `
                        <div class="alert alert-success">
                            Ячейка успешно создана! ID: ${data.id}
                        </div>
                    `;
                    this.reset();
                } catch (error) {
                    console.error('Ошибка:', error);
                    responseMessage.innerHTML = `
                        <div class="alert alert-danger">
                            Ошибка: ${error.message}
                        </div>
                    `;
                }
            });
        }
        
        // Обработчики кнопок действий
        const archiveBtn = container.querySelector('.storage-archive');
        if (archiveBtn) {
            archiveBtn.addEventListener('click', function() {
                console.log(`Архивирование склада ${storageId}`);
                alert(`Склад ${storageId} будет архивирован`);
            });
        }
        
        const deleteBtn = container.querySelector('.storage-delete');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function() {
                if (confirm(`Вы уверены, что хотите удалить склад ${storageId}?`)) {
                    console.log(`Удаление склада ${storageId}`);
                    alert(`Склад ${storageId} будет удален`);
                }
            });
        }
    }
    
document.addEventListener("DOMContentLoaded", function() {
    fetchStorage();
});