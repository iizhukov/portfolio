import type { Project as ApiProject } from '@shared/api/types/projects'
import { adaptApiProjectToFinder } from '../utils/project-adapter'
import type { Project } from '../types/finder'
import { STORAGE_KEYS } from '@shared/constants/storage'
import { safeJsonParse } from '@shared/utils/safe-json'
import { isBrowser } from '@shared/utils/browser'

interface ProjectData {
  id: string
  name: string
  type: 'folder' | 'file'
  icon: string
  fileType?: string
  url?: string
  children?: string[]
}

type StoreUpdateCallback = () => void

class ProjectsStore {
  private projects: Map<string, ProjectData> = new Map()
  private initialized = false
  private updateCounter = 0
  private listeners: Set<StoreUpdateCallback> = new Set()

  private notifyListeners(): void {
    this.updateCounter++
    this.listeners.forEach(callback => callback())
  }

  subscribe(callback: StoreUpdateCallback): () => void {
    this.listeners.add(callback)
    return () => {
      this.listeners.delete(callback)
    }
  }

  getUpdateCounter(): number {
    return this.updateCounter
  }

  private loadFromStorage(): void {
    if (!isBrowser) return

    try {
      const stored = localStorage.getItem(STORAGE_KEYS.FINDER_PROJECTS)
      if (stored) {
        const parsed = safeJsonParse<Record<string, ProjectData>>(stored, {})
        this.projects = new Map(Object.entries(parsed))
        this.initialized = true
      }
    } catch (error) {
      console.error('Failed to load projects from storage:', error)
    }
  }

  private saveToStorage(): void {
    if (!isBrowser) return

    try {
      const obj = Object.fromEntries(this.projects)
      localStorage.setItem(STORAGE_KEYS.FINDER_PROJECTS, JSON.stringify(obj))
    } catch (error) {
      console.error('Failed to save projects to storage:', error)
    }
  }

  private projectDataToProject(data: ProjectData): Project {
    const project: Project = {
      id: data.id,
      name: data.name,
      type: data.type,
      icon: data.icon,
      fileType: data.fileType as Project['fileType'],
      url: data.url,
    }

    if (data.children && data.children.length > 0) {
      project.children = data.children
        .map(childId => {
          const childData = this.projects.get(childId)
          if (!childData) return null
          return this.projectDataToProject(childData)
        })
        .filter((p): p is Project => p !== null)
    }

    return project
  }

  private apiProjectToData(apiProject: ApiProject): ProjectData {
    const normalized = adaptApiProjectToFinder(apiProject)
    return {
      id: normalized.id,
      name: normalized.name,
      type: normalized.type,
      icon: normalized.icon,
      fileType: normalized.fileType,
      url: normalized.url,
      children: normalized.children?.map(child => child.id),
    }
  }

  private mergeProjectData(data: ProjectData): void {
    const existing = this.projects.get(data.id)
    
    if (existing) {
      const existingChildrenIds = new Set(existing.children || [])
      const newChildrenIds = new Set(data.children || [])
      const mergedChildrenIds = Array.from(new Set([...existingChildrenIds, ...newChildrenIds]))
      
      this.projects.set(data.id, {
        ...existing,
        ...data,
        children: mergedChildrenIds.length > 0 ? mergedChildrenIds : undefined,
      })
    } else {
      this.projects.set(data.id, data)
    }
  }

  private mergeProjectTree(apiProject: ApiProject): void {
    const normalized = adaptApiProjectToFinder(apiProject)
    
    const data: ProjectData = {
      id: normalized.id,
      name: normalized.name,
      type: normalized.type,
      icon: normalized.icon,
      fileType: normalized.fileType,
      url: normalized.url,
      children: normalized.children?.map(child => child.id),
    }
    
    this.mergeProjectData(data)
    
    if (normalized.children) {
      for (const child of normalized.children) {
        const childData: ProjectData = {
          id: child.id,
          name: child.name,
          type: child.type,
          icon: child.icon,
          fileType: child.fileType,
          url: child.url,
          children: child.children?.map(grandChild => grandChild.id),
        }
        this.mergeProjectData(childData)
        
        if (child.children) {
          for (const grandChild of child.children) {
            const grandChildData: ProjectData = {
              id: grandChild.id,
              name: grandChild.name,
              type: grandChild.type,
              icon: grandChild.icon,
              fileType: grandChild.fileType,
              url: grandChild.url,
            }
            this.mergeProjectData(grandChildData)
          }
        }
      }
    }
  }

  initialize(): void {
    if (this.initialized) return
    this.loadFromStorage()
    this.initialized = true
  }

  addProjects(apiProjects: ApiProject[]): void {
    for (const apiProject of apiProjects) {
      this.mergeProjectTree(apiProject)
    }
    this.saveToStorage()
    this.notifyListeners()
  }

  addProject(apiProject: ApiProject): void {
    this.mergeProjectTree(apiProject)
    this.saveToStorage()
    this.notifyListeners()
  }

  getProject(id: string): Project | undefined {
    const data = this.projects.get(id)
    if (!data) return undefined
    return this.projectDataToProject(data)
  }

  getRootProjects(): Project[] {
    const roots: Project[] = []
    const allIds = new Set(this.projects.keys())
    
    for (const [id, data] of this.projects.entries()) {
      let hasParent = false
      for (const other of this.projects.values()) {
        if (other.children?.includes(id)) {
          hasParent = true
          break
        }
      }
      if (!hasParent) {
        roots.push(this.projectDataToProject(data))
      }
    }
    
    return roots.sort((a, b) => {
      if (a.type === 'folder' && b.type !== 'folder') return -1
      if (a.type !== 'folder' && b.type === 'folder') return 1
      return a.name.localeCompare(b.name, undefined, { sensitivity: 'base' })
    })
  }

  getChildren(parentId: string): Project[] {
    const parent = this.projects.get(parentId)
    if (!parent) {
      return []
    }
    
    if (!parent.children || parent.children.length === 0) {
      return []
    }
    
    return parent.children
      .map(childId => {
        const childData = this.projects.get(childId)
        if (!childData) return null
        return this.projectDataToProject(childData)
      })
      .filter((p): p is Project => p !== null)
      .sort((a, b) => {
        if (a.type === 'folder' && b.type !== 'folder') return -1
        if (a.type !== 'folder' && b.type === 'folder') return 1
        return a.name.localeCompare(b.name, undefined, { sensitivity: 'base' })
      })
  }

  getProjectByPath(path: string[]): Project | null {
    if (path.length === 0) {
      return null
    }

    let current: Project | null = null
    const rootProjects = this.getRootProjects()
    
    for (let i = 0; i < path.length; i++) {
      const pathId = path[i]
      
      if (i === 0) {
        current = rootProjects.find(p => p.id === pathId) || null
      } else {
        if (!current) return null
        const parent: Project = current
        current = this.getChildren(parent.id).find(p => p.id === pathId) || null
      }
      
      if (!current) return null
    }
    
    return current
  }

  clear(): void {
    this.projects.clear()
    if (isBrowser) {
      localStorage.removeItem(STORAGE_KEYS.FINDER_PROJECTS)
    }
  }
}

export const projectsStore = new ProjectsStore()

