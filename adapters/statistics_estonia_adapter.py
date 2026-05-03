import re

import pandas as pd

from adapters.base_source_adapter import BaseSourceAdapter
from adapters.base_target_adapter import BaseTargetAdapter
from messages import ConfigSetResponse, ProcessedGlossaryData, SchemaValidationResponse


class StatisticsEstoniaAdapter(BaseSourceAdapter, BaseTargetAdapter):

    display_name = "Statistics Estonia"

    def __init__(self):
        self._data_term_prefix = ""
        self._data_term_suffix = ""
        self._business_term_prefix = ""
        self._business_term_suffix = ""
        self._data_term_duplicate = 2
        self._data_term_description = 3
        self._technical_fields = 1

    # ------------------------------------------------------------------ #
    # BaseSourceAdapter
    # ------------------------------------------------------------------ #

    @property
    def required_source_files(self) -> dict:
        return {
            'business_glossary': 'Business Glossary',
            'data_glossary': 'Data Glossary',
        }

    def required_columns(self, file_key: str) -> list:
        if file_key == 'business_glossary':
            return [
                'MÕISTE_ET',
                'SEOSE TÜÜP',
                'SEOTUD MÕISTE',
                'MÄÄRATLUS VÕI SELGITUS_ET',
            ]
        if file_key == 'data_glossary':
            return [
                'ÄRISÕNASTIKU TERMIN',
                'ANDMESÕNASTIKU TERMIN',
                'Tabeli nimi',
                'Välja nimi',
                'Kommentaarid',
                'KOOSTAMISE MÄRKUSED',
            ]
        return []

    @property
    def available_config_options(self) -> dict:
        return {
            'data_term_duplicate': {
                1: "Empty name on duplicates after first",
                2: "Append numeric suffix (_2, _3, \u2026)",
                3: "Keep duplicates with identical names",
                4: "Exclude duplicates after first occurrence",
            },
            'data_term_description': {
                1: "Database commentary only",
                2: "Author commentary only",
                3: "Database // author commentary (combined)",
                4: "Leave empty",
            },
            'technical_fields': {
                1: "Include all fields",
                2: "Exclude technical and unused fields",
                3: "Include technical, exclude unused",
                4: "Include unused, exclude technical",
            },
        }

    def get_config(self) -> dict:
        return {
            'data_term_prefix':      self._data_term_prefix,
            'data_term_suffix':      self._data_term_suffix,
            'business_term_prefix':  self._business_term_prefix,
            'business_term_suffix':  self._business_term_suffix,
            'data_term_duplicate':   self._data_term_duplicate,
            'data_term_description': self._data_term_description,
            'technical_fields':      self._technical_fields,
        }

    def set_config(self, req) -> ConfigSetResponse:
        param, value = req.parameter, req.value

        prefix_suffix = (
            'data_term_prefix', 'data_term_suffix',
            'business_term_prefix', 'business_term_suffix',
        )
        int_params = (
            'data_term_duplicate', 'data_term_description', 'technical_fields',
        )

        if param in prefix_suffix:
            if value != "" and (len(value) < 2 or len(value) > 8):
                return ConfigSetResponse(
                    success=False,
                    error=f"'{param}' must be empty or 2\u20138 characters (got {len(value)})",
                )
            setattr(self, f"_{param}", value)
            return ConfigSetResponse(success=True, error=None)

        if param in int_params:
            if not isinstance(value, int) or value not in range(1, 5):
                return ConfigSetResponse(
                    success=False,
                    error=f"'{param}' must be an integer from 1 to 4",
                )
            setattr(self, f"_{param}", value)
            return ConfigSetResponse(success=True, error=None)

        return ConfigSetResponse(success=False, error=f"Unknown parameter: '{param}'")

    def validate_schema(self, req) -> SchemaValidationResponse:
        errors = []
        source_dfs = req.source_dfs
        for file_key, label in self.required_source_files.items():
            if file_key not in source_dfs:
                errors.append(f"Source file '{file_key}' was not provided")
                continue
            df = source_dfs[file_key]
            missing = [c for c in self.required_columns(file_key) if c not in df.columns]
            if missing:
                errors.append(f"Missing required columns from {label}: {missing}")
        return SchemaValidationResponse(valid=len(errors) == 0, errors=errors)

    # ------------------------------------------------------------------ #
    # Helper methods
    # ------------------------------------------------------------------ #

    @staticmethod
    def _is_technical_field(txt: str) -> bool:
        return bool(re.search(r"tehniline tunnus", txt, re.IGNORECASE))

    @staticmethod
    def _is_unused(txt: str) -> bool:
        return bool(re.search(r"ei ole kasutuses", txt, re.IGNORECASE))

    def _get_term_name(self, raw_term: str, duplicates_dict: dict) -> str:
        base = self._data_term_prefix + raw_term + self._data_term_suffix
        if raw_term in duplicates_dict:
            duplicates_dict[raw_term] += 1
            if self._data_term_duplicate == 1:
                return ""
            if self._data_term_duplicate == 2:
                return f"{base}_{duplicates_dict[raw_term]}"
            if self._data_term_duplicate == 3:
                return base
            # option 4: caller checks count and skips
            return base
        else:
            duplicates_dict[raw_term] = 1
            return base

    def _resolve_description(self, row) -> str:
        opt = self._data_term_description
        komm = "" if pd.isna(row['Kommentaarid']) else str(row['Kommentaarid'])
        notes = "" if pd.isna(row['KOOSTAMISE MÄRKUSED']) else str(row['KOOSTAMISE MÄRKUSED'])
        if opt == 1:
            return komm
        if opt == 2:
            return notes
        if opt == 3:
            if komm and notes:
                return f"{komm} // {notes}"
            return komm or notes
        return ""  # opt == 4

    def _process_data_glossary(self, df_dg: pd.DataFrame) -> tuple:
        """Returns (df_term_rows, df_col_term_rel_rows, df_term_rel_rows) for the data glossary."""
        columns_term = ['name', 'color', 'description', 'type', 'domain', 'owner']
        columns_col = ['connection', 'schema', 'object', 'column', 'term']
        columns_rel = ['sourceName', 'relation', 'targetName']
        df_term = pd.DataFrame(columns=columns_term)
        df_col = pd.DataFrame(columns=columns_col)
        df_rel = pd.DataFrame(columns=columns_rel)
        duplicates_dict: dict = {}

        for _, row in df_dg.iterrows():
            if pd.isna(row['ANDMESÕNASTIKU TERMIN']):
                continue

            raw_term = str(row['ANDMESÕNASTIKU TERMIN']).strip().lower()
            term_name = self._get_term_name(raw_term, duplicates_dict)

            # Exclude duplicates after first occurrence (option 4)
            if duplicates_dict[raw_term] > 1 and self._data_term_duplicate == 4:
                continue

            # Technical/unused field filtering
            notes_txt = "" if pd.isna(row['KOOSTAMISE MÄRKUSED']) else str(row['KOOSTAMISE MÄRKUSED'])
            is_tech = self._is_technical_field(notes_txt)
            is_unused = self._is_unused(notes_txt)

            if self._technical_fields == 2 and (is_tech or is_unused):
                continue
            if self._technical_fields == 3 and is_unused:
                continue
            if self._technical_fields == 4 and is_tech:
                continue

            description = self._resolve_description(row)

            df_term = pd.concat([df_term, pd.DataFrame([{
                'name': term_name,
                'color': "",
                'description': description,
                'type': "Term",
                'domain': "",
                'owner': "",
            }])], ignore_index=True)

            df_col = pd.concat([df_col, pd.DataFrame([{
                'connection': "",
                'schema': "",
                'object': str(row['Tabeli nimi']),
                'column': str(row['Välja nimi']),
                'term': term_name,
            }])], ignore_index=True)

            if pd.isna(row['ÄRISÕNASTIKU TERMIN']):
                continue

            for source_term in str(row['ÄRISÕNASTIKU TERMIN']).split(','):
                st = source_term.strip()
                if not st:
                    continue
                source_name = self._business_term_prefix + st.lower() + self._business_term_suffix
                df_rel = pd.concat([df_rel, pd.DataFrame([{
                    'sourceName': source_name,
                    'relation': "Related to",
                    'targetName': term_name,
                }])], ignore_index=True)

        return df_term, df_col, df_rel

    def _process_business_glossary(self, df_bg: pd.DataFrame) -> tuple:
        """Returns (df_term_rows, df_term_rel_rows) for the business glossary."""
        columns_term = ['name', 'color', 'description', 'type', 'domain', 'owner']
        columns_rel = ['sourceName', 'relation', 'targetName']
        df_term = pd.DataFrame(columns=columns_term)
        df_rel = pd.DataFrame(columns=columns_rel)
        seen_terms: set = set()

        for _, row in df_bg.iterrows():
            raw_name = str(row['MÕISTE_ET']).lower()
            term_name = self._business_term_prefix + raw_name + self._business_term_suffix

            if raw_name not in seen_terms:
                seen_terms.add(raw_name)
                description = "" if pd.isna(row['MÄÄRATLUS VÕI SELGITUS_ET']) else str(row['MÄÄRATLUS VÕI SELGITUS_ET'])
                df_term = pd.concat([df_term, pd.DataFrame([{
                    'name': term_name,
                    'color': "",
                    'description': description,
                    'type': "Concept",
                    'domain': "",
                    'owner': "",
                }])], ignore_index=True)

            # Skip relation rows where either relation field is absent
            if pd.isna(row['SEOTUD MÕISTE']) or str(row['SEOTUD MÕISTE']).strip() == "" or pd.isna(row['SEOSE TÜÜP']):
                continue

            relation_map = {
                "KUULUB GRUPPI": "Belongs to group",
                "SEOTUD": "Related to",
                "LAIEM": "Child of",
                "KITSAM": "Parent of",
            }
            relation = relation_map.get(str(row['SEOSE TÜÜP']))
            if relation is None:
                continue  # unknown relation type — skip row

            target_raw = str(row['SEOTUD MÕISTE']).lower()
            target_name = self._business_term_prefix + target_raw + self._business_term_suffix

            df_rel = pd.concat([df_rel, pd.DataFrame([{
                'sourceName': term_name,
                'relation': relation,
                'targetName': target_name,
            }])], ignore_index=True)

        return df_term, df_rel

    # ------------------------------------------------------------------ #
    # BaseSourceAdapter — process_sources
    # ------------------------------------------------------------------ #

    def process_sources(self, source_dfs: dict) -> ProcessedGlossaryData:
        df_dg = source_dfs['data_glossary']
        df_bg = source_dfs['business_glossary']

        dg_term, dg_col, dg_rel = self._process_data_glossary(df_dg)
        bg_term, bg_rel = self._process_business_glossary(df_bg)

        df_term = pd.concat([dg_term, bg_term], ignore_index=True)
        df_col_term_rel = dg_col.reset_index(drop=True)
        df_term_rel = pd.concat([dg_rel, bg_rel], ignore_index=True)

        return ProcessedGlossaryData(
            df_term=df_term,
            df_col_term_rel=df_col_term_rel,
            df_term_rel=df_term_rel,
        )

    # ------------------------------------------------------------------ #
    # BaseTargetAdapter
    # ------------------------------------------------------------------ #

    @property
    def required_target_files(self) -> dict:
        return {
            'business_glossary': 'Business Glossary',
            'data_glossary': 'Data Glossary',
        }

    def output_columns(self, file_key: str) -> list:
        columns = {
            'business_glossary': [
                'MÕISTE_ET',
                'SEOSE TÜÜP',
                'SEOTUD MÕISTE',
                'MÄÄRATLUS VÕI SELGITUS_ET',
            ],
            'data_glossary': [
                'ÄRISÕNASTIKU TERMIN',
                'ANDMESÕNASTIKU TERMIN',
                'Tabeli nimi',
                'Välja nimi',
                'Kommentaarid',
                'KOOSTAMISE MÄRKUSED',
            ],
        }
        return columns.get(file_key, [])

    def write_output(self, data, target_paths: dict):
        business_df = self._build_business_glossary_output(data)
        data_df = self._build_data_glossary_output(data)

        business_df.to_csv(
            target_paths['business_glossary'],
            index=False,
            sep=';',
            encoding='utf-8',
        )
        data_df.to_csv(
            target_paths['data_glossary'],
            index=False,
            sep=';',
            encoding='utf-8',
        )

    def _build_business_glossary_output(self, data) -> pd.DataFrame:
        concept_rows = data.df_term[data.df_term['type'] == 'Concept'].fillna("")
        concept_names = set(concept_rows['name'].tolist())
        relation_map = {
            'Belongs to group': 'KUULUB GRUPPI',
            'Related to': 'SEOTUD',
            'Child of': 'LAIEM',
            'Parent of': 'KITSAM',
        }

        descriptions = concept_rows.set_index('name')['description'].to_dict()
        relation_rows = []
        seen_sources = set()

        for _, row in data.df_term_rel.fillna("").iterrows():
            source_name = row['sourceName']
            target_name = row['targetName']
            if source_name not in concept_names or target_name not in concept_names:
                continue

            relation = relation_map.get(row['relation'])
            if relation is None:
                continue

            seen_sources.add(source_name)
            relation_rows.append({
                'MÕISTE_ET': source_name,
                'SEOSE TÜÜP': relation,
                'SEOTUD MÕISTE': target_name,
                'MÄÄRATLUS VÕI SELGITUS_ET': descriptions.get(source_name, ''),
            })

        for _, row in concept_rows.iterrows():
            if row['name'] in seen_sources:
                continue
            relation_rows.append({
                'MÕISTE_ET': row['name'],
                'SEOSE TÜÜP': '',
                'SEOTUD MÕISTE': '',
                'MÄÄRATLUS VÕI SELGITUS_ET': row['description'],
            })

        return pd.DataFrame(relation_rows, columns=self.output_columns('business_glossary'))

    def _build_data_glossary_output(self, data) -> pd.DataFrame:
        term_rows = data.df_term[data.df_term['type'] == 'Term'].fillna("")
        term_names = set(term_rows['name'].tolist())
        concept_names = set(data.df_term[data.df_term['type'] == 'Concept'].fillna("")['name'].tolist())
        descriptions = term_rows.groupby('name')['description'].first().to_dict()

        business_links = {}
        for _, row in data.df_term_rel.fillna("").iterrows():
            source_name = row['sourceName']
            target_name = row['targetName']
            if row['relation'] != 'Related to':
                continue
            if source_name not in concept_names or target_name not in term_names:
                continue
            business_links.setdefault(target_name, []).append(source_name)

        rows = []
        for _, row in data.df_col_term_rel.fillna("").iterrows():
            term_name = row['term']
            linked_terms = business_links.get(term_name, [])
            rows.append({
                'ÄRISÕNASTIKU TERMIN': ', '.join(dict.fromkeys(linked_terms)),
                'ANDMESÕNASTIKU TERMIN': term_name,
                'Tabeli nimi': row['object'],
                'Välja nimi': row['column'],
                'Kommentaarid': descriptions.get(term_name, ''),
                'KOOSTAMISE MÄRKUSED': '',
            })

        return pd.DataFrame(rows, columns=self.output_columns('data_glossary'))
