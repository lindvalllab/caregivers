# Caregivers Project

This repository contains the code for our paper "Associations Between Family Member Involvement and Outcomes of Patients Admitted to the Intensive Care Unit".

## List of Tables

- [Table 1: Patient Characteristics](https://github.com/lindvalllab/caregivers/blob/master/notebooks/tables/table-2_without-neither.ipynb)
- [Table 2: Goals of Care Conversations](https://github.com/lindvalllab/caregivers/blob/master/notebooks/models/without-neither/summary.ipynb)
- [Table 3: Limitations in Life-Sustaining Treatments (LLST) Conversations](https://github.com/lindvalllab/caregivers/blob/master/notebooks/models/without-neither/summary.ipynb)
- [Table 4: 3-Month Mortality](https://github.com/lindvalllab/caregivers/blob/master/notebooks/models/without-neither/summary.ipynb)

## Development Setup

### Clone the repository

```bash
git clone https://github.com/lindvalllab/caregivers.git
cd caregivers
```

### Set up a virtual environment

I use `venv` since it's already in `.gitignore`, but you can use whatever you like.

```bash
python3.7 -m venv venv
source venv/bin/activate
```

To tell Jupyter that your virtual environment exists:

```
python3.7 -m ipykernel install --user --name=<whatever_you_want>
```

This will make the active virtual environment (`venv`, if you've been following the previous steps) available to you use in Jupyter. ([Reference](https://www.zainrizvi.io/blog/jupyter-notebooks-best-practices-use-virtual-environments/))

### Install requirements

```bash
pip install -r requirements.txt
```

### Run the notebooks

```bash
cd notebooks  # optional, can also navigate to the directory after running `jupyter lab`
jupyter lab
```

### Run the tests

The test files can be found in the `tests` directory. To run them, simply run the following.

```
cd caregivers
pytest
```
