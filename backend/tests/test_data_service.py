import pandas as pd
from io import BytesIO
import pytest
import asyncio
from fastapi import UploadFile

from backend.app.services.data_service import DataService
from backend.app.models.data_upload import DataUpload

class DummyUpload:
    def __init__(self):
        self.id = 1
        self.file_name = None
        self.upload_metadata = None
        self.user_id = 1

class DummyQuery:
    def __init__(self, obj):
        self.obj = obj
    def filter(self, *args, **kwargs):
        return self
    def first(self):
        return self.obj

class DummyDB:
    def __init__(self, upload):
        self.upload = upload
    def query(self, model):
        assert model is DataUpload
        return DummyQuery(self.upload)
    def add(self, obj):
        pass
    def commit(self):
        pass
    def refresh(self, obj):
        pass

def create_excel_upload():
    df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    df2 = pd.DataFrame({'A': [5, 6, 7], 'B': [8, 9, 10]})
    combined = pd.concat([df1, df2], ignore_index=True)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df1.to_excel(writer, index=False, sheet_name='Sheet1')
        df2.to_excel(writer, index=False, sheet_name='Sheet2')
    buffer.seek(0)
    upload = UploadFile(filename='test.xlsx', file=BytesIO(buffer.getvalue()))
    return upload, combined

def create_csv_upload(delimiter: str):
    df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    csv_bytes = df.to_csv(sep=delimiter, index=False).encode('utf-8')
    upload = UploadFile(filename='test.csv', file=BytesIO(csv_bytes))
    return upload, df

def test_process_uploaded_file_multi_sheet():
    upload, combined = create_excel_upload()
    dummy_upload = DummyUpload()
    db = DummyDB(dummy_upload)
    service = DataService()
    result = asyncio.run(service.process_uploaded_file(upload, 1, db))

    assert result['row_count'] == len(combined)
    assert result['processed_data']['row_count'] == len(combined)
    assert result['processed_data']['records'] == combined.to_dict('records')

def test_validate_data_file_multi_sheet():
    upload, combined = create_excel_upload()
    service = DataService()
    result = asyncio.run(service.validate_data_file(upload))
    assert result['valid'] is True
    assert result['row_count'] == len(combined)
    assert result['columns'] == list(combined.columns)


@pytest.mark.parametrize("delimiter", [" ", "\t"])
def test_validate_space_or_tab_delimited_csv(delimiter):
    upload, df = create_csv_upload(delimiter)
    service = DataService()
    result = asyncio.run(service.validate_data_file(upload))
    assert result['valid'] is True
    assert result['columns'] == list(df.columns)

