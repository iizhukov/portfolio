import type { Project as ApiProject } from '../api/types'
import type { Project as FinderProject, FileType } from '../types/finder'
import { getFileIcon } from './file-icons'

export const adaptApiProjectToFinder = (apiProject: ApiProject): FinderProject => {
  const finderProject: FinderProject = {
    id: String(apiProject.id),
    name: apiProject.name,
    type: apiProject.type,
    icon: getFileIcon(apiProject.type, apiProject.file_type),
    url: apiProject.url || undefined,
  }

  if (apiProject.file_type) {
    finderProject.fileType = apiProject.file_type as FileType
  }

  if (apiProject.children && apiProject.children.length > 0) {
    finderProject.children = apiProject.children.map(adaptApiProjectToFinder)
  }

  return finderProject
}

