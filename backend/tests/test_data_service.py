import pandas as pd
from io import BytesIO
import pytest
from fastapi import UploadFile

from backend.app.services.data_service import DataService
from backend.app.models.data_upload import DataUpload

class DummyUpload:
    def __init__(self):
        self.file_name = None
        self.upload_metadata = None

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

@pytest.mark.asyncio
async def test_process_uploaded_file_multi_sheet():
    upload, combined = create_excel_upload()
    dummy_upload = DummyUpload()
    db = DummyDB(dummy_upload)
    service = DataService()
    result = await service.process_uploaded_file(upload, 1, db)

    assert result['row_count'] == len(combined)
    assert result['processed_data']['row_count'] == len(combined)
    assert result['processed_data']['records'] == combined.to_dict('records')

@pytest.mark.asyncio
async def test_validate_data_file_multi_sheet():
    upload, combined = create_excel_upload()
    service = DataService()
    result = await service.validate_data_file(upload)
    assert result['valid'] is True
    assert result['row_count'] == len(combined)
    assert result['columns'] == list(combined.columns)

