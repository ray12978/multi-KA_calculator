# multi-Krippendorff's Alpha alculator

## How to use

### prepare files

#### dataset structure
```
├──labels
|    ├──annontator_1
|    |    ├── data1.json
|    |    └── ...
|    ├──annontator_2
|    |    ├── data1.json
|    |    └── ...


the sub-folder name must be "annontator_{i}"
number of files in each annontator folder must be equal
```
run script
```
python run.py -f ./labels
```
* -f: directory path of labels folder
