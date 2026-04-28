from pydantic import BaseModel
from typing import List, Dict, Any

class KPIData(BaseModel):
    total: int
    activos: int
    cerrados: int
    con_retraso: int

class NameCount(BaseModel):
    name: str
    value: int

class TimelineCount(BaseModel):
    mes: str
    cantidad: int

class DashboardStatsResponse(BaseModel):
    kpis: KPIData
    por_departamento: List[NameCount]
    por_delito: List[NameCount]
    timeline: List[TimelineCount]
    por_perito: List[NameCount]
