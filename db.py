from typing import Any, Dict, List
from psycopg2 import connect, ProgrammingError
from psycopg2.extras import RealDictCursor
from flask import g
import os
import logging

_logger = logging.getLogger(__name__)


def get_db():
    if 'db' not in g:
        g.db = connect(
            host=os.environ['PGDB_HOST'],
            port=os.environ['PGDB_PORT'],
            database=os.environ['PGDB_NAME'],
            user=os.environ['PGDB_USER'],
            password=os.environ['PGDB_PASS']
        )
    return g.db


def search(query: str, params: tuple = None) -> List[Dict]:
    db = get_db()
    _logger.warning(f"Search query, params: {query}, {params}")
    with db.cursor(cursor_factory=RealDictCursor) as cr:
        cr.execute(query, params)
        res = cr.fetchall()
        _logger.warning(f"Search result: {res}")
    return res


def read(table_name: str, record_id: int, fields: tuple = None) -> Dict:
    to_select = '*'
    if fields:
        to_select = ','.join(list(map(lambda f: "\"{}\"".format(f), fields)))
    query = """select {} from {} where id=%s""".format(to_select, table_name)
    params = (record_id, )
    _logger.warning(f"Read query, params: {query}, {params}")
    db = get_db()
    with db.cursor(cursor_factory=RealDictCursor) as cr:
        cr.execute(query, params)
        res = cr.fetchone()
        _logger.warning(f"Read result: {res}")
    return res


def write(table_name: str, record_id: int,  **kwargs) -> int:
    if not kwargs:
        raise ValueError("No fields and values defined for updating record")
    db = get_db()
    fn, fp, fv, fu = _prepare_fields(**kwargs)
    fv.append(record_id)
    query = """update {} set {} where id=%s""".format(table_name, fu)
    _logger.warning(f"Modify query, params: {query}, {fv}")
    with db.cursor() as cr:
        cr.execute(query, fv)
    db.commit()
    return True


def create(table_name: str, return_id=True, **kwargs) -> int:
    """
    :return: New record ID
    """
    if not kwargs:
        raise ValueError("No fields and values defined for creating record")
    db = get_db()
    fn, fp, fv, fu = _prepare_fields(**kwargs)
    query = """insert into {} ({}) values ({}) {}""".format(table_name, fn, fp, 'returning id' if return_id else '')
    _logger.warning(f"Create query, params: {query}, {fv}")
    with db.cursor() as cr:
        cr.execute(query, fv)
        res = cr.fetchone()
        if type(res) in [tuple, list, set] and len(res) > 0:
            res = res[0]
        _logger.warning(f"Created record id: {res}")
    db.commit()
    return res


def unlink(table_name: str, record_id: int) -> bool:
    db = get_db()
    query = """delete from {} where id=%s""".format(table_name)
    params = (record_id, )
    _logger.warning(f"Delete query, params: {query}, {params}")
    try:
        with db.cursor() as cr:
            cr.execute(query, params)
    except ProgrammingError as pe:
        _logger.warning(f"Delete error: {str(pe)}")
        return False
    finally:
        db.commit()
    return True


def _prepare_fields(**kwargs) -> tuple:
    if not kwargs:
        raise ValueError('No kwargs defined for field parser')
    field_substitutions = ["%s"] * len(kwargs.keys())
    field_names_list = list(map(lambda f: "\"{}\"".format(f), kwargs.keys()))
    field_names = ','.join(field_names_list)
    field_updates = ','.join([f'{k}={v}' for k, v in dict(zip(field_names_list, field_substitutions)).items()])
    field_placeholders = ','.join(field_substitutions)
    field_values = list(kwargs.values())
    return field_names, field_placeholders, field_values, field_updates


