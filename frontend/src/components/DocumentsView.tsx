import React, { useState, useEffect, useRef } from 'react';
import { 
  Database, 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  Search, 
  Layers, 
  Clock, 
  HardDrive
} from 'lucide-react';
import type { DocumentItem } from '../types/decision';
import { listDocuments, uploadDocument } from '../services/api';

export const DocumentsView: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocs = async () => {
    try {
      setLoading(true);
      const data = await listDocuments();
      setDocuments(data);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      await uploadDocument(file);
      await fetchDocs();
    } catch (err: any) {
      alert(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const filteredDocs = documents.filter(d => 
    d.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (d.preview && d.preview.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="min-h-screen bg-[#10131C] text-[#E8E9ED] p-8 lg:p-12 overflow-y-auto">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-[#262D3D] gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <Database className="w-4 h-4 text-[#2F8F8B]" />
              <span className="font-mono text-xs text-[#2F8F8B] font-bold uppercase tracking-wider">
                Knowledge Base & Vector Store
              </span>
            </div>
            <h1 className="font-serif text-3xl font-bold text-[#E8E9ED] mt-2">
              ChromaDB Ingested Document Corpus
            </h1>
            <p className="text-xs text-[#8E96A5] mt-1 font-sans">
              All documents uploaded here are automatically parsed, chunked, and embedded for hybrid BM25 + dense vector retrieval in decision workflows.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="inline-flex items-center space-x-2 px-4 py-2.5 bg-[#2F8F8B] hover:bg-[#277875] text-white rounded-lg font-mono text-xs font-bold uppercase tracking-wider transition-colors shadow-md disabled:opacity-50"
            >
              <UploadCloud className="w-4 h-4" />
              <span>{uploading ? 'Chunking & Indexing...' : 'Upload Document'}</span>
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.md,.markdown,.txt"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>
        </div>

        {/* Search & Stats Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-[#181D2B] border border-[#262D3D] p-4 rounded-lg flex items-center space-x-3">
            <HardDrive className="w-5 h-5 text-[#2F8F8B]" />
            <div>
              <div className="font-mono text-[10px] text-[#8E96A5] uppercase">Total Documents</div>
              <div className="font-mono text-base font-bold text-[#E8E9ED]">{documents.length}</div>
            </div>
          </div>
          <div className="bg-[#181D2B] border border-[#262D3D] p-4 rounded-lg flex items-center space-x-3">
            <Layers className="w-5 h-5 text-[#4C8B5B]" />
            <div>
              <div className="font-mono text-[10px] text-[#8E96A5] uppercase">Indexed Chunks</div>
              <div className="font-mono text-base font-bold text-[#4C8B5B]">
                {documents.reduce((acc, d) => acc + d.chunk_count, 0)}
              </div>
            </div>
          </div>
          <div className="bg-[#181D2B] border border-[#262D3D] p-4 rounded-lg flex items-center space-x-3">
            <CheckCircle2 className="w-5 h-5 text-[#D9A441]" />
            <div>
              <div className="font-mono text-[10px] text-[#8E96A5] uppercase">Vector Embeddings</div>
              <div className="font-mono text-base font-bold text-[#D9A441]">all-MiniLM-L6-v2</div>
            </div>
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-[#8E96A5]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter documents by title or indexed snippet..."
            className="w-full bg-[#181D2B] border border-[#262D3D] rounded-lg pl-10 pr-4 py-2.5 text-xs text-[#E8E9ED] placeholder:text-[#8E96A5] focus:border-[#2F8F8B] outline-none font-mono"
          />
        </div>

        {/* Document Cards Grid */}
        {loading ? (
          <div className="text-center py-12 font-mono text-xs text-[#8E96A5]">
            Loading documents from database...
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="text-center py-16 border-2 border-dashed border-[#262D3D] rounded-xl space-y-3">
            <FileText className="w-8 h-8 text-[#8E96A5] mx-auto opacity-50" />
            <div className="font-mono text-xs text-[#8E96A5]">
              No documents indexed yet. Upload an architecture RFC or benchmark document to begin.
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredDocs.map((doc) => (
              <div
                key={doc.id}
                className="bg-[#181D2B] border border-[#262D3D] hover:border-[#2F8F8B]/50 rounded-xl p-5 space-y-3 transition-all group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-9 h-9 rounded bg-[#10131C] border border-[#262D3D] flex items-center justify-center text-[#2F8F8B]">
                      <FileText className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="font-mono text-xs font-bold text-[#E8E9ED] line-clamp-1">
                        {doc.filename}
                      </div>
                      <div className="font-mono text-[10px] text-[#8E96A5]">
                        {doc.file_type.toUpperCase()} • {(doc.file_size_bytes / 1024).toFixed(1)} KB
                      </div>
                    </div>
                  </div>

                  <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-[#4C8B5B]/15 text-[#4C8B5B] font-bold">
                    {doc.chunk_count} Chunks
                  </span>
                </div>

                {doc.preview && (
                  <p className="text-xs text-[#8E96A5] font-sans line-clamp-2 bg-[#10131C] p-2.5 rounded border border-[#262D3D]/60 leading-relaxed">
                    "{doc.preview}"
                  </p>
                )}

                <div className="flex items-center justify-between font-mono text-[10px] text-[#8E96A5] pt-2 border-t border-[#262D3D]">
                  <span className="flex items-center space-x-1">
                    <Clock className="w-3 h-3 text-[#8E96A5]" />
                    <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                  </span>
                  <span className="text-[#2F8F8B] font-semibold">Indexed in Chroma</span>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
};
