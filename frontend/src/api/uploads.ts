import { api } from "@/lib/api";

export function uploadFile(file: File) {
  const form = new FormData();
  form.append("file", file);
  return api.post("/uploads", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

export function validateUpload(uploadId: number) {
  return api.post(`/uploads/${uploadId}/validate`);
}

export function ingestUpload(uploadId: number) {
  return api.post(`/uploads/${uploadId}/ingest`);
}
