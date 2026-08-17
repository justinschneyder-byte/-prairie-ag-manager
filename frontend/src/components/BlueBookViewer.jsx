import { useEffect, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";
import { api } from "../api.js";

pdfjs.GlobalWorkerOptions.workerSrc = new URL("pdfjs-dist/build/pdf.worker.min.mjs", import.meta.url).toString();

export default function BlueBookViewer({ onClose }) {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [pdfDoc, setPdfDoc] = useState(null);
  const [loadError, setLoadError] = useState("");
  const [pageInput, setPageInput] = useState("1");

  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [searchProgress, setSearchProgress] = useState(0);
  const [searched, setSearched] = useState(false);

  const [viewportWidth, setViewportWidth] = useState(window.innerWidth);
  useEffect(() => {
    const onResize = () => setViewportWidth(window.innerWidth);
    window.addEventListener("resize", onResize);
    window.addEventListener("orientationchange", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      window.removeEventListener("orientationchange", onResize);
    };
  }, []);

  useEffect(() => {
    setPageInput(String(pageNumber));
  }, [pageNumber]);

  function onDocumentLoadSuccess(pdf) {
    setNumPages(pdf.numPages);
    setPdfDoc(pdf);
  }

  async function handleSearch(e) {
    e.preventDefault();
    if (!pdfDoc || !query.trim()) return;
    setSearching(true);
    setSearched(true);
    setResults([]);
    setSearchProgress(0);
    const q = query.trim().toLowerCase();
    const found = [];

    for (let i = 1; i <= pdfDoc.numPages; i++) {
      try {
        const page = await pdfDoc.getPage(i);
        const content = await page.getTextContent();
        const text = content.items.map((item) => item.str).join(" ");
        const lower = text.toLowerCase();
        const idx = lower.indexOf(q);
        if (idx !== -1) {
          const start = Math.max(0, idx - 40);
          const end = Math.min(text.length, idx + q.length + 40);
          const snippet = `${start > 0 ? "…" : ""}${text.slice(start, end).trim()}${end < text.length ? "…" : ""}`;
          found.push({ page: i, snippet });
        }
      } catch {
        // couldn't extract text for this page — skip it, don't fail the whole search
      }
      setSearchProgress(i);
    }

    setResults(found);
    setSearching(false);
  }

  function jumpTo(page) {
    setPageNumber(page);
  }

  function handlePageInputSubmit(e) {
    e.preventDefault();
    const n = Number(pageInput);
    if (Number.isFinite(n) && n >= 1 && n <= (numPages || 1)) {
      setPageNumber(n);
    } else {
      setPageInput(String(pageNumber));
    }
  }

  return (
    <div className="pdf-viewer-overlay">
      <div className="pdf-viewer-toolbar">
        <button className="btn secondary" onClick={onClose}>
          ✕ Close
        </button>

        <form onSubmit={handlePageInputSubmit} className="pdf-page-nav">
          <button
            type="button"
            className="icon-btn"
            onClick={() => setPageNumber((p) => Math.max(1, p - 1))}
            disabled={pageNumber <= 1}
          >
            ‹
          </button>
          <input type="text" inputMode="numeric" value={pageInput} onChange={(e) => setPageInput(e.target.value)} />
          <span style={{ fontSize: "0.85rem", color: "var(--color-text-muted)" }}>/ {numPages ?? "…"}</span>
          <button
            type="button"
            className="icon-btn"
            onClick={() => setPageNumber((p) => Math.min(numPages || p, p + 1))}
            disabled={!!numPages && pageNumber >= numPages}
          >
            ›
          </button>
        </form>

        <form onSubmit={handleSearch} className="pdf-search-form">
          <input type="text" placeholder="Search product name…" value={query} onChange={(e) => setQuery(e.target.value)} />
          <button className="btn secondary" type="submit" disabled={searching || !pdfDoc}>
            {searching ? `Searching ${searchProgress}/${numPages}…` : "Search"}
          </button>
        </form>
      </div>

      <div className="pdf-viewer-body">
        {searched && (
          <div className="pdf-search-results">
            {searching && (
              <p className="empty-state">
                Searching page {searchProgress} of {numPages}…
              </p>
            )}
            {!searching && results.length === 0 && <p className="empty-state">No matches for "{query}".</p>}
            {!searching &&
              results.map((r) => (
                <button key={r.page} className="pdf-search-result" onClick={() => jumpTo(r.page)}>
                  <strong>Page {r.page}</strong>
                  <span>{r.snippet}</span>
                </button>
              ))}
          </div>
        )}

        <div className="pdf-viewer-page">
          {loadError && <p className="error-text">Couldn't load the PDF: {loadError}</p>}
          <Document
            file={api.blueBookFileUrl()}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={(err) => setLoadError(err.message)}
            loading={<p className="empty-state">Loading PDF…</p>}
          >
            <Page pageNumber={pageNumber} width={Math.min(720, viewportWidth - 32)} />
          </Document>
        </div>
      </div>
    </div>
  );
}
