
import pandas as pd
import json
from fastapi import UploadFile
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..models.data_upload import DataUpload
from ..models.audit_log import AuditLog, AuditAction

class DataService:
    async def process_uploaded_file(self, file: UploadFile, upload_id: int, db: Session) -> Dict[str, Any]:
        """Process uploaded CSV/Excel/JSON file and extract data"""
        content = await file.read()
        
        try:
            # Determine file type and parse accordingly
            if file.filename.endswith('.csv'):
                df = pd.read_csv(
                    pd.io.common.StringIO(content.decode("utf-8")),
                    sep=None,
                    engine="python",
                )
            elif file.filename.endswith(('.xlsx', '.xls')):
                sheets = pd.read_excel(pd.io.common.BytesIO(content), sheet_name=None)
                df = pd.concat(sheets.values(), ignore_index=True)
            elif file.filename.endswith('.json'):
                data = json.loads(content.decode('utf-8'))
                df = pd.json_normalize(data)
            else:
                raise ValueError("Unsupported file format")
            
            # Basic data validation
            if df.empty:
                raise ValueError("File contains no data")
            
            # Store processed data and entire dataset for later analysis
            processed_data = {
                "columns": df.columns.tolist(),
                "row_count": len(df),
                "sample_data": df.head(5).to_dict("records"),
                "data_types": df.dtypes.astype(str).to_dict(),
                "records": df.to_dict("records")
            }

            # Persist metadata in the DataUpload record
            upload = db.query(DataUpload).filter(DataUpload.id == upload_id).first()
            if upload:
                upload.file_name = file.filename
                upload.upload_metadata = json.dumps(processed_data)
                db.commit()
                db.refresh(upload)

                log = AuditLog(
                    user_id=upload.user_id,
                    action=AuditAction.upload,
                    target_type="data_upload",
                    target_id=upload.id,
                    details=f"Uploaded file {file.filename}",
                )
                db.add(log)
                db.commit()
                if hasattr(db, "added"):
                    db.added = upload

            return {
                "row_count": len(df),
                "columns": df.columns.tolist(),
                "processed_data": processed_data
            }
            
        except Exception as e:
            raise ValueError(f"Error processing file: {str(e)}")
    
    async def validate_data_file(self, file: UploadFile) -> Dict[str, Any]:
        """Validate uploaded data file without processing"""
        content = await file.read()
        
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(
                    pd.io.common.StringIO(content.decode("utf-8")),
                    sep=None,
                    engine="python",
                )
            elif file.filename.endswith(('.xlsx', '.xls')):
                sheets = pd.read_excel(pd.io.common.BytesIO(content), sheet_name=None)
                df = pd.concat(sheets.values(), ignore_index=True)
            elif file.filename.endswith('.json'):
                data = json.loads(content.decode('utf-8'))
                df = pd.json_normalize(data)
            else:
                return {"valid": False, "error": "Unsupported file format"}
            
            return {
                "valid": True,
                "row_count": len(df),
                "columns": df.columns.tolist(),
                "sample_data": df.head(3).to_dict('records')
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
