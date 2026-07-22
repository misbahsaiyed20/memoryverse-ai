/**
 * Document API client — list, rename, delete, download, and upload
 * (with progress) against the Sprint 3 backend endpoints.
 *
 * Backend success responses are wrapped as {success, message, data} —
 * these helpers unwrap that envelope so components just deal with plain
 * data. Errors from apiFetch/fetch calls propagate as rejected promises;
 * components decide how to surface them.
 */
import { apiFetch } from "@/lib/api";
import { getFirebaseAuth } from "@/lib/firebase";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export interface DocumentItem {
  id: string;
  title: string;
  original_filename: string;
  file_extension: string;
  mime_type: string;
  file_size: number;
  status: "UPLOADED" | "PROCESSING" | "PROCESSED" | "FAILED" | "ARCHIVED";
  created_at: string;
  updated_at: string;
  processed_at: string | null;
  has_extracted_text: boolean;
  processing_error: string | null;
}

interface ApiEnvelope<T> {
  success: boolean;
  message: string;
  data: T;
}

async function extractErrorMessage(res: Response, fallback: string): Promise<string> {
  try {
    const body = await res.json();
    return body.detail || body.message || fallback;
  } catch {
    return fallback;
  }
}

export async function listDocuments(): Promise<DocumentItem[]> {
  const res = await apiFetch("/api/v1/documents");
  if (!res.ok) throw new Error(await extractErrorMessage(res, "Failed to load documents."));
  const body: ApiEnvelope<DocumentItem[]> = await res.json();
  return body.data;
}

export async function renameDocument(id: string, title: string): Promise<DocumentItem> {
  const res = await apiFetch(`/api/v1/documents/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error(await extractErrorMessage(res, "Failed to rename document."));
  const body: ApiEnvelope<DocumentItem> = await res.json();
  return body.data;
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await apiFetch(`/api/v1/documents/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error(await extractErrorMessage(res, "Failed to delete document."));
}

export async function processDocument(id: string): Promise<{ status: DocumentItem["status"] }> {
  const res = await apiFetch(`/api/v1/documents/${id}/process`, { method: "POST" });
  if (!res.ok) throw new Error(await extractErrorMessage(res, "Failed to start processing."));
  const body: ApiEnvelope<{ status: DocumentItem["status"] }> = await res.json();
  return body.data;
}

export async function downloadDocument(id: string, filename: string): Promise<void> {
  const user = getFirebaseAuth().currentUser;
  if (!user) throw new Error("Not authenticated.");
  const idToken = await user.getIdToken();

  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${id}/download`, {
    headers: { Authorization: `Bearer ${idToken}` },
  });
  if (!res.ok) throw new Error(await extractErrorMessage(res, "Failed to download document."));

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const link = window.document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

/**
 * Uploads with progress via XHR (fetch has no upload-progress event).
 * Returns both the result promise and an abort() to cancel mid-upload.
 */
export function uploadDocument(
  file: File,
  onProgress: (percent: number) => void,
): { promise: Promise<DocumentItem>; abort: () => void } {
  const xhr = new XMLHttpRequest();

  const promise = new Promise<DocumentItem>((resolve, reject) => {
    (async () => {
      const user = getFirebaseAuth().currentUser;
      if (!user) {
        reject(new Error("Not authenticated."));
        return;
      }
      const idToken = await user.getIdToken();

      const formData = new FormData();
      formData.append("file", file);

      xhr.open("POST", `${API_BASE_URL}/api/v1/documents/upload`);
      xhr.setRequestHeader("Authorization", `Bearer ${idToken}`);

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          onProgress(Math.round((event.loaded / event.total) * 100));
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const body: ApiEnvelope<DocumentItem> = JSON.parse(xhr.responseText);
            resolve(body.data);
          } catch {
            reject(new Error("Unexpected response from server."));
          }
        } else {
          try {
            const body = JSON.parse(xhr.responseText);
            reject(new Error(body.detail || body.message || "Upload failed."));
          } catch {
            reject(new Error("Upload failed."));
          }
        }
      };

      xhr.onerror = () => reject(new Error("Upload failed — network error."));
      xhr.send(formData);
    })();
  });

  return { promise, abort: () => xhr.abort() };
}
