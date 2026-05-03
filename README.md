# Metadata Migration Tool

This application converts metadata between adapter-defined formats using a Tkinter GUI. In the current repository, the main supported end-to-end flow is:

- Source: Statistics Estonia CSV files
- Target: SelectZero import CSV files

The app has two ways to run:

- a packaged Windows executable at `dist\\main\\main.exe`
- the Python source code via `main.py`

## Run The Packaged App

Use this option if you already have a built `dist` folder.

### What you need

- Windows
- dist.zip from the latest release`

### How to run

1. Extract `dist.zip` to a location of your choice. 
2. Open `dist\\main`.
3. Double-click `main.exe`.

You can also run it from Command Prompt:

```bat
cd c:\Users\Administrator\PycharmProjects\hobby_projects
dist\main\main.exe
```

### If the executable is missing

The executable is built from `main.spec`. If `dist\\main\\main.exe` is not present yet, run the Python version or build the executable with PyInstaller.

Example build command:

```bat
cd c:\Users\Administrator\PycharmProjects\hobby_projects
pyinstaller main.spec
```

## Run With Python

Use this option for development or if the packaged executable has not been built yet.

### Prerequisites

- Python 3.10+ on Windows
- `pip`
- Tkinter available in your Python installation

Tkinter is part of the standard Python installation on most Windows installs. The only non-stdlib runtime dependency used by the app is `pandas`.

### Install requirements

From the project root:

```bat
cd c:\Users\Administrator\PycharmProjects\hobby_projects
py -m pip install --upgrade pip
py -m pip install pandas
```

If you also want to run tests:

```bat
py -m pip install pytest
```

### Run the app

From the project root:

```bat
cd c:\Users\Administrator\PycharmProjects\hobby_projects
py main.py
```

### Optional: run tests

```bat
cd c:\Users\Administrator\PycharmProjects\hobby_projects
pytest
```

## How To Use The App

The GUI is a four-step flow.

### View 1: Adapter Selection

Purpose:

- choose the source adapter
- choose the target adapter
- provide all required input CSV files for the selected source adapter

What to do:

1. Select a source format.
2. Select a target format.
3. Use `Browse` to choose each required input CSV.
4. Click `Next ->`.

What happens:

- every selected input file is validated before you can continue
- input files must be readable CSV files with a `.csv` extension
- invalid input stays on the same screen and shows an inline error

### View 2: Settings

Purpose:

- configure source-specific processing rules
- configure target-specific output values
- start translation

What to do:

1. Review source settings such as prefixes, suffixes, duplicate handling, description handling, and technical field handling.
2. Fill target settings such as connection, schema, owner, and color.
3. Click `Translate`.

What happens:

- each setting is validated when changed
- invalid values are rejected and reverted in the entry field
- `connection` must be set before translation can proceed
- the app reads the source CSVs, validates their schema, and produces in-memory preview data

### View 3: Translation Preview

Purpose:

- inspect the generated output before any files are written

What you see:

- `Terms`
- `Column-Term Relations`
- `Term Relations`

What to do:

1. Review the rows in each tab.
2. Click `Accept ->` if the data looks correct.
3. Click `<- Reject` if you want to go back and change settings.

What happens:

- `Reject` returns to the settings view
- `Accept` stores the preview data and opens the output file selection view

### View 4: Save Output Files

Purpose:

- choose where the translated files should be written

What to do:

1. Pick one output path for each file required by the selected target adapter.
2. Click `Write`.

What happens:

- every output path is validated before writing
- output paths must end with `.csv`
- parent directories must already exist
- existing files are rejected and will not be overwritten
- output paths must not duplicate any source path or any other output path
- on success, the app shows the written file paths and exits

## Default Example Flow

For the current built-in adapters, a typical flow is:

1. Source adapter: `Statistics Estonia`
2. Target adapter: `SelectZero`
3. Input files:
   - `test_business_glossary.csv`
   - `test_data_glossary.csv`
4. Set a non-empty SelectZero `connection`
5. Translate
6. Review the preview
7. Save the three output CSV files

## How To Write An Adapter

Adapters isolate format-specific logic from the model and GUI.

In this repository, adapter discovery is based on subclass registration plus imports from `adapters/__init__.py`. If your adapter is not imported there, it will not appear in the UI.

### Decide what your adapter supports

An adapter can support:

- source behavior by inheriting `BaseSourceAdapter`
- target behavior by inheriting `BaseTargetAdapter`
- both, by inheriting both base classes

The current concrete adapters implement both sides.

### Source adapter responsibilities

If your adapter can be used as a source, implement:

- `display_name`
- `required_source_files`
- `required_columns(file_key)`
- `available_config_options`
- `get_config()`
- `set_config(req)`
- `validate_schema(req)`
- `process_sources(source_dfs)`

`process_sources(source_dfs)` must return a `ProcessedGlossaryData` object with these DataFrames:

- `df_term`
- `df_col_term_rel`
- `df_term_rel`

Those DataFrames must match the normalized intermediate model used by the preview and target adapters.

### Target adapter responsibilities

If your adapter can be used as a target, implement:

- `display_name`
- `required_target_files`
- `output_columns(file_key)`
- `get_config()`
- `set_config(req)`
- `write_output(data, target_paths)`

`write_output` receives the normalized `ProcessedGlossaryData` and must write all required target files.

### Minimal skeleton

```python
from adapters.base_source_adapter import BaseSourceAdapter
from adapters.base_target_adapter import BaseTargetAdapter
from messages import (
	ConfigSetResponse,
	ProcessedGlossaryData,
	SchemaValidationResponse,
)


class MyAdapter(BaseSourceAdapter, BaseTargetAdapter):
	display_name = "My Adapter"

	def __init__(self):
		self._example_setting = ""

	@property
	def required_source_files(self) -> dict:
		return {
			"input_a": "Input A",
		}

	def required_columns(self, file_key: str) -> list:
		return ["column_a", "column_b"]

	@property
	def available_config_options(self) -> dict:
		return {
			"mode": {
				1: "Mode 1",
				2: "Mode 2",
			}
		}

	def get_config(self) -> dict:
		return {
			"example_setting": self._example_setting,
		}

	def set_config(self, req) -> ConfigSetResponse:
		if req.parameter == "example_setting":
			self._example_setting = req.value
			return ConfigSetResponse(success=True, error=None)
		return ConfigSetResponse(success=False, error=f"Unknown parameter: {req.parameter}")

	def validate_schema(self, req) -> SchemaValidationResponse:
		errors = []
		for file_key, dataframe in req.source_dfs.items():
			missing = [col for col in self.required_columns(file_key) if col not in dataframe.columns]
			if missing:
				errors.append(f"{file_key} missing columns: {missing}")
		return SchemaValidationResponse(valid=not errors, errors=errors)

	def process_sources(self, source_dfs: dict) -> ProcessedGlossaryData:
		raise NotImplementedError

	@property
	def required_target_files(self) -> dict:
		return {
			"output_a": "Output A",
		}

	def output_columns(self, file_key: str) -> list:
		return ["field_1", "field_2"]

	def write_output(self, data, target_paths: dict):
		raise NotImplementedError
```

### Register the adapter

1. Add a new file under `adapters/`, for example `adapters/my_adapter.py`.
2. Implement your adapter class there.
3. Import it in `adapters/__init__.py`.

Example:

```python
from adapters.my_adapter import MyAdapter
```

That import is what makes the subclass visible when the controller inspects available adapter classes.

### Match the normalized intermediate schema

If you implement a source adapter, `process_sources` should build these normalized tables:

#### `df_term`

Columns:

- `name`
- `color`
- `description`
- `type`
- `domain`
- `owner`

#### `df_col_term_rel`

Columns:

- `connection`
- `schema`
- `object`
- `column`
- `term`

#### `df_term_rel`

Columns:

- `sourceName`
- `relation`
- `targetName`

The target adapter may overwrite some preview/output values from its own config, such as `connection`, `schema`, `owner`, and `color`.

### Validation guidance

When writing adapters, keep these rules in mind:

- return descriptive errors from `set_config` instead of raising for normal validation failures
- return missing-column details from `validate_schema`
- handle empty and null values safely during processing
- keep format-specific logic inside the adapter, not in the model or GUI

## Project Structure

Key files:

- `main.py` - application entry point
- `main.spec` - PyInstaller spec for `dist\\main\\main.exe`
- `controller.py` - window navigation and request dispatch
- `model.py` - validation, CSV loading, processing, and writing orchestration
- `messages.py` - request/response named tuples
- `adapters/` - source and target adapter implementations
- `gui/` - Tkinter views
- `tests/` - pytest suite
