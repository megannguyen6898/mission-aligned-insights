
import pandas as pd
import json
from fastapi import UploadFile
from sqlalchemy.orm import Session
from typing import Dict, Any

class DataService:
    async def process_uploaded_file(self, file: UploadFile, upload_id: int, db: Session) -> Dict[str, Any]:
        """Process uploaded file and extract structured data when possible."""
        content = await file.read()
        
        try:
            # Determine file type and parse accordingly
            if file.filename.endswith('.csv'):
                df = pd.read_csv(pd.io.common.StringIO(content.decode('utf-8')))
            elif file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(pd.io.common.BytesIO(content))
            elif file.filename.endswith('.json'):
                data = json.loads(content.decode('utf-8'))
                df = pd.json_normalize(data)
            elif file.filename.endswith(('.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg')):
                # For binary documents and images we cannot easily parse rows
                # yet, so just store metadata
                return {
                    "row_count": 0,
                    "columns": [],
                    "processed_data": {
                        "filename": file.filename,
                        "size": len(content)
                    }
                }
            else:
                raise ValueError("Unsupported file format")
            
            # Basic data validation
            if df.empty:
                raise ValueError("File contains no data")
            
            # Store processed data (in production, save to file system or cloud storage)
            numeric_summary = {}
            for col in df.select_dtypes(include='number').columns:
                numeric_summary[col] = float(df[col].sum())

            processed_data = {
                "columns": df.columns.tolist(),
                "row_count": len(df),
                "sample_data": df.head(5).to_dict('records'),
                "data_types": df.dtypes.astype(str).to_dict(),
                "numeric_summary": numeric_summary,
            }
            
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
                df = pd.read_csv(pd.io.common.StringIO(content.decode('utf-8')))
            elif file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(pd.io.common.BytesIO(content))
            elif file.filename.endswith('.json'):
                data = json.loads(content.decode('utf-8'))
                df = pd.json_normalize(data)
            elif file.filename.endswith(('.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg')):
                return {"valid": True, "row_count": 0, "columns": []}
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
