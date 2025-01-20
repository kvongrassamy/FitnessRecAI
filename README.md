# FitnessRecAI
This project is to create an AI Agent to provide recommendations to weight lifter and information on to create quality workouts


- Set up a PyMongo Server/DB and replace the connection string in database.py.  You will need a .env file that will have your username and password

- Use the following JSON files to insert into you PyMong DB
    - Create a DB named fitnessguide and insert JSON:
    ```bash
        {"_id":{"$oid":"678bc7861aea6a0258b0737c"},"title":"Sub-Topic","description":"Please provide sub topics that would provide a roadmap for your workout.  You can ask you AI Partner for any recommendations","topics":[],"created_at":{"$date":{"$numberLong":"1737158400000"}},"mongo_id":{"$oid":"678bc7861aea6a0258b0737c"}}
    ```
    - Create a DB named resources and insert JSON:
      
    ```bash
        {"_id":{"$oid":"678bccc81aea6a0258b073c3"},"name":"ResourceTitle","description":"ResourceDesc","asset":"SomePath","resource_type":"VideoOfSomeSort","created_at":{"$date":{"$numberLong":"1737158400000"}}}
    ```

- activate the env with 
```bash 
./fitnessguideai/Scripts/activate 
```

- install requirements: 
```bash
pip install -r requirements
```

- In CMD/GitBash/PS run Parlant with: 
```bash
parlant-server -p 8501 --module "service"
```

- In CMD/GitBash/PS run Parlant with: 
```bash
streamlit run Home.py
```
