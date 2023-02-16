import os
import tabula
import pandas as pd
import warnings
import numpy as np

pd.set_option("display.float_format", "{:.2f}".format)
warnings.simplefilter(action="ignore", category=FutureWarning)


class BancoInterFundos:
    def run(self):
        self._load_data()
        self._extract_product()

        # Transform
        self._rename_columns()
        self._reorder_colums()
        self._transform_columns()
        print(self.df.shape)

    def _load_data(self):
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        banco_inter_path = os.path.join(data_path, "banco_inter")
        banco_inter_file = os.path.join(banco_inter_path, "extrato-posicao-fundos.pdf")

        print(f"Loading {banco_inter_file}")
        self.dfs = tabula.read_pdf(banco_inter_file, lattice=True)

    def _extract_product(self):
        """A leitura do arquivo PDF gera vários DF.
        Para cada novo PRODUTO de investimento é necessário
        rever essa lógica"""

        # INTER CONSERVADOR FIRF CP
        des_produto = self.dfs[2].columns[0]
        self.df = pd.DataFrame(
            columns=self.dfs[2].iloc[0].values, data=[self.dfs[2].iloc[1].values]
        )
        self.df["des_produto"] = des_produto
        self.df["des_categoria_investimento"] = "Renda Variável"

    def _rename_columns(self):
        self.df.rename(
            columns={
                "Data Cotação": "dt_cotacao",
                "Qtde Cota": "qt_cota",
                "Valor Cota": "vlr_cota",
                "Valor Aplicado": "vlr_aplicado",
                "Valor Bruto": "vlr_bruto",
                "IR Previsto": "vlr_ir_previsto",
                "IOF Previsto": "vlr_iof_previsto",
                "Valor Liquido": "vlr_liquido",
            },
            inplace=True,
        )

    def _reorder_colums(self):
        # fmt: off
        self.df = self.df[
            [
                "des_categoria_investimento", "des_produto", 
                "dt_cotacao", "qt_cota", "vlr_cota", 
                "vlr_aplicado", "vlr_bruto", "vlr_ir_previsto", 
                "vlr_iof_previsto", "vlr_liquido"
            ]
        ]
        # fmt:on

    def _transform_columns(self):
        self.df["des_produto"] = self.df["des_produto"].str.lstrip().str.rstrip()

        self.df["dt_cotacao"] = pd.to_datetime(self.df["dt_cotacao"], format="%d/%m/%Y")

        self.df["qt_cota"] = (
            self.df["qt_cota"]
            .str.replace("R\$", "")
            .str.replace(".", "")
            .str.replace(",", ".")
            .astype(np.float32)
        )

        self.df["vlr_cota"] = (
            self.df["vlr_cota"]
            .str.replace("R\$", "")
            .str.replace(".", "")
            .str.replace(",", ".")
            .astype(np.float32)
        )

        self.df["vlr_aplicado"] = (
            self.df["vlr_aplicado"]
            .str.replace("R\$", "")
            .str.replace(".", "")
            .str.replace(",", ".")
            .str.replace("-", "0")
            .astype(np.float32)
        )

        self.df["vlr_bruto"] = (
            self.df["vlr_bruto"]
            .str.replace("R\$", "")
            .str.replace(".", "")
            .str.replace(",", ".")
            .str.replace("-", "0")
            .astype(np.float32)
        )

        self.df["vlr_ir_previsto"] = (
            self.df["vlr_ir_previsto"]
            .str.replace("R\$", "")
            .str.replace(".", "")
            .str.replace(",", ".")
            .str.replace("-", "0")
            .astype(np.float32)
        )

        self.df["vlr_iof_previsto"] = (
            self.df["vlr_iof_previsto"]
            .str.replace("R\$", "")
            .str.replace(".", "")
            .str.replace(",", ".")
            .str.replace("-", "0")
            .astype(np.float32)
        )

        self.df["vlr_liquido"] = (
            self.df["vlr_liquido"]
            .str.replace("R\$", "")
            .str.replace(".", "")
            .str.replace(",", ".")
            .astype(np.float32)
        )
