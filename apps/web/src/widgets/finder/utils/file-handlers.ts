import { type Project } from '../types/finder'

/**
 * Обработка открытия файлов разных типов.
 * Все файлы хранятся в MinIO, используется только URL.
 */
export const handleFileOpen = (project: Project): void => {
  if (project.type === 'folder') {
    return // Папки обрабатываются отдельно
  }

  if (!project.url) {
    console.warn(`No URL for file: ${project.name}`)
    alert(`[Заглушка] Файл ${project.name} не имеет URL`)
    return
  }

  const fileType = project.fileType || 'folder'

  switch (fileType) {
    case 'readme':
      handleReadme(project)
      break
    case 'architecture':
      handleArchitecture(project)
      break
    case 'demo':
      handleDemo(project)
      break
    case 'github':
      handleGithub(project)
      break
    case 'database':
      handleDatabase(project)
      break
    case 'swagger':
      handleSwagger(project)
      break
    default:
      // Для неизвестных типов просто открываем URL
      window.open(project.url, '_blank')
  }
}

/**
 * Обработка README файла.
 * В будущем: открыть модальное окно с markdown контентом из URL.
 */
const handleReadme = (project: Project): void => {
  // TODO: Загрузить markdown из URL и открыть модальное окно с markdown viewer
  if (project.url) {
    // Временная заглушка: открываем URL в новой вкладке
    // В будущем: загрузить контент и показать в модальном окне
    window.open(project.url, '_blank')
  }
}

/**
 * Обработка файла архитектуры (excalidraw).
 * В будущем: открыть embedded excalidraw viewer из URL.
 */
const handleArchitecture = (project: Project): void => {
  // TODO: Загрузить excalidraw данные из URL и открыть embedded viewer
  if (project.url) {
    // Временная заглушка: открываем URL в новой вкладке
    // В будущем: загрузить excalidraw данные и показать в embedded viewer
    window.open(project.url, '_blank')
  }
}

/**
 * Обработка ссылки на демо.
 * Открывает демо в новой вкладке.
 */
const handleDemo = (project: Project): void => {
  if (project.url) {
    window.open(project.url, '_blank')
  }
}

/**
 * Обработка ссылки на GitHub.
 * Открывает репозиторий в новой вкладке.
 */
const handleGithub = (project: Project): void => {
  if (project.url) {
    window.open(project.url, '_blank')
  }
}

/**
 * Обработка диаграммы базы данных (dbdiagram).
 * В будущем: открыть embedded dbdiagram viewer из URL.
 */
const handleDatabase = (project: Project): void => {
  // TODO: Загрузить dbdiagram данные из URL и открыть embedded viewer
  if (project.url) {
    // Временная заглушка: открываем URL в новой вкладке
    // В будущем: загрузить dbdiagram данные и показать в embedded viewer
    window.open(project.url, '_blank')
  }
}

/**
 * Обработка Swagger документации.
 * В будущем: открыть упрощенный swagger viewer (только просмотр, без возможности запускать запросы).
 */
const handleSwagger = (project: Project): void => {
  // TODO: Загрузить swagger/openapi spec из URL и открыть read-only viewer
  if (project.url) {
    // Временная заглушка: открываем URL в новой вкладке
    // В будущем: загрузить swagger spec и показать в read-only viewer
    window.open(project.url, '_blank')
  }
}

