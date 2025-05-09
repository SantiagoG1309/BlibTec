// Función para mostrar mensajes
const showMessage = (message, type = 'info') => {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} fade-in`;
    alertDiv.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;

    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        setTimeout(() => {
            alertDiv.classList.add('fade-out');
            setTimeout(() => alertDiv.remove(), 300);
        }, 5000);
    }
};

// Validación visual de formularios
const enhanceFormValidation = () => {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('focus', () => input.classList.add('focused'));
            input.addEventListener('blur', () => {
                input.classList.remove('focused');
                if (input.required && !input.value.trim()) {
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });
        });

        form.addEventListener('submit', (e) => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
            }
        });
    });
};

// Mejoras en tablas (ordenamiento + filas clickeables)
const enhanceTables = () => {
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const link = row.querySelector('a');
            if (link) {
                row.style.cursor = 'pointer';
                row.addEventListener('click', (e) => {
                    if (!e.target.matches('a, button')) {
                        link.click();
                    }
                });
            }
        });

        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            if (!header.classList.contains('no-sort')) {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => sortTable(table, index));
            }
        });
    });
};

// Ordenar tabla por columna
const sortTable = (table, column) => {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAsc = table.querySelector('th').classList.contains('asc');

    table.querySelectorAll('th').forEach(th => th.classList.remove('asc', 'desc'));

    rows.sort((a, b) => {
        const aVal = a.cells[column].textContent.trim().toLowerCase();
        const bVal = b.cells[column].textContent.trim().toLowerCase();
        return isAsc ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
    });

    table.querySelectorAll('th')[column].classList.add(isAsc ? 'desc' : 'asc');

    rows.forEach(row => tbody.appendChild(row));
};

// Búsqueda con debounce
const enhanceSearch = () => {
    const searchInputs = document.querySelectorAll('input[type="search"]');
    searchInputs.forEach(input => {
        let timeout;
        input.addEventListener('input', (e) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                const form = input.closest('form');
                if (form) form.submit();
            }, 500);
        });
    });
};

// Activar enlace activo en navegación
const enhanceNavigation = () => {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
};

// Manejo de botones de préstamo
const handlePrestamo = () => {
    const prestamoButtons = document.querySelectorAll('.btn-prestamo');
    prestamoButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const libroId = button.dataset.libroId;
            try {
                const response = await fetch(`/prestamos/solicitar/${libroId}/`);
                if (response.ok) {
                    showMessage('<i class="fas fa-check-circle"></i> Solicitud enviada', 'success');
                    button.disabled = true;
                    button.innerHTML = '<i class="fas fa-hourglass-half"></i> Solicitado';
                } else {
                    showMessage('<i class="fas fa-exclamation-triangle"></i> Error al solicitar', 'danger');
                }
            } catch (error) {
                showMessage('<i class="fas fa-wifi-slash"></i> Problema de conexión', 'danger');
            }
        });
    });
};

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    enhanceFormValidation();
    enhanceTables();
    enhanceSearch();
    enhanceNavigation();
    handlePrestamo();

    // Eliminar mensajes antiguos
    const messages = document.querySelectorAll('.messages .alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.classList.add('fade-out');
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});