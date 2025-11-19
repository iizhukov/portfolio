from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import Optional, Sequence

from models.project import ProjectModel
from schemas.project import ProjectCreateSchema, ProjectUpdateSchema


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_projects(self, parent_id: Optional[int] = None, depth: Optional[int] = None) -> Sequence[ProjectModel]:
        if parent_id is not None:
            query = select(ProjectModel).where(ProjectModel.parent_id == parent_id).options(selectinload(ProjectModel.children))
        else:
            query = select(ProjectModel).where(ProjectModel.parent_id.is_(None)).options(selectinload(ProjectModel.children))
        
        result = await self.db.execute(query)
        projects = result.scalars().unique().all()

        effective_depth = depth if depth is not None else None
        for project in projects:
            await self._load_children_with_depth(project, effective_depth, 0)

        return projects

    async def get_project_by_id(self, project_id: int, depth: Optional[int] = None) -> Optional[ProjectModel]:
        result = await self.db.execute(
            select(ProjectModel)
            .where(ProjectModel.id == project_id)
            .options(selectinload(ProjectModel.children))
        )
        project = result.scalar_one_or_none()

        if project:
            await self._load_children_with_depth(project, depth, 0)

        return project

    async def get_project_tree(self, root_id: Optional[int] = None) -> Sequence[ProjectModel]:
        from sqlalchemy.orm import selectinload
        
        if root_id is not None:
            result = await self.db.execute(
                select(ProjectModel)
                .where(ProjectModel.id == root_id)
                .options(selectinload(ProjectModel.children))
            )
            root = result.scalar_one_or_none()
            if root:
                await self._load_children_recursive(root)
                return [root]
            return []
        else:
            result = await self.db.execute(
                select(ProjectModel)
                .where(ProjectModel.parent_id.is_(None))
                .options(selectinload(ProjectModel.children))
            )
            roots = result.scalars().all()
            for root in roots:
                await self._load_children_recursive(root)
            return roots
    
    async def _load_children_recursive(self, project: ProjectModel):
        if project.children:
            for child in project.children:
                result = await self.db.execute(
                    select(ProjectModel)
                    .where(ProjectModel.id == child.id)
                    .options(selectinload(ProjectModel.children))
                )
                loaded_child = result.scalar_one_or_none()
                if loaded_child and loaded_child.children:
                    await self._load_children_recursive(loaded_child)
    
    async def _load_children_with_depth(self, project: ProjectModel, depth: Optional[int], current_level: int):
        if depth is not None and current_level >= depth:
            project.children = []
            return
        
        if not project.children:
            return
        
        for child in project.children:
            result = await self.db.execute(
                select(ProjectModel)
                .where(ProjectModel.id == child.id)
                .options(selectinload(ProjectModel.children))
            )
            loaded_child = result.scalar_one_or_none()
            if loaded_child:
                await self._load_children_with_depth(loaded_child, depth, current_level + 1)

    async def create_project(self, project_data: ProjectCreateSchema) -> ProjectModel:
        new_project = ProjectModel(
            name=project_data.name,
            type=project_data.type,
            file_type=project_data.file_type,
            parent_id=project_data.parent_id,
            url=project_data.url,
        )

        self.db.add(new_project)
        await self.db.commit()
        await self.db.refresh(new_project)

        return new_project

    async def update_project(self, project_id: int, project_data: ProjectUpdateSchema) -> Optional[ProjectModel]:
        update_data = project_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return await self.get_project_by_id(project_id, depth=None)
        
        await self.db.execute(
            update(ProjectModel)
            .where(ProjectModel.id == project_id)
            .values(**update_data)
        )

        await self.db.commit()
        
        project = await self.get_project_by_id(project_id, depth=None)
        return project

    async def delete_project(self, project_id: int) -> bool:
        result = await self.db.execute(
            delete(ProjectModel).where(ProjectModel.id == project_id)
        )

        await self.db.commit()

        return result.rowcount > 0

