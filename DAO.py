import DTO

# Data Access Objects:
class _Vaccines:
    def __init__(self, _conn):
        self._conn = _conn

    def insert(self, vaccine):
        self._conn.execute("""
               INSERT INTO vaccines (id, date, supplier, quantity) VALUES (?, ?, ?, ?)
           """, (vaccine.id, vaccine.date, vaccine.supplier, vaccine.quantity))

    def get_max_id(self):
        cursor = self._conn.cursor()
        cursor.execute("SELECT id FROM vaccines WHERE id = (SELECT MAX(id) FROM vaccines)")
        max_id = cursor.fetchone()[0]
        return max_id

    def get_vaccines_quantities(self):
        return self._conn.execute("""
                   SELECT vaccines.quantity FROM vaccines
                   """).fetchall()

    def get_vaccines_dates(self):
        return self._conn.execute("SELECT date FROM vaccines").fetchall()

    def update_quantity(self, vaccine, new_amount):
        self._conn.execute("UPDATE vaccines SET quantity = (?) WHERE id = (?)", [new_amount, vaccine.id])

    def get_vaccines(self):
        all_vaccines = self._conn.execute("SELECT * FROM vaccines").fetchall()
        return [DTO.Vaccine(*vac) for vac in all_vaccines]

    def delete_vac(self, vaccine):
        self._conn.execute("DELETE FROM vaccines WHERE id = ?", [vaccine.id])


class _Suppliers:
    def __init__(self, _conn):
        self._conn = _conn

    def insert(self, supplier):
        self._conn.execute("""
               INSERT INTO suppliers (id, name, logistic) VALUES (?, ?, ?)
           """, (supplier.id, supplier.name, supplier.logistic))

    def get_id(self, name_):
        cursor = self._conn.cursor()
        cursor.execute("SELECT id FROM suppliers WHERE name = (?)", [name_])
        return cursor.fetchone()[0]

    def get_logistic(self, name_):
        cursor = self._conn.cursor()
        cursor.execute("SELECT logistic FROM suppliers WHERE name = (?)", [name_])
        return cursor.fetchone()[0]


class _Clinics:
    def __init__(self, _conn):
        self._conn = _conn

    def insert(self, clinic):
        self._conn.execute("""
               INSERT INTO clinics (id, location, demand, logistic) VALUES (?, ?, ?, ?)
           """, (clinic.id, clinic.location, clinic.demand, clinic.logistic))

    def get_clinics_demands(self):
        return self._conn.execute("""
            SELECT demand FROM clinics
            """).fetchall()

    def get_clinic_id_by_location(self, location):
        cursor = self._conn.cursor()
        cursor.execute("SELECT id FROM clinics WHERE location = (?)", [location])
        return cursor.fetchone()[0]

    def reduce_demand(self, id_, amount):
        cursor = self._conn.cursor()
        cursor.execute("SELECT demand FROM clinics WHERE id = (?)", [id_])
        curr_demand = cursor.fetchone()[0]
        self._conn.execute("UPDATE clinics SET demand = (?) WHERE id = (?)", [curr_demand - amount, id_])

    def get_logistic(self, id_):
        cursor = self._conn.cursor()
        cursor.execute("SELECT logistic FROM clinics WHERE id = (?)", [id_])
        return cursor.fetchone()[0]


class _Logistics:
    def __init__(self, _conn):
        self._conn = _conn

    def insert(self, logistic):
        self._conn.execute("""
               INSERT INTO logistics (id, name, count_sent, count_received) VALUES (?, ?, ?, ?)
           """, (logistic.id, logistic.name, logistic.count_sent, logistic.count_received))

    def get_current_amount_received(self, log_id):
        cursor = self._conn.cursor()
        cursor.execute("SELECT count_received FROM logistics WHERE id = (?)", [log_id])
        return int(cursor.fetchone()[0])

    def update_count_received(self, current_amount, amount, log_id):
        self._conn.execute("""
                       UPDATE logistics SET count_received = (?) WHERE id = (?)         
        """, [amount + current_amount, log_id])

    def update_count_sent(self, amount, log_id):
        cursor = self._conn.cursor()
        cursor.execute("SELECT count_sent FROM logistics WHERE id = (?)", [log_id])
        curr_count_sent = cursor.fetchone()[0]
        self._conn.execute("UPDATE logistics SET count_sent = (?) WHERE id = (?)", [curr_count_sent + amount, log_id])

    def get_logistics_count_received(self):
        return self._conn.execute("""
            SELECT count_received FROM logistics
            """).fetchall()

    def get_logistics_count_sent(self):
        return self._conn.execute("""
            SELECT count_sent FROM logistics
            """).fetchall()






