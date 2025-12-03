import pandas as pd
import numpy as np
import os
from glob import glob
import re

# Configuração para visualização
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

class DataNormalizer:
    def __init__(self):
        self.idhm_data = []
        self.nascimentos_data = []
        
    def load_idhm_files(self, file_patterns):
        """Carrega e normaliza todos os arquivos de IDHM"""
        print("Carregando dados de IDHM...")
        
        # Mapeamento de anos baseado nos nomes dos arquivos
        year_mapping = {
            'data.xlsx': 2000,
            'data (1).xlsx': 2010,
            'data (2).xlsx': 2017,
            'data (3).xlsx': 2018,
            'data (4).xlsx': 2019,
            'data (5).xlsx': 2020,
            'data (6).xlsx': 2021,
            'data (7).xlsx': 2022
        }
        
        for file_pattern in file_patterns:
            files = glob(file_pattern)
            for file in files:
                file_name = os.path.basename(file)
                
                # Pular se não for arquivo Excel
                if not file_name.endswith('.xlsx'):
                    continue
                    
                year = year_mapping.get(file_name, 2000)
                
                try:
                    df = pd.read_excel(file)
                    df['Ano'] = year
                    self.idhm_data.append(df)
                    print(f"✓ {file_name} - {year} carregado")
                except Exception as e:
                    print(f"✗ Erro ao carregar {file_name}: {e}")
    
    def load_nascimentos_files(self, file_patterns):
        """Carrega e normaliza todos os arquivos de nascimentos"""
        print("\nCarregando dados de nascimentos...")
        
        # Mapeamento de anos baseado nos nomes dos arquivos CSV
        csv_year_mapping = {
            'sinasc_cnv_nvuf133906177_1_252_233.csv': 2000,
            'sinasc_cnv_nvuf133948177_1_252_233.csv': 2010,
            'sinasc_cnv_nvuf134057177_1_252_233.csv': 2016,
            'sinasc_cnv_nvuf134117177_1_252_233.csv': 2017,
            'sinasc_cnv_nvuf134132177_1_252_233.csv': 2018,
            'sinasc_cnv_nvuf134154177_1_252_233.csv': 2019,
            'sinasc_cnv_nvuf134252177_1_252_233.csv': 2020,
            'sinasc_cnv_nvuf134305177_1_252_233.csv': 2021
        }
        
        for file_pattern in file_patterns:
            files = glob(file_pattern)
            for file in files:
                file_name = os.path.basename(file)
                
                # Pular se não for arquivo CSV
                if not file_name.startswith('sinasc_cnv_nvuf'):
                    continue
                    
                try:
                    # Usar mapeamento direto para os anos
                    year = csv_year_mapping.get(file_name, 2000)
                    
                    # Tentar diferentes encodings
                    encodings = ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8']
                    
                    for encoding in encodings:
                        try:
                            # Ler arquivo CSV
                            df = pd.read_csv(file, encoding=encoding, sep=';', 
                                           skiprows=3, skipfooter=10, engine='python',
                                           na_values=['-', '..', '...', ''],  # Tratar valores especiais
                                           thousands='.')
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        print(f"✗ Não foi possível ler {file_name} com nenhum encoding")
                        continue
                    
                    # Limpar nomes das colunas
                    df.columns = [str(col).strip().replace('"', '') for col in df.columns]
                    
                    # Adicionar ano CORRETO
                    df['Ano'] = year
                    
                    self.nascimentos_data.append(df)
                    print(f"✓ {file_name} - {year} carregado")
                    
                except Exception as e:
                    print(f"✗ Erro ao carregar {file_name}: {e}")
    
    def normalize_idhm_data(self):
        """Normaliza os dados de IDHM"""
        print("\nNormalizando dados de IDHM...")
        
        all_idhm = []
        for df in self.idhm_data:
            # Verificar e padronizar nomes das colunas
            df_clean = df.copy()
            
            # Renomear colunas para padrão
            column_mapping = {
                'Territorialidade': 'Estado',
                'Posição IDHM': 'Posicao_IDHM',
                'IDHM': 'IDHM',
                'Posição IDHM Renda': 'Posicao_Renda',
                'IDHM Renda': 'IDHM_Renda',
                'Posição IDHM Educação': 'Posicao_Educacao',
                'IDHM Educação': 'IDHM_Educacao',
                'Posição IDHM Longevidade': 'Posicao_Longevidade',
                'IDHM Longevidade': 'IDHM_Longevidade'
            }
            
            # Aplicar mapeamento
            for old_col, new_col in column_mapping.items():
                if old_col in df_clean.columns:
                    df_clean = df_clean.rename(columns={old_col: new_col})
            
            # Manter apenas colunas relevantes
            keep_columns = ['Estado', 'Ano', 'IDHM', 'IDHM_Renda', 'IDHM_Educacao', 'IDHM_Longevidade']
            available_columns = [col for col in keep_columns if col in df_clean.columns]
            df_clean = df_clean[available_columns]
            
            # Limpar nomes dos estados
            df_clean['Estado'] = df_clean['Estado'].str.strip()
            
            all_idhm.append(df_clean)
        
        # Concatenar todos os dados
        if all_idhm:
            idhm_combined = pd.concat(all_idhm, ignore_index=True)
            # Ordenar
            idhm_combined = idhm_combined.sort_values(['Ano', 'Estado'])
            print(f"✓ Dados de IDHM normalizados: {len(idhm_combined)} registros")
            print(f"   - Anos disponíveis: {sorted(idhm_combined['Ano'].unique())}")
            print(f"   - Estados disponíveis: {idhm_combined['Estado'].nunique()}")
        else:
            idhm_combined = pd.DataFrame()
            print("✗ Nenhum dado de IDHM foi carregado")
        
        return idhm_combined
    
    def normalize_nascimentos_data(self):
        """Normaliza os dados de nascimentos por idade da mãe"""
        print("\nNormalizando dados de nascimentos...")
        
        all_nascimentos = []
        
        for df in self.nascimentos_data:
            df_clean = df.copy()
            
            # Encontrar coluna de território
            territorio_col = None
            for col in df_clean.columns:
                if any(term in str(col).lower() for term in ['região', 'unidade', 'território']):
                    territorio_col = col
                    break
            
            if not territorio_col:
                print("✗ Coluna de território não encontrada")
                continue
                
            # Renomear coluna de território
            df_clean = df_clean.rename(columns={territorio_col: 'Territorio'})
            
            # Identificar colunas de faixa etária
            faixa_etaria_cols = []
            total_col = None
            
            for col in df_clean.columns:
                col_str = str(col).lower()
                if any(term in col_str for term in ['anos', 'idade', '10 a 14', '15 a 19', '20 a 24', '25 a 29', 
                                                   '30 a 34', '35 a 39', '40 a 44', 'menor']):
                    faixa_etaria_cols.append(col)
                elif 'total' in col_str:
                    total_col = col
            
            # Processar cada linha (estado/região)
            for idx, row in df_clean.iterrows():
                territorio = str(row['Territorio']) if pd.notna(row.get('Territorio')) else 'Desconhecido'
                ano = row['Ano']
                total = row.get(total_col, 0) if total_col else 0
                
                # Processar apenas estados (linhas que começam com ".. ")
                if '.. ' not in territorio:
                    continue
                    
                estado_limpo = territorio.replace('.. ', '').strip()
                
                # Para cada faixa etária, criar um registro
                for faixa_col in faixa_etaria_cols:
                    if faixa_col not in ['Territorio', 'Ano', total_col]:
                        nascimentos = row.get(faixa_col, 0)
                        
                        # Tratar valores especiais
                        if pd.isna(nascimentos) or str(nascimentos).strip() in ['-', '..', '...', '']:
                            continue
                            
                        try:
                            # Converter para número - tratamento robusto
                            if isinstance(nascimentos, str):
                                nascimentos_clean = str(nascimentos).strip()
                                # Remover pontos de milhar e converter vírgula para ponto decimal
                                nascimentos_clean = nascimentos_clean.replace('.', '').replace(',', '.')
                                nascimentos_num = float(nascimentos_clean)
                            else:
                                nascimentos_num = float(nascimentos)
                            
                            # Normalizar nome da faixa etária
                            faixa_normalizada = self.normalizar_faixa_etaria(str(faixa_col))
                            
                            # Converter total também
                            if total:
                                if isinstance(total, str):
                                    total_clean = str(total).strip().replace('.', '').replace(',', '.')
                                    total_num = float(total_clean)
                                else:
                                    total_num = float(total)
                            else:
                                total_num = 0
                            
                            all_nascimentos.append({
                                'Estado': estado_limpo,
                                'Ano': ano,
                                'Faixa_Etaria': faixa_normalizada,
                                'Nascimentos': int(nascimentos_num),
                                'Total_Ano': int(total_num)
                            })
                            
                        except (ValueError, TypeError) as e:
                            # Silenciar erros para valores inválidos
                            continue
        
        if not all_nascimentos:
            print("✗ Nenhum dado de nascimentos processado")
            return pd.DataFrame()
            
        nascimentos_combined = pd.DataFrame(all_nascimentos)
        
        # Agrupar para evitar duplicatas
        if not nascimentos_combined.empty:
            nascimentos_combined = nascimentos_combined.groupby(
                ['Estado', 'Ano', 'Faixa_Etaria'], as_index=False
            ).agg({
                'Nascimentos': 'sum',
                'Total_Ano': 'first'
            })
        
        print(f"✓ Dados de nascimentos normalizados: {len(nascimentos_combined)} registros")
        
        # Mostrar estatísticas dos dados processados
        if not nascimentos_combined.empty:
            print(f"   - Estados: {nascimentos_combined['Estado'].nunique()}")
            print(f"   - Anos: {sorted(nascimentos_combined['Ano'].unique())}")
            print(f"   - Faixas etárias: {nascimentos_combined['Faixa_Etaria'].unique()}")
        
        return nascimentos_combined
    
    def normalizar_faixa_etaria(self, faixa):
        """Normaliza os nomes das faixas etárias"""
        faixa = str(faixa).lower().strip()
        
        if '10 a 14' in faixa or '10-14' in faixa:
            return '10-14 anos'
        elif '15 a 19' in faixa or '15-19' in faixa:
            return '15-19 anos'
        elif '20 a 24' in faixa or '20-24' in faixa:
            return '20-24 anos'
        elif '25 a 29' in faixa or '25-29' in faixa:
            return '25-29 anos'
        elif '30 a 34' in faixa or '30-34' in faixa:
            return '30-34 anos'
        elif '35 a 39' in faixa or '35-39' in faixa:
            return '35-39 anos'
        elif '40 a 44' in faixa or '40-44' in faixa:
            return '40-44 anos'
        elif 'menor' in faixa or '<10' in faixa:
            return 'Menor de 10 anos'
        elif 'ignorada' in faixa:
            return 'Idade ignorada'
        else:
            return 'Outras idades'
    
    def create_comparison_dataset(self):
        """Cria dataset final para comparação IDHM vs Idade da Mãe"""
        print("\nCriando dataset de comparação...")
        
        # Normalizar dados
        idhm_df = self.normalize_idhm_data()
        nascimentos_df = self.normalize_nascimentos_data()
        
        if idhm_df.empty or nascimentos_df.empty:
            print("✗ Dados insuficientes para criar dataset de comparação")
            print(f"   - IDHM: {len(idhm_df)} registros")
            print(f"   - Nascimentos: {len(nascimentos_df)} registros")
            return pd.DataFrame()
        
        print(f"   - Anos IDHM: {sorted(idhm_df['Ano'].unique())}")
        print(f"   - Anos Nascimentos: {sorted(nascimentos_df['Ano'].unique())}")
        print(f"   - Estados IDHM: {idhm_df['Estado'].nunique()}")
        print(f"   - Estados Nascimentos: {nascimentos_df['Estado'].nunique()}")
        
        # Criar resumo por estado/ano para nascimentos
        nascimentos_resumo = nascimentos_df.groupby(['Estado', 'Ano', 'Faixa_Etaria']).agg({
            'Nascimentos': 'sum',
            'Total_Ano': 'first'
        }).reset_index()
        
        # Calcular percentual por faixa etária
        nascimentos_resumo['Percentual'] = (nascimentos_resumo['Nascimentos'] / 
                                           nascimentos_resumo['Total_Ano']) * 100
        
        # DEBUG: Mostrar alguns exemplos antes do merge
        print(f"\n   - Exemplo de dados IDHM:")
        print(idhm_df[['Estado', 'Ano', 'IDHM']].head())
        print(f"\n   - Exemplo de dados Nascimentos:")
        print(nascimentos_resumo[['Estado', 'Ano', 'Faixa_Etaria', 'Percentual']].head())
        
        # Juntar com dados de IDHM
        comparison_df = pd.merge(
            nascimentos_resumo, 
            idhm_df, 
            on=['Estado', 'Ano'], 
            how='inner'
        )
        
        print(f"✓ Dataset de comparação criado: {len(comparison_df)} registros")
        
        if not comparison_df.empty:
            print(f"   - Anos combinados: {sorted(comparison_df['Ano'].unique())}")
            print(f"   - Estados combinados: {comparison_df['Estado'].nunique()}")
        
        return comparison_df
    
    def save_normalized_data(self, output_dir='dados_normalizados'):
        """Salva os dados normalizados"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        comparison_df = self.create_comparison_dataset()
        
        if comparison_df.empty:
            print("✗ Nenhum dado para salvar")
            # Salvar datasets individuais mesmo sem junção
            idhm_df = self.normalize_idhm_data()
            nascimentos_df = self.normalize_nascimentos_data()
            
            if not idhm_df.empty:
                idhm_df.to_csv(f'{output_dir}/idhm_normalizado.csv', index=False, encoding='utf-8')
                print(f"✓ idhm_normalizado.csv salvo ({len(idhm_df)} registros)")
            
            if not nascimentos_df.empty:
                nascimentos_df.to_csv(f'{output_dir}/nascimentos_normalizado.csv', index=False, encoding='utf-8')
                print(f"✓ nascimentos_normalizado.csv salvo ({len(nascimentos_df)} registros)")
            
            return pd.DataFrame()
        
        # Salvar datasets
        comparison_df.to_csv(f'{output_dir}/comparacao_idhm_idade_mae.csv', index=False, encoding='utf-8')
        
        # Salvar datasets individuais também
        idhm_df = self.normalize_idhm_data()
        nascimentos_df = self.normalize_nascimentos_data()
        
        if not idhm_df.empty:
            idhm_df.to_csv(f'{output_dir}/idhm_normalizado.csv', index=False, encoding='utf-8')
        
        if not nascimentos_df.empty:
            nascimentos_df.to_csv(f'{output_dir}/nascimentos_normalizado.csv', index=False, encoding='utf-8')
        
        print(f"\n✅ Dados salvos em '{output_dir}/'")
        print(f"   - comparacao_idhm_idade_mae.csv ({len(comparison_df)} registros)")
        if not idhm_df.empty:
            print(f"   - idhm_normalizado.csv ({len(idhm_df)} registros)") 
        if not nascimentos_df.empty:
            print(f"   - nascimentos_normalizado.csv ({len(nascimentos_df)} registros)")
        
        return comparison_df

# Exemplo de uso
def main():
    # Inicializar normalizador
    normalizer = DataNormalizer()
    
    # Carregar arquivos (ajuste os caminhos conforme necessário)
    print("=== CARREGANDO ARQUIVOS ===")
    normalizer.load_idhm_files('data*.xlsx')
    normalizer.load_nascimentos_files('sinasc_cnv_nvuf*.csv')
    
    # Processar e salvar dados
    print("\n=== PROCESSANDO DADOS ===")
    df_comparacao = normalizer.save_normalized_data()
    
    if df_comparacao.empty:
        print("\n⚠️  Não foi possível criar o dataset combinado, mas os dados individuais foram salvos.")
        print("   Verifique se os anos dos arquivos IDHM e Nascimentos coincidem.")
        return
    
    # Mostrar estatísticas
    print("\n📊 ESTATÍSTICAS DO DATASET:")
    print(f"Total de registros: {len(df_comparacao)}")
    print(f"Estados únicos: {df_comparacao['Estado'].nunique()}")
    print(f"Anos: {sorted(df_comparacao['Ano'].unique())}")
    print(f"Faixas etárias: {df_comparacao['Faixa_Etaria'].unique()}")
    
    # Exemplo de análise rápida
    print("\n🔍 EXEMPLO DE ANÁLISE (Mães adolescentes 15-19 anos vs IDHM Educação):")
    adolescentes = df_comparacao[df_comparacao['Faixa_Etaria'] == '15-19 anos']
    if not adolescentes.empty:
        correlacao = adolescentes['Percentual'].corr(adolescentes['IDHM_Educacao'])
        print(f"Correlação entre % mães adolescentes e IDHM Educação: {correlacao:.3f}")
        
        # Top 5 estados com maior % de mães adolescentes (último ano disponível)
        ultimo_ano = adolescentes['Ano'].max()
        top_adolescentes = adolescentes[adolescentes['Ano'] == ultimo_ano].nlargest(5, 'Percentual')
        print(f"\n📈 Top 5 estados com maior % de mães adolescentes ({ultimo_ano}):")
        for _, row in top_adolescentes.iterrows():
            print(f"   {row['Estado']}: {row['Percentual']:.1f}% (IDHM Educ: {row['IDHM_Educacao']:.3f})")
    else:
        print("✗ Nenhum dado de mães adolescentes encontrado")

if __name__ == "__main__":
    main()