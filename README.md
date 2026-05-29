# ELFS (Event Log Filtering and Similarity)

Filters process event logs to discover Petri nets from those process variants. Moreover, it provides a similarity 
analysis to compare process models.

---

## Requirements

- Python 3.12+

## Installation

```bash
cd elfs
pip install -e .
```

## Usage

### Import Event Logs

Import process event log from .csv or .xes file

```
elfs import
```

### Filter Event Log

Filter process event log by provided filtering options and discover Petri nets form filtered logs

```
elfs filtering
```

### Similarity Analysis

Conduct a pairwise or matrixwise similarity analysis with two or more models

```
elfs similarity
```

### Manage Event Logs and Petri Nets

Rename or delete importet event logs and discovered Petri nets

```
elfs manage
```