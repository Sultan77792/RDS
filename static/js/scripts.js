// ==========================================================================
// Вспомогательные функции
// ==========================================================================

/**
 * Переключает видимость дополнительных полей в зависимости от состояния чекбоксов.
 */
function toggleFields() {
    const fieldGroups = [
        { checkbox: 'lo_flag', fields: 'lo_fields' },
        { checkbox: 'aps_flag', fields: 'aps_fields' },
        { checkbox: 'kps_flag', fields: 'kps_fields' },
        { checkbox: 'mio_flag', fields: 'mio_fields' },
        { checkbox: 'other_org_flag', fields: 'other_org_fields' }
    ];

    fieldGroups.forEach(({ checkbox, fields }) => {
        try {
            const cb = document.getElementById(checkbox);
            const fg = document.getElementById(fields);
            if (!cb || !fg) {
                console.warn(`Элемент с ID ${checkbox} или ${fields} не найден`);
                return;
            }
            const isChecked = cb.checked;
            fg.style.transition = 'all 0.3s ease-in-out';
            if (isChecked) {
                fg.classList.remove('hidden');
                requestAnimationFrame(() => fg.classList.add('visible'));
            } else {
                fg.classList.remove('visible');
                fg.addEventListener('transitionend', () => fg.classList.add('hidden'), { once: true });
            }
        } catch (error) {
            console.error(`Ошибка в toggleFields для ${checkbox}:`, error);
        }
    });
}

/**
 * Задерживает выполнение функции, предотвращая частые вызовы.
 * @param {Function} func - Функция для выполнения.
 * @param {number} wait - Задержка в миллисекундах.
 * @returns {Function} Дебounced-функция.
 */
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            try {
                func(...args);
            } catch (error) {
                console.error('Ошибка в debounce:', error);
            }
        }, wait);
    };
}

/**
 * Прокручивает страницу вверх с плавной анимацией.
 */
function scrollToTop() {
    try {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
        console.error('Ошибка в scrollToTop:', error);
    }
}

/**
 * Форматирует число в локализованную строку.
 * @param {number|string} num - Число для форматирования.
 * @returns {string} Форматированное число или "—" при ошибке.
 */
function formatNumber(num) {
    try {
        if (!num && num !== 0) return '—';
        return Number(num).toLocaleString('ru-RU', { maximumFractionDigits: 2 });
    } catch (error) {
        console.error('Ошибка в formatNumber:', error);
        return '—';
    }
}

/**
 * Изменяет размер iframe в зависимости от содержимого.
 * @param {HTMLElement} iframe - Элемент iframe.
 * @returns {void}
 */
function resizeIframe(iframe) {
    if (!iframe) {
        console.warn('Iframe не передан в resizeIframe');
        return;
    }
    try {
        const iframeDoc = iframe.contentWindow.document;
        if (!iframeDoc) {
            console.warn('Документ iframe не доступен');
            return;
        }

        function updateHeight() {
            const body = iframeDoc.body;
            const html = iframeDoc.documentElement;
            const height = Math.max(
                body.scrollHeight,
                body.offsetHeight,
                html.clientHeight,
                html.scrollHeight,
                html.offsetHeight
            );
            iframe.style.height = `${height}px`;
        }

        updateHeight();

        const observer = new MutationObserver(debounce(updateHeight, 100));
        observer.observe(iframeDoc.body, {
            childList: true,
            subtree: true,
            attributes: true,
            characterData: true
        });

        const resizeHandler = debounce(updateHeight, 100);
        window.addEventListener('resize', resizeHandler);

        iframe.addEventListener('unload', () => {
            observer.disconnect();
            window.removeEventListener('resize', resizeHandler);
        });
    } catch (error) {
        console.error('Ошибка в resizeIframe:', error);
    }
}

/**
 * Переключает тёмную тему и сохраняет выбор в localStorage.
 */
function toggleDarkTheme() {
    try {
        document.body.classList.toggle('dark-theme');
        const isDarkTheme = document.body.classList.contains('dark-theme');
        localStorage.setItem('theme', isDarkTheme ? 'dark' : 'light');

        const iframe = document.getElementById('dash-iframe');
        if (iframe) {
            function applyThemeToIframe() {
                const iframeDoc = iframe.contentWindow.document;
                if (!iframeDoc) {
                    console.warn('Документ iframe не доступен для применения темы');
                    return;
                }
                if (isDarkTheme) {
                    iframeDoc.body.classList.add('dark-theme');
                } else {
                    iframeDoc.body.classList.remove('dark-theme');
                }
                updateIframeFilterStyles(iframeDoc);
                resizeIframe(iframe);
            }

            if (iframe.contentWindow.document.readyState === 'complete') {
                applyThemeToIframe();
            } else {
                iframe.addEventListener('load', applyThemeToIframe, { once: true });
            }
        }
    } catch (error) {
        console.error('Ошибка в toggleDarkTheme:', error);
    }
}

/**
 * Обновляет стили фильтров внутри iframe для соответствия теме.
 * @param {Document} iframeDoc - Документ внутри iframe.
 */
function updateIframeFilterStyles(iframeDoc) {
    try {
        const resetButton = iframeDoc.querySelector('#reset-filters');
        if (resetButton) {
            resetButton.className = 'btn reset-filters';
            resetButton.textContent = 'Сбросить';
            resetButton.title = 'Сбросить все фильтры';
            resetButton.setAttribute('aria-label', 'Сбросить все фильтры');
        }

        const filterContainer = iframeDoc.querySelector('.table-filters');
        if (filterContainer) {
            filterContainer.style.display = 'flex';
            filterContainer.style.justifyContent = 'center';
            filterContainer.style.alignItems = 'center';
        }

        const dropdowns = iframeDoc.querySelectorAll('#year-dropdown, #region-dropdown');
        dropdowns.forEach(dropdown => {
            const isDarkTheme = document.body.classList.contains('dark-theme');
            dropdown.style.color = isDarkTheme ? '#E5E7EB' : '#111827';
            dropdown.style.background = isDarkTheme ? '#374151' : '#fff';
            const options = dropdown.querySelectorAll('option');
            options.forEach(option => {
                option.style.color = isDarkTheme ? '#E5E7EB' : '#111827';
                option.style.background = isDarkTheme ? '#374151' : '#fff';
            });
        });

        const dashCards = iframeDoc.querySelectorAll('.dash-card');
        dashCards.forEach(card => {
            const isDarkTheme = document.body.classList.contains('dark-theme');
            card.style.background = isDarkTheme ? '#2D3748' : '#fff';
            const h3 = card.querySelector('h3');
            const p = card.querySelector('p');
            if (h3) h3.style.color = isDarkTheme ? '#E5E7EB' : '#111827';
            if (p) p.style.color = isDarkTheme ? '#E5E7EB' : '#1E3A8A';
        });

        const dashTableContainer = iframeDoc.querySelector('#fire-table .dash-table-container');
        if (dashTableContainer) {
            const isDarkTheme = document.body.classList.contains('dark-theme');
            dashTableContainer.style.background = isDarkTheme ? '#2D3748' : '#fff';
            const table = dashTableContainer.querySelector('table');
            if (table) table.style.background = isDarkTheme ? '#2D3748' : '#fff';
            const ths = dashTableContainer.querySelectorAll('th');
            const tds = dashTableContainer.querySelectorAll('td');
            ths.forEach(th => {
                th.style.color = 'white';
                th.style.background = '#1E3A8A';
            });
            tds.forEach(td => {
                td.style.color = isDarkTheme ? '#E5E7EB' : '#111827';
                td.style.background = isDarkTheme ? '#2D3748' : '#fff';
            });
            const evenRows = dashTableContainer.querySelectorAll('tr:nth-child(even) td');
            evenRows.forEach(td => {
                td.style.background = isDarkTheme ? '#374151' : '#F9FAFB';
            });
            const hoverRows = dashTableContainer.querySelectorAll('tr:hover td');
            hoverRows.forEach(td => {
                td.style.background = isDarkTheme ? '#6B7280' : '#DBEAFE';
            });
        }

        const themeToggleInIframe = iframeDoc.querySelector('button[style*="position: fixed; bottom: 20px; left: 20px;"]');
        if (themeToggleInIframe) themeToggleInIframe.remove();

        const scrollBtnInIframe = iframeDoc.querySelector('button[style*="position: fixed; bottom: 20px; right: 20px;"]');
        if (scrollBtnInIframe) scrollBtnInIframe.remove();
    } catch (error) {
        console.error('Ошибка в updateIframeFilterStyles:', error);
    }
}

/**
 * Создаёт обёртку с меткой для элемента ввода.
 * @param {string} labelText - Текст метки.
 * @param {HTMLElement} inputElement - Элемент ввода.
 * @returns {HTMLElement} Обёртка с меткой и элементом.
 */
function createFilterLabel(labelText, inputElement) {
    try {
        const wrapper = document.createElement('div');
        wrapper.style.display = 'flex';
        wrapper.style.flexDirection = 'column';
        wrapper.style.alignItems = 'flex-start';

        const label = document.createElement('label');
        label.textContent = labelText;
        label.style.fontWeight = '500';
        label.style.color = 'var(--text-light)';
        label.style.fontSize = '1em';
        label.style.marginBottom = '6px';
        label.setAttribute('for', inputElement.id || `${labelText.toLowerCase().replace(':', '')}-${Math.random().toString(36).substr(2, 9)}`);
        inputElement.id = inputElement.id || label.getAttribute('for');

        wrapper.appendChild(label);
        wrapper.appendChild(inputElement);
        return wrapper;
    } catch (error) {
        console.error('Ошибка в createFilterLabel:', error);
        return document.createElement('div');
    }
}

/**
 * Инициализирует DataTable с кастомными настройками.
 * @param {HTMLElement} table - Таблица для инициализации.
 * @param {Object} [customOptions] - Пользовательские настройки DataTables.
 * @returns {Object|null} Экземпляр DataTable или null при ошибке.
 */
function initializeDataTable(table, customOptions = {}) {
    try {
        if (!table) {
            console.warn('Таблица не передана в initializeDataTable');
            return null;
        }
        if ($.fn.DataTable.isDataTable(table)) {
            $(table).DataTable().destroy();
        }

        const defaultOptions = {
            order: [[1, 'desc']],
            paging: true,
            searching: true,
            scrollX: true,
            language: {
                search: "Поиск:",
                lengthMenu: "Показать _MENU_ записей",
                info: "Показано с _START_ по _END_ из _TOTAL_ записей",
                infoEmpty: "Нет доступных записей",
                infoFiltered: "(отфильтровано из _MAX_ записей)",
                zeroRecords: "Записи не найдены",
                paginate: {
                    first: "Первый",
                    last: "Последний",
                    next: "Следующий",
                    previous: "Предыдущий"
                }
            },
            drawCallback: function (settings) {
                $(table).find('thead').show();
                $(table).find('thead th').css({
                    'position': 'sticky',
                    'top': '0',
                    'z-index': '10',
                    'background': 'var(--primary)',
                    'color': 'white',
                    'box-shadow': '0 2px 4px rgba(0, 0, 0, 0.1)'
                });

                const $table = $(table);
                const $thead = $table.find('thead');
                const $tbody = $table.find('tbody');
                const $ths = $thead.find('th');
                const $rows = $tbody.find('tr');

                $ths.each((index, th) => {
                    let maxWidth = 100;
                    const $th = $(th);

                    const thText = $th.text();
                    const tempSpan = $('<span>').text(thText).css({
                        'font-size': $th.css('font-size'),
                        'font-weight': $th.css('font-weight'),
                        'font-family': $th.css('font-family'),
                        'white-space': 'nowrap',
                        'position': 'absolute',
                        'visibility': 'hidden'
                    });
                    $('body').append(tempSpan);
                    maxWidth = Math.max(maxWidth, tempSpan.width() + 32);
                    tempSpan.remove();

                    $rows.each((rowIndex, row) => {
                        const $td = $(row).find('td').eq(index);
                        const tdText = $td.text();
                        const tempTdSpan = $('<span>').text(tdText).css({
                            'font-size': $td.css('font-size'),
                            'font-family': $td.css('font-family'),
                            'white-space': 'nowrap',
                            'position': 'absolute',
                            'visibility': 'hidden'
                        });
                        $('body').append(tempTdSpan);
                        maxWidth = Math.max(maxWidth, tempTdSpan.width() + 32);
                        tempTdSpan.remove();
                    });

                    $th.css('width', `${maxWidth}px`);
                    $rows.each((rowIndex, row) => {
                        $(row).find('td').eq(index).css('width', `${maxWidth}px`);
                    });
                });

                const tableWrapper = $table.closest('.table-wrapper');
                const scrollHandler = () => {
                    const scrollTop = tableWrapper.scrollTop();
                    const navbarHeight = document.querySelector('.navbar')?.offsetHeight || 0;
                    const newTop = Math.min(scrollTop, navbarHeight);
                    $ths.css('top', newTop);
                };
                tableWrapper.off('scroll').on('scroll', scrollHandler);
            }
        };

        if (table.id === 'audit-log-table') {
            defaultOptions.order = [[0, 'desc']];
            defaultOptions.lengthMenu = [5, 10, 25, 50, 100];
            defaultOptions.pageLength = 10;
            defaultOptions.scrollX = false;
        }

        if (table.id === 'summary-table') {
            defaultOptions.order = [[1, 'desc']];
            defaultOptions.scrollX = true;
            defaultOptions.lengthMenu = [5, 10, 25, 50, 100];
            defaultOptions.pageLength = 10;
        }

        const options = { ...defaultOptions, ...customOptions };
        const dataTable = $(table).DataTable(options);

        $(table).find('td').each(function () {
            const content = $(this).text().trim();
            if (content && content !== '—') {
                $(this).attr('data-tooltip', content);
            }
        });

        return dataTable;
    } catch (error) {
        console.error('Ошибка в initializeDataTable:', error);
        return null;
    }
}

/**
 * Показывает модальное окно с данными строки таблицы.
 * @param {Array} rowData - Данные строки.
 * @param {Array} headers - Заголовки таблицы.
 */
function showModal(rowData, headers) {
    try {
        const existingModal = document.querySelector('.modal');
        if (existingModal) {
            existingModal.remove();
        }

        document.body.classList.add('modal-open');

        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'flex';
        modal.style.animation = 'fadeIn 0.3s ease-in-out';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'modal-title');

        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.style.animation = 'slideIn 0.3s ease-in-out';

        const closeBtn = document.createElement('span');
        closeBtn.className = 'close-modal';
        closeBtn.innerHTML = '×';
        closeBtn.setAttribute('aria-label', 'Закрыть модальное окно');

        const closeModal = () => {
            modal.style.animation = 'fadeIn 0.3s ease-in-out reverse';
            modalContent.style.animation = 'slideIn 0.3s ease-in-out reverse';
            setTimeout(() => {
                modal.remove();
                document.body.classList.remove('modal-open');
            }, 300);
        };

        closeBtn.addEventListener('click', closeModal);

        const title = document.createElement('h3');
        title.textContent = 'Детали записи';
        title.id = 'modal-title';

        modalContent.appendChild(closeBtn);
        modalContent.appendChild(title);

        headers.forEach((header, index) => {
            const p = document.createElement('p');
            p.innerHTML = `<strong>${header}:</strong> ${rowData[index] || '—'}`;
            modalContent.appendChild(p);
        });

        modal.appendChild(modalContent);
        document.body.appendChild(modal);

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });

        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);

        closeBtn.focus();

        const iframe = document.getElementById('dash-iframe');
        if (iframe) resizeIframe(iframe);
    } catch (error) {
        console.error('Ошибка в showModal:', error);
        document.body.classList.remove('modal-open');
    }
}

/**
 * Создаёт и настраивает фильтры для DataTable.
 * @param {HTMLElement} table - Таблица.
 * @param {Object} dataTable - Экземпляр DataTable.
 * @param {HTMLElement} filterContainer - Контейнер для фильтров.
 * @param {HTMLElement} loader - Элемент загрузки.
 */
function setupTableFilters(table, dataTable, filterContainer, loader) {
    try {
        const applyFilters = () => {
            loader.style.display = 'block';
            loader.style.opacity = '1';
            setTimeout(() => {
                dataTable.draw();
                loader.style.opacity = '0';
                loader.addEventListener('transitionend', () => loader.style.display = 'none', { once: true });
                filterContainer.style.transition = 'background 0.3s';
                filterContainer.style.background = '#E5E7EB';
                setTimeout(() => filterContainer.style.background = '', 300);
                const iframe = document.getElementById('dash-iframe');
                if (iframe) resizeIframe(iframe);
            }, 500);
        };

        const resetButton = document.createElement('button');
        resetButton.textContent = 'Сбросить';
        resetButton.className = 'btn reset-filters';
        resetButton.title = 'Сбросить все фильтры';
        resetButton.setAttribute('aria-label', 'Сбросить все фильтры');

        if (table.id === 'fires-table') {
            const regionFilter = document.createElement('select');
            regionFilter.innerHTML = '<option value="">Все регионы</option>';
            const regions = [...new Set(dataTable.column(2).data().toArray())].sort();
            regions.forEach(region => {
                const option = document.createElement('option');
                option.value = region;
                option.textContent = region;
                regionFilter.appendChild(option);
            });

            const dateFilter = document.createElement('input');
            dateFilter.type = 'date';
            const areaFilter = document.createElement('input');
            areaFilter.type = 'number';
            areaFilter.placeholder = 'Площадь (га)';

            regionFilter.title = 'Фильтр по региону';
            dateFilter.title = 'Фильтр по дате';
            areaFilter.title = 'Фильтр по площади (га)';

            filterContainer.appendChild(createFilterLabel('Регион:', regionFilter));
            filterContainer.appendChild(createFilterLabel('Дата:', dateFilter));
            filterContainer.appendChild(createFilterLabel('Площадь:', areaFilter));
            filterContainer.appendChild(resetButton);

            $.fn.dataTable.ext.search.push((settings, data, dataIndex) => {
                const region = regionFilter.value;
                const date = dateFilter.value;
                const area = parseFloat(areaFilter.value) || 0;

                const rowRegion = data[2] || '';
                const rowDate = data[1] || '';
                const rowArea = parseFloat(data[8]) || 0;

                if (region && rowRegion !== region) return false;
                if (date && rowDate !== date) return false;
                if (area && rowArea < area) return false;
                return true;
            });

            regionFilter.addEventListener('change', applyFilters);
            dateFilter.addEventListener('change', applyFilters);
            areaFilter.addEventListener('input', debounce(applyFilters, 500));

            resetButton.addEventListener('click', () => {
                regionFilter.value = '';
                dateFilter.value = '';
                areaFilter.value = '';
                applyFilters();
            });
        } else if (table.id === 'summary-table') {
            const regionFilter = document.createElement('select');
            regionFilter.innerHTML = '<option value="">Все регионы</option>';
            const regions = [...new Set(dataTable.column(0).data().toArray())].sort();
            regions.forEach(region => {
                const option = document.createElement('option');
                option.value = region;
                option.textContent = region;
                regionFilter.appendChild(option);
            });

            regionFilter.title = 'Фильтр по региону';

            filterContainer.appendChild(createFilterLabel('Регион:', regionFilter));
            filterContainer.appendChild(resetButton);

            $.fn.dataTable.ext.search.push((settings, data, dataIndex) => {
                const region = regionFilter.value;
                const rowRegion = data[0] || '';
                if (region && rowRegion !== region) return false;
                return true;
            });

            regionFilter.addEventListener('change', applyFilters);

            resetButton.addEventListener('click', () => {
                regionFilter.value = '';
                applyFilters();
            });
        }
    } catch (error) {
        console.error('Ошибка в setupTableFilters:', error);
    }
}

// ==========================================================================
// Инициализация при загрузке страницы
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    try {
        if (localStorage.getItem('theme') === 'dark') {
            document.body.classList.add('dark-theme');
        }

        if (!window.location.pathname.includes('/dash/')) {
            const themeToggle = document.createElement('button');
            themeToggle.innerHTML = document.body.classList.contains('dark-theme') ? '☀️' : '🌙';
            themeToggle.style.cssText = `
                position: fixed;
                bottom: 20px;
                left: 20px;
                padding: 10px;
                background: #fff;
                border: 1px solid var(--border-light);
                border-radius: 50%;
                cursor: pointer;
                z-index: 1000;
                transition: all 0.2s ease-in-out;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            `;
            themeToggle.setAttribute('aria-label', 'Переключить тему');
            themeToggle.addEventListener('click', () => {
                toggleDarkTheme();
                themeToggle.innerHTML = document.body.classList.contains('dark-theme') ? '☀️' : '🌙';
                themeToggle.style.transform = 'rotate(180deg)';
                setTimeout(() => themeToggle.style.transform = 'rotate(0deg)', 300);
            });
            document.body.appendChild(themeToggle);

            const scrollBtn = document.createElement('button');
            scrollBtn.innerHTML = '↑';
            scrollBtn.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 10px 15px;
                background: var(--primary);
                color: white;
                border: none;
                border-radius: 50%;
                cursor: pointer;
                z-index: 1000;
                transition: all 0.2s ease-in-out;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            `;
            scrollBtn.setAttribute('aria-label', 'Прокрутить вверх');
            scrollBtn.addEventListener('click', scrollToTop);
            document.body.appendChild(scrollBtn);
        }

        // Управление видимостью полей формы
        const checkboxes = document.querySelectorAll('#lo_flag, #aps_flag, #kps_flag, #mio_flag, #other_org_flag');
        if (checkboxes.length > 0) {
            toggleFields(); // Устанавливаем начальное состояние
            checkboxes.forEach(cb => cb.addEventListener('change', toggleFields));
        }

        document.querySelectorAll('table:not(.dataTable) td').forEach(td => {
            const num = parseFloat(td.textContent);
            if (!isNaN(num)) td.textContent = formatNumber(num);
        });

        const loader = document.createElement('div');
        loader.className = 'loader';
        loader.style.cssText = `
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 3000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        loader.innerHTML = '<span style="font-size: 1em; color: var(--text-light); display: block; text-align: center; margin-top: 10px;">Загрузка...</span>';
        document.body.appendChild(loader);

        document.querySelectorAll('.table-filters, .column-toggle').forEach(el => {
            el.style.animation = 'slideDown 0.3s ease-in-out';
        });

        const tables = document.querySelectorAll('.table-wrapper table');
        tables.forEach(table => {
            const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
            const tableWrapper = table.parentElement;

            const controlsContainer = document.createElement('div');
            controlsContainer.className = 'table-controls';

            const filterContainer = document.createElement('div');
            filterContainer.className = 'table-filters';

            const tableId = table.id || `table-${Math.random().toString(36).substr(2, 9)}`;
            table.id = tableId;
            const savedVisibility = JSON.parse(localStorage.getItem(`column-visibility-${tableId}`)) || {};

            tableWrapper.insertBefore(controlsContainer, tableWrapper.firstChild);

            const dataTable = initializeDataTable(table);

            if (dataTable) {
                $(table).on('click', 'tbody tr', function () {
                    const rowData = dataTable.row(this).data();
                    showModal(rowData, headers);
                });

                setupTableFilters(table, dataTable, filterContainer, loader);

                if (filterContainer.children.length > 0) {
                    controlsContainer.appendChild(filterContainer);
                }

                const columnToggleContainer = document.createElement('div');
                columnToggleContainer.className = 'column-toggle';
                headers.forEach((header, index) => {
                    const toggleWrapper = document.createElement('label');
                    const toggle = document.createElement('input');
                    toggle.type = 'checkbox';
                    toggle.checked = savedVisibility[index] !== undefined ? savedVisibility[index] : true;
                    toggle.dataset.column = index;
                    toggle.addEventListener('change', (e) => {
                        const colIndex = e.target.dataset.column;
                        const column = dataTable.column(colIndex);
                        column.visible(e.target.checked);
                        savedVisibility[colIndex] = e.target.checked;
                        localStorage.setItem(`column-visibility-${tableId}`, JSON.stringify(savedVisibility));
                        const iframe = document.getElementById('dash-iframe');
                        if (iframe) resizeIframe(iframe);
                    });
                    const label = document.createElement('span');
                    label.textContent = header;
                    toggleWrapper.appendChild(toggle);
                    toggleWrapper.appendChild(label);
                    columnToggleContainer.appendChild(toggleWrapper);

                    if (savedVisibility[index] !== undefined) {
                        dataTable.column(index).visible(savedVisibility[index]);
                    }
                });

                if (columnToggleContainer.children.length > 0) {
                    controlsContainer.appendChild(columnToggleContainer);
                }

                table.querySelectorAll('tr').forEach((row, index) => {
                    if (index === 0) return;
                    const toggleBtn = document.createElement('button');
                    toggleBtn.textContent = '>';
                    toggleBtn.className = 'toggle-row';
                    toggleBtn.style.cssText = `
                        display: none;
                        padding: 4px 8px;
                        background: var(--primary);
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        margin-right: 10px;
                    `;
                    toggleBtn.setAttribute('aria-label', 'Развернуть строку');
                    row.firstElementChild.insertBefore(toggleBtn, row.firstElementChild.firstChild);
                    toggleBtn.addEventListener('click', () => {
                        row.classList.toggle('expanded');
                        toggleBtn.textContent = row.classList.contains('expanded') ? 'v' : '>';
                        toggleBtn.setAttribute('aria-label', row.classList.contains('expanded') ? 'Свернуть строку' : 'Развернуть строку');
                    });
                });
            }
        });
    } catch (error) {
        console.error('Ошибка при загрузке страницы:', error);
    }
});