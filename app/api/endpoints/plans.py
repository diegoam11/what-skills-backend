from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, col
from app.core.database import get_session
from app.models.plan import Plan
from app.models.user import User
from app.api.endpoints.auth import get_current_user
from datetime import datetime, timedelta
from typing import List

router = APIRouter()

# Inicializar
@router.post("/seed", status_code=201)
def seed_plans(session: Session = Depends(get_session)):
    if session.exec(select(Plan)).first():
        return {"message": "Los planes ya existen."}

    plans_data = [
        Plan(code="TRIAL", name="Plan Trial", description="Prueba gratuita", price=0.0, duration_days=7, is_trial=True, display_order=1, features=["Acceso básico"]),
        Plan(code="MONTHLY", name="Plan Mensual", description="Pago mes a mes", price=29.90, duration_days=30, is_trial=False, display_order=2, features=["Acceso total"]),
        Plan(code="ANNUAL", name="Plan Anual", description="Ahorra 2 meses", price=299.00, duration_days=365, is_trial=False, display_order=3, features=["Mentoría incluida"])
    ]
    for plan in plans_data:
        session.add(plan)
    session.commit()
    return {"message": "Planes creados exitosamente."}

# CRUD PÚBLICO/ADMIN ---

@router.get("/", response_model=List[Plan])
def get_plans(session: Session = Depends(get_session)):
    """Devuelve todos los planes ordenados"""
    return session.exec(select(Plan).order_by(col(Plan.display_order))).all()

@router.post("/", response_model=Plan)
def create_plan(plan: Plan, session: Session = Depends(get_session)):
    """Crear un nuevo plan (Solo Admin debería poder)"""
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan

@router.put("/{plan_id}", response_model=Plan)
def update_plan(plan_id: int, plan_update: Plan, session: Session = Depends(get_session)):
    """Actualizar un plan existente"""
    db_plan = session.get(Plan, plan_id)
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    # Actualizamos campos
    plan_data = plan_update.model_dump(exclude_unset=True)
    for key, value in plan_data.items():
        
        if key != "id": 
            setattr(db_plan, key, value)
            
    session.add(db_plan)
    session.commit()
    session.refresh(db_plan)
    return db_plan

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, session: Session = Depends(get_session)):
    """Eliminar un plan"""
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    session.delete(plan)
    session.commit()
    return None

# SUSCRIPCIÓN DE USUARIO
@router.post("/subscribe/{plan_code}")
def subscribe_to_plan(
    plan_code: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    plan = session.exec(select(Plan).where(Plan.code == plan_code)).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    # Lógica de fechas
    now = datetime.utcnow()
    start_date = now
    if current_user.subscription_end and current_user.subscription_end > now:
        start_date = current_user.subscription_end # Sumar al final del actual

    new_end_date = start_date + timedelta(days=plan.duration_days)
    
    # Actualizar User
    current_user.plan_code = plan.code
    current_user.subscription_end = new_end_date
    current_user.subscription_status = "active"
    
    session.add(current_user)
    session.commit()
    
    return {"message": f"Suscrito a {plan.name}", "expires_at": new_end_date}

# CANCELAR SUSCRIPCIÓN
@router.post("/cancel")
def cancel_subscription(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Regresa al usuario al plan TRIAL inmediatamente (o podrías dejar que termine el periodo)"""
    trial = session.exec(select(Plan).where(Plan.code == "TRIAL")).first()
    if not trial:
        raise HTTPException(status_code=500, detail="Plan TRIAL no configurado")

    current_user.plan_code = "TRIAL"
    current_user.subscription_status = "cancelled"
    # Opcional: current_user.subscription_end = datetime.utcnow() 
    
    session.add(current_user)
    session.commit()
    return {"message": "Suscripción cancelada. Has vuelto al plan gratuito."}