function CreateIframeModal(srcdoc, title = "", timeout = 0, options = {}) {
    // Проверяем, является ли srcdoc URL или HTML
    const isUrl = validateUrl(srcdoc);
    const isHtml = /<\/?[a-z][\s\S]*>/i.test(srcdoc);
    
    // Генерируем уникальный ID для iframe
    const iframeId = generateId(16);
    
    // Опции по умолчанию
    const defaultOptions = {
        width: '90%',
        maxWidth: '1200px',
        height: '90vh',
        closeOnBackgroundClick: true,
        showPrintButton: true,
        showCloseButton: true,
        modalClass: '',
        ...options
    };
    
    setTimeout(() => {
        // Удаляем предыдущие модальные окна iframe
        const existingModals = document.querySelectorAll('.modal-iframe-container');
        existingModals.forEach(modal => modal.remove());
        
        // Создаем структуру модального окна
        const modalHtml = `
            <div class="modal-iframe-container fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 backdrop-blur-sm">
                <div class="modal-iframe-wrapper bg-white rounded-3xl shadow-2xl overflow-hidden ${defaultOptions.modalClass}"
                     style="width: ${defaultOptions.width}; max-width: ${defaultOptions.maxWidth}; height: ${defaultOptions.height};">
                    
                    <!-- Заголовок модального окна -->
                    <div class="modal-header flex justify-between items-center p-6 border-b border-gray-200 bg-gray-50">
                        <h3 class="modal-title text-2xl font-bold text-gray-900 truncate">
                            ${title || 'Загрузка...'}
                        </h3>
                        <div class="modal-actions flex items-center gap-3">
                            ${defaultOptions.showPrintButton ? `
                                <button class="modal-print-btn flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-full hover:bg-primary-dark transition-all text-sm font-medium">
                                    <i class="fas fa-print"></i>
                                    <span class="hidden sm:inline">Печать</span>
                                </button>
                            ` : ''}
                            
                            ${defaultOptions.showCloseButton ? `
                                <button class="modal-close-btn text-gray-500 hover:text-gray-700 text-2xl transition-all">
                                    <i class="fas fa-times"></i>
                                </button>
                            ` : ''}
                        </div>
                    </div>
                    
                    <!-- Контентная область -->
                    <div class="modal-content-wrapper h-[calc(100%-80px)] overflow-hidden">
                        <div class="modal-content h-full w-full">
                            <!-- iframe или HTML контент будет вставлен сюда -->
                        </div>
                    </div>
                    
                    <!-- Индикатор загрузки -->
                    <div class="modal-loader absolute inset-0 flex items-center justify-center bg-white bg-opacity-90 hidden">
                        <div class="loader-spinner w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                    </div>
                </div>
            </div>
        `;
        
        // Вставляем модальное окно в DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modalContainer = document.querySelector('.modal-iframe-container:last-child');
        const modalContent = modalContainer.querySelector('.modal-content');
        const modalLoader = modalContainer.querySelector('.modal-loader');
        
        // Показываем индикатор загрузки
        modalLoader.classList.remove('hidden');
        
        // Обработчики событий для модального окна
        const setupModalEvents = () => {
            // Кнопка закрытия
            const closeBtn = modalContainer.querySelector('.modal-close-btn');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => closeIframeModal(modalContainer));
            }
            
            // Кнопка печати
            const printBtn = modalContainer.querySelector('.modal-print-btn');
            if (printBtn) {
                printBtn.addEventListener('click', () => {
                    if (isUrl) {
                        // Для iframe пытаемся печатать содержимое iframe
                        const iframe = modalContent.querySelector('iframe');
                        if (iframe && iframe.contentWindow) {
                            iframe.contentWindow.print();
                        }
                    } else {
                        // Для HTML контента печатаем текущее окно
                        window.print();
                    }
                });
            }
            
            // Закрытие по клику на фон
            if (defaultOptions.closeOnBackgroundClick) {
                modalContainer.addEventListener('click', (e) => {
                    if (e.target === modalContainer) {
                        closeIframeModal(modalContainer);
                    }
                });
            }
            
            // Закрытие по клавише ESC
            const handleEscape = (e) => {
                if (e.key === 'Escape') {
                    closeIframeModal(modalContainer);
                }
            };
            document.addEventListener('keydown', handleEscape);
            
            // Сохраняем обработчик для последующего удаления
            modalContainer.dataset.escapeHandler = 'handleEscape';
        };
        
        // Загружаем контент
        if (isUrl) {
            // Если это URL, создаем iframe
            const iframe = document.createElement('iframe');
            iframe.id = `iframe-${iframeId}`;
            iframe.name = `modalFrame-${iframeId}`;
            iframe.className = 'w-full h-full border-0';
            iframe.src = srcdoc;
            iframe.title = title;
            iframe.allow = 'fullscreen';
            
            // Обработчик загрузки iframe
            iframe.onload = () => {
                modalLoader.classList.add('hidden');
                
                // Обновляем заголовок, если он был указан в iframe
                try {
                    const iframeTitle = iframe.contentDocument?.title;
                    if (iframeTitle && iframeTitle !== title) {
                        const titleElement = modalContainer.querySelector('.modal-title');
                        if (titleElement) {
                            titleElement.textContent = iframeTitle;
                        }
                    }
                } catch (e) {
                    // Игнорируем ошибки CORS
                }
            };
            
            iframe.onerror = () => {
                modalLoader.classList.add('hidden');
                modalContent.innerHTML = `
                    <div class="h-full flex flex-col items-center justify-center p-8 text-center">
                        <i class="fas fa-exclamation-triangle text-red-500 text-5xl mb-4"></i>
                        <h4 class="text-xl font-bold text-gray-900 mb-2">Ошибка загрузки</h4>
                        <p class="text-gray-600 mb-4">Не удалось загрузить содержимое по указанному адресу.</p>
                        <p class="text-sm text-gray-500">Проверьте URL или попробуйте позже.</p>
                    </div>
                `;
            };
            
            modalContent.appendChild(iframe);
            
        } else if (isHtml) {
            // Если это HTML, вставляем напрямую
            modalContent.innerHTML = srcdoc;
            
            // Добавляем базовые стили для HTML контента
            const style = document.createElement('style');
            style.textContent = `
                .modal-content > * {
                    max-height: 100%;
                    overflow-y: auto;
                    padding: 1.5rem;
                }
                .modal-content > *::-webkit-scrollbar {
                    width: 8px;
                }
                .modal-content > *::-webkit-scrollbar-track {
                    background: #f1f1f1;
                    border-radius: 4px;
                }
                .modal-content > *::-webkit-scrollbar-thumb {
                    background: #888;
                    border-radius: 4px;
                }
                .modal-content > *::-webkit-scrollbar-thumb:hover {
                    background: #555;
                }
            `;
            modalContent.appendChild(style);
            
            // Скрываем индикатор загрузки
            setTimeout(() => {
                modalLoader.classList.add('hidden');
            }, 100);
            
        } else {
            // Если это простой текст
            modalContent.innerHTML = `
                <div class="h-full flex items-center justify-center p-8">
                    <div class="text-center">
                        <p class="text-gray-700 text-lg">${srcdoc}</p>
                    </div>
                </div>
            `;
            modalLoader.classList.add('hidden');
        }
        
        // Настраиваем события после добавления контента
        setTimeout(setupModalEvents, 100);
        
        // Блокируем прокрутку body
        document.body.style.overflow = 'hidden';
        
        // Добавляем анимацию появления
        setTimeout(() => {
            modalContainer.style.opacity = '0';
            modalContainer.style.transform = 'scale(0.95)';
            modalContainer.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
            
            requestAnimationFrame(() => {
                modalContainer.style.opacity = '1';
                modalContainer.style.transform = 'scale(1)';
            });
        }, 10);
        
    }, timeout);
    
    // Возвращаем ID iframe если это был вызов из события
    return iframeId;
}

/**
 * Закрывает модальное окно iframe
 * @param {HTMLElement} modalContainer - Контейнер модального окна
 */
function closeIframeModal(modalContainer) {
    if (!modalContainer) return;
    
    // Удаляем обработчик ESC
    const escapeHandler = modalContainer.dataset.escapeHandler;
    if (escapeHandler) {
        document.removeEventListener('keydown', window[escapeHandler]);
    }
    
    // Анимация исчезновения
    modalContainer.style.opacity = '0';
    modalContainer.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
        modalContainer.remove();
        
        // Восстанавливаем прокрутку body если больше нет модальных окон
        if (!document.querySelector('.modal-iframe-container')) {
            document.body.style.overflow = '';
        }
    }, 200);
}

/**
 * Вспомогательная функция для проверки URL
 * @param {string} string - Строка для проверки
 * @returns {boolean} - true если это валидный URL
 */
function validateUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

/**
 * Генератор случайного ID
 * @param {number} length - Длина ID
 * @returns {string} - Сгенерированный ID
 */
function generateId(length) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}