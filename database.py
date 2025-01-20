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

from pymongo import MongoClient
from typing import Optional, List
import os
from dotenv import load_dotenv
from model import FitnessGuide, Resource
from bson import ObjectId
from pymongo.operations import SearchIndexModel
from sentence_transformers import SentenceTransformer

load_dotenv()

# MongoDB connection string
PWD = os.getenv("MONGO_PWD")
USER = os.getenv("MONGO_USER")
#MONGO_URI = f"mongodb+srv://{USER}:{PWD}@database.0o8ty.mongodb.net/?retryWrites=true&w=majority&appName=database"
MONGO_URI = f"mongodb+srv://{USER}:{PWD}@cluster0.jajjk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Initialize the model with specific configuration
model = SentenceTransformer("BAAI/bge-large-en-v1.5", trust_remote_code=True)

def get_embedding(data):
   """Generates vector embeddings for the given data."""

   embedding = model.encode(data)
   return embedding.tolist()


class Database:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client.fitnessguide
       
    def create_fitnessguide(self, fitnessguide: FitnessGuide) -> str:
        """Create a new fitnessguide"""

        data = fitnessguide.model_dump(exclude={"_id"})
        result = self.db.fitnessguide.insert_one(data)
        return str(result.inserted_id)
    
    def update_fitnessguide(self, fitnessguide_id: str, fitnessguide: FitnessGuide) -> bool:
        """Update an existing fitnessguide"""
        print(fitnessguide)
        print(fitnessguide_id)
        data = fitnessguide.model_dump(exclude={"_id"})
        print(data)
        result = self.db.fitnessguide.update_one(
            {'mongo_id': ObjectId(fitnessguide_id)},
            {'$set': data}
        )
        return result.modified_count > 0
    
    def get_fitnessguide(self, fitnessguide_id: str) -> Optional[FitnessGuide]:
        """Get a fitnessguide by ID"""
        data = self.db.fitnessguide.find_one({'mongo_id': ObjectId(fitnessguide_id)})
        if data:
            data['mongo_id'] = data.pop('_id')
            return FitnessGuide.model_validate(data)
        return None
    
    def get_fitnessguide_by_title(self, title: str) -> Optional[FitnessGuide]:
        """Get a fitnessguide by title"""
        data = self.db.fitnessguide.find_one({'title': title})
        if data:
            data['mongo_id'] = data.pop('_id')
            return FitnessGuide.model_validate(data)
        return None
    
    def get_all_fitnessguide(self) -> List[FitnessGuide]:
        """Get all fitnessguide"""
        data = list(self.db.fitnessguide.find())
        fitnessguide = []
        for item in data:
            item['mongo_id'] = item.pop('_id')
            #item['_id'] = item.pop('_id')
            fitnessguide.append(FitnessGuide.model_validate(item))
        return fitnessguide

    def create_resource(self, resource: Resource) -> str:
        """Create a new resource"""
        data = resource.model_dump(exclude={"mongo_id"})
        embedding = get_embedding(resource.description + resource.name)
        data["embedding"] = embedding
        result = self.db.resources.insert_one(data)
        return str(result.inserted_id)
    
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get a resource by ID"""
        data = self.db.resources.find_one({'_id': ObjectId(resource_id)})
        if data:
            data['mongo_id'] = data.pop('_id')
            return Resource.model_validate(data)
        return None
    
    def get_resource_by_slug(self, slug: str) -> Optional[Resource]:
        """Get a resource by slug"""
        data = self.db.resources.find_one({'slug': slug})
        if data:
            data['mongo_id'] = data.pop('_id')
            return Resource.model_validate(data)
        return None

    def get_all_resources(self) -> List[Resource]:
        """Get all resources"""
        data = list(self.db.resources.find())
        resources = []
        for item in data:
            item['_id'] = item.pop('_id')
            resources.append(Resource.model_validate(item))
        return resources

    def search_resources(self, query: str, limit: int = 2) -> list[Resource]:
        """Search resources using vector similarity
        
        Args:
            query: The search query text
            limit: Maximum number of results to return (default 5)
            
        Returns:
            List of Resource objects sorted by relevance
        """
        query_embedding = get_embedding(query)
        
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "queryVector": query_embedding,
                    "path": "embedding",
                    "numCandidates": limit * 10,  # Internal limit for pre-filtering
                    "limit": limit
                }
            },
            {
                "$project": {
                    "name": 1,
                    "description": 1,
                    "asset": 1,
                    "resource_type": 1,
                    "created_at": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        results = list(self.db.resources.aggregate(pipeline))
        resources = []
        
        for item in results:
            # Convert ObjectId to string for mongo_id
            item['mongo_id'] = str(item.pop('_id'))
            # Remove score from the item before creating Resource object
            score = item.pop('score', 0)
            resources.append(Resource.model_validate(item))
            
        return resources

    def create_index(self):
        collection = self.db.resources
        
        # List and drop all search indexes
        try:
            indexes = list(collection.list_search_indexes())
            for index in indexes:

                index_name = index.get("name")
                if index_name:
                    print(f"Dropping index: {index_name}")
                    collection.drop_index(index_name)
            print("Dropped all existing search indexes")
        except Exception as e:
            print(f"Error handling existing indexes: {e}")
            
        # Create your index model, then create the search index
        search_index_model = SearchIndexModel(
            definition={
                "mappings": {
                    "dynamic": True,
                    "fields": {
                        "embedding": {
                            "type": "knnVector",
                            "dimensions": 1024,
                            "similarity": "cosine"
                        }
                    }
                }
            },
            name="vector_index"
        )
        
        # Wait a bit before creating new index
        import time
        time.sleep(2)
        
        result = collection.create_search_index(model=search_index_model)
        print("New search index named " + result + " is building.")
        
        # Wait for initial sync to complete
        print("Polling to check if the index is ready. This may take up to a minute.")
        predicate = lambda index: index.get("queryable") is True
        while True:
            indices = list(collection.list_search_indexes(name="vector_index"))
            if len(indices) and predicate(indices[0]):
                break
            time.sleep(1)  # Add small delay between checks

        print(result + " is ready for querying.")

    def update_all_embeddings(self):
        """Update embeddings for all existing resources"""
        print("Updating embeddings for all resources...")
        resources = self.get_all_resources()
        for resource in resources:
            # Generate new embedding
            embedding = get_embedding(resource.description + resource.name)
            # Update in database
            self.db.resources.update_one(
                {"_id": ObjectId(resource.mongo_id)},
                {"$set": {"embedding": embedding}}
            )
            print(f"Updated embedding for resource: {resource.name}")

if __name__ == "__main__":
    db = Database()
    results = db.search_resources("python")
    print("\nSearch Results:")
    for resource in results:
        print(f"- {resource.name}: {resource.description}")