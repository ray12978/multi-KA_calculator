import glob
import os
from os import listdir
import pandas as pd
import re
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fold_path', help='The directory path used for calculating annotation consistency.',
                        type=str, default='./labels', dest='fold_path')
    args = parser.parse_args()
    return args


def calcu_agreement(Folder_Path):
    Folders = list(filter(lambda x: 'annotator' in x, listdir(Folder_Path)))
    print('Fold path: "{0}"\nCalculating...\nThe total number of annotators is {1}'
          .format(args.fold_path, len(Folders)))
    if len(Folders) == 1:
        KripAlpha = 0
        print(f'Krippendorff\'s Alpha is {KripAlpha}')
        return
    i = 0
    j = 0

    Row_indices = []
    Label_subset = []

    if not Row_indices:
        Row_indices = Folders

    Column_annotator = list(
        set(list(map(lambda x: x.split('\\')[-1], glob.glob(os.path.join(Folder_Path, '*', '*.json'))))))

    DF_AnnotateInfo = pd.DataFrame(index=Row_indices, columns=Column_annotator)
    for folder_i in Folders:
        File_Path = Folder_Path + '\\' + folder_i
        Files = listdir(File_Path)
        if len(Files) == 0:
            print('Error')
            raise FileNotFoundError('Files Length is 0')
        for file_i in Files:
            with open(File_Path + '\\' + file_i, encoding='utf8') as f:
                Annotated = f.read()
            Rule1 = re.search(r'"flags": {([^(})]+)', Annotated)
            Ans = Rule1.group(1).split(',')

            CalLabel = ""

            for k in Ans:
                Ans_split = k.split(':')
                Label_Name = re.sub(r"\s*\"", "", Ans_split[0])
                if 'true' in Ans_split[1]:
                    CalLabel += Label_Name + ','

            if CalLabel == '':
                DF_AnnotateInfo.loc[folder_i][file_i] = 'nan'
            else:
                DF_AnnotateInfo.loc[folder_i][file_i] = CalLabel.strip(',')

            j += 1
            if CalLabel != '':
                Label_subset.append(CalLabel.strip(','))

        i += 1
        j = 0

    Label_subset = set(Label_subset)

    Total_label_num = []
    for i in range(len(DF_AnnotateInfo.columns)):
        Col_sets = DF_AnnotateInfo[DF_AnnotateInfo.columns[i]].to_list()
        Col_sets = [x for x in Col_sets if x != 'nan']
        cnt_label = 0

        Col_subsets = set(Col_sets)

        for j in Col_subsets:
            for k in Col_sets:
                if isinstance(j, str) and isinstance(k, str):
                    if set(j).issubset(k):
                        cnt_label += 1
        Total_label_num.append(str(cnt_label))
    DF_AnnotateInfo.loc[len(DF_AnnotateInfo.index)] = Total_label_num
    DF_AnnotateInfo = DF_AnnotateInfo.rename(index={DF_AnnotateInfo.index[-1]: "nl"})

    Row_indices = Label_subset
    Column_annotator = Label_subset

    DF_CoinMat = pd.DataFrame(index=Row_indices, columns=Column_annotator)

    Row_ItrNum = 0
    for i in range(len(DF_CoinMat.columns)):
        for j in range(Row_ItrNum, len(DF_CoinMat.index)):
            CoinMat_Value = 0
            for Col_i in range(len(DF_AnnotateInfo.columns)):
                OnePicLabelnums = DF_AnnotateInfo[DF_AnnotateInfo.columns[Col_i]][:-1].tolist()
                Dic_AnnInfo_Col = {}
                for temp_i in set(OnePicLabelnums):
                    if temp_i == 'nan':
                        continue
                    if OnePicLabelnums.count(temp_i) > 0:
                        Dic_AnnInfo_Col[temp_i] = OnePicLabelnums.count(temp_i)

                nl = float(DF_AnnotateInfo.loc['nl'].tolist()[Col_i])

                if Dic_AnnInfo_Col.get(DF_CoinMat.index[j], -1) > 0 and Dic_AnnInfo_Col.get(DF_CoinMat.columns[i],
                                                                                            -1) > 0:
                    dup_labelnum = float(Dic_AnnInfo_Col[DF_CoinMat.index[j]])
                    Minuend = 0.0
                    dup_labelnum2 = float(Dic_AnnInfo_Col[DF_CoinMat.columns[i]])

                    for AnnInfo_key in Dic_AnnInfo_Col:
                        if set(str(DF_CoinMat.index[j]).split(',')).issubset(set(str(AnnInfo_key).split(','))):
                            Minuend = Minuend + Dic_AnnInfo_Col[AnnInfo_key]
                    Minuend = Minuend - dup_labelnum

                    if DF_CoinMat.columns[i] == DF_CoinMat.index[j] and nl - 1 != 0:
                        if dup_labelnum > 1 and Minuend == 0:
                            CoinMat_Value = CoinMat_Value + round(1 * dup_labelnum / (nl - 1), 4)
                        elif dup_labelnum >= 1 and Minuend > 0:
                            CoinMat_Value = CoinMat_Value + round(Minuend * dup_labelnum / (nl - 1), 4)
                        else:
                            CoinMat_Value = CoinMat_Value + round(Minuend / (nl - 1), 4)
                    else:
                        if dup_labelnum >= 1 and dup_labelnum2 >= 1:
                            CoinMat_Value = CoinMat_Value + round(dup_labelnum * dup_labelnum2 / (nl - 1), 4)
                else:
                    nl = float(DF_AnnotateInfo.loc['nl'].tolist()[Col_i])
            DF_CoinMat[DF_CoinMat.index[j]][DF_CoinMat.columns[i]] = CoinMat_Value
            DF_CoinMat[DF_CoinMat.columns[i]][DF_CoinMat.index[j]] = CoinMat_Value
        Row_ItrNum += 1

    Total_label_num2 = []
    for i2 in range(len(DF_CoinMat.columns)):
        Col_sets2 = DF_CoinMat[DF_CoinMat.columns[i2]].to_list()
        cnt_label2 = 0
        for j2 in Col_sets2:
            cnt_label2 += float(j2)
        Total_label_num2.append(str(cnt_label2))
    DF_CoinMat.loc[len(DF_CoinMat.index)] = Total_label_num2
    DF_CoinMat = DF_CoinMat.rename(index={DF_CoinMat.index[-1]: "Tal"})

    TriNum = 0

    Row_indices = Label_subset
    Column_annotator = Label_subset

    DF_DiffMat = pd.DataFrame(index=Row_indices, columns=Column_annotator)

    for i in range(len(DF_CoinMat.columns)):
        for j in range(TriNum, len(DF_CoinMat.index) - 1):
            if DF_CoinMat.columns[i] == DF_CoinMat.index[j]:
                DF_DiffMat[DF_CoinMat.columns[i]][DF_CoinMat.index[j]] = 0
                continue
            Diff = 0.0
            Str_cols = DF_CoinMat.columns[i].split(',')
            Str_Inds = DF_CoinMat.index[j].split(',')
            for i_cols in range(len(Str_cols)):
                if Str_cols[i_cols] in Str_Inds:
                    Diff += 1
            Str_cols.extend(Str_Inds)
            DF_DiffMat[DF_CoinMat.columns[i]][DF_CoinMat.index[j]] = 1.0 - float(Diff / (len(set(Str_cols))))
            DF_DiffMat[DF_CoinMat.index[j]][DF_CoinMat.columns[i]] = 1.0 - float(Diff / (len(set(Str_cols))))
        TriNum += 1

    PVMutiByDelta = 0.0
    N1and2MutiByDelta = 0.0
    for Ind_num in range(len(DF_CoinMat.columns)):
        for col_num in range(len(DF_CoinMat.columns)):
            if col_num < Ind_num:
                continue
            N1and2MutiByDelta += float(DF_CoinMat[DF_CoinMat.columns[Ind_num]]['Tal']) * float(
                DF_CoinMat[DF_CoinMat.columns[col_num]]['Tal']) * (
                                         float(DF_DiffMat[DF_CoinMat.columns[Ind_num]][DF_CoinMat.index[col_num]]) ** 2)
            PVMutiByDelta += float(DF_CoinMat[DF_CoinMat.columns[Ind_num]][DF_CoinMat.index[col_num]]) * (
                    float(DF_DiffMat[DF_CoinMat.columns[Ind_num]][DF_CoinMat.index[col_num]]) ** 2)

    Total_CoinMat_num = 0.0
    for CoinMat_nums in range(len(DF_CoinMat.columns)):
        Total_CoinMat_num += float(DF_CoinMat.loc['Tal'].tolist()[CoinMat_nums])

    KripAlpha = 1.0 - (Total_CoinMat_num - 1.0) * (PVMutiByDelta / N1and2MutiByDelta)
    print(f'Krippendorff\'s Alpha is {KripAlpha}')


def main(args):
    calcu_agreement(args.fold_path)


if __name__ == '__main__':
    args = parse_args()
    main(args)
