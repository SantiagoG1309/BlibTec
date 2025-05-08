// Funciones de utilidad
const showMessage = (message, type = 'info') => {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} fade-in`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        setTimeout(() => alertDiv.remove(), 5000);
    }
};

// Mejoras en formularios
const enhanceFormValidation = () => {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            // Añadir clase de animación al focus
            input.addEventListener('focus', () => {
                input.classList.add('focused');
            });

            input.addEventListener('blur', () => {
                input.classList.remove('focused');
                // Validación básica
                if (input.required && !input.value) {
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });
        });

        // Prevenir envío múltiple
        form.addEventListener('submit', (e) => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = 'Procesando...';
            }
        });
    });
};

// Mejoras en tablas
const enhanceTables = () => {
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        // Hacer filas clickeables si tienen enlace
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

        // Ordenamiento de columnas
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            if (!header.classList.contains('no-sort')) {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => sortTable(table, index));
            }
        });
    });
};

// Función para ordenar tablas
const sortTable = (table, column) => {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAsc = table.querySelector('th').classList.contains('asc');

    // Limpiar clases de ordenamiento previas
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('asc', 'desc');
    });

    // Ordenar filas
    rows.sort((a, b) => {
        const aVal = a.cells[column].textContent.trim();
        const bVal = b.cells[column].textContent.trim();
        return isAsc ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
    });

    // Actualizar clase de ordenamiento
    table.querySelectorAll('th')[column].classList.add(isAsc ? 'desc' : 'asc');

    // Reordenar DOM
    rows.forEach(row => tbody.appendChild(row));
};

// Mejoras en la búsqueda
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

// Mejoras en la navegación
const enhanceNavigation = () => {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
};

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    enhanceFormValidation();
    enhanceTables();
    enhanceSearch();
    enhanceNavigation();

    // Manejar mensajes de Django
    const messages = document.querySelectorAll('.messages .alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.classList.add('fade-out');
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});

// Funcionalidad de préstamo
const handlePrestamo = () => {
    const prestamoButtons = document.querySelectorAll('.btn-prestamo');
    prestamoButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const libroId = button.dataset.libroId;
            try {
                const response = await fetch(`/prestamos/solicitar/${libroId}/`);
                if (response.ok) {
                    showMessage('Solicitud de préstamo enviada correctamente', 'success');
                    button.disabled = true;
                    button.textContent = 'Solicitado';
                } else {
                    showMessage('Error al solicitar el préstamo', 'danger');
                }
            } catch (error) {
                showMessage('Error de conexión', 'danger');
            }
        });
    });
};

// Inicializar funcionalidad de préstamo
document.addEventListener('DOMContentLoaded', handlePrestamo);