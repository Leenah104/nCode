import streamlit as st
from dataclasses import dataclass

st.set_page_config(page_title="Task Scheduler", layout="centered")

# Styling
st.markdown("""
    <style>
        body, .stApp {
            background-color: #ffeded;
            color: black;
        }

        label, .stTextInput label, .stNumberInput label, .stSelectbox label {
            color: black !important;
            font-weight: 600;
        }

        input[type="text"],
        .stTextInput input,
        .stNumberInput input,
        .stSelectbox div {
            color: black !important;
            background-color: white !important;
            border-radius: 10px !important;
        }

        .stButton > button,
        .stForm button {
            background-color: #A2D5C6 !important;
            color: black !important;
            border: none;
            border-radius: 10px;
            padding: 0.5em 1em;
            font-weight: bold;
        }

        .stAlert[data-baseweb="notification"][data-kind="success"] {
            background-color: #B3EACD !important;
            color: black !important;
        }

        .stAlert[data-baseweb="notification"][data-kind="warning"] {
            background-color: #FFD1D1 !important;
            color: black !important;
        }

        .stAlert[data-baseweb="notification"][data-kind="info"] {
            background-color: #D0E8FF !important;
            color: black !important;
        }
        .remaining-time {
            font-size: 1.1em;
            font-weight: bold;
            padding: 8px;
            border-radius: 10px;
            background-color: #f0f0f0;
            margin: 10px 0;
        }
      
        .task-item {
            padding: 8px;
            margin: 5px 0;
            border-left: 4px solid #A2D5C6;
            background-color: #f9f9f9;
        }

        button[data-baseweb="button"] {
            background-color: #A2D5C6 !important;
            color: black !important;
            border: none !important;
            border-radius: 50% !important;
            width: 30px !important;
            height: 30px !important;
            margin: 0 5px !important;
        }
        
        button[data-baseweb="button"]:hover {
            background-color: #8EC4B4 !important;
            transform: scale(1.1) !important;
        }
        
      
        input[type="number"] {
            text-align: center !important;
            font-weight: bold !important;
        }
        
        
        .stNumberInput > label {
            font-size: 1.1em !important;
            color: #333 !important;
        }

    </style>
""", unsafe_allow_html=True)

@dataclass
class Task:
    name: str
    duration: int
    priority: int

class TaskSchedulerAI:
    def __init__(self, tasks, max_time):
        self.tasks = tasks
        self.max_time = max_time
    
    def evaluate(self, task):
      priority_weight = 10
      time_feasibility = min(1,self.max_time / task.duration) if task.duration > 0 else 0
      return (task.priority * priority_weight) * time_feasibility
      
    
    def schedule(self):
        scheduled = []
        remaining_time = self.max_time
        
        while remaining_time > 0 and self.tasks:
    # اختيار المهمة ذات الدرجة الأعلى
            best_task = min(self.tasks, key=lambda x: (x.priority, x.duration))
            
            if best_task.duration <= remaining_time:
                scheduled.append(best_task)
                remaining_time -= best_task.duration
                self.tasks.remove(best_task)
            else:
                break
        
        return scheduled, self.max_time - remaining_time
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

st.title("Smart Task Scheduler")
available_time = st.number_input("Available Time (minutes)", min_value=1, step=1, key='time_input')  #
st.write(f"Specified Available Time: {available_time} minutes") #

current_used = sum(t.duration for t in st.session_state.tasks)
remaining_time = max(0, available_time - current_used)
st.markdown(f"""<div class="remaining-time"> Remaining Time:
  <b>{remaining_time}</b> / {available_time} minutes </div>
""", unsafe_allow_html=True)


with st.form("task_form"):
    task_name = st.text_input("Task Name")
    task_duration = st.number_input("Duration (minutes)", min_value=1, step=1)
    task_priority = st.selectbox("Priority", [1, 2, 3], format_func=lambda x: f"{x} - {'High' if x == 1 else 'Medium' if x == 2 else 'Low'}")
    submitted = st.form_submit_button("Add Task")
    if submitted and task_name.strip():
        total_duration = sum(t.duration for t in st.session_state.tasks) + task_duration
        if total_duration <= available_time:
            st.session_state.tasks.append(Task(task_name, task_duration, task_priority))
            st.success("Task added successfully!")
            st.rerun()
        else:
            st.warning(f"Cannot add task! Total duration will exceed available time ({available_time} minutes)")

    remaining_time = available_time - sum(t.duration for t in st.session_state.tasks) 
    st.write(f"Remaining time: {remaining_time}/{available_time} minutes")
        
if st.button("Schedule Tasks"):
  if st.session_state.tasks:
    scheduler = TaskSchedulerAI(st.session_state.tasks.copy(), available_time)
    scheduled, total_used = scheduler.schedule()
    st.subheader("Scheduled Tasks:")
    for i, task in enumerate(scheduled[::-1], 1):
      st.write(f"{i}.{task.name} - {task.duration} min - Priority: {task.priority}")
    progress_ratio = total_used / available_time
    st.progress(progress_ratio)
    st.info(f"Total time used: {total_used} / {available_time} minutes ({progress_ratio:.0%})")
  else:
    st.warning("No tasks to schedule.")
         
if st.button("Clear All Tasks"):
    st.session_state.tasks.clear()
    st.success("All tasks cleared!")
