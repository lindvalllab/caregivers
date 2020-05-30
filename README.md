# Caregivers Project

## Development Setup

### Clone the repository
```bash
git clone https://github.com/lindvalllab/caregivers.git
cd caregivers
```

### Set up a virtual environment
I use `venv` since it's already in `.gitignore`, but you can use whatever you like.

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install requirements
```bash
pip install -r requirements.txt
```

### Run the notebooks
```bash
cd notebooks  # optional, can also navigate to the directory after running `jupyter notebook`
jupyter notebook
```

