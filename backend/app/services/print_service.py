"""
Print Service — generates an HTML print-ready version of a passport.
The frontend can open this in a new tab and call window.print().
"""
from app.schemas.passport import PassportCardOut


def _val(v) -> str:
    return str(v) if v is not None else "—"


def generate_print_html(passport: PassportCardOut) -> str:
    v = passport.current_version
    if not v:
        return "<html><body><p>Нет данных для печати.</p></body></html>"

    d = v.device
    storages = "".join(
        f"<tr><td>{s.storage_kind}</td><td>{_val(s.controller_type)}</td>"
        f"<td>{_val(s.capacity_gb)} ГБ</td><td>{s.quantity}</td></tr>"
        for s in v.storage_devices
    )
    monitors = "".join(
        f"<tr><td>{_val(m.model)}</td><td>{_val(m.diagonal)}</td>"
        f"<td>{_val(m.serial_number)}</td><td>{_val(m.inventory_number)}</td></tr>"
        for m in v.monitors
    )
    peripherals = "".join(
        f"<tr><td>{p.peripheral_type}</td><td>{_val(p.model)}</td>"
        f"<td>{_val(p.serial_number)}</td><td>{_val(p.inventory_number)}</td></tr>"
        for p in v.peripherals
    )
    software = "".join(
        f"<tr><td>{s.software_name}</td><td>{_val(s.version)}</td>"
        f"<td>{_val(s.license_valid_until)}</td></tr>"
        for s in v.software_installations
    )

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Паспорт {_val(v.passport_number)}</title>
<style>
  body {{ font-family: Arial, sans-serif; font-size: 12px; margin: 20px; }}
  h1 {{ font-size: 16px; text-align: center; }}
  h2 {{ font-size: 13px; border-bottom: 1px solid #000; margin-top: 16px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
  th, td {{ border: 1px solid #999; padding: 4px 8px; text-align: left; }}
  th {{ background: #eee; }}
  .row {{ display: flex; gap: 20px; margin-bottom: 4px; }}
  .label {{ font-weight: bold; min-width: 160px; }}
  @media print {{ button {{ display: none; }} }}
</style>
</head>
<body>
<h1>Паспорт ПК / ноутбука № {_val(v.passport_number)}</h1>
<p style="text-align:center">UID: {passport.passport_uid} &nbsp;|&nbsp; Версия: {v.version_number}</p>

<h2>Сотрудник</h2>
<div class="row"><span class="label">ФИО:</span><span>{_val(v.employee_fio)}</span></div>
<div class="row"><span class="label">Должность:</span><span>{_val(v.position)}</span></div>
<div class="row"><span class="label">Подразделение:</span><span>{_val(v.department)}</span></div>
<div class="row"><span class="label">Кабинет:</span><span>{_val(v.room)}</span></div>
<div class="row"><span class="label">Ответственный:</span><span>{_val(v.responsible_fio)}</span></div>
<div class="row"><span class="label">Дата заполнения:</span><span>{_val(v.fill_date)}</span></div>

<h2>Устройство</h2>
{"".join([
    f'<div class="row"><span class="label">Тип:</span><span>{_val(d.device_type)}</span></div>',
    f'<div class="row"><span class="label">Модель:</span><span>{_val(d.model)}</span></div>',
    f'<div class="row"><span class="label">Серийный номер:</span><span>{_val(d.serial_number)}</span></div>',
    f'<div class="row"><span class="label">Инв. номер:</span><span>{_val(d.inventory_number)}</span></div>',
    f'<div class="row"><span class="label">Процессор:</span><span>{_val(d.cpu)}</span></div>',
    f'<div class="row"><span class="label">ОЗУ:</span><span>{_val(d.ram_gb)} ГБ</span></div>',
    f'<div class="row"><span class="label">Видеокарта:</span><span>{_val(d.gpu_model)} ({_val(d.gpu_type)})</span></div>',
]) if d else "<p>—</p>"}

<h2>Накопители</h2>
<table><tr><th>Тип</th><th>Интерфейс</th><th>Объём</th><th>Кол-во</th></tr>{storages or "<tr><td colspan=4>—</td></tr>"}</table>

<h2>Мониторы</h2>
<table><tr><th>Модель</th><th>Диагональ</th><th>Серийный №</th><th>Инв. №</th></tr>{monitors or "<tr><td colspan=4>—</td></tr>"}</table>

<h2>Периферия</h2>
<table><tr><th>Тип</th><th>Модель</th><th>Серийный №</th><th>Инв. №</th></tr>{peripherals or "<tr><td colspan=4>—</td></tr>"}</table>

<h2>Программное обеспечение</h2>
<table><tr><th>Название</th><th>Версия</th><th>Лицензия до</th></tr>{software or "<tr><td colspan=3>—</td></tr>"}</table>

<h2>Подписи</h2>
<div class="row"><span class="label">Подпись сотрудника:</span><span>{_val(v.user_signature)}</span></div>
<div class="row"><span class="label">Подпись техника:</span><span>{_val(v.tech_signature)}</span></div>

<br><button onclick="window.print()">🖨 Печать</button>
</body>
</html>"""
