from adapters.base_source_adapter import BaseSourceAdapter
from adapters.base_target_adapter import BaseTargetAdapter
from messages import ConfigSetResponse


class SelectZeroAdapter(BaseSourceAdapter, BaseTargetAdapter):

    display_name = "SelectZero"

    def __init__(self):
        self._connection = ""
        self._schema = "public"
        self._owner = ""
        self._color = ""

    # ------------------------------------------------------------------ #
    # BaseSourceAdapter (stubbed — no sample SelectZero input files)
    # ------------------------------------------------------------------ #

    @property
    def required_source_files(self) -> dict:
        return {
            'terms':       'Terms file',
            'col_term_rel': 'Column\u2013term relations file',
            'term_rel':    'Term relations file',
        }

    def required_columns(self, file_key: str) -> list:
        raise NotImplementedError("SelectZeroAdapter source reading is not yet implemented")

    @property
    def available_config_options(self) -> dict:
        return {}

    def validate_schema(self, req):
        raise NotImplementedError("SelectZeroAdapter source reading is not yet implemented")

    def process_sources(self, source_dfs: dict):
        raise NotImplementedError("SelectZeroAdapter source reading is not yet implemented")

    # ------------------------------------------------------------------ #
    # BaseTargetAdapter
    # ------------------------------------------------------------------ #

    @property
    def required_target_files(self) -> dict:
        return {
            'terms':       'Terms file',
            'col_term_rel': 'Column\u2013term relations file',
            'term_rel':    'Term relations file',
        }

    def output_columns(self, file_key: str) -> list:
        columns = {
            'terms':       ['name', 'color', 'description', 'type', 'domain', 'owner'],
            'col_term_rel': ['connection', 'schema', 'object', 'column', 'term'],
            'term_rel':    ['sourceName', 'relation', 'targetName'],
        }
        return columns.get(file_key, [])

    def get_config(self) -> dict:
        return {
            'connection': self._connection,
            'schema':     self._schema,
            'owner':      self._owner,
            'color':      self._color,
        }

    def set_config(self, req) -> ConfigSetResponse:
        param, value = req.parameter, req.value

        if param in ('connection', 'owner', 'schema'):
            if value != "" and (len(value) < 2 or len(value) > 40):
                return ConfigSetResponse(
                    success=False,
                    error=f"'{param}' must be 2\u201340 characters when non-empty",
                )
            setattr(self, f"_{param}", value)
            return ConfigSetResponse(success=True, error=None)

        if param == 'color':
            if len(value) > 40:
                return ConfigSetResponse(
                    success=False,
                    error="'color' must be at most 40 characters",
                )
            self._color = value
            return ConfigSetResponse(success=True, error=None)

        return ConfigSetResponse(success=False, error=f"Unknown parameter: '{param}'")

    def write_output(self, data, target_paths: dict):
        frame_by_key = {
            'terms': data.df_term,
            'col_term_rel': data.df_col_term_rel,
            'term_rel': data.df_term_rel,
        }

        for file_key, path in target_paths.items():
            dataframe = frame_by_key[file_key].reindex(columns=self.output_columns(file_key)).fillna("")
            dataframe.to_csv(path, index=False, sep=';', encoding='utf-8')
