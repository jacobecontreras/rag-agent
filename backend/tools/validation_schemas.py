import logging
from pydantic import BaseModel, Field
from typing import Optional, List, Union, Dict, Any

logger = logging.getLogger(__name__)


class ReportListSchema(BaseModel):
    """Schema for viewReportList - accepts no parameters"""
    pass


class ArtifactListSchema(BaseModel):
    """Schema for viewArtifactList"""
    job_name: str = Field(..., min_length=1)
    model_config = {"extra": "forbid"}


class ArtifactDataSchema(BaseModel):
    """Schema for viewArtifactData"""
    job_name: str = Field(..., min_length=1)
    artifact_type_id: Union[int, List[int]] = Field(...)
    limit: int = Field(default=100, gt=0)
    offset: int = Field(default=0, ge=0)
    model_config = {"extra": "forbid"}


class GrepSearchSchema(BaseModel):
    """Schema for grepSearch"""
    pattern: str = Field(..., min_length=1)
    job_name: str = Field(..., min_length=1)
    artifact_type_id: Optional[Union[int, List[int]]] = Field(default=None)
    limit: int = Field(default=50, gt=0)
    case_sensitive: bool = Field(default=False)
    model_config = {"extra": "forbid"}


class SemanticSearchSchema(BaseModel):
    """Schema for semanticSearch"""
    query: str = Field(..., min_length=1)
    job_name: Optional[str] = Field(default=None)
    n_results: int = Field(default=10, gt=0)
    model_config = {"extra": "forbid"}


# Simple tool schema mapping
TOOL_SCHEMAS = {
    "viewReportList": ReportListSchema,
    "viewArtifactList": ArtifactListSchema,
    "viewArtifactData": ArtifactDataSchema,
    "grepSearch": GrepSearchSchema,
    "semanticSearch": SemanticSearchSchema,
}