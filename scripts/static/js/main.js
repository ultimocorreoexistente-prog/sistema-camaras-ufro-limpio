// JavaScript principal del sistema
(function() {
    'use strict';
    
    // Confirmar eliminaciones
    const botonesEliminar = document.querySelectorAll('[data-action="delete"]');
    botonesEliminar.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('¿Está seguro de que desea eliminar este elemento?')) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Auto-dismiss de alertas
    const alertas = document.querySelectorAll('.alert:not(.alert-permanent)');
    alertas.forEach(alerta => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alerta);
            bsAlert.close();
        }, 5000);
    });
    
    // Validación de formularios
    const formularios = document.querySelectorAll('.needs-validation');
    Array.from(formularios).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
})();
