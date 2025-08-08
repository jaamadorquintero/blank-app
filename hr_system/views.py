"""Vistas básicas para el sistema de RRHH."""
from datetime import datetime, date

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import (
    Base,
    AttendanceRecord,
    Payroll,
    Permit,
    Worker,
)

app = Flask(__name__)
engine = create_engine("sqlite:///hr.db")
Session = sessionmaker(bind=engine)


@app.route("/")
def index():
    """Página de inicio con accesos a los módulos principales."""
    return render_template("index.html")


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


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    app.run(debug=True)
