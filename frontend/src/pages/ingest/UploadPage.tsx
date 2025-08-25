import React from "react";
import UploadWidget from "@/components/ingest/UploadWidget";

const UploadPage: React.FC = () => (
  <div className="space-y-6">
    <h1 className="text-3xl font-bold text-gray-900">Ingest Upload</h1>
    <UploadWidget />
  </div>
);

export default UploadPage;

