import pandas as pd


def excel12table(filename, sheetname, out1, out2, skrows=0, natype='--'):
    df = pd.read_excel(filename, sheet_name=sheetname, skiprows=skrows)
    print(df.columns)
    df = df.dropna(subset=[u'机构全称'])
    print(df)



excel12table(u'珠海2.xlsx', u'珠海-质押式回购机构交易简明表', 'repo_2_1.xlsx', 'repo_2_2.xlsx')
