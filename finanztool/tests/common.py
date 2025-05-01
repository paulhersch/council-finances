import finanztool
from os.path import dirname
from pandas import read_csv


def load_templates():
    samples = dirname(finanztool.__file__) + "/csv_samples"
    templates = {
        f_name: read_csv(samples + f'/{f_name}.csv') for f_name in finanztool.lib.files.FILES
    }
    return templates


def templates_fixture(table):
    def ret(f):
        def wrapper(*args, **kwargs):
            templates = load_templates()
            return f(templates[table])
        return wrapper
    return ret
