# multi-KA_calculator

## How to use

### Prepare files

#### Eample
```
labels
|-annontator_1
     |-123ag12.json
     ...
|-annontator_2
     |-123ag12.json
     ...
     
The sub-folder name must be "annontator_{i}"

Number of files in each annontator must be equal

The file extension must be ".json."
```
#### Install
```
git clone https://github.com/ray12978/multi-KA_calculator.git
cd multi-KA_calculator
pip install -r requirements.txt
```

#### Run script
```
python run.py -f ./labels
```
* -f: directory path of labels folder
