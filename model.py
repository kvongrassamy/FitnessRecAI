# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2024)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_pydantic_code_schema__(
        cls,
        _source_type: Any,
        _handler: GetJsonSchemaHandler,
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.str_schema(),
                core_schema.is_instance_schema(ObjectId),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x:str(x) if isinstance(x, ObjectId) else x
            ),
        )
    
class SubTopic(BaseModel):
    name: str
    completed: bool = False

class Topic(BaseModel):
    name: str
    subtopics: List[SubTopic] = []
    completed: bool = False

class FitnessGuide(BaseModel):
    title: str
    description: str = ""
    topics: List[Topic]
    created_at: datetime = Field(default_factory=datetime.now)
    mongo_id: Optional[ObjectId] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

class Resource(BaseModel):
    name: str
    description: str
    asset: str = ""  # URL or file path
    resource_type: str  # video, article, code_example, etc.
    created_at: datetime = Field(default_factory=datetime.now)
    mongo_id: Optional[ObjectId] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }