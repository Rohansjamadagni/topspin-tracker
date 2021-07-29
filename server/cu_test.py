import copy_csv_utils as cu
import new_csv_utils as ncu

column_names = ['L-shoulder', 'R-shoulder',
       'L-elbow', 'R-elbow',
       'L-wrist', 'R-wrist']

divisions = ['X', 'Y', 'Z']

columns = []

for column in column_names:
    for div in divisions:
        columns.append(f'{column}-{div}')

columns.append('Timestamp')

# columns = ['start', 'r_sr', 'r_st']

csv = ncu.CSV(filename='cu.csv', columns=columns)

content = [list(range(0, 19)) for _ in range(0, 2)]

# columns = ['a', 'b', 'c']

# cu.initialize_csv('cu.csv')
#
# cu.write_list_to_csv('cu.csv', content)

csv.add_list(content)
# csv.save()
csv.filter_columns(5, 2, columns=columns[:-1], overwrite=True)
