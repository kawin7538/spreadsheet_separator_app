import numpy as np
import pandas as pd
from faker import Faker
from tqdm import tqdm

faker_obj = Faker()

# Excel1, 1 sheet with 299 categories (1000 each), with 5 columns
df1 = pd.DataFrame(columns=['hsub_code', 'fname', 'lname', 'gender', 'dob', 'address'])
list_hsub_code = sorted(['{:05d}'.format(item) for item in np.random.randint(10000, 100000, 299)])

for idx in tqdm(range(len(list_hsub_code))):
    df1 = pd.concat([df1, pd.DataFrame({
        'hsub_code': [list_hsub_code[idx]]*1000,
        'fname': [faker_obj.first_name() for jdx in range(1000)],
        'lname': [faker_obj.last_name() for jdx in range(1000)],
        'gender': [faker_obj.passport_gender() for jdx in range(1000)],
        'dob': [faker_obj.date_of_birth() for jdx in range(1000)],
        'address': [faker_obj.address() for jdx in range(1000)],
    })])
    
df1.to_excel("data_example/example1.xlsx", index=False)

# Excel2, multiple sheets with 1000 each
with pd.ExcelWriter("data_example/example2.xlsx") as writer:
    for hsub_code in tqdm(list_hsub_code):
        inspected_df = df1[df1['hsub_code']==hsub_code]
        inspected_df.to_excel(writer, sheet_name=hsub_code, index=False)