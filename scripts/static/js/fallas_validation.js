// Validación anti-duplicados de fallas - CRÍTICO
(function() {
    'use strict';
    
    const formFalla = document.getElementById('formNuevaFalla');
    const equipoTipoSelect = document.getElementById('equipo_tipo');
    const equipoIdSelect = document.getElementById('equipo_id');
    const btnEnviar = document.getElementById('btnEnviar');
    const alertaDuplicado = document.getElementById('alertaDuplicado');
    const mensajeDuplicado = document.getElementById('mensajeDuplicado');
    
    let fallaExistente = null;
    
    // Cargar equipos según tipo seleccionado
    if (equipoTipoSelect && equipoIdSelect) {
        equipoTipoSelect.addEventListener('change', function() {
            const tipo = this.value;
            equipoIdSelect.innerHTML = '<option value="">Seleccione...</option>';
            
            if (tipo && window.equiposData && window.equiposData[tipo]) {
                window.equiposData[tipo].forEach(equipo => {
                    const option = document.createElement('option');
                    option.value = equipo.id;
                    option.textContent = `${equipo.codigo} - ${equipo.nombre || 'Sin nombre'}`;
                    equipoIdSelect.appendChild(option);
                });
            }
            
            // Limpiar alerta al cambiar tipo
            alertaDuplicado.classList.add('d-none');
            btnEnviar.disabled = false;
        });
        
        // Validar al seleccionar equipo específico
        equipoIdSelect.addEventListener('change', function() {
            const equipoTipo = equipoTipoSelect.value;
            const equipoId = this.value;
            
            if (equipoTipo && equipoId) {
                validarFallaDuplicada(equipoTipo, equipoId);
            }
        });
    }
    
    // Función principal de validación anti-duplicados
    function validarFallaDuplicada(equipoTipo, equipoId) {
        // Mostrar loading
        btnEnviar.disabled = true;
        btnEnviar.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Validando...';
        
        // Llamada AJAX a la API de validación
        fetch(`/api/fallas/validar?equipo_tipo=${equipoTipo}&equipo_id=${equipoId}`)
            .then(response => response.json())
            .then(data => {
                if (!data.permitir) {
                    // Existe falla duplicada
                    mostrarAlertaDuplicado(data.mensaje);
                    btnEnviar.disabled = true;
                    btnEnviar.innerHTML = '<i class="bi bi-x-circle"></i> No se puede reportar (Falla Existente)';
                    fallaExistente = data.falla_existente;
                } else {
                    // OK, se puede reportar
                    ocultarAlertaDuplicado();
                    btnEnviar.disabled = false;
                    btnEnviar.innerHTML = '<i class="bi bi-check-circle"></i> Reportar Falla';
                    fallaExistente = null;
                }
            })
            .catch(error => {
                console.error('Error validando falla:', error);
                // En caso de error, permitir continuar pero mostrar advertencia
                btnEnviar.disabled = false;
                btnEnviar.innerHTML = '<i class="bi bi-check-circle"></i> Reportar Falla';
            });
    }
    
    // Mostrar alerta de duplicado
    function mostrarAlertaDuplicado(mensaje) {
        mensajeDuplicado.textContent = mensaje;
        alertaDuplicado.classList.remove('d-none');
        alertaDuplicado.classList.add('show');
        
        // Scroll a la alerta
        alertaDuplicado.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    // Ocultar alerta de duplicado
    function ocultarAlertaDuplicado() {
        alertaDuplicado.classList.add('d-none');
        alertaDuplicado.classList.remove('show');
    }
    
    // Validar antes de enviar formulario
    if (formFalla) {
        formFalla.addEventListener('submit', function(e) {
            const equipoTipo = equipoTipoSelect.value;
            const equipoId = equipoIdSelect.value;
            
            if (!equipoTipo || !equipoId) {
                e.preventDefault();
                alert('Debe seleccionar el tipo de equipo y el equipo específico');
                return false;
            }
            
            // Si hay falla existente, prevenir envío
            if (fallaExistente) {
                e.preventDefault();
                alert('No se puede reportar la falla porque ya existe una falla activa para este equipo. Debe cerrar o cancelar la falla anterior.');
                return false;
            }
        });
    }
    
})();
