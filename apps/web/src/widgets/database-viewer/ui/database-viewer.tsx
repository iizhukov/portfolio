import { useEffect, useMemo, useState } from 'react'
import mermaid from 'mermaid'
import { getFileUrl } from '@shared/utils/url'

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
})

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

const buildMermaidDiagram = (dbml: string) => {
  const { tables, relations } = parseDbml(dbml)
  const lines: string[] = ['erDiagram']

  tables.forEach(table => {
    const tableName = sanitizeName(table.name).toUpperCase()
    lines.push(`    ${tableName} {`)
    table.columns.forEach(column => {
      const attr =
        column.attributes?.map(attr => attr.toUpperCase()).join(' ') ??
        ''
      lines.push(`        ${column.type} ${column.name}${attr ? ` ${attr}` : ''}`)
    })
    lines.push('    }')
  })

  relations.forEach(rel => {
    lines.push(
      `    ${rel.leftTable.toUpperCase()} ||--o{ ${rel.rightTable.toUpperCase()} : "${rel.label}"`
    )
  })

  return lines.join('\n')
}

export const DatabaseViewer = ({ url, title }: DatabaseViewerProps) => {
  const [dbml, setDbml] = useState<string>('')
  const [svg, setSvg] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

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

  const mermaidText = useMemo(() => {
    if (!dbml) return ''
    try {
      return buildMermaidDiagram(dbml)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to parse DBML')
      return ''
    }
  }, [dbml])

  useEffect(() => {
    let cancelled = false
    const renderDiagram = async () => {
      if (!mermaidText) return
      try {
        const { svg } = await mermaid.render(
          `db-diagram-${Date.now()}`,
          mermaidText
        )
        if (!cancelled) {
          setSvg(svg)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to render diagram')
        }
      }
    }

    renderDiagram()
    return () => {
      cancelled = true
    }
  }, [mermaidText])

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
    <div className="w-full h-full bg-window-bg overflow-auto p-6">
      {title && (
        <h2 className="text-2xl font-semibold text-window-text mb-4">{title}</h2>
      )}
      <div
        className="bg-[#1f2433] rounded-xl p-4 shadow-inner"
        dangerouslySetInnerHTML={{ __html: svg }}
      />
    </div>
  )
}

