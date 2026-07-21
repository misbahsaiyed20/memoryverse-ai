import { FileImage, FileText, File as FileIcon } from "lucide-react";

const IMAGE_EXTENSIONS = new Set(["png", "jpg", "jpeg"]);
const TEXT_EXTENSIONS = new Set(["pdf", "doc", "docx", "txt"]);

export function DocumentFileIcon({
  extension,
  className,
}: {
  extension: string;
  className?: string;
}) {
  const ext = extension.toLowerCase();
  if (IMAGE_EXTENSIONS.has(ext)) return <FileImage className={className} size={20} />;
  if (TEXT_EXTENSIONS.has(ext)) return <FileText className={className} size={20} />;
  return <FileIcon className={className} size={20} />;
}
