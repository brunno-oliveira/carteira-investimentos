import os
import pandas as pd
import warnings
import numpy as np

pd.set_option("display.float_format", "{:.2f}".format)
warnings.simplefilter(action="ignore", category=FutureWarning)


class TesouroDireto:
    def run(self):
        self._load_data()

        # Transform
        self._drop_columns()
        self._rename_columns()
        self._filter_data()
        self._transform_columns()
        print(self.df.shape)

    def _load_data(self):
        data_path = os.path.join(os.path.dirname(__file__), "data")
        b3_posicao = os.path.join(data_path, "b3_posicao")
        b3_arquivo = os.path.join(b3_posicao, "posicao-2023-02-03.xlsx")

        print(f"Loading {b3_arquivo}")
        self.df = pd.read_excel(b3_arquivo, sheet_name="Tesouro Direto")
        print(f"df.shape: {self.df.shape}")

    def _drop_columns(self):
        self.df.drop(
            columns=[
                "Instituição",
                "Código ISIN",
                "Quantidade Disponível",
                "Quantidade Indisponível",
                "Motivo",
                "Valor Atualizado",
            ],
            inplace=True,
        )

    def _rename_columns(self):
        self.df.rename(
            columns={
                "Produto": "des_produto",
                "Indexador": "indexador",
                "Vencimento": "dt_vencimento",
                "Quantidade": "quantidade",
                "Valor Aplicado": "vlr_aplicado",
                "Valor bruto": "vlr_bruto",
                "Valor líquido": "vlr_liquido",
            },
            inplace=True,
        )

    def _filter_data(self):
        self.df = self.df[
            (~self.df["des_produto"].isna()) & (~self.df["indexador"].isna())
        ]

    def _transform_columns(self):
        self.df["des_produto"] = self.df["des_produto"].str.lstrip().str.rstrip()
        self.df["indexador"] = self.df["indexador"].str.lstrip().str.rstrip()

        self.df["dt_vencimento"] = pd.to_datetime(
            self.df["dt_vencimento"], format="%d/%m/%Y"
        )

        self.df["quantidade"] = self.df["quantidade"].astype(np.int32)

        self.df["vlr_aplicado"] = self.df["vlr_aplicado"].astype(np.float32)
        self.df["vlr_bruto"] = self.df["vlr_bruto"].astype(np.float32)
        self.df["vlr_liquido"] = self.df["vlr_liquido"].astype(np.float32)

        self.df["tp_investimento"] = "Renda Fixa"


TesouroDireto().run()
