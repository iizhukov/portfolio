import { useEffect, useMemo, useState, useCallback } from 'react'
import ReactFlow, {
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  BackgroundVariant,
} from 'reactflow'
import type { Node, Edge, Connection } from 'reactflow'
import 'reactflow/dist/style.css'
import { getFileUrl } from '@shared/utils/url'
import { validateDbml } from '@shared/utils/validators'
import './database-viewer.css'

interface DatabaseViewerProps {
  url: string
  title?: string
}

interface DbColumn {
  name: string
  type: string
  attributes?: string[]
}

interface DbTable {
  name: string
  columns: DbColumn[]
}

interface DbRelation {
  leftTable: string
  rightTable: string
  leftColumn: string
  rightColumn: string
  label: string
}

const sanitizeName = (name: string) => name.replace(/[^a-zA-Z0-9_]/g, '_')

const parseDbml = (dbml: string) => {
  const tables: DbTable[] = []
  const relations: DbRelation[] = []
  const tableRegex = /Table\s+"?([\w\s]+?)"?\s*\{([\s\S]*?)\}/gi
  let tableMatch: RegExpExecArray | null

  while ((tableMatch = tableRegex.exec(dbml)) !== null) {
    const [, tableName, body] = tableMatch
    const columns: DbColumn[] = []
    body
      .split('\n')
      .map(line => line.trim())
      .filter(line => line && !line.startsWith('//') && !line.startsWith('Note'))
      .forEach(line => {
        const columnMatch = line.match(/^"?(?<name>[\w\s]+?)"?\s+(?<type>[^\s[]+)/)
        if (columnMatch?.groups) {
          const attrs = Array.from(line.matchAll(/\[(.*?)\]/g)).map(match => match[1])
          columns.push({
            name: columnMatch.groups.name.trim(),
            type: columnMatch.groups.type.trim(),
            attributes: attrs,
          })
        }
      })

    tables.push({
      name: tableName.trim(),
      columns,
    })
  }

  const relationRegex = /Ref\s*:\s*([^\s]+)\s+([<>-]+)\s+([^\s]+)/gi
  let relationMatch: RegExpExecArray | null
  while ((relationMatch = relationRegex.exec(dbml)) !== null) {
    const [, left, arrow, right] = relationMatch
    const [leftTable, leftColumn] = left.split('.')
    const [rightTable, rightColumn] = right.split('.')
    const isLeftParent = arrow.includes('<')

    relations.push({
      leftTable: sanitizeName(isLeftParent ? rightTable : leftTable),
      rightTable: sanitizeName(isLeftParent ? leftTable : rightTable),
      leftColumn: isLeftParent ? rightColumn : leftColumn,
      rightColumn: isLeftParent ? leftColumn : rightColumn,
      label: `${leftColumn} → ${rightColumn}`,
    })
  }

  return { tables, relations }
}

const buildNodesAndEdges = (dbml: string) => {
  const { tables, relations } = parseDbml(dbml)
  const nodes: Node[] = []
  const edges: Edge[] = []

  const nodeWidth = 250
  const nodeHeightBase = 60
  const columnsPerRow = 3
  const spacingX = 350
  const spacingY = 400

  tables.forEach((table, index) => {
    const row = Math.floor(index / columnsPerRow)
    const col = index % columnsPerRow
    const x = col * spacingX + 100
    const y = row * spacingY + 100

    const columnHeight = 30
    const headerHeight = 50
    const padding = 20
    const nodeHeight = headerHeight + table.columns.length * columnHeight + padding

    nodes.push({
      id: sanitizeName(table.name),
      type: 'default',
      position: { x, y },
      data: {
        label: (
          <div
            style={{
              width: nodeWidth,
              height: nodeHeight,
              background: '#fbfbfb',
              borderRadius: '4px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              overflow: 'hidden',
              boxSizing: 'border-box',
            }}
          >
            <div
              style={{
                background: '#316896',
                padding: '12px',
                borderBottom: '2px solid #2a5a7a',
                fontWeight: 600,
                fontSize: '14px',
                color: 'white',
              }}
            >
              {table.name}
            </div>
            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
              {table.columns.map((column, colIndex) => {
                const attrs = column.attributes?.join(', ') || ''
                return (
                  <div
                    key={colIndex}
                    style={{
                      padding: '6px 12px',
                      borderBottom: '1px solid #e5e5e5',
                      fontSize: '12px',
                      background: '#f2f2f2',
                    }}
                  >
                    <span style={{ color: '#666' }}>{column.type}</span>{' '}
                    <strong style={{ color: '#333', marginLeft: '8px' }}>{column.name}</strong>
                    {attrs && (
                      <span style={{ color: '#999', marginLeft: '8px', fontSize: '10px' }}>
                        [{attrs}]
                      </span>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        ),
      },
      style: {
        width: nodeWidth,
        height: nodeHeight,
        background: 'transparent',
        border: 'none',
        padding: 0,
      },
    })
  })

  relations.forEach((rel, index) => {
    edges.push({
      id: `edge-${index}`,
      source: rel.leftTable,
      target: rel.rightTable,
      label: rel.label,
      type: 'smoothstep',
      style: { stroke: '#666', strokeWidth: 2 },
      labelStyle: { fill: '#333', fontWeight: 500 },
      labelBgStyle: { fill: 'white', fillOpacity: 0.9 },
    })
  })

  return { nodes, edges }
}

export const DatabaseViewer = ({ url, title }: DatabaseViewerProps) => {
  const [dbml, setDbml] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    if (!dbml) return { nodes: [], edges: [] }
    try {
      const validation = validateDbml(dbml)
      if (!validation.valid) {
        setError(validation.error || 'Invalid DBML structure')
        return { nodes: [], edges: [] }
      }
      return buildNodesAndEdges(dbml)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to parse DBML')
      return { nodes: [], edges: [] }
    }
  }, [dbml])

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  useEffect(() => {
    setNodes(initialNodes)
    setEdges(initialEdges)
  }, [initialNodes, initialEdges, setNodes, setEdges])

  const onConnect = useCallback(
    (params: Connection) => setEdges(eds => addEdge(params, eds)),
    [setEdges]
  )

  useEffect(() => {
    let cancelled = false
    const loadDbml = async () => {
      try {
        setLoading(true)
        setError(null)
        const fileUrl = getFileUrl(url)
        const response = await fetch(fileUrl)
        if (!response.ok) {
          throw new Error(`Failed to load DBML: ${response.statusText}`)
        }
        const text = await response.text()
        if (!cancelled) {
          setDbml(text)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load DBML')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    if (url) {
      loadDbml()
    } else {
      setError('DBML file URL is missing')
      setLoading(false)
    }

    return () => {
      cancelled = true
    }
  }, [url])

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-window-bg text-window-text-secondary">
        Loading database diagram...
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-window-bg text-red-400">
        {error}
      </div>
    )
  }

  return (
    <div className="w-full h-full bg-window-bg flex flex-col">
      <div className="flex-1 rounded-xl m-6 border-2 border-gray-200 database-viewer-container">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
          nodesDraggable
          nodesConnectable={false}
          elementsSelectable
        >
          <Controls />
          <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#e5e5e5" />
        </ReactFlow>
      </div>
    </div>
  )
}
