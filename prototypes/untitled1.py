# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 11:03:41 2026

@author: benle
"""

import pandas as pd
import plotly.graph_objects as go
from dataclasses import dataclass
from typing import List, Dict

# --- Configuration: The "Departmental Calibration" ---
# Adjust these numbers to match your department's reality.
LOAD_FACTORS = {
    "weeks_in_term": 15,
    
    # 1. Administrative (The "Enrollment Tax")
    # Hours per student per semester (emails, DSARs, logistics)
    "admin_scaling": 0.01, # the extra hours per student, per week
    "admin_flat": 4, # the flat time it takes, simply to set up and admin any course. one time, not weekly
    "admin_1st_time": 4, # extra time in creating from scratch. again, setting up a course one time, not weekly
    
    # preparation stuff
    "prep_1st_time": 1, # the extra time it takes to create a new course
    "prep_per_hour": 0.5, # the time it takes to prepare the intellectual materials for a lab or lecture
    
    # 2. Lab Operations (The "Safety/Risk Tax")
    # Base hours per semester per section for safety oversight
    "lab_safety_base": 1, # time per section, per week
    # Hours per week per section for complex prep/waste (e.g., Organic vs. Comp Chem)
    "lab_prep_weekly": 0.5,       
    
    # 3. Personnel Management (The "Delegation Tax")
    # Hours per semester managing/training 1 TA
    "personnel_scaling": 0.1,  # the extra hours, per ta  
    "personnel_flat": 2, # the time it takes to admin with a TA/la, no matter way.  Meetings, etc. 
    
    # 4. Live Interactions (The "Time Tax")  handled entirely by course info
    
    # 5. Assessment (The "Grading Tax")
    # Base hours per student per semester
    "assessment_baseline": 0, # any extra time it takes to administrate an assessment.  Flat
}

@dataclass
class TeachingAssignment:
    name: str
    
    n_students: int
    n_tas: int
    n_las: int
    n_graders: int
    
    weekly_lecture_hours: float
    weekly_office_hours: float
    
    prof_lab_sections_per_week: int
    ta_only_lab_sections_per_week: int
    lab_hours_per_section_per_week: float
    lab_prep_scaling: float
    
    weekly_assessment_hours: int
    
    # Multipliers for specific course nature
    is_new_prep: bool = False
    grading_intensity: float = 1.0 # 0.5 for Scantron, 3.0 for Lab Reports
    lab_prep: bool = False # if there is setup and waste to manage
    
    def calculate_load(self) -> Dict[str, float]:
        """Calculates total hours per semester for each of the 6 categories."""
        
        # 1. Administrative.  Running the course.  Not including prep
        admin_flat = 0
        if self.is_new_prep:
            admin_flat += LOAD_FACTORS["admin_1st_time"]
            
        admin_weekly = LOAD_FACTORS["admin_flat"] + (self.n_students * LOAD_FACTORS["admin_scaling"])
       
        admin_load = admin_flat + admin_weekly*LOAD_FACTORS["weeks_in_term"]
        
        
        # Course prep
        prep_flat = 0
        if self.is_new_prep:
            prep_flat += LOAD_FACTORS["prep_1st_time"]
        
        prep_weekly = (self.weekly_lecture_hours + self.lab_hours_per_section_per_week) * LOAD_FACTORS["prep_per_hour"] 
        
        prep_load = prep_flat + prep_weekly*LOAD_FACTORS["weeks_in_term"]
        
        
        # 2. Lab Operations (Safety, Supply Chain, Waste)
        lab_flat = 0
        lab_weekly = (self.prof_lab_sections_per_week + self.ta_only_lab_sections_per_week) * (LOAD_FACTORS["lab_safety_base"])
        if self.lab_prep:
            lab_weekly += lab_weekly + (self.prof_lab_sections_per_week + self.ta_only_lab_sections_per_week) * (LOAD_FACTORS["lab_prep_weekly"])
        lab_load = lab_flat + lab_weekly*LOAD_FACTORS["weeks_in_term"]
        
        
        # 3. Personnel Management (Scales with N TAs)
        mgmt_flat = 0
        mgmt_weekly = LOAD_FACTORS["personnel_flat"] + (self.n_tas + self.n_las + self.n_graders) * LOAD_FACTORS["personnel_scaling"]
        
        mgmt_load = mgmt_flat + mgmt_weekly*LOAD_FACTORS["weeks_in_term"]
        
        # 4. Live Interactions (Fixed Schedule)
        live_weekly = self.weekly_lecture_hours + (self.prof_lab_sections_per_week*self.lab_hours_per_section_per_week) + self.weekly_office_hours
        live_load = live_weekly*LOAD_FACTORS["weeks_in_term"]
        
        # 6. Assessment (Grading)
        assessment_weekly = self.weekly_assessment_hours
        
        assessment_load = assessment_weekly*LOAD_FACTORS["weeks_in_term"]

        return {
            "Course": self.name,
            "Administrative": round(admin_load, 1),
            "Preparation": round(prep_load, 1),
            "Lab Operations": round(lab_load, 1),
            "Management": round(mgmt_load, 1),
            "Live Interaction": round(live_load, 1),
            "Assessment": round(assessment_load, 1),
            "Total Load": round(admin_load + lab_load + mgmt_load + live_load + prep_load + assessment_load, 1)
        }

def visualize_load(assignments: List[TeachingAssignment]):
    """Generates a stacked bar chart comparing the assignments."""
    
    # Calculate data
    data = [a.calculate_load() for a in assignments]
    df = pd.DataFrame(data)
    
    # Categories to stack
    categories = ['Administrative', 'Lab Operations', 'Management', 'Live Interaction', 'Preparation', 'Assessment']
    
    fig = go.Figure()

    for category in categories:
        fig.add_trace(go.Bar(
            name=category,
            x=df['Course'],
            y=df[category],
            text=df[category],
            textposition='auto'
        ))

    fig.update_layout(
        title='Teaching Load Composition Analysis',
        xaxis_title='Course Assignment',
        yaxis_title='Estimated Workload Hours (Semester)',
        barmode='stack',
        template='plotly_white',
        legend_title="Workload Bucket"
    )
    
    # Calculate average total for a reference line
    fig.add_hline(y=15*40, line_dash="dash", line_color="gray", annotation_text="40 hour week")

    fig.show("browser")
    
    # Print the raw table for verification
    print(df.to_string(index=False))

# --- MAIN: Comparison Example ---

if __name__ == "__main__":
    
    # Assignment 1: The "Mega-Lecture" (Gen Chem)
    # High student count, high management, low lab responsibility.
    gen_chem = TeachingAssignment(
        name= "CHEM 110H",
        
        n_students= 50,
        n_tas= 1,
        n_las= 4,
        n_graders= 1, 
        
        weekly_lecture_hours= 4.5,
        weekly_office_hours= 3,
        
        prof_lab_sections_per_week=  0,
        ta_only_lab_sections_per_week= 0,
        lab_hours_per_section_per_week= 0,
        lab_prep_scaling= 0,
        
        weekly_assessment_hours = 2,
        
    )

    # Assignment 2: The "Lab Director" (Organic Lab)
    # Low student count, High lab hours, High safety risk, High grading depth.
    # Note: 4 sections of 4 hours = 16 contact hours.
    organic_lab = TeachingAssignment(
        name= "CHEM 110",
        
        n_students= 380,
        n_tas= 4,
        n_las= 4,
        n_graders= 0,
        
        weekly_lecture_hours= 3,
        weekly_office_hours= 1,
        
        prof_lab_sections_per_week= 0,
        ta_only_lab_sections_per_week= 0,
        lab_hours_per_section_per_week= 0,
        lab_prep_scaling= 0,
        
        weekly_assessment_hours = 1,
    )

    # Run the comparison
    visualize_load([gen_chem, organic_lab])