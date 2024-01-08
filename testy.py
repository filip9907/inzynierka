import unittest
import pandas as pd
from csv_to_db import (
    del_unit,
    remove_spaces_from_column_names,
    remove_spaces_from_data,
    drop_columns_with_all_nan,
    split_dataframe_to_list,
    set_dataframe_names_from_rodzaj,
    get_dataframe_by_name,
    handle_24_hour_time,
    prepare_data
)
# Import your functions here

class TestDataPreparationFunctions(unittest.TestCase):

    def setUp(self):
        # Initialize test data
        self.test_df = pd.DataFrame({
            'Rodzaj': ['A [Unit1]', 'B [Unit2]', 'A [Unit1]', 'C [Unit3]'],
            'Data': ['2022-01-01 12:30', '2022-01-02 24:15', '2022-01-03 08:45', '2022-01-04 18:00']
        })

    def test_del_unit(self):
        result_df = del_unit(self.test_df)
        self.assertFalse('[' in result_df['Rodzaj'].iloc[0])

    def test_remove_spaces_from_column_names(self):
        result_df = remove_spaces_from_column_names(self.test_df)
        self.assertEqual(result_df.columns.str.contains(' ').any(), False)

    def test_remove_spaces_from_data(self):
        result_df = remove_spaces_from_data(self.test_df)
        self.assertEqual(result_df.isin([' 24:']).any().any(), False)

    def test_drop_columns_with_all_nan(self):
        result_df = drop_columns_with_all_nan(self.test_df)
        self.assertTrue('Data' in result_df.columns)

    def test_split_dataframe_to_list(self):
        result_list = split_dataframe_to_list(self.test_df, 'Rodzaj')
        self.assertEqual(len(result_list), len(self.test_df['Rodzaj'].unique()))

    def test_set_dataframe_names_from_rodzaj(self):
        result_list = split_dataframe_to_list(self.test_df, 'Rodzaj')
        set_dataframe_names_from_rodzaj(result_list)
        self.assertTrue(hasattr(result_list[0], 'name'))




    def test_handle_24_hour_time(self):
        result_value = handle_24_hour_time('2022-01-02 24:15')
        self.assertEqual(result_value, '2022-01-03 00:15')

    def test_prepare_data(self):
        result_list = prepare_data(self.test_df)
        self.assertTrue(len(result_list) > 0)


if __name__ == '__main__':
    unittest.main()
