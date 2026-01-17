import numpy as np
import pandas as pd
from faker import Faker
from tqdm import tqdm

faker_obj = Faker()

# Excel1, 1 sheet with 129 categories (328 each), with 6 columns
df1 = pd.DataFrame(columns=['hsub_code', 'pid', 'fname', 'lname', 'gender', 'dob', 'address'])
list_hsub_code = sorted(['{:05d}'.format(item) for item in np.random.randint(10000, 100000, 129)])
list_df1 = list()

for idx in tqdm(range(len(list_hsub_code))):
    list_df1.append(pd.DataFrame({
        'hsub_code': [list_hsub_code[idx]]*328,
        'pid': np.random.randint(10000000, 99999999, 328).astype(str),
        'fname': [faker_obj.first_name() for jdx in range(328)],
        'lname': [faker_obj.last_name() for jdx in range(328)],
        'gender': [faker_obj.passport_gender() for jdx in range(328)],
        'dob': [faker_obj.date_of_birth() for jdx in range(328)],
        'address': [faker_obj.address() for jdx in range(328)],
    }))

df1 = pd.concat(list_df1)
df1 = df1.sample(frac=1)
    
df1.to_excel("data_example/example1.xlsx", index=False)

# Excel2, multiple sheets with 328 each
with pd.ExcelWriter("data_example/example2.xlsx") as writer:
    for hsub_code in tqdm(list_hsub_code):
        inspected_df = df1[df1['hsub_code']==hsub_code]
        inspected_df.to_excel(writer, sheet_name=hsub_code, index=False)

#####

# Excel1-large, 1 sheet with 299 categories (2500 each), with 6 columns
df1 = pd.DataFrame(columns=['hsub_code', 'pid', 'fname', 'lname', 'gender', 'dob', 'address'])
list_hsub_code = sorted(['{:05d}'.format(item) for item in np.random.randint(10000, 100000, 299)])
list_df1 = list()

for idx in tqdm(range(len(list_hsub_code))):
    list_df1.append(pd.DataFrame({
        'hsub_code': [list_hsub_code[idx]]*2500,
        'pid': np.random.randint(10000000, 99999999, 2500).astype(str),
        'fname': [faker_obj.first_name() for jdx in range(2500)],
        'lname': [faker_obj.last_name() for jdx in range(2500)],
        'gender': [faker_obj.passport_gender() for jdx in range(2500)],
        'dob': [faker_obj.date_of_birth() for jdx in range(2500)],
        'address': [faker_obj.address() for jdx in range(2500)],
    }))

df1 = pd.concat(list_df1)
df1 = df1.sample(frac=1)
    
df1.to_excel("data_example/example1-large.xlsx", index=False)

# Excel2-large, multiple sheets with 5000 each
with pd.ExcelWriter("data_example/example2-large.xlsx") as writer:
    for hsub_code in tqdm(list_hsub_code):
        inspected_df = df1[df1['hsub_code']==hsub_code]
        inspected_df.to_excel(writer, sheet_name=hsub_code, index=False)