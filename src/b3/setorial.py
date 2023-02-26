import os

import pandas as pd

pd.set_option("display.float_format", "{:.2f}".format)


class Setorial:
    @staticmethod
    def get_setorial() -> pd.DataFrame:
        """
        https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/acoes/consultas/classificacao-setorial/

        Returns:
            pd.DataFrame: _description_
        """
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        b3_setorial = os.path.join(data_path, "b3_setorial.csv")

        return pd.read_csv(b3_setorial, sep=";", encoding="latin")
