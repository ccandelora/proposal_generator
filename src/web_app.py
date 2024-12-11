import streamlit as st
import json
from proposal_generator import ProposalGenerator
import os
import tempfile
import traceback

st.set_page_config(page_title="AI Proposal Generator", layout="wide")

st.title("AI Proposal Generator")

# Initialize session state
if 'proposal_content' not in st.session_state:
    st.session_state.proposal_content = None
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = None
if 'pdf_generated' not in st.session_state:
    st.session_state.pdf_generated = False
if 'mockups' not in st.session_state:
    st.session_state.mockups = None

# Sidebar for template selection and analysis options
st.sidebar.title("Settings")
template_name = st.sidebar.selectbox(
    "Select Template",
    ["default", "software_development", "consulting", "marketing"],
    index=0
)

# Analysis Options in Sidebar
st.sidebar.header("Analysis Options")
website_analysis = st.sidebar.checkbox("Include Website Analysis", value=True)
competitor_analysis = st.sidebar.checkbox("Include Competitor Analysis", value=True)
seo_analysis = st.sidebar.checkbox("Include SEO Analysis", value=True)
performance_analysis = st.sidebar.checkbox("Include Performance Analysis", value=True)
design_mockups = st.sidebar.checkbox("Generate Design Mockups", value=True)
sentiment_analysis = st.sidebar.checkbox("Include Social Media Sentiment", value=True)

# Main form
st.header("Project Details")

with st.form("proposal_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        project_type = st.text_input("Project Type")
        client_name = st.text_input("Client Name")
        client_website = st.text_input("Client Website URL")
        timeline = st.text_input("Timeline")
        location = st.text_input("Business Location")
    
    with col2:
        industry = st.text_input("Industry")
        budget_range = st.text_input("Budget Range")
        target_audience = st.text_input("Target Audience")
        company_size = st.selectbox("Company Size", ["1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"])
    
    business_goals = st.text_area("Business Goals and Objectives")
    description = st.text_area("Project Description")
    features = st.text_area("Features (one per line)")
    
    # Competitor Analysis Section
    if competitor_analysis:
        st.subheader("Competitor Analysis")
        known_competitors = st.text_area("Known Competitor Websites (one per line)")
        market_positioning = st.selectbox("Current Market Position", ["Market Leader", "Strong Competitor", "Established Player", "Emerging Player"])
        unique_selling_points = st.text_area("Unique Selling Points (one per line)")
    
    submitted = st.form_submit_button("Generate Proposal")

if submitted:
    if not all([project_type, description, timeline, budget_range]):
        st.error("Please fill in all required fields.")
    else:
        with st.spinner("Generating proposal... This may take a few minutes."):
            try:
                # Prepare client brief
                client_brief = {
                    "client_name": client_name,
                    "project_type": project_type,
                    "industry": industry,
                    "description": description,
                    "features": [f.strip() for f in features.split('\n') if f.strip()],
                    "timeline": timeline,
                    "budget_range": budget_range,
                    "target_audience": target_audience,
                    "client_website": client_website,
                    "location": location,
                    "company_size": company_size,
                    "business_goals": [g.strip() for g in business_goals.split('\n') if g.strip()],
                    "market_position": market_positioning if competitor_analysis else None,
                    "unique_selling_points": [u.strip() for u in unique_selling_points.split('\n') if u.strip()] if competitor_analysis else [],
                    "competitors": [c.strip() for c in known_competitors.split('\n') if c.strip()] if competitor_analysis else [],
                    "analysis_options": {
                        "website_analysis": website_analysis,
                        "competitor_analysis": competitor_analysis,
                        "seo_analysis": seo_analysis,
                        "performance_analysis": performance_analysis,
                        "design_mockups": design_mockups,
                        "sentiment_analysis": sentiment_analysis
                    }
                }
                
                # Generate proposal
                generator = ProposalGenerator()
                try:
                    proposal_content = generator.create_proposal(client_brief)
                    
                    # Store proposal content
                    st.session_state.proposal_content = proposal_content
                    
                    # Generate PDF
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        try:
                            st.session_state.pdf_path = generator.generate_pdf(
                                proposal_content, 
                                tmp_file.name
                            )
                            st.session_state.pdf_generated = True
                        except Exception as e:
                            st.error(f"Error generating PDF: {str(e)}")
                            traceback.print_exc()
                    
                    # Show success message
                    st.success("Proposal generated successfully!")
                    
                except Exception as e:
                    st.error(f"Error generating proposal: {str(e)}")
                    traceback.print_exc()
            except Exception as e:
                st.error(f"An error occurred while generating the proposal: {str(e)}")
                traceback.print_exc()

# Display mockups if available
if st.session_state.mockups:
    st.header("Design Mockups")
    mockup_cols = st.columns(2)
    
    # Handle different mockup return formats
    if isinstance(st.session_state.mockups, dict):
        mockups_list = []
        for page_name, mockup_data in st.session_state.mockups.items():
            if isinstance(mockup_data, str):
                # If mockup_data is a direct path
                mockups_list.append((page_name, mockup_data))
            elif isinstance(mockup_data, dict) and 'path' in mockup_data:
                # If mockup_data is a dictionary containing path
                mockups_list.append((page_name, mockup_data['path']))
    else:
        # If mockups is a list or other format
        mockups_list = []
        if isinstance(st.session_state.mockups, list):
            for mockup in st.session_state.mockups:
                if isinstance(mockup, dict):
                    name = mockup.get('name', 'Mockup')
                    path = mockup.get('path', '')
                    if path:
                        mockups_list.append((name, path))
    
    # Display mockups
    for i, (page_name, mockup_path) in enumerate(mockups_list):
        if isinstance(mockup_path, str) and os.path.exists(mockup_path):
            with mockup_cols[i % 2]:
                st.image(mockup_path, caption=page_name)

# Display download button and preview outside the form
if st.session_state.proposal_content is not None:
    if st.session_state.pdf_generated and st.session_state.pdf_path:
        try:
            with open(st.session_state.pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="Download Proposal PDF",
                    data=pdf_file,
                    file_name="proposal.pdf",
                    mime="application/pdf"
                )
            # Clean up temporary file after download button is created
            os.unlink(st.session_state.pdf_path)
        except Exception as e:
            st.error(f"Error with PDF download: {str(e)}")
            traceback.print_exc()
    
    # Display preview
    st.header("Proposal Preview")
    st.markdown(str(st.session_state.proposal_content)) 