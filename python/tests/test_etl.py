"""
Pruebas unitarias para los componentes del módulo ETL.
"""

import unittest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.name_parser import parse_full_name
from src.excel_reader import sanitize_amount, clean_codigo, clean_dni, clean_date
from src.sql_generator import sql_escape_str, sql_escape_date, sql_escape_num, chunk_list


class TestNameParser(unittest.TestCase):
    def test_compound_paterno(self):
        pat, mat, nom = parse_full_name("DE LA CRUZ ALVARADO FLORENTINO")
        self.assertEqual(pat, "DE LA CRUZ")
        self.assertEqual(mat, "ALVARADO")
        self.assertEqual(nom, "FLORENTINO")

    def test_widow_materno(self):
        pat, mat, nom = parse_full_name("AGURTO SERQUEN VDA.DE SIPION GREGORIA")
        self.assertEqual(pat, "AGURTO")
        self.assertEqual(mat, "SERQUEN VDA.DE SIPION")
        self.assertEqual(nom, "GREGORIA")

    def test_particle_de_paz(self):
        pat, mat, nom = parse_full_name("ARRUNATEGUI DE PAZ GLORIA ROSALVA")
        self.assertEqual(pat, "ARRUNATEGUI")
        self.assertEqual(mat, "DE PAZ")
        self.assertEqual(nom, "GLORIA ROSALVA")

    def test_married_surname_in_materno(self):
        pat, mat, nom = parse_full_name("FERNANDEZ DIAZ DE VASQUEZ FELICITAS")
        self.assertEqual(pat, "FERNANDEZ")
        self.assertEqual(mat, "DIAZ DE VASQUEZ")
        self.assertEqual(nom, "FELICITAS")

    def test_santa_cruz(self):
        pat, mat, nom = parse_full_name("SANTA CRUZ SIGUENAS DE TORRES SILVIA")
        self.assertEqual(pat, "SANTA CRUZ")
        self.assertEqual(mat, "SIGUENAS DE TORRES")
        self.assertEqual(nom, "SILVIA")

    def test_two_words(self):
        pat, mat, nom = parse_full_name("PEREZ JUAN")
        self.assertEqual(pat, "PEREZ")
        self.assertIsNone(mat)
        self.assertEqual(nom, "JUAN")

    def test_single_word(self):
        pat, mat, nom = parse_full_name("RAMIREZ")
        self.assertEqual(pat, "RAMIREZ")
        self.assertIsNone(mat)
        self.assertIsNone(nom)

    def test_empty(self):
        pat, mat, nom = parse_full_name("")
        self.assertIsNone(pat)
        self.assertIsNone(mat)
        self.assertIsNone(nom)


class TestSanitizers(unittest.TestCase):
    def test_sanitize_amount(self):
        self.assertEqual(sanitize_amount("0,10"), 0.10)
        self.assertEqual(sanitize_amount("777,90"), 777.90)
        self.assertEqual(sanitize_amount("1,800,00"), 1800.00)
        self.assertEqual(sanitize_amount("46,202,00"), 46202.00)
        self.assertEqual(sanitize_amount("1.234,56"), 1234.56)
        self.assertEqual(sanitize_amount("1,234.56"), 1234.56)
        self.assertEqual(sanitize_amount(150.5), 150.50)
        self.assertEqual(sanitize_amount(None), 0.0)
        self.assertEqual(sanitize_amount(""), 0.0)

    def test_clean_codigo(self):
        self.assertEqual(clean_codigo("0212"), "0212")
        self.assertEqual(clean_codigo(8132.0), "8132")
        self.assertEqual(clean_codigo(None), None)

    def test_clean_dni(self):
        self.assertEqual(clean_dni("42758074"), "42758074")
        self.assertEqual(clean_dni("16527253.0"), "16527253")
        self.assertEqual(clean_dni("16527253.00"), "16527253")
        self.assertEqual(clean_dni(16527253.0), "16527253")
        self.assertEqual(clean_dni("12345"), "00012345")
        self.assertIsNone(clean_dni(None))

    def test_clean_date(self):
        self.assertEqual(clean_date("1980-03-06"), "1980-03-06")
        self.assertEqual(clean_date("06/03/1980"), "1980-03-06")
        self.assertEqual(clean_date("29286.00"), "1980-03-06")
        self.assertEqual(clean_date("35578.00"), "1997-05-28")
        self.assertEqual(clean_date("37319.00"), "2002-03-04")
        self.assertIsNone(clean_date("PERMANENTE"))
        self.assertIsNone(clean_date(0.0))
        self.assertIsNone(clean_date(None))


class TestSqlHelpers(unittest.TestCase):
    def test_sql_escape_str(self):
        self.assertEqual(sql_escape_str("O'CONNOR"), "'O''CONNOR'")
        self.assertEqual(sql_escape_str(None), "NULL")

    def test_sql_escape_date(self):
        self.assertEqual(sql_escape_date("1980-03-06"), "'1980-03-06'::date")
        self.assertEqual(sql_escape_date(None), "NULL::date")

    def test_chunk_list(self):
        items = list(range(12))
        chunks = list(chunk_list(items, 5))
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0], [0, 1, 2, 3, 4])
        self.assertEqual(chunks[1], [5, 6, 7, 8, 9])
        self.assertEqual(chunks[2], [10, 11])


if __name__ == "__main__":
    unittest.main()
