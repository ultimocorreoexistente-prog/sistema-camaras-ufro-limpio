# services/notificacion_service.py
"""
Servicio de notificaciones
Maneja el envío de notificaciones por email, SMS y dentro del sistema
"""

import smtplib
import ssl
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os

class NotificacionService:
"""Servicio para manejar notificaciones"""

def __init__(self, db_session=None):
self.db = db_session

# Configuración de email
self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
self.smtp_user = os.environ.get('SMTP_USER', '')
self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
self.from_email = os.environ.get('FROM_EMAIL', 'noreply@ufrontera.cl')

# Configuración de SMS (ejemplo con servicio externo)
self.sms_api_key = os.environ.get('SMS_API_KEY', '')
self.sms_endpoint = os.environ.get('SMS_ENDPOINT', '')

def send_email(self, to_emails: List[str], subject: str, body: str,
html_body: str = None, attachments: List[Dict] = None) -> Dict[str, Any]:
"""
Envía un email con opciones avanzadas
"""
if not all([self.smtp_server, self.smtp_user, self.smtp_password]):
return {
'success': False,
'error': 'Configuración de SMTP incompleta'
}

try:
# Crear mensaje
msg = MimeMultipart('alternative')
msg['From'] = self.from_email
msg['To'] = ', '.join(to_emails)
msg['Subject'] = subject
msg['X-Priority'] = '3' # Normal priority

# Cuerpo del mensaje
if html_body:
# HTML version
html_part = MimeText(html_body, 'html', 'utf-8')
msg.attach(html_part)

# Text version
text_part = MimeText(body, 'plain', 'utf-8')
msg.attach(text_part)
else:
text_part = MimeText(body, 'plain', 'utf-8')
msg.attach(text_part)

# Adjuntos
if attachments:
for attachment in attachments:
with open(attachment['path'], 'rb') as f:
part = MimeBase('application', 'octet-stream')
part.set_payload(f.read())

encoders.encode_base64(part)
part.add_header(
'Content-Disposition',
f'attachment; filename= {attachment["filename"]}'
)
msg.attach(part)

# Enviar email
context = ssl.create_default_context()
with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
server.starttls(context=context)
server.login(self.smtp_user, self.smtp_password)
text = msg.as_string()
server.sendmail(self.from_email, to_emails, text)

# Registrar notificación
self._register_notification(
tipo='email',
destinatarios=to_emails,
asunto=subject,
contenido=html_body or body,
estado='enviado'
)

return {
'success': True,
'message': f'Email enviado a {len(to_emails)} destinatario(s)'
}

except Exception as e:
# Registrar error
self._register_notification(
tipo='email',
destinatarios=to_emails,
asunto=subject,
contenido=html_body or body,
estado='error',
error=str(e)
)

return {
'success': False,
'error': f'Error enviando email: {str(e)}'
}

def send_sms(self, phone_numbers: List[str], message: str) -> Dict[str, Any]:
"""
Envía SMS (requiere configuración de servicio externo)
"""
if not self.sms_api_key:
return {
'success': False,
'error': 'API de SMS no configurada'
}

try:
sent_count = 0
errors = []

for phone in phone_numbers:
try:
# Aquí iría la implementación específica del servicio de SMS
# Ejemplo genérico:
payload = {
'to': phone,
'message': message,
'api_key': self.sms_api_key
}

# Hacer petición HTTP al servicio de SMS
# response = requests.post(self.sms_endpoint, json=payload)

sent_count += 1

except Exception as e:
errors.append(f'Error enviando SMS a {phone}: {str(e)}')

# Registrar notificación
self._register_notification(
tipo='sms',
destinatarios=phone_numbers,
asunto='SMS',
contenido=message,
estado='enviado' if sent_count > 0 else 'error'
)

return {
'success': sent_count > 0,
'sent_count': sent_count,
'errors': errors
}

except Exception as e:
return {
'success': False,
'error': f'Error enviando SMS: {str(e)}'
}

def send_system_notification(self, user_id: int, title: str, message: str,
type: str = 'info', data: Dict = None) -> bool:
"""
Envía notificación dentro del sistema
"""
try:
self.db.execute(
"""
INSERT INTO notificaciones (user_id, titulo, mensaje, tipo, data, created_at)
VALUES (%s, %s, %s, %s, %s, %s)
""",
(user_id, title, message, type, json.dumps(data or {}), datetime.now())
)
self.db.commit()
return True

except Exception as e:
print(f"Error enviando notificación del sistema: {e}")
self.db.rollback()
return False

def notify_failure(self, failure_data: Dict) -> Dict[str, Any]:
"""
Envía notificaciones específicas para fallas
"""
results = []

# Obtener usuarios que deben ser notificados
notify_users = self.db.execute(
"""
SELECT u.* FROM usuarios u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id
WHERE r.notifications_failure = true AND u.activo = true
"""
).fetchall()

if not notify_users:
return {
'success': False,
'error': 'No hay usuarios configurados para recibir notificaciones de fallas'
}

# Preparar contenido
subject = f" Nueva Falla Reportada: {failure_data.get('titulo', 'Sin título')}"

# Email HTML
html_body = f"""
<html>
<body>
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
<h style="color: #d3ff;"> Nueva Falla Reportada</h>

<div style="background-color: #f5f5f5; padding: 0px; border-radius: 5px; margin: 0px 0;">
<h3 style="margin-top: 0; color: #333;">Detalles de la Falla</h3>

<p><strong>Título:</strong> {failure_data.get('titulo', 'N/A')}</p>
<p><strong>Descripción:</strong> {failure_data.get('descripcion', 'N/A')}</p>
<p><strong>Severidad:</strong>
<span style="color: {'#d3ff' if failure_data.get('severidad') == 'alta' else '#ff9800' if failure_data.get('severidad') == 'media' else '#4caf50'}; font-weight: bold;">
{failure_data.get('severidad', 'N/A').upper()}
</span>
</p>
<p><strong>Cámara:</strong> {failure_data.get('camara', 'N/A')}</p>
<p><strong>Fecha de reporte:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
<p><strong>Reportado por:</strong> {failure_data.get('reportado_por', 'N/A')}</p>
</div>

<p>Por favor, revise el sistema para más detalles y tomar las acciones necesarias.</p>

<div style="margin-top: 30px; padding-top: 0px; border-top: 1px solid #eee; color: #666; font-size: 1px;">
<p>Este es un mensaje automático del Sistema de Cámaras UFRO.</p>
</div>
</div>
</body>
</html>
"""

# Texto plano
text_body = f"""
NUEVA FALLA REPORTADA

Título: {failure_data.get('titulo', 'N/A')}
Descripción: {failure_data.get('descripcion', 'N/A')}
Severidad: {failure_data.get('severidad', 'N/A').upper()}
Cámara: {failure_data.get('camara', 'N/A')}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Reportado por: {failure_data.get('reportado_por', 'N/A')}

Por favor, revise el sistema para más detalles.
"""

# Enviar emails
for user in notify_users:
try:
email_result = self.send_email(
to_emails=[user.email],
subject=subject,
body=text_body,
html_body=html_body
)

# También enviar notificación interna
self.send_system_notification(
user_id=user.id,
title="Nueva Falla Reportada",
message=f"Falla: {failure_data.get('titulo', '')} - Severidad: {failure_data.get('severidad', '').upper()}",
type='failure',
data=failure_data
)

results.append({
'user_id': user.id,
'email': user.email,
'success': email_result['success'],
'error': email_result.get('error')
})

except Exception as e:
results.append({
'user_id': user.id,
'email': user.email,
'success': False,
'error': str(e)
})

return {
'success': True,
'results': results,
'total_notifications': len(results)
}

def notify_maintenance(self, maintenance_data: Dict, users_to_notify: List[int] = None) -> Dict[str, Any]:
"""
Envía notificaciones de mantenimiento programado
"""
if not users_to_notify:
# Obtener usuarios por defecto
users_to_notify = [u.id for u in self.db.execute(
"SELECT id FROM usuarios WHERE activo = true"
).fetchall()]

results = []

subject = f" Mantenimiento Programado: {maintenance_data.get('tipo', 'General')}"

html_body = f"""
<html>
<body>
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
<h style="color: #1976d;"> Mantenimiento Programado</h>

<div style="background-color: #e3ffd; padding: 0px; border-radius: 5px; margin: 0px 0;">
<h3 style="margin-top: 0; color: #333;">Detalles del Mantenimiento</h3>

<p><strong>Tipo:</strong> {maintenance_data.get('tipo', 'N/A')}</p>
<p><strong>Descripción:</strong> {maintenance_data.get('descripcion', 'N/A')}</p>
<p><strong>Cámaras afectadas:</strong> {maintenance_data.get('camaras_afectadas', 'N/A')}</p>
<p><strong>Fecha programada:</strong> {maintenance_data.get('fecha_programada', 'N/A')}</p>
<p><strong>Duración estimada:</strong> {maintenance_data.get('duracion_estimada', 'N/A')}</p>
<p><strong>Técnico responsable:</strong> {maintenance_data.get('tecnico', 'N/A')}</p>
</div>

<p style="color: #d3ff; font-weight: bold;">
Durante el mantenimiento, los sistemas pueden experimentar interrupciones temporales.
</p>
</div>
</body>
</html>
"""

for user_id in users_to_notify:
user = self.db.execute(
"SELECT * FROM usuarios WHERE id = %s", (user_id,)
).fetchone()

if user:
email_result = self.send_email(
to_emails=[user.email],
subject=subject,
body=html_body,
html_body=html_body
)

self.send_system_notification(
user_id=user_id,
title="Mantenimiento Programado",
message=f"{maintenance_data.get('tipo', '')} - {maintenance_data.get('fecha_programada', '')}",
type='maintenance',
data=maintenance_data
)

results.append({
'user_id': user_id,
'email': user.email,
'success': email_result['success']
})

return {
'success': True,
'results': results
}

def _register_notification(self, tipo: str, destinatarios: List[str],
asunto: str, contenido: str, estado: str,
error: str = None) -> bool:
"""
Registra una notificación en la base de datos
"""
try:
self.db.execute(
"""
INSERT INTO notificaciones_log (
tipo, destinatarios, asunto, contenido, estado, error, created_at
) VALUES (%s, %s, %s, %s, %s, %s, %s)
""",
(tipo, json.dumps(destinatarios), asunto, contenido, estado, error, datetime.now())
)
self.db.commit()
return True

except Exception as e:
print(f"Error registrando notificación: {e}")
self.db.rollback()
return False

def get_user_notifications(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
"""
Obtiene notificaciones de un usuario
"""
try:
results = self.db.execute(
"""
SELECT * FROM notificaciones
WHERE user_id = %s
ORDER BY created_at DESC
LIMIT %s
""",
(user_id, limit)
).fetchall()

return [{
'id': row.id,
'titulo': row.titulo,
'mensaje': row.mensaje,
'tipo': row.tipo,
'data': json.loads(row.data) if row.data else {},
'read_at': row.read_at,
'created_at': row.created_at
} for row in results]

except Exception as e:
print(f"Error obteniendo notificaciones: {e}")
return []

def mark_notification_read(self, notification_id: int, user_id: int) -> bool:
"""
Marca una notificación como leída
"""
try:
self.db.execute(
"""
UPDATE notificaciones
SET read_at = %s
WHERE id = %s AND user_id = %s
""",
(datetime.now(), notification_id, user_id)
)
self.db.commit()
return True

except Exception as e:
print(f"Error marcando notificación como leída: {e}")
self.db.rollback()
return False

def get_notification_statistics(self) -> Dict[str, Any]:
"""
Obtiene estadísticas de notificaciones
"""
try:
stats = {}

# Total de notificaciones por tipo
tipos = self.db.execute("""
SELECT tipo, COUNT(*) as cantidad
FROM notificaciones_log
GROUP BY tipo
""").fetchall()

stats['por_tipo'] = {row.tipo: row.cantidad for row in tipos}

# Total por estado
estados = self.db.execute("""
SELECT estado, COUNT(*) as cantidad
FROM notificaciones_log
GROUP BY estado
""").fetchall()

stats['por_estado'] = {row.estado: row.cantidad for row in estados}

# Notificaciones de las últimas 4 horas
yesterday = datetime.now() - timedelta(days=1)
recent = self.db.execute(
"SELECT COUNT(*) FROM notificaciones_log WHERE created_at >= %s",
(yesterday,)
).fetchone()[0]

stats['ultimas_4h'] = recent

return stats

except Exception as e:
print(f"Error obteniendo estadísticas: {e}")
return {}