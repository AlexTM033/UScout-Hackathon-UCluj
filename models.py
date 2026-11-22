from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class PositionEntry(BaseModel):
    code: str
    name: str
    minutes: int = 0
    totalMinutes: int = 0
    percentageOfPlaytime: float = 0.0

class TacticalProfile(BaseModel):
    primaryPosition: Optional[PositionEntry] = None
    secondaryPositions: List[PositionEntry] = []

class MetaData(BaseModel):
    totalPlayers: int
    currentPage: int
    totalPages: int

class PlayerResponse(BaseModel):
    wyId: int
    shortName: str
    firstName: str
    lastName: str
    birthDate: Optional[str]
    positionCode: Optional[str]
    minutesOnField: int
    performance_score: float
    market_value: Optional[int] = None
    photoUrl: Optional[str] = None
    club: Optional[str] = None
    foot: Optional[str] = None
    nationality: Optional[str] = None
    contractExpiration: Optional[str] = None
    systemFitPercentage: Optional[float] = None
    tacticalProfile: Optional[TacticalProfile] = None
    
    class Config:
        from_attributes = True

class PlayerDetailedResponse(PlayerResponse):
    normalized_stats: Dict[str, Any]

class PaginatedPlayerResponse(BaseModel):
    data: List[PlayerResponse]
    meta: MetaData

class IntegrationFactor(BaseModel):
    title: str
    status: str # "OPTIM" | "MEDIU" | "CRITIC"
    score: int
    description: str

class PersonalityReport(BaseModel):
    traits: List[str]
    summary: str

class AIDecisionMatrix(BaseModel):
    pros: List[str]
    cons: List[str]

class IntegrationReportResponse(BaseModel):
    riskPercentage: int
    factors: List[IntegrationFactor]
    personality: PersonalityReport
    aiDecisionMatrix: Optional[AIDecisionMatrix] = None

class TacticalPlayerInfo(BaseModel):
    id: int
    name: str
    positionDetails: str
    marketValue: str

class TacticalMetric(BaseModel):
    label: str
    playerScore: int
    targetScore: int
    difference: int

class TacticalEvaluation(BaseModel):
    positionMatched: str
    overallFitPercentage: int
    metrics: List[TacticalMetric]

class TacticalDNAResponse(BaseModel):
    player: TacticalPlayerInfo
    tacticalEvaluation: TacticalEvaluation
class RadarScores(BaseModel):
    Shooting: int
    Passing: int
    Dribbling: int
    Defending: int
    Physicality: int
    Mentality: int

class PlayerStatsResponse(BaseModel):
    goals: int
    assists: int
    cleanSheets: int
    yellowCards: int
    redCards: int
    radarScores: RadarScores
class AITwinPlayer(BaseModel):
    id: int
    name: str
    age: int
    position: str
    similarityScore: float
    explanation: str
    photoUrl: Optional[str] = None
    radarScores: Optional[dict] = None

class AITwinResponse(BaseModel):
    targetPlayerName: str
    twins: List[AITwinPlayer]
