"""Vistas básicas para el sistema de RRHH."""
from datetime import datetime, date, timedelta

from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import (
    Base,
    AttendanceRecord,
    Incident,
    Payroll,
    Permit,
    PermitStatus,
    Worker,
)

app = Flask(__name__)
engine = create_engine("sqlite:///hr.db")
Session = sessionmaker(bind=engine)


@app.route("/admin/workers")
def admin_workers():
    """Vista general del personal."""
    session = Session()
    workers = session.query(Worker).order_by(Worker.full_name).all()
    return render_template("admin_dashboard.html", workers=workers)


@app.route("/reports/attendance")
def attendance_report():
    """Reporte básico de asistencia con filtros por trabajador."""
    worker_id = request.args.get("worker_id")
    session = Session()
    query = session.query(AttendanceRecord)
    if worker_id:
        query = query.filter_by(worker_id=worker_id)
    records = query.order_by(AttendanceRecord.check_in.desc()).all()
    return render_template("attendance_report.html", records=records)


@app.route("/permits/new", methods=["GET", "POST"])
def new_permit():
    """Formulario de solicitud de permisos."""
    session = Session()
    if request.method == "POST":
        permit = Permit(
            worker_id=request.form["worker_id"],
            permit_type=request.form["permit_type"],
            start=datetime.fromisoformat(request.form["start"]),
            end=datetime.fromisoformat(request.form["end"]),
            justification=request.form.get("justification"),
        )
        session.add(permit)
        session.commit()
        return jsonify({"status": "ok"})
    workers = session.query(Worker).all()
    return render_template("permit_form.html", workers=workers)


@app.route("/incidents", methods=["GET"])
def list_incidents():
    """Listado simple de incidencias."""
    session = Session()
    incidents = session.query(Incident).order_by(Incident.created_at.desc()).all()
    return render_template("incident_list.html", incidents=incidents)


@app.route("/incidents/new", methods=["GET", "POST"])
def new_incident():
    """Registro de incidencias."""
    session = Session()
    if request.method == "POST":
        incident = Incident(
            worker_id=request.form["worker_id"],
            incident_type=request.form["incident_type"],
            description=request.form.get("description"),
        )
        session.add(incident)
        session.commit()
        return jsonify({"status": "ok"})
    workers = session.query(Worker).all()
    return render_template("incident_form.html", workers=workers)


@app.route("/attendance/quick", methods=["POST"])
def quick_attendance():
    """Registro rápido de asistencia usando número de empleado."""
    employee_number = request.form["employee_number"]
    session = Session()
    worker = session.query(Worker).filter_by(employee_number=employee_number).first()
    if not worker:
        return jsonify({"status": "error", "message": "Empleado no encontrado"}), 404
    now = datetime.utcnow()
    today_start = datetime.combine(date.today(), datetime.min.time())
    record = (
        session.query(AttendanceRecord)
        .filter(
            AttendanceRecord.worker_id == worker.id,
            AttendanceRecord.check_in >= today_start,
        )
        .first()
    )
    if record and record.check_out is None:
        record.check_out = now
        message = "Salida registrada"
    else:
        record = AttendanceRecord(worker_id=worker.id, check_in=now)
        session.add(record)
        message = "Entrada registrada"
    session.commit()
    return jsonify({"status": "ok", "message": message, "timestamp": now.isoformat()})


def _calculate_payroll(session, worker, week_start):
    """Calcula la nómina semanal para un trabajador."""
    start_dt = datetime.combine(week_start, datetime.min.time())
    end_dt = start_dt + timedelta(days=7)
    records = (
        session.query(AttendanceRecord)
        .filter(
            AttendanceRecord.worker_id == worker.id,
            AttendanceRecord.check_in >= start_dt,
            AttendanceRecord.check_in < end_dt,
        )
        .all()
    )
    days_worked = len({r.check_in.date() for r in records if r.check_out})
    total_hours = sum(
        (r.check_out - r.check_in).total_seconds() / 3600
        for r in records
        if r.check_out
    )
    overtime_hours = max(0, total_hours - days_worked * 8)
    permits = (
        session.query(Permit)
        .filter(
            Permit.worker_id == worker.id,
            Permit.status == PermitStatus.APPROVED,
            Permit.start >= start_dt,
            Permit.end < end_dt,
        )
        .all()
    )
    permit_unpaid_hours = sum(
        (p.end - p.start).total_seconds() / 3600 for p in permits
    )
    base_salary = worker.daily_salary * days_worked
    overtime_pay = overtime_hours * worker.daily_salary / 8 * 1.5
    deductions = permit_unpaid_hours * worker.daily_salary / 8
    total_pay = base_salary + overtime_pay - deductions
    payroll = Payroll(
        worker_id=worker.id,
        week_start=start_dt.date(),
        base_salary=base_salary,
        days_worked=days_worked,
        overtime_hours=overtime_hours,
        overtime_rate=1.5,
        bonuses=0,
        deductions=deductions,
        permit_unpaid_hours=permit_unpaid_hours,
        total_pay=total_pay,
    )
    session.add(payroll)
    session.commit()
    return payroll, overtime_pay


@app.route("/payroll/calculate", methods=["GET", "POST"])
def calculate_payroll_view():
    """Formulario y resultado del cálculo de nómina semanal."""
    session = Session()
    if request.method == "POST":
        worker_id = int(request.form["worker_id"])
        week_start = datetime.fromisoformat(request.form["week_start"]).date()
        worker = session.get(Worker, worker_id)
        payroll, overtime_pay = _calculate_payroll(session, worker, week_start)
        return render_template(
            "payroll_report.html",
            worker=worker,
            payroll=payroll,
            overtime_pay=overtime_pay,
        )
    workers = session.query(Worker).all()
    return render_template("payroll_form.html", workers=workers)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    app.run(debug=True)
