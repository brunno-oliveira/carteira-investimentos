import os
import tabula
import pandas as pd
import warnings
import numpy as np

pd.set_option("display.float_format", "{:.2f}".format)
warnings.simplefilter(action="ignore", category=FutureWarning)


class BancoInterRendaFixa:
    def run(self):
        self._load_data()
        self._extract_product()

        # Transform
        self._drop_columns()
        self._rename_columns()
        self._reorder_colums()
        self._transform_columns()
        print(self.df.shape)

    def _load_data(self):
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        banco_inter_path = os.path.join(data_path, "banco_inter")
        banco_inter_file = os.path.join(
            banco_inter_path, "extrato-posicao-renda-fixa.pdf"
        )

        print(f"Loading {banco_inter_file}")
        self.dfs = tabula.read_pdf(banco_inter_file, lattice=True)

    def _extract_product(self):
        """A leitura do arquivo PDF gera vários DF.
        Para cada novo PRODUTO de investimento é necessário
        rever essa lógica"""

        # CDB POS DI LIQUIDEZ DIARIA
        des_produto_cdi_pos_liquidez_diaria = self.dfs[2].columns[0]
        df_cdi_pos_liquidez_diaria = self.dfs[3]
        df_cdi_pos_liquidez_diaria = df_cdi_pos_liquidez_diaria[
            ~df_cdi_pos_liquidez_diaria["Nota"].isna()
        ]
        df_cdi_pos_liquidez_diaria["des_produto"] = des_produto_cdi_pos_liquidez_diaria

        # CRA ZILOR E16S1
        des_produto_cra_zilor_e16s1 = self.dfs[4].columns[0]
        df_cra_zilor_e16s1 = self.dfs[5]
        df_cra_zilor_e16s1 = df_cra_zilor_e16s1[~df_cra_zilor_e16s1["Nota"].isna()]
        df_cra_zilor_e16s1["des_produto"] = des_produto_cra_zilor_e16s1

        # DEBENTURE MNAU13
        des_debenture_mnau13 = self.dfs[6].columns[0]
        df_debenture_mnau13 = self.dfs[7]
        df_debenture_mnau13 = df_debenture_mnau13[~df_debenture_mnau13["Nota"].isna()]
        df_debenture_mnau13["des_produto"] = des_debenture_mnau13

        # LCA BOCOM
        des_lca_bocom = self.dfs[8].columns[0]
        df_lca_bocom = self.dfs[9]
        df_lca_bocom = df_lca_bocom[~df_lca_bocom["Nota"].isna()]
        df_lca_bocom["des_produto"] = des_lca_bocom

        # LCI DI LIQUIDEZ 90 DIAS
        des_lci_di_liquidez_90_dias = self.dfs[10].columns[0]
        df_lci_di_liquidez_90_dias = self.dfs[11]
        df_lci_di_liquidez_90_dias = df_lci_di_liquidez_90_dias[
            ~df_lci_di_liquidez_90_dias["Nota"].isna()
        ]
        df_lci_di_liquidez_90_dias["des_produto"] = des_lci_di_liquidez_90_dias

        self.df = pd.concat(
            [
                df_cdi_pos_liquidez_diaria,
                df_cra_zilor_e16s1,
                df_debenture_mnau13,
                df_lca_bocom,
                df_lci_di_liquidez_90_dias,
            ]
        )

        self.df["des_categoria_investimento"] = "Renda Fixa"

    def _drop_columns(self):
        self.df.drop(
            columns=[
                "Nota",
            ],
            inplace=True,
        )

    def _rename_columns(self):
        self.df.rename(
            columns={
                "Data Início": "dt_inicio",
                "Data\rVencimento": "dt_vencimento",
                "Valor\rAplicação": "vlr_aplicado",
                "Tipo\rAplicação": "tp_aplicacao",
                "Taxa\rAplicação": "taxa_aplicao",
                "Valor\rRendimento": "vlr_rendimento",
                "Valor\rRetirada": "vlr_retirada",
                "Valor\rDesconto": "vlr_desconto",
                "Valor\rBruto": "vlr_bruto",
                "Valor Previsão\rDesconto": "vlr_previsao_desconto",
                "Valor\rLíquido": "vlr_liquido",
                "IR/IOF": "vlr_ir_iof",
            },
            inplace=True,
        )

    def _reorder_colums(self):
        # fmt: off
        self.df = self.df[
            [
                "des_categoria_investimento", "des_produto", 
                "dt_inicio", "dt_vencimento", "vlr_aplicado", 
                "tp_aplicacao", "taxa_aplicao", "vlr_rendimento", 
                "vlr_retirada", "vlr_desconto", "vlr_bruto", 
                "vlr_previsao_desconto", "vlr_liquido", "vlr_ir_iof"
            ]
        ]
        # fmt:on

    def _transform_columns(self):
        self.df["des_produto"] = self.df["des_produto"].str.lstrip().str.rstrip()
        self.df["tp_aplicacao"] = self.df["tp_aplicacao"].str.lstrip().str.rstrip()
        self.df["taxa_aplicao"] = self.df["taxa_aplicao"].str.lstrip().str.rstrip()

        self.df["dt_inicio"] = pd.to_datetime(self.df["dt_inicio"], format="%d/%m/%Y")
        self.df["dt_vencimento"] = pd.to_datetime(
            self.df["dt_vencimento"], format="%d/%m/%Y"
        )

        self.df["vlr_aplicado"] = (
            self.df["vlr_aplicado"]
            .str.replace("R\$", "")
            .str.replace(".", "")
            .str.replace(",", ".")
            .astype(np.float32)
        )

        self.df["vlr_rendimento"] = (
            self.df["vlr_rendimento"]
            .str.replace("R\$", "")
            .str.replace(".", "")
            .str.replace(",", ".")
            .str.replace("-", "0")
            .astype(np.float32)
        )

        self.df["vlr_retirada"] = (
            self.df["vlr_retirada"]
            .str.replace("R\$", "")
            .str.replace(".", "")
            .str.replace(",", ".")
            .str.replace("-", "0")
            .astype(np.float32)
        )

        self.df["vlr_desconto"] = (
            self.df["vlr_desconto"]
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
            .astype(np.float32)
        )

        self.df["vlr_previsao_desconto"] = (
            self.df["vlr_previsao_desconto"]
            .str.replace("R\$", "")
            .str.replace(".", "")
            .str.replace(",", ".")
            .astype(np.float32)
        )

        self.df["vlr_liquido"] = (
            self.df["vlr_liquido"]
            .str.replace("R\$", "")
            .str.replace(".", "")
            .str.replace(",", ".")
            .astype(np.float32)
        )

        self.df["vlr_ir_iof"] = (
            self.df["vlr_ir_iof"]
            .str.replace("R\$", "")
            .str.replace(".", "")
            .str.replace(",", ".")
            .astype(np.float32)
        )
