"""
构建 ORM 对象模型映射底层物理表
作者：Hackerdallas
"""
from sqlalchemy import Column, Integer, String, Float, JSON
from database import Base

class POIBase(Base):
    __tablename__ = "poi_base"

    poi_id = Column(Integer, primary_key=True, autoincrement=True)
    poi_name = Column(String(255), nullable=False)
    category_name = Column(String(100), nullable=False, index=True)
    lng = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    district = Column(String(50))

class FPIPattern(Base):
    __tablename__ = "fpi_patterns"

    pattern_id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_name = Column(String(255), nullable=False, unique=True)
    pattern_display_name = Column(String(500))
    fpi_score = Column(Float, nullable=False, index=True)
    pattern_order = Column(Integer, nullable=False)
    instance_count = Column(Integer, default=0)

class PatternInstance(Base):
    __tablename__ = "pattern_instances"

    instance_id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_id = Column(Integer, nullable=False, index=True)
    poi_id_list = Column(JSON, nullable=False)
    
class CategoryMapping(Base):
    __tablename__ = "category_mapping"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(100), nullable=False, unique=True)
    category_code = Column(String(1), nullable=False, unique=True)
    category_order = Column(Integer, nullable=False)
    description = Column(String(500))
    poi_count = Column(Integer, default=0)

class DistrictStatistics(Base):
    __tablename__ = "district_statistics"

    stat_id = Column(Integer, primary_key=True, autoincrement=True)
    district = Column(String(50), nullable=False, index=True)
    category_name = Column(String(100), nullable=False)
    poi_count = Column(Integer, default=0)
    pattern_count = Column(Integer, default=0)
