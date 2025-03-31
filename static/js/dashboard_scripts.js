// Конфигурация приложения
const APP_CONFIG = {
    CACHE: {
      DATA_TTL: 5 * 60 * 1000, // 5 минут кэширования данных
      GEOJSON_TTL: 24 * 60 * 60 * 1000 // 24 часа для GeoJSON
    },
    MAP: {
      minZoom: 5,
      maxZoom: 10,
      bounds: [[40, 44], [56, 88]],
      center: [48.0196, 66.9237],
      tileLayer: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution: '© OpenStreetMap contributors'
    },
    DEBOUNCE: {
      FILTERS: 300, // Задержка для фильтров
      RESIZE: 100 // Задержка для ресайза
    },
    COLORS: {
      damageScale: [
        { value: 0, color: '#FFEDA0' },
        { value: 10, color: '#FED976' },
        { value: 20, color: '#FEB24C' },
        { value: 50, color: '#FD8D3C' },
        { value: 100, color: '#FC4E2A' },
        { value: 200, color: '#E31A1C' },
        { value: 500, color: '#BD0026' },
        { value: 1000, color: '#800026' }
      ],
      charts: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
    }
  };
  
  // Состояние приложения
  const AppState = {
    data: {
      all: [],
      filtered: [],
      regions: []
    },
    components: {
      map: null,
      geoJsonLayer: null,
      legend: null,
      dataTable: null,
      charts: {},
      geoJsonData: null
    },
    ui: {
      isLoading: false,
      pendingRequests: new Set(),
      regionDropdownInitialized: false
    }
  };
  
  // Утилиты
  const Utils = {
    formatNumber: (() => {
      const cache = new Map();
      return (value) => {
        if (value === null || value === undefined || value === 'None') return '—';
        if (value === 0) return '0';
        const cacheKey = `${value}`;
        if (cache.has(cacheKey)) return cache.get(cacheKey);
        const formatted = Number(value).toLocaleString('ru-RU', { maximumFractionDigits: 2 });
        cache.set(cacheKey, formatted);
        return formatted;
      };
    })(),
  
    debounce(func, wait, immediate = false) {
      let timeout;
      return function() {
        const context = this, args = arguments;
        const later = () => {
          timeout = null;
          if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
      };
    },
  
    getColorForValue(value, scale) {
      for (let i = scale.length - 1; i >= 0; i--) {
        if (value >= scale[i].value) return scale[i].color;
      }
      return scale[0].color;
    },
  
    sanitizeDate(date) {
      if (!date || date === 'None') return '';
      return date;
    }
  };
  
  // Работа с данными
  const DataService = {
    async loadFireData(startDate = '', endDate = '', regions = ['all']) {
      startDate = Utils.sanitizeDate(startDate);
      endDate = Utils.sanitizeDate(endDate);
  
      if (!this.validateDates(startDate, endDate)) return;
  
      const cacheKey = `fire_data_${startDate}_${endDate}_${regions.join(',')}`;
      const cachedData = this.getCachedData(cacheKey);
      
      if (cachedData) {
        this.processFireData(cachedData, regions);
        return;
      }
  
      const requestId = Symbol();
      AppState.ui.pendingRequests.add(requestId);
      AppState.ui.isLoading = true;
      UI.showLoader();
  
      try {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        if (!regions.includes('all')) {
          regions.forEach(r => params.append('regions', r));
        }
  
        const response = await fetch(`/api/fires?${params.toString()}`, {
          headers: { 'Accept': 'application/json' }
        });
  
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || `HTTP error: ${response.status}`);
        }
  
        const data = await response.json();
        this.cacheData(cacheKey, data);
        this.processFireData(data, regions);
      } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        UI.showError(error.message);
      } finally {
        AppState.ui.pendingRequests.delete(requestId);
        AppState.ui.isLoading = false;
        UI.hideLoader();
      }
    },
  
    async loadGeoJSON() {
      if (AppState.components.geoJsonData) return AppState.components.geoJsonData;
  
      const cached = localStorage.getItem('geojson_cache');
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        if (Date.now() - timestamp < APP_CONFIG.CACHE.GEOJSON_TTL) {
          AppState.components.geoJsonData = data;
          return data;
        }
      }
  
      try {
        const response = await fetch('/static/regions.geojson');
        if (!response.ok) throw new Error(`Ошибка загрузки GeoJSON: ${response.statusText}`);
        
        const data = await response.json();
        if (!data?.features?.length) throw new Error('GeoJSON пустой или некорректный');
  
        localStorage.setItem('geojson_cache', JSON.stringify({
          data,
          timestamp: Date.now()
        }));
  
        AppState.components.geoJsonData = data;
        return data;
      } catch (error) {
        console.error("Ошибка загрузки GeoJSON:", error);
        try {
          const backupResponse = await fetch('/static/regions_backup.geojson');
          const backupData = await backupResponse.json();
          console.warn("Используется резервный GeoJSON");
          return backupData;
        } catch (backupError) {
          console.error("Резервный GeoJSON недоступен:", backupError);
          throw error;
        }
      }
    },
  
    validateDates(startDate, endDate) {
      const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
      
      if (startDate && !dateRegex.test(startDate)) {
        UI.showAlert('Неверный формат начальной даты! Используйте yyyy-MM-dd.');
        return false;
      }
      if (endDate && !dateRegex.test(endDate)) {
        UI.showAlert('Неверный формат конечной даты! Используйте yyyy-MM-dd.');
        return false;
      }
      if (startDate && endDate && new Date(startDate) > new Date(endDate)) {
        UI.showAlert('Начальная дата не может быть больше конечной!');
        return false;
      }
      return true;
    },
  
    processFireData(data, regions) {
      if (!data?.summary_data) throw new Error('Нет данных в summary_data');
  
      AppState.data.all = data.summary_data;
      AppState.data.regions = [...new Set(data.summary_data.map(item => item.region))].sort();
      this.updateFilteredData(regions);
      
      UI.updateDashboard();
      if (!AppState.ui.regionDropdownInitialized) {
        UI.initRegionDropdown();
        AppState.ui.regionDropdownInitialized = true;
      }
      UI.updateRegionDropdown(regions);
    },
  
    updateFilteredData(regions) {
      AppState.data.filtered = regions.includes('all') || regions.length === 0
        ? [...AppState.data.all]
        : AppState.data.all.filter(d => regions.includes(d.region));
    },
  
    getCachedData(key) {
      const cached = localStorage.getItem(key);
      if (!cached) return null;
      
      const { data, timestamp } = JSON.parse(cached);
      if (Date.now() - timestamp > APP_CONFIG.CACHE.DATA_TTL) {
        localStorage.removeItem(key);
        return null;
      }
      
      return data;
    },
  
    cacheData(key, data) {
      localStorage.setItem(key, JSON.stringify({
        data,
        timestamp: Date.now()
      }));
    }
  };
  
  // Работа с картой
  const MapService = {
    init() {
      if (AppState.components.map) return;
  
      AppState.components.map = L.map('map', {
        minZoom: APP_CONFIG.MAP.minZoom,
        maxZoom: APP_CONFIG.MAP.maxZoom,
        maxBounds: APP_CONFIG.MAP.bounds,
        maxBoundsViscosity: 1.0
      }).setView(APP_CONFIG.MAP.center, 5);
  
      L.tileLayer(APP_CONFIG.MAP.tileLayer, {
        attribution: APP_CONFIG.MAP.attribution
      }).addTo(AppState.components.map);
  
      AppState.components.map.fitBounds(APP_CONFIG.MAP.bounds);
    },
  
    async update() {
      if (!AppState.components.map) this.init();
      
      try {
        const geoJsonData = await DataService.loadGeoJSON();
        this.renderGeoJSON(geoJsonData);
        this.addLegend();
        AppState.components.map.invalidateSize();
      } catch (error) {
        console.error("Ошибка обновления карты:", error);
        UI.showError(`Ошибка загрузки карты: ${error.message}`);
      }
    },
  
    renderGeoJSON(geoJsonData) {
      if (AppState.components.geoJsonLayer) {
        AppState.components.map.removeLayer(AppState.components.geoJsonLayer);
        AppState.components.geoJsonLayer = null;
      }
  
      if (AppState.components.legend) {
        AppState.components.map.removeControl(AppState.components.legend);
        AppState.components.legend = null;
      }
  
      AppState.components.geoJsonLayer = L.geoJSON(geoJsonData, {
        style: this.getRegionStyle.bind(this),
        onEachFeature: this.bindPopupToFeature.bind(this)
      }).addTo(AppState.components.map);
    },
  
    getRegionStyle(feature) {
      const regionData = AppState.data.filtered.find(r => r.region === feature.properties.region);
      const damageArea = regionData ? regionData.total_damage_area : 0;
      
      return {
        fillColor: Utils.getColorForValue(damageArea, APP_CONFIG.COLORS.damageScale),
        weight: 2,
        opacity: 1,
        color: 'white',
        fillOpacity: 0.7
      };
    },
  
    bindPopupToFeature(feature, layer) {
      const regionData = AppState.data.filtered.find(r => r.region === feature.properties.region);
      layer.bindPopup(`
        <b>Регион:</b> ${feature.properties.region || '—'}<br>
        <b>Площадь пожаров:</b> ${Utils.formatNumber(regionData?.total_damage_area || 0)} га<br>
        <b>Ущерб:</b> ${Utils.formatNumber(regionData?.total_damage_tenge || 0)} тг
      `);
    },
  
    addLegend() {
      AppState.components.legend = L.control({ position: 'bottomright' });
      
      AppState.components.legend.onAdd = () => {
        const div = L.DomUtil.create('div', 'info legend');
        div.innerHTML = '<h4 style="margin: 0 0 5px 0; font-size: 14px;">Площадь пожаров (га)</h4>';
        
        APP_CONFIG.COLORS.damageScale.forEach((grade, i) => {
          const nextGrade = APP_CONFIG.COLORS.damageScale[i + 1];
          div.innerHTML += `
            <div style="display: flex; align-items: center; margin-bottom: 2px;">
              <i style="background: ${grade.color}; width: 18px; height: 18px; display: inline-block; margin-right: 5px;"></i>
              <span style="font-size: 12px;">${grade.value}${nextGrade ? '–' + nextGrade.value : '+'}</span>
            </div>`;
        });
        
        div.style.background = '#fff';
        div.style.padding = '10px';
        div.style.borderRadius = '4px';
        div.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';
        return div;
      };
      
      AppState.components.legend.addTo(AppState.components.map);
    }
  };
  
  // Работа с графиками
  const ChartService = {
    updateAll() {
      const isDarkTheme = document.body.classList.contains('dark-theme');
      const textColor = isDarkTheme ? '#E5E7EB' : '#111827';
      const gridColor = isDarkTheme ? '#4B5563' : '#E5E7EB';
      
      this.updateChart('bar-chart', this.getBarChartConfig(textColor, gridColor));
      this.updateChart('scatter-chart', this.getScatterChartConfig(textColor, gridColor));
      this.updateChart('doughnut-chart', this.getDoughnutChartConfig(textColor));
    },
  
    updateChart(chartId, config) {
      const canvas = document.getElementById(chartId);
      if (!canvas) return;
  
      if (AppState.components.charts[chartId]) {
        AppState.components.charts[chartId].destroy();
      }
  
      AppState.components.charts[chartId] = new Chart(canvas, config);
      this.addChartControls(chartId);
    },
  
    getBarChartConfig(textColor, gridColor) {
      const labels = AppState.data.filtered.map(item => item.region);
      const areaData = AppState.data.filtered.map(item => item.total_damage_area || 0);
      const fireCountData = AppState.data.filtered.map(item => item.fire_count || 0);
  
      return {
        type: 'bar',
        data: {
          labels,
          datasets: [
            { 
              label: 'Площадь (га)', 
              data: areaData, 
              backgroundColor: '#36A2EB', 
              borderColor: '#36A2EB', 
              borderWidth: 1 
            },
            { 
              label: 'Пожары', 
              data: fireCountData, 
              backgroundColor: '#FFCE56', 
              borderColor: '#FFCE56', 
              borderWidth: 1 
            }
          ]
        },
        options: this.getCommonChartOptions(textColor, gridColor),
        plugins: [ChartDataLabels, ChartZoom]
      };
    },
  
    getScatterChartConfig(textColor, gridColor) {
      return {
        type: 'scatter',
        data: {
          datasets: AppState.data.filtered.map((item, idx) => ({
            label: item.region,
            data: [{ 
              x: item.total_damage_area || 0, 
              y: item.total_damage_tenge || 0 
            }],
            backgroundColor: APP_CONFIG.COLORS.charts[idx % APP_CONFIG.COLORS.charts.length],
            pointRadius: 6,
            pointHoverRadius: 8
          }))
        },
        options: {
          ...this.getCommonChartOptions(textColor, gridColor),
          scales: {
            x: {
              title: { display: true, text: 'Площадь (га)', color: textColor },
              ticks: { color: textColor, font: { size: 10 } },
              grid: { color: gridColor }
            },
            y: {
              title: { display: true, text: 'Ущерб (тг)', color: textColor },
              ticks: { color: textColor, font: { size: 10 } },
              grid: { color: gridColor }
            }
          }
        },
        plugins: [ChartZoom]
      };
    },
  
    getDoughnutChartConfig(textColor) {
      return {
        type: 'doughnut',
        data: {
          labels: AppState.data.filtered.map(item => item.region),
          datasets: [{
            label: 'Площадь (га)',
            data: AppState.data.filtered.map(item => item.total_damage_area || 0),
            backgroundColor: APP_CONFIG.COLORS.charts
          }]
        },
        options: {
          ...this.getCommonChartOptions(textColor),
          plugins: {
            ...this.getCommonChartOptions(textColor).plugins,
            datalabels: { 
              color: '#fff', 
              font: { size: 10 }, 
              formatter: Utils.formatNumber 
            }
          }
        },
        plugins: [ChartDataLabels]
      };
    },
  
    getCommonChartOptions(textColor, gridColor) {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            align: 'center',
            labels: {
              color: textColor,
              font: { size: 12 },
              boxWidth: 20,
              padding: 10
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: { size: 12 },
            bodyFont: { size: 10 },
            callbacks: {
              label: ctx => {
                const datasetLabel = ctx.dataset.label || '';
                const value = Utils.formatNumber(ctx.raw || ctx.raw.y);
                const label = ctx.label || '';
                return `${label}: ${datasetLabel} - ${value}`;
              },
              afterLabel: ctx => {
                const regionData = AppState.data.filtered.find(item => item.region === ctx.label);
                if (regionData) {
                  return [
                    `Пожары: ${Utils.formatNumber(regionData.fire_count)}`,
                    `Люди: ${Utils.formatNumber(regionData.total_people)}`,
                    `Техника: ${Utils.formatNumber(regionData.total_technic)}`
                  ];
                }
                return '';
              }
            }
          },
          zoom: {
            zoom: {
              wheel: { enabled: true },
              pinch: { enabled: true },
              mode: 'xy'
            },
            pan: {
              enabled: true,
              mode: 'xy'
            }
          }
        },
        animation: {
          duration: 1000,
          easing: 'easeInOutQuart'
        }
      };
    },
  
    addChartControls(chartId) {
      const container = document.getElementById(`${chartId}-container`);
      if (!container) return;
  
      const existingBtn = container.querySelector('.chart-download-btn');
      if (existingBtn) existingBtn.remove();
  
      const downloadBtn = document.createElement('button');
      downloadBtn.className = 'chart-download-btn';
      downloadBtn.innerHTML = '📥';
      downloadBtn.title = 'Скачать график';
      downloadBtn.onclick = () => this.exportChartToImage(chartId);
  
      container.appendChild(downloadBtn);
  
      const canvas = document.getElementById(chartId);
      canvas.addEventListener('dblclick', () => {
        if (AppState.components.charts[chartId]) {
          AppState.components.charts[chartId].resetZoom();
        }
      });
    },
  
    exportChartToImage(chartId) {
      const container = document.getElementById(`${chartId}-container`);
      if (!container) return;
  
      html2canvas(container, {
        scale: 1.5,
        useCORS: true,
        logging: false,
        width: container.offsetWidth,
        height: container.offsetHeight,
        onclone: (clonedDoc) => {
          const clonedContainer = clonedDoc.getElementById(`${chartId}-container`);
          clonedContainer.style.width = `${container.offsetWidth}px`;
          clonedContainer.style.height = `${container.offsetHeight}px`;
          const downloadBtn = clonedContainer.querySelector('.chart-download-btn');
          if (downloadBtn) downloadBtn.style.display = 'none';
        }
      }).then(canvas => {
        const link = document.createElement('a');
        link.download = `${chartId}.jpg`;
        link.href = canvas.toDataURL('image/jpeg', 1.0);
        link.click();
      }).catch(error => {
        console.error('Ошибка экспорта графика:', error);
        UI.showAlert('Не удалось экспортировать график');
      });
    }
  };
  
  // Работа с таблицей
  const TableService = {
    init() {
      if (AppState.components.dataTable) {
        AppState.components.dataTable.destroy();
      }
  
      this.renderTable();
      this.initDataTable();
    },
  
    renderTable() {
      const tbody = document.getElementById('table-body');
      if (!tbody) return;
  
      tbody.innerHTML = AppState.data.filtered.map(row => `
        <tr>
          <td data-tooltip="${row.region || '—'}">${row.region || '—'}</td>
          <td>${Utils.formatNumber(row.fire_count)}</td>
          <td>${Utils.formatNumber(row.total_damage_area)}</td>
          <td>${Utils.formatNumber(row.total_damage_tenge)}</td>
          <td>${Utils.formatNumber(row.total_people)}</td>
          <td>${Utils.formatNumber(row.total_technic)}</td>
          <td>${Utils.formatNumber(row.total_aircraft)}</td>
          <td>${Utils.formatNumber(row.aps_people)}</td>
          <td>${Utils.formatNumber(row.aps_technic)}</td>
          <td>${Utils.formatNumber(row.aps_aircraft)}</td>
        </tr>
      `).join('');
    },
  
    initDataTable() {
      AppState.components.dataTable = $('#dashboard-table').DataTable({
        pageLength: 10,
        language: { url: "/static/js/ru.json" },
        responsive: true,
        order: [[1, 'desc']],
        dom: 'Bfrtip',
        buttons: [{ 
          text: 'Экспорт в Excel', 
          action: this.exportToExcel 
        }],
        drawCallback: () => {
          $('#dashboard-table thead th').css({
            position: 'sticky',
            top: '0',
            'z-index': '10',
            background: 'var(--primary)',
            color: 'white'
          });
        }
      });
  
      $('#dashboard-table tbody').on('click', 'tr', function() {
        const rowData = AppState.components.dataTable.row(this).data();
        UI.showModal(
          rowData, 
          ['Регион', 'Пожары', 'Площадь (га)', 'Ущерб (тг)', 'Люди', 'Техника', 'Авиация', 'Люди АПС', 'Техника АПС', 'Авиация АПС']
        );
      });
    },
  
    exportToExcel() {
      const headers = [
        'Регион', 'Количество пожаров', 'Площадь ущерба (га)', 
        'Ущерб (тг)', 'Всего людей', 'Всего техники', 'Всего авиации', 
        'Люди АПС', 'Техника АПС', 'Авиация АПС'
      ];
      
      const data = AppState.data.filtered.map(row => [
        row.region || '—', 
        row.fire_count || 0, 
        row.total_damage_area || 0, 
        row.total_damage_tenge || 0,
        row.total_people || 0, 
        row.total_technic || 0, 
        row.total_aircraft || 0, 
        row.aps_people || 0,
        row.aps_technic || 0, 
        row.aps_aircraft || 0
      ]);
  
      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.aoa_to_sheet([headers, ...data]);
      XLSX.utils.book_append_sheet(wb, ws, 'Сводка по пожарам');
      XLSX.writeFile(wb, 'Fire_Summary.xlsx');
    }
  };
  
  // Пользовательский интерфейс
  const UI = {
    initRegionDropdown() {
      const dropdown = document.getElementById('region-dropdown');
      if (!dropdown) return;
  
      dropdown.innerHTML = `
        <div style="padding: 5px;">
          <label><input type="checkbox" value="all" checked> Все регионы</label>
        </div>
      `;
  
      AppState.data.regions.forEach(region => {
        dropdown.insertAdjacentHTML('beforeend', `
          <div style="padding: 5px;">
            <label><input type="checkbox" value="${region}"> ${region}</label>
          </div>
        `);
      });
  
      this.setupRegionDropdownEvents(dropdown);
    },
  
    setupRegionDropdownEvents(dropdown) {
      const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]');
      const allCheckbox = dropdown.querySelector('input[value="all"]');
  
      checkboxes.forEach(cb => {
        cb.addEventListener('change', () => {
          const selected = Array.from(checkboxes)
            .filter(c => c.checked && c.value !== 'all')
            .map(c => c.value);
  
          if (cb.value === 'all' && cb.checked) {
            checkboxes.forEach(c => {
              if (c.value !== 'all') c.checked = false;
            });
          } else if (cb.value !== 'all') {
            allCheckbox.checked = selected.length === 0;
          }
  
          const regions = allCheckbox.checked ? ['all'] : selected;
          const startDate = Utils.sanitizeDate(document.getElementById('start-date').value);
          const endDate = Utils.sanitizeDate(document.getElementById('end-date').value);
          
          DataService.loadFireData(startDate, endDate, regions);
        });
      });
    },
  
    updateRegionDropdown(selectedRegions) {
      const checkboxes = document.querySelectorAll('#region-dropdown input[type="checkbox"]');
      const allCheckbox = document.querySelector('#region-dropdown input[value="all"]');
  
      if (selectedRegions.includes('all')) {
        allCheckbox.checked = true;
        checkboxes.forEach(cb => {
          if (cb.value !== 'all') cb.checked = false;
        });
      } else {
        allCheckbox.checked = false;
        checkboxes.forEach(cb => {
          if (cb.value !== 'all') {
            cb.checked = selectedRegions.includes(cb.value);
          }
        });
      }
    },
  
    updateCards() {
      const totals = AppState.data.filtered.reduce((acc, item) => ({
        fire_count: acc.fire_count + (item.fire_count || 0),
        damage_area: acc.damage_area + (item.total_damage_area || 0),
        damage_tenge: acc.damage_tenge + (item.total_damage_tenge || 0),
        people: acc.people + (item.total_people || 0),
        technic: acc.technic + (item.total_technic || 0),
        aircraft: acc.aircraft + (item.total_aircraft || 0)
      }), { 
        fire_count: 0, 
        damage_area: 0, 
        damage_tenge: 0, 
        people: 0, 
        technic: 0, 
        aircraft: 0 
      });
  
      document.getElementById('total-fires').textContent = Utils.formatNumber(totals.fire_count);
      document.getElementById('total-area').textContent = `${Utils.formatNumber(totals.damage_area)} га`;
      document.getElementById('total-damage').textContent = `${Utils.formatNumber(totals.damage_tenge)} тг`;
      document.getElementById('total-people').textContent = Utils.formatNumber(totals.people);
      document.getElementById('total-technic').textContent = Utils.formatNumber(totals.technic);
      document.getElementById('total-aircraft').textContent = Utils.formatNumber(totals.aircraft);
    },
  
    updateDashboard() {
      this.updateCards();
      TableService.init();
      ChartService.updateAll();
      MapService.update();
    },
  
    showModal(rowData, headers) {
      const modal = document.createElement('div');
      modal.className = 'modal';
      modal.style.display = 'flex';
      modal.style.animation = 'fadeIn 0.3s ease-in-out';
  
      const modalContent = document.createElement('div');
      modalContent.className = 'modal-content';
      modalContent.innerHTML = `
        <span class="close-modal">×</span>
        <h3>Детали региона</h3>
        ${headers.map((header, i) => `
          <p><strong>${header}:</strong> ${rowData[i] || '—'}</p>
        `).join('')}
      `;
  
      const closeModal = () => {
        modal.style.animation = 'fadeIn 0.3s ease-in-out reverse';
        setTimeout(() => modal.remove(), 300);
      };
  
      modalContent.querySelector('.close-modal').addEventListener('click', closeModal);
      modal.addEventListener('click', e => {
        if (e.target === modal) closeModal();
      });
      document.addEventListener('keydown', e => {
        if (e.key === 'Escape') closeModal();
      }, { once: true });
  
      modal.appendChild(modalContent);
      document.body.appendChild(modal);
    },
  
    showLoader() {
      // Реализация индикатора загрузки
      const loader = document.getElementById('loader');
      if (loader) loader.style.display = 'block';
    },
  
    hideLoader() {
      // Скрытие индикатора загрузки
      const loader = document.getElementById('loader');
      if (loader) loader.style.display = 'none';
    },
  
    showError(message) {
      document.querySelectorAll('.dash-graph').forEach(container => {
        container.innerHTML = `<p class="text-danger">Ошибка: ${message}</p>`;
      });
    },
  
    showAlert(message) {
      alert(message);
    },
  
    toggleTheme() {
      document.body.classList.toggle('dark-theme');
      localStorage.setItem('theme', 
        document.body.classList.contains('dark-theme') ? 'dark' : 'light'
      );
      ChartService.updateAll();
    },
  
    init() {
      if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-theme');
      }
  
      const themeToggle = document.createElement('button');
      themeToggle.className = 'btn theme-toggle';
      themeToggle.innerHTML = document.body.classList.contains('dark-theme') ? '☀️' : '🌙';
      themeToggle.style.position = 'fixed';
      themeToggle.style.bottom = '20px';
      themeToggle.style.left = '20px';
      themeToggle.onclick = this.toggleTheme;
      document.body.appendChild(themeToggle);
  
      const scrollBtn = document.createElement('button');
      scrollBtn.className = 'btn scroll-btn';
      scrollBtn.innerHTML = '↑';
      scrollBtn.style.position = 'fixed';
      scrollBtn.style.bottom = '20px';
      scrollBtn.style.right = '20px';
      scrollBtn.onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });
      document.body.appendChild(scrollBtn);
  
      const regionToggle = document.getElementById('region-toggle');
      const regionDropdown = document.getElementById('region-dropdown');
      if (regionToggle && regionDropdown) {
        regionToggle.addEventListener('click', () => {
          regionDropdown.style.display = regionDropdown.style.display === 'block' ? 'none' : 'block';
        });
        
        document.addEventListener('click', e => {
          if (!regionToggle.contains(e.target)) {
            regionDropdown.style.display = 'none';
          }
        });
      }
  
      const startDateInput = document.getElementById('start-date');
      const endDateInput = document.getElementById('end-date');
      
      if (startDateInput && endDateInput) {
        startDateInput.value = Utils.sanitizeDate(startDateInput.value);
        endDateInput.value = Utils.sanitizeDate(endDateInput.value);
        
        const handleDateChange = Utils.debounce(() => {
          const startDate = Utils.sanitizeDate(startDateInput.value);
          const endDate = Utils.sanitizeDate(endDateInput.value);
          const regions = Array.from(
            document.querySelectorAll('#region-dropdown input[type="checkbox"]:checked')
          ).map(cb => cb.value);
          
          DataService.loadFireData(startDate, endDate, regions);
        }, APP_CONFIG.DEBOUNCE.FILTERS);
        
        startDateInput.addEventListener('change', handleDateChange);
        endDateInput.addEventListener('change', handleDateChange);
      }
    }
  };
  
  // Инициализация приложения
  document.addEventListener('DOMContentLoaded', () => {
    UI.init();
    
    const startDate = Utils.sanitizeDate(document.getElementById('start-date')?.value);
    const endDate = Utils.sanitizeDate(document.getElementById('end-date')?.value);
    
    DataService.loadFireData(startDate, endDate);
    DataService.loadGeoJSON().catch(console.error);
  });
  
  // Оптимизация ресайза
  window.addEventListener('resize', Utils.debounce(() => {
    if (AppState.components.map) {
      AppState.components.map.invalidateSize();
    }
  }, APP_CONFIG.DEBOUNCE.RESIZE));