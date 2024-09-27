import time
from tool.Utils import read_excel_to_dict_list

def test_read_excel_to_dict_list():
    file_path = "/Users/bo.liu/Documents/Buddy/文档/1.5.6.1/xlsx/0925/数据埋点-联影听觉管家0925113201.xlsx"
    sheet_name = "埋点 V1.5.6.1"
    data_dicts = read_excel_to_dict_list(file_path, sheet_name)
    for data_dict in data_dicts:
        time.sleep(0.05)
        print(data_dict)

def main():
    test_read_excel_to_dict_list()

if __name__ == '__main__':
    main()