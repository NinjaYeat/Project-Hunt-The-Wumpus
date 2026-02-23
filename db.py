#! /usr/bin/env python3
import os
import psycopg
from psycopg.rows import dict_row

def get_conn():
    return psycopg.connect(
        host=os.environ.get("DB_HOST", "student.endor.be"),
        port=int(os.environ.get("DB_PORT", "5433")),
        dbname=os.environ.get("DB_NAME", "py12"),
        user=os.environ.get("DB_USER", "py12"),
        password=os.environ.get("DB_PASSWORD", "baiglu06floivou"),
        row_factory=dict_row,
    )