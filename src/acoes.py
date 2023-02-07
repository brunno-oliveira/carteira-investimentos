import os
import numpy as np
import pandas as pd
pd.set_option('display.float_format', '{:.2f}'.format)

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class Acoes:
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
        self.df = pd.read_excel(b3_arquivo, sheet_name='Acoes')
        print(f"df.shape: {self.df.shape}")

    def _drop_columns(self):
        self.df.drop(columns=['Conta', 'Código ISIN / Distribuição', 'Escriturador', 
        'Quantidade Disponível', 'Quantidade Indisponível', 
        'Motivo', 'Preço de Fechamento'], inplace=True)

    def _rename_columns(self):
        self.df.rename(
            columns={
                'Produto' : 'des_produto',
                'Instituição' : 'des_conta',
                'Código de Negociação' : 'des_movimentacao',
                'Código de Negociação' : 'cod_acao',
                'Tipo' : 'tp_acao',
                'Quantidade' : 'quantidade',
                'Valor Atualizado' : 'vlr_total'
            }, 
            inplace=True
        )

    def _filter_data(self):
        self.df = self.df[(~self.df['des_produto'].isna()) & (~self.df['des_conta'].isna())]

    def _transform_columns(self):
        self.df['des_produto'] = self.df['des_produto'].str.lstrip().str.rstrip()
        self.df['des_produto'] = self.df['des_produto'].str[7:]
        self.df['des_produto'] = self.df['des_produto'].str.replace('- TRANSMISSORA', 'TRANSMISSORA')
        self.df['vlr_total'] = self.df['vlr_total'].astype(np.float32)        

Acoes().run()