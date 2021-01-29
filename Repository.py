import atexit
import sqlite3
from DAO import _Clinics
from DAO import _Logistics
from DAO import _Suppliers
from DAO import _Vaccines

# The Repository
class _Repository:
    def __init__(self):
        self._conn = sqlite3.connect('database.db')
        self.Vaccines = _Vaccines(self._conn)
        self.Suppliers = _Suppliers(self._conn)
        self.Clinics = _Clinics(self._conn)
        self.Logistics = _Logistics(self._conn)

    def _close(self):
        self._conn.commit()
        self._conn.close()

    def create_tables(self):
        self._conn.executescript("""
        CREATE TABLE vaccines (
            id INTEGER PRIMARY KEY,
            date DATE NOT NULL,
            supplier INTEGER,
            quantity INTEGER NOT NULL,

            FOREIGN KEY(supplier) REFERENCES Supplier(id)
        );

        CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY,
            name STRING NOT NULL,
            logistic INTEGER,

            FOREIGN KEY(logistic) REFERENCES Logistic(id)
        );

        CREATE TABLE clinics (
            id INTEGER PRIMARY KEY,
            location STRING NOT NULL,
            demand INTEGER NOT NULL,
            logistic INTEGER,

            FOREIGN KEY(logistic) REFERENCES Logistic(id)
        );

        CREATE TABLE logistics (
            id INTEGER PRIMARY KEY,
            name STRING NOT NULL,
            count_sent INTEGER NOT NULL,
            count_received INTEGER NOT NULL
        );
    """)


# the repository singleton
repo = _Repository()
atexit.register(repo._close)