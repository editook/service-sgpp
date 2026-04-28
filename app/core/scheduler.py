import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.core.database import SessionLocal
from app.models.case import Case

logger = logging.getLogger(__name__)

def check_alarms():
    """ Tarea diaria para la verificación y alerta de Casos """
    db: Session = SessionLocal()
    today = date.today()
    try:
        casos_activos = db.query(Case).filter(Case.estado == 'Activo').all()
        for caso in casos_activos:
            # Recreamos la logica de dias_reales en python para las alertas
            dias_reales = (today - caso.fecha_ingreso).days
            dias_faltantes = caso.plazo_dias - dias_reales
            
            if dias_faltantes == 5:
                logger.info(f"ALERTA: Faltan 5 días para vencimiento. Caso {caso.codigo_unico} - Perito ID {caso.perito_id}")
                # TODO: Enviar correo electronico real integrando smtp
            elif dias_faltantes < 0:
                logger.warning(f"VENCIDO: El Caso {caso.codigo_unico} (Perito ID {caso.perito_id}) ha superado su plazo inicial.")
                # TODO: Enviar notificación al sistema
    except Exception as e:
        logger.error(f"Error procesando alarmas CRON: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Ejecuta todos los dias a las 00:01 AM
    scheduler.add_job(check_alarms, CronTrigger(hour=0, minute=1))
    scheduler.start()
    logger.info("Scheduler de Notificaciones Automáticas iniciado.")
