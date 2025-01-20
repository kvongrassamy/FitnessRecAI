import streamlit as st
from database import Database
from model import FitnessGuide, Topic, SubTopic
from datetime import datetime
from components.chat import init_chat, show_chat
from parlant.client import ParlantClient
from agents import agent_guide

# Initialize database
db = Database()

def init_session_state():
    """Initialize session state variables"""
    if "checkbox_states" not in st.session_state:
        st.session_state.checkbox_states = {}
    if "show_topic_creator" not in st.session_state:
        st.session_state.show_topic_creator = False
    if "show_subtopic_creator" not in st.session_state:
        st.session_state.show_subtopic_creator = None
    
    # Initialize chat with fitnessguide agent
    init_chat(agent_guide.id)

def get_all_fitnessguide():
    """Get all available fitnessguide"""
    return db.get_all_fitnessguide()

def save_progress(fitnessguide: FitnessGuide):
    """Save progress by updating the fitnessguide"""
    try:
        # Create a copy of the fitnessguide to avoid modifying the original
        fitnessguide_data = fitnessguide.model_dump()
        updated_fitnessguide = FitnessGuide.model_validate(fitnessguide_data)
        
        # Update subtopic completion status from session state
        for topic in updated_fitnessguide.topics:
            for subtopic in topic.subtopics:
                checkbox_key = f"checkbox_{subtopic.name}"
                if checkbox_key in st.session_state.checkbox_states:
                    subtopic.completed = st.session_state.checkbox_states[checkbox_key]
            # Update topic completion based on subtopics
            topic.completed = all(subtopic.completed for subtopic in topic.subtopics)
        
        # Save updated fitnessguide
        return db.update_fitnessguide(str(fitnessguide.mongo_id), updated_fitnessguide)
    except Exception as e:
        st.error(f"Error saving progress: {str(e)}")
        return False

def toggle_checkbox(key):
    """Toggle checkbox without triggering rerun"""
    st.session_state.checkbox_states[key] = not st.session_state.checkbox_states.get(key, False)

def create_topic_form(fitnessguide: FitnessGuide):
    """Show form to create a new topic"""
    with st.form(key="new_topic_form"):
        st.subheader("Create New Topic")
        name = st.text_input("Topic Name")
        
        if st.form_submit_button("Create Topic"):
            if name:
                # Create new topic
                new_topic = Topic(
                    name=name,
                    subtopics=[],
                    completed=False
                )
                fitnessguide.topics.append(new_topic)
                # Save fitnessguide
                if db.update_fitnessguide(str(fitnessguide.mongo_id), fitnessguide):
                    st.success("Topic created successfully!")
                    st.session_state.show_topic_creator = False
                    st.rerun()
                else:
                    st.error("Failed to create topic. Please try again.")
            else:
                st.error("Please fill in all fields.")

def create_subtopic_form(fitnessguide: FitnessGuide, parent_topic: Topic):
    """Show form to create a new subtopic"""
    with st.form(key=f"new_subtopic_form_{parent_topic.name}"):
        st.subheader(f"Create New Subtopic in {parent_topic.name}")
        name = st.text_input("Subtopic Name")
        
        if st.form_submit_button("Create Subtopic"):
            if name:
                # Create new subtopic
                new_subtopic = SubTopic(
                    name=name,
                    completed=False
                )
                
                # Find parent topic and add subtopic
                for topic in fitnessguide.topics:
                    if topic.name == parent_topic.name:
                        topic.subtopics.append(new_subtopic)
                        break
                #fitnessguide_id = db.create_fitnessguide(fitnessguide)
                # Save fitnessguide
                #if db.update_fitnessguide(str(fitnessguide.mongo_id), fitnessguide):
                if db.update_fitnessguide(str(fitnessguide.mongo_id), fitnessguide):
                    st.success("Subtopic created successfully!")
                    st.session_state.show_subtopic_creator = None
                    st.rerun()
                else:
                    st.error("Failed to create subtopic. Please try again.")
            else:
                st.error("Please fill in all fields.")

@st.fragment()
def display_topic(topic: Topic, fitnessguide: FitnessGuide):
    """Display a single topic and its subtopics"""
    # Display subtopics
    for subtopic in topic.subtopics:
        checkbox_key = f"checkbox_{subtopic.name}"
        
        # Initialize checkbox state if not exists
        if checkbox_key not in st.session_state.checkbox_states:
            st.session_state.checkbox_states[checkbox_key] = subtopic.completed

        st.checkbox(
            label=subtopic.name,
            value=st.session_state.checkbox_states[checkbox_key],
            key=checkbox_key,
            on_change=toggle_checkbox,
            args=(checkbox_key,),
        )

    if st.button("Add Subtopic", key=f"add_subtopic_{topic.name}", help="Add new subtopic"):
        st.session_state.show_subtopic_creator = topic.name

    if st.session_state.show_subtopic_creator == topic.name:
        create_subtopic_form(fitnessguide, topic)

def show_fitnessguide():
    st.title("Learning Fitness Guide and Goals")
    
    # Initialize session state
    init_session_state()
    
    fitnessguide = get_all_fitnessguide()
    
    if not fitnessguide:
        st.warning("No fitnessguide available. Please check your database connection.")
        return
    
    # If we have multiple fitnessguide, let user select one
    if len(fitnessguide) > 1:
        selected_fitnessguide = st.selectbox(
            "Select a fitness guide",
            fitnessguide,
            format_func=lambda x: x.title
        )
    else:
        selected_fitnessguide = fitnessguide[0]
    
    # Display fitnessguide details
    st.header(selected_fitnessguide.title)
    if selected_fitnessguide.description:
        st.write(selected_fitnessguide.description)
    
    # Display topics
    for topic in selected_fitnessguide.topics:
        with st.expander(topic.name, expanded=True):
            display_topic(topic, selected_fitnessguide)

    if st.button("Add Topic", key="add_topic", help="Add new topic"):
        st.session_state.show_topic_creator = True

    if st.button("Save Progress", type="primary"):
        if save_progress(selected_fitnessguide):
            st.success("Progress saved successfully!")
        else:
            st.error("Failed to save progress. Please try again.")
    
    # Show topic creator if requested
    if st.session_state.show_topic_creator:
        create_topic_form(selected_fitnessguide)
    
    # Show chat interface at the bottom
    show_chat()

if __name__ == "__main__":
    show_fitnessguide()