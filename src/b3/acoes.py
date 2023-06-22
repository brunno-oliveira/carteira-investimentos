import os
import numpy as np
import pandas as pd
import warnings

try:
    from b3.setorial import Setorial
except ModuleNotFoundError:
    from setorial import Setorial

pd.set_option("display.float_format", "{:.2f}".format)
warnings.simplefilter(action="ignore", category=FutureWarning)


class Acoes:
    def run(self) -> pd.DataFrame:
        self._load_data()

        # Transform
        self._drop_columns()
        self._rename_columns()
        self._filter_data()
        self._merge_setor()
        self._transform_columns()
        self._reorder_colums()
        print(self.df.shape)
        return self.df

    def _load_data(self):
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        b3_posicao = os.path.join(data_path, "b3_posicao")
        b3_arquivo = os.path.join(b3_posicao, "posicao-2023-06-20.xlsx")

        print(f"Loading {b3_arquivo}")
        self.df = pd.read_excel(b3_arquivo, sheet_name="Acoes")
        print(f"df.shape: {self.df.shape}")

    def _drop_columns(self):
        self.df.drop(
            columns=[
                "Conta",
                "Código ISIN / Distribuição",
                "Escriturador",
                "Quantidade Disponível",
                "Quantidade Indisponível",
                "Motivo",
                "Preço de Fechamento",
            ],
            inplace=True,
        )

    def _rename_columns(self):
        self.df.rename(
            columns={
                "Produto": "des_produto",
                "Instituição": "des_conta",
                "Código de Negociação": "cod_acao",
                "Tipo": "tp_acao",
                "Quantidade": "quantidade",
                "Valor Atualizado": "vlr_total",
            },
            inplace=True,
        )

    def _filter_data(self):
        self.df = self.df[
            (~self.df["des_produto"].isna()) & (~self.df["des_conta"].isna())
        ]

    def _merge_setor(self):
        self.df["tmp_cod_acao"] = self.df["cod_acao"].str[0:4]
        self.df = pd.merge(
            self.df, Setorial.get_setorial(), left_on="tmp_cod_acao", right_on="codigo"
        )
        self.df.drop(
            columns=["tmp_cod_acao", "codigo"],
            inplace=True,
        )

        self.df["setor"] = self.df["setor"].str.lstrip().str.rstrip()
        self.df["subsetor"] = self.df["subsetor"].str.lstrip().str.rstrip()
        self.df["segmento"] = self.df["segmento"].str.lstrip().str.rstrip()
        self.df["listagem_segmento"] = (
            self.df["listagem_segmento"].str.lstrip().str.rstrip()
        )

    def _transform_columns(self):
        self.df["des_produto"] = self.df["des_produto"].str.lstrip().str.rstrip()
        self.df["des_produto"] = self.df["des_produto"].str[7:]
        self.df["des_produto"] = self.df["des_produto"].str.replace(
            "- TRANSMISSORA", "TRANSMISSORA"
        )

        self.df["des_conta"] = self.df["des_conta"].str.lstrip().str.rstrip()
        self.df["cod_acao"] = self.df["cod_acao"].str.lstrip().str.rstrip()
        self.df["tp_acao"] = self.df["tp_acao"].str.lstrip().str.rstrip()

        self.df["quantidade"] = self.df["quantidade"].astype(np.int32)
        self.df["vlr_total"] = self.df["vlr_total"].astype(np.float32)

        self.df["des_categoria_investimento"] = "Renda Variável"
        self.df["des_tipo_investimento"] = "Ações"

        # Porcentual da carteira
        self.df["vlr_total_carteira"] = self.df["vlr_total"].sum()
        self.df["pct_vlr_acao"] = (
            self.df["vlr_total"] / self.df["vlr_total_carteira"]
        ) * 100

        # Por Segmento
        df_group_setor = (
            self.df[["setor", "vlr_total"]]
            .groupby(["setor"])
            .sum()
            .reset_index()
            .rename(columns={"vlr_total": "vlr_total_setor"})
        )
        def_group_subsetor = (
            self.df[["subsetor", "vlr_total"]]
            .groupby(["subsetor"])
            .sum()
            .reset_index()
            .rename(columns={"vlr_total": "vlr_total_subsetor"})
        )
        df_group_segmento = (
            self.df[["segmento", "vlr_total"]]
            .groupby(["segmento"])
            .sum()
            .reset_index()
            .rename(columns={"vlr_total": "vlr_total_segmento"})
        )

        self.df = pd.merge(self.df, df_group_setor, on="setor")
        self.df = pd.merge(self.df, def_group_subsetor, on="subsetor")
        self.df = pd.merge(self.df, df_group_segmento, on="segmento")

        self.df["pct_vlr_total_setor"] = (
            self.df["vlr_total_setor"] / self.df["vlr_total_carteira"]
        ) * 100
        self.df["pct_vlr_total_subsetor"] = (
            self.df["vlr_total_subsetor"] / self.df["vlr_total_carteira"]
        ) * 100
        self.df["pct_vlr_total_segmento"] = (
            self.df["vlr_total_segmento"] / self.df["vlr_total_carteira"]
        ) * 100

    def _reorder_colums(self):
        self.df = self.df[
            [
                "des_categoria_investimento",
                "des_tipo_investimento",
                "des_conta",
                "setor",
                "subsetor",
                "segmento",
                "listagem_segmento",
                "tp_acao",
                "des_produto",
                "cod_acao",
                "quantidade",
                "vlr_total",
                "pct_vlr_acao",
                "vlr_total_setor",
                "pct_vlr_total_setor",
                "vlr_total_subsetor",
                "pct_vlr_total_subsetor",
                "vlr_total_segmento",
                "pct_vlr_total_segmento",
            ]
        ]
