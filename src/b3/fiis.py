import os
import numpy as np
import pandas as pd
import warnings

pd.set_option("display.float_format", "{:.2f}".format)
warnings.simplefilter(action="ignore", category=FutureWarning)


class FIIs:
    def run(self) -> pd.DataFrame:
        self._load_data()

        # Transform
        self._drop_columns()
        self._rename_columns()
        self._filter_data()
        self._transform_columns()
        self._reorder_colums()
        print(self.df.shape)
        return self.df

    def _load_data(self):
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        b3_posicao = os.path.join(data_path, "b3_posicao")
        b3_arquivo = os.path.join(b3_posicao, "posicao-2023-02-17.xlsx")

        print(f"Loading {b3_arquivo}")
        self.df = pd.read_excel(b3_arquivo, sheet_name="Fundo de Investimento")
        print(f"df.shape: {self.df.shape}")

    def _drop_columns(self):
        self.df.drop(
            columns=[
                "Conta",
                "Código ISIN / Distribuição",
                "Administrador",
                "Quantidade Disponível",
                "Quantidade Indisponível",
                "Motivo",
                "Preço de Fechamento",
                "Tipo",
            ],
            inplace=True,
        )

    def _rename_columns(self):
        self.df.rename(
            columns={
                "Produto": "des_produto",
                "Instituição": "des_conta",
                "Código de Negociação": "cod_acao",
                "Quantidade": "quantidade",
                "Valor Atualizado": "vlr_total",
            },
            inplace=True,
        )

    def _filter_data(self):
        self.df = self.df[
            (~self.df["des_produto"].isna()) & (~self.df["des_conta"].isna())
        ]

    def _transform_columns(self):
        self.df["des_produto"] = self.df["des_produto"].str.lstrip().str.rstrip()
        self.df["des_conta"] = self.df["des_conta"].str.lstrip().str.rstrip()
        self.df["vlr_total"] = self.df["vlr_total"].astype(np.float32)

        self.df["des_tipo"] = self.df["cod_acao"].map(
            {
                "BTLG11": "Tijolo",
                "KNRI11": "Tijolo",
                "XPML11": "Tijolo",
                "KNCA11": "Papel",
                "OUJP11": "Papel",
            }
        )

        self.df["des_segmento"] = self.df["cod_acao"].map(
            {
                "BTLG11": "Logística",
                "KNRI11": "Híbrido",
                "XPML11": "Shoppings",
                "KNCA11": "Títulos e Valores Mobiliários",
                "OUJP11": "Títulos e Valores Mobiliários",
            }
        )

        self.df["des_categoria_investimento"] = "Renda Variável"

    def _reorder_colums(self):
        # fmt: off
        self.df = self.df[
            [
                "des_categoria_investimento", "des_conta", 
                "des_tipo", "des_segmento", "des_produto", 
                "cod_acao", "quantidade", "vlr_total",
            ]
        ]
        # fmt: on