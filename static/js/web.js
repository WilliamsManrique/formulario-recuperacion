// Convertir código a mayúsculas automáticamente
        document.querySelector('input[name="codigo"]').addEventListener('input', function() {
            this.value = this.value.toUpperCase().replace(/[^A-Z0-9\-_]/g, '');
        });

        // Establecer fecha de mantenimiento por defecto (hoy + 30 días)
        document.addEventListener('DOMContentLoaded', function() {
            const hoy = new Date();
            const fechaMantenimiento = document.querySelector('input[name="fecha_mantenimiento"]');
            const fechaRegistro = document.querySelector('input[name="fecha_registro"]');
            
            // Fecha de mantenimiento por defecto: hoy + 30 días
            const fechaMant = new Date(hoy);
            fechaMant.setDate(fechaMant.getDate() + 30);
            
            if (fechaMantenimiento && !fechaMantenimiento.value) {
                fechaMantenimiento.value = fechaMant.toISOString().split('T')[0];
            }
            
            if (fechaRegistro) {
                fechaRegistro.value = hoy.toISOString().split('T')[0];
            }
            
            // Validación del formulario
            const formulario = document.querySelector('form');
            formulario.addEventListener('submit', function(event) {
                const codigo = document.querySelector('input[name="codigo"]').value.trim();
                const tipoEquipo = document.querySelector('select[name="tipo_equipo"]').value;
                const marca = document.querySelector('input[name="marca"]').value.trim();
                
                if (!codigo || !tipoEquipo || !marca) {
                    event.preventDefault();
                    alert('Por favor, complete los campos obligatorios (Código, Tipo de Equipo y Marca)');
                    return false;
                }
                
                return true;
            });
        });