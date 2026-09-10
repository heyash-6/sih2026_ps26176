import { useState, useEffect, useMemo } from 'react'
import { getDatabaseTables, getTableData, triggerSync } from '../services/api'

export default function DatabaseExplorer({ lang }) {
  const [tables, setTables] = useState([])
  const [selectedTable, setSelectedTable] = useState('pfz_zones')
  const [tableData, setTableData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [viewMode, setViewMode] = useState('table') // 'table' | 'json'
  const [copied, setCopied] = useState(false)
  const [limit, setLimit] = useState(50)
  const [error, setError] = useState(null)

  const fetchTables = async () => {
    try {
      const res = await getDatabaseTables()
      if (res && res.tables) {
        setTables(res.tables)
      }
    } catch (err) {
      console.error('Failed to load database tables:', err)
    }
  }

  const fetchTableRows = async (tableName, rowLimit = limit) => {
    setLoading(true)
    setError(null)
    try {
      const res = await getTableData(tableName, rowLimit)
      if (res && res.rows) {
        setTableData(res)
      } else if (res && res.error) {
        setError(res.error)
        setTableData({ table: tableName, count: 0, rows: [] })
      } else {
        setTableData({ table: tableName, count: 0, rows: [] })
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch table records.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTables()
  }, [])

  useEffect(() => {
    if (selectedTable) {
      fetchTableRows(selectedTable, limit)
    }
  }, [selectedTable, limit])

  const handleSync = async () => {
    setSyncing(true)
    try {
      await triggerSync()
      await fetchTables()
      await fetchTableRows(selectedTable, limit)
    } catch (err) {
      console.error('Sync error:', err)
    } finally {
      setSyncing(false)
    }
  }

  const handleCopyJson = () => {
    if (!tableData?.rows) return
    navigator.clipboard.writeText(JSON.stringify(tableData.rows, null, 2))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Filter rows based on search term across all columns
  const filteredRows = useMemo(() => {
    if (!tableData?.rows) return []
    if (!searchTerm.trim()) return tableData.rows
    const q = searchTerm.toLowerCase()
    return tableData.rows.filter(row =>
      Object.values(row).some(val =>
        val !== null && val !== undefined && String(val).toLowerCase().includes(q)
      )
    )
  }, [tableData, searchTerm])

  // Extract columns dynamically from rows
  const columns = useMemo(() => {
    if (!tableData?.rows || tableData.rows.length === 0) return []
    const cols = Object.keys(tableData.rows[0])
    return cols
  }, [tableData])

  const activeMeta = tables.find(t => t.name === selectedTable)

  return (
    <div className="dbExplorerContainer">
      {/* Top Banner */}
      <div className="dbBanner">
        <div className="dbBannerLeft">
          <div className="dbBadgeRow">
            <span className="dbStatusBadge dbOnline">● Supabase Connected</span>
            <span className="dbStatusBadge dbRls">🔓 RLS Disabled (All Tables Visible)</span>
            <span className="dbStatusBadge dbProject">Project: byikekhtwiewlpxbuwgo</span>
          </div>
          <h2 className="dbTitle">Supabase Live Database & Tables</h2>
          <p className="dbSubtitle">
            Directly browse, query, inspect, and verify all 9 database tables populated by autonomous marine agents and satellite feeds.
          </p>
        </div>

        <div className="dbBannerActions">
          <a
            href="https://supabase.com/dashboard/project/byikekhtwiewlpxbuwgo/editor"
            target="_blank"
            rel="noopener noreferrer"
            className="dbActionBtn dbSupabaseBtn"
          >
            ⚡ Open in Supabase Dashboard ↗
          </a>
          <button
            className="dbActionBtn dbSyncBtn"
            onClick={handleSync}
            disabled={syncing}
          >
            {syncing ? '🔄 Ingesting...' : '📡 Ingest Live Marine Data'}
          </button>
          <button
            className="dbActionBtn dbRefreshBtn"
            onClick={() => {
              fetchTables()
              fetchTableRows(selectedTable, limit)
            }}
          >
            ⟳ Refresh
          </button>
        </div>
      </div>

      {/* Table Selection Cards */}
      <div className="dbTablesGrid">
        {tables.map(t => {
          const isSelected = t.name === selectedTable
          return (
            <button
              key={t.name}
              className={`dbTableCard ${isSelected ? 'active' : ''}`}
              onClick={() => setSelectedTable(t.name)}
            >
              <div className="dbTableCardTop">
                <span className="dbTableIcon">{t.icon || '⛃'}</span>
                <span className={`dbRowCountPill ${t.row_count > 0 ? 'hasData' : 'empty'}`}>
                  {t.row_count} {t.row_count === 1 ? 'row' : 'rows'}
                </span>
              </div>
              <div className="dbTableCardName">{t.title}</div>
              <div className="dbTableCardSchema"><code>public.{t.name}</code></div>
              <div className="dbTableCardDesc">{t.desc}</div>
            </button>
          )
        })}
      </div>

      {/* Active Table Viewer */}
      <div className="dbViewerCard">
        <div className="dbViewerHeader">
          <div className="dbViewerTitleGroup">
            <h3>
              <span className="dbViewerIcon">{activeMeta?.icon || '⛃'}</span>
              <span>{activeMeta?.title || selectedTable}</span>
              <code>public.{selectedTable}</code>
            </h3>
            <p className="dbViewerDesc">{activeMeta?.desc}</p>
          </div>

          <div className="dbViewerControls">
            <div className="dbSearchWrap">
              <span className="dbSearchIcon">🔍</span>
              <input
                type="text"
                className="dbSearchInput"
                placeholder={`Search ${selectedTable}...`}
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
              />
              {searchTerm && (
                <button className="dbSearchClear" onClick={() => setSearchTerm('')}>✕</button>
              )}
            </div>

            <div className="dbLimitSelect">
              <label>Rows:</label>
              <select value={limit} onChange={e => setLimit(Number(e.target.value))}>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>

            <div className="dbViewModeToggle">
              <button
                className={`dbModeBtn ${viewMode === 'table' ? 'active' : ''}`}
                onClick={() => setViewMode('table')}
              >
                📊 Table
              </button>
              <button
                className={`dbModeBtn ${viewMode === 'json' ? 'active' : ''}`}
                onClick={() => setViewMode('json')}
              >
                {'{ }'} JSON
              </button>
            </div>

            <button
              className="dbCopyBtn"
              onClick={handleCopyJson}
              title="Copy table records to clipboard as JSON"
            >
              {copied ? '✓ Copied' : '📋 Copy JSON'}
            </button>
          </div>
        </div>

        {/* Status bar */}
        <div className="dbStatusBar">
          <span>
            Showing <b>{filteredRows.length}</b> of <b>{tableData?.count || 0}</b> loaded rows
            {searchTerm && ` (filtered from ${tableData?.rows?.length || 0})`}
          </span>
          {loading && <span className="dbLoadingText">⚡ Querying Supabase REST API...</span>}
        </div>

        {/* Content area */}
        {error && (
          <div className="dbErrorNotice">
            <b>Database Error:</b> {error}
          </div>
        )}

        {loading && !tableData && (
          <div className="dbLoadingPlaceholder">
            <div className="dbSpinner" />
            <p>Fetching records from Supabase table <code>{selectedTable}</code>...</p>
          </div>
        )}

        {!loading && filteredRows.length === 0 && !error && (
          <div className="dbEmptyState">
            <div className="dbEmptyIcon">📂</div>
            <h4>No records match the current view</h4>
            <p>
              {searchTerm
                ? `No rows found matching "${searchTerm}". Clear search to view all records.`
                : `Table "${selectedTable}" is currently empty. Click "Ingest Live Marine Data" to populate it.`}
            </p>
          </div>
        )}

        {/* TABLE VIEW */}
        {viewMode === 'table' && filteredRows.length > 0 && (
          <div className="dbTableScrollWrapper">
            <table className="dbDataTable">
              <thead>
                <tr>
                  <th className="dbRowIndexTh">#</th>
                  {columns.map(col => (
                    <th key={col} className="dbColTh">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filteredRows.map((row, idx) => (
                  <tr key={row.id || idx}>
                    <td className="dbRowIndexTd">{idx + 1}</td>
                    {columns.map(col => {
                      const val = row[col]
                      return (
                        <td key={col} className="dbDataTd">
                          {renderCellValue(col, val)}
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* JSON VIEW */}
        {viewMode === 'json' && filteredRows.length > 0 && (
          <div className="dbJsonWrapper">
            <pre className="dbJsonPre">
              {JSON.stringify(filteredRows, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {/* Supabase Reference Card */}
      <div className="dbRefCard">
        <div className="dbRefHeader">
          <span className="dbRefIcon">ℹ️</span>
          <h4>How to view and manage tables directly in the Supabase Cloud Console</h4>
        </div>
        <div className="dbRefGrid">
          <div className="dbRefItem">
            <strong>Table Editor</strong>
            <p>Direct GUI table viewer and editor with filters, sorting, and cell editing.</p>
            <a
              href="https://supabase.com/dashboard/project/byikekhtwiewlpxbuwgo/editor"
              target="_blank"
              rel="noopener noreferrer"
              className="dbRefLink"
            >
              Go to Table Editor ↗
            </a>
          </div>
          <div className="dbRefItem">
            <strong>SQL Editor</strong>
            <p>Run custom PostgreSQL queries, execute aggregations, and inspect schema structures.</p>
            <a
              href="https://supabase.com/dashboard/project/byikekhtwiewlpxbuwgo/sql"
              target="_blank"
              rel="noopener noreferrer"
              className="dbRefLink"
            >
              Go to SQL Editor ↗
            </a>
          </div>
          <div className="dbRefItem">
            <strong>Authentication & Users</strong>
            <p>Inspect registered captain accounts, session tokens, and security roles.</p>
            <a
              href="https://supabase.com/dashboard/project/byikekhtwiewlpxbuwgo/auth/users"
              target="_blank"
              rel="noopener noreferrer"
              className="dbRefLink"
            >
              Go to Auth Users ↗
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

function renderCellValue(col, val) {
  if (val === null || val === undefined) {
    return <span className="dbNullVal">—</span>
  }

  if (typeof val === 'boolean') {
    return val ? (
      <span className="dbBoolBadge dbTrue">true</span>
    ) : (
      <span className="dbBoolBadge dbFalse">false</span>
    )
  }

  if (typeof val === 'object') {
    return <code className="dbObjectCode">{JSON.stringify(val)}</code>
  }

  const str = String(val)

  // Format ISO timestamps
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(str)) {
    try {
      const d = new Date(str)
      return (
        <span className="dbDateVal" title={str}>
          {d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })} {d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}
        </span>
      )
    } catch {
      return str
    }
  }

  // Highlight ID columns
  if (col === 'id' || col.endsWith('_id') || col === 'zone_code') {
    return <span className="dbIdBadge">{str}</span>
  }

  // Highlight score / confidence
  if (col === 'confidence_score' || col === 'risk_level') {
    return <span className="dbHighlightBadge">{str}</span>
  }

  // Coordinates
  if (col === 'latitude' || col === 'longitude') {
    return <span className="dbCoordVal">{Number(val).toFixed(4)}°</span>
  }

  return str
}
