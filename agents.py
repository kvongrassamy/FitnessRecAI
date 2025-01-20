from parlant.client import (
   GuidelineContent,
   GuidelinePayload,
   ParlantClient,
   Payload,
)


client = ParlantClient(base_url="http://localhost:8501")
agent_home = client.agents.create(
            name="HomeAIAgent",
            description="Technical support specialist",
        )

client = ParlantClient(base_url="http://localhost:8501")
agent_guide = client.agents.create(
            name="FitnessGuideAIAgent",
            description="Provide recommendations on what your workouts should be at the users experience level",
        )

agent_resource_first = client.agents.create(
            name="ResourceAIAgent",
            description="Provide videos and documentation on fitness",
        )


evaluation = client.evaluations.create(
    agent_id=agent_resource_first.id,
    payloads=[
       Payload(
         kind="guideline",
         guideline=GuidelinePayload(
             content=GuidelineContent(
                condition="User wants to create a new resource",
                action="""Ensure the user provides the appropiate details like name, some sort of asset like a link or a book title and 
                the type of resource like book tutorial etc.
                """,
             ),
             operation="add",
             coherence_check=True,
             connection_proposition=True,
         )
       )
    ],
)

# Wait for the evaluation to complete and get the invoice
invoices = client.evaluations.retrieve(
    evaluation.id,
    wait_for_completion=60,  # Wait up to 60 seconds
).invoices

if all(invoice.approved for invoice in invoices):
    agent_resource = client.agents.create(
                name="ResourceAIAgent",
                description="Provide videos and documentation on fitness",
            )