import os
import tabula
import pandas as pd
import warnings
import numpy as np

pd.set_option("display.float_format", "{:.2f}".format)
warnings.simplefilter(action="ignore", category=FutureWarning)


class BancoInterRendaFixa:
    def run(self) -> pd.DataFrame:
        self._load_data()
        self._extract_product()

        # Transform
        self._drop_columns()
        self._rename_columns()
        self._transform_columns()
        self._reorder_colums()
        print(self.df.shape)
        return self.df

    def _load_data(self):
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        banco_inter_path = os.path.join(data_path, "banco_inter")
        banco_inter_file = os.path.join(
            banco_inter_path, "extrato-posicao-renda-fixa.pdf"
        )

        print(f"Loading {banco_inter_file}")
        self.dfs = tabula.read_pdf(banco_inter_file, lattice=True, pages="all")

    def _extract_product(self):
        """A leitura do arquivo PDF gera vários DF.
        A lógica começa pulando os dois primeiros DFs da lista
        pois são informações de cabeçalho.
        """

        list_des_produto = []
        list_df_conteudo = []
        inicio_produtos = 2
        for index in range(inicio_produtos, len(self.dfs)):
            if index % 2 == 0:
                list_des_produto.append(self.dfs[index].columns[0].upper())
            else:
                list_df_conteudo.append(self.dfs[index])

        list_df_renda_fixa = []
        for des_produto, df_conteudo in zip(list_des_produto, list_df_conteudo):
            df_tmp = df_conteudo.copy()
            """Produtos com mais de uma nota (investimentos em datas diferente)
            possuem mais de uma linha de registro e sempre aparece uma linha em branco.
            """
            df_tmp = df_tmp[~df_tmp["Nota"].isna()]

            df_tmp["des_produto"] = des_produto
            if "CDB" in des_produto:
                df_tmp["subsetor"] = "CDB"
            elif "CRA" in des_produto:
                df_tmp["subsetor"] = "CRA"
            elif "CRI" in des_produto:
                df_tmp["subsetor"] = "CRI"
            elif "DEBENTURE" in des_produto:
                df_tmp["subsetor"] = "DEBENTURE"
            elif "LCA" in des_produto:
                df_tmp["subsetor"] = "LCA"
            elif "LCI" in des_produto:
                df_tmp["subsetor"] = "LCI"
            elif "CANAIS DE ATENDIMENTO INTER" in des_produto:
                pass
            else:
                raise Exception(f"Produto {des_produto} ainda nao configurado.")
            list_df_renda_fixa.append(df_tmp)

        self.df = pd.concat(list_df_renda_fixa).reset_index().drop(columns="index")
        self.df["des_categoria_investimento"] = "Renda Fixa"
        self.df["setor"] = "OUTROS"

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
            .str.replace("%", "")
            .str.replace(".", "")
            .str.replace(",", ".")
            .astype(np.float32)
        )

    def _reorder_colums(self):
        self.df = self.df[
            [
                "des_categoria_investimento",
                "setor",
                "subsetor",
                "des_produto",
                "dt_inicio",
                "dt_vencimento",
                "vlr_aplicado",
                "tp_aplicacao",
                "taxa_aplicao",
                "vlr_rendimento",
                "vlr_retirada",
                "vlr_desconto",
                "vlr_bruto",
                "vlr_previsao_desconto",
                "vlr_liquido",
                "vlr_ir_iof",
            ]
        ]


BancoInterRendaFixa().run()
