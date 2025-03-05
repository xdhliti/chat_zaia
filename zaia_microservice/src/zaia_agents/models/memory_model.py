from typing import TypedDict, List

class MemoryRecord(TypedDict):
    memory: str
    event: str

class MemoryAddResponse(TypedDict):
    results: List[MemoryRecord]