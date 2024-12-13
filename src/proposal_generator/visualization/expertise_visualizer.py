from typing import Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
import numpy as np
import json

class ExpertiseVisualizer:
    """Visualize agent expertise and relationships."""
    
    def generate_expertise_dashboard(self, expertise_map: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive expertise visualization dashboard."""
        try:
            dashboard = {
                'skill_radar': self._create_skill_radar(expertise_map),
                'domain_heatmap': self._create_domain_heatmap(expertise_map),
                'experience_timeline': self._create_experience_timeline(expertise_map),
                'expertise_network': self._create_expertise_network(expertise_map),
                'specialization_sunburst': self._create_specialization_sunburst(expertise_map)
            }
            
            # Convert numpy arrays to lists
            return self._convert_numpy_to_lists(dashboard)
            
        except Exception as e:
            return {
                'error': str(e),
                'data': None
            }
    
    def _convert_numpy_to_lists(self, obj: Any) -> Any:
        """Convert numpy arrays and numbers to Python native types."""
        if isinstance(obj, dict):
            return {key: self._convert_numpy_to_lists(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_to_lists(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.bool_)):
            return bool(obj)
        elif isinstance(obj, np.complex_):
            return {'real': obj.real, 'imag': obj.imag}
        return obj
    
    def _create_skill_radar(self, expertise_map: Dict[str, Any]) -> Dict[str, Any]:
        """Create radar chart of agent skills."""
        try:
            fig = go.Figure()
            
            for agent_id, data in expertise_map.items():
                skills = []
                scores = []
                
                for domain, domain_data in data['domains'].items():
                    skills.append(domain)
                    scores.append(domain_data['skill_level'])
                
                # Add agent trace
                fig.add_trace(go.Scatterpolar(
                    r=scores,
                    theta=skills,
                    fill='toself',
                    name=agent_id
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                showlegend=True,
                title="Agent Skill Radar"
            )
            
            return fig.to_dict()
        except Exception as e:
            return {'error': str(e)}
    
    def _create_domain_heatmap(self, expertise_map: Dict[str, Any]) -> Dict[str, Any]:
        """Create heatmap of domain expertise."""
        try:
            # Create lists for heatmap data
            agents = []
            domains = []
            skill_levels = []
            
            for agent_id, data in expertise_map.items():
                for domain, domain_data in data['domains'].items():
                    agents.append(agent_id)
                    domains.append(domain)
                    skill_levels.append(domain_data['skill_level'])
            
            # Create DataFrame
            df = pd.DataFrame({
                'Agent': agents,
                'Domain': domains,
                'Skill Level': skill_levels
            })
            
            # Pivot the data for heatmap
            heatmap_data = df.pivot(index='Agent', columns='Domain', values='Skill Level')
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values.tolist(),  # Convert numpy array to list
                x=list(heatmap_data.columns),    # Convert index to list
                y=list(heatmap_data.index),      # Convert index to list
                colorscale='Viridis',
                colorbar=dict(title='Skill Level')
            ))
            
            fig.update_layout(
                title="Domain Expertise Heatmap",
                xaxis_title="Domains",
                yaxis_title="Agents"
            )
            
            return fig.to_dict()
        except Exception as e:
            return {'error': str(e)}
    
    def _create_experience_timeline(self, expertise_map: Dict[str, Any]) -> Dict[str, Any]:
        """Create timeline of agent experience growth."""
        try:
            # Create lists for timeline data
            agents = []
            domains = []
            experiences = []
            success_rates = []
            
            for agent_id, data in expertise_map.items():
                for domain, domain_data in data['domains'].items():
                    agents.append(agent_id)
                    domains.append(domain)
                    experiences.append(domain_data['experience_count'])
                    success_rates.append(domain_data['success_rate'])
            
            # Create DataFrame
            df = pd.DataFrame({
                'Agent': agents,
                'Domain': domains,
                'Experience': experiences,
                'Success Rate': success_rates
            })
            
            fig = px.line(df, 
                         x='Experience',
                         y='Success Rate',
                         color='Agent',
                         facet_col='Domain',
                         title="Experience Growth Timeline")
            
            return fig.to_dict()
        except Exception as e:
            return {'error': str(e)}
    
    def _create_expertise_network(self, expertise_map: Dict[str, Any]) -> Dict[str, Any]:
        """Create network visualization of agent expertise relationships."""
        try:
            G = nx.Graph()
            
            # Add nodes for agents and domains
            for agent_id in expertise_map:
                G.add_node(agent_id, node_type='agent')
                
            for data in expertise_map.values():
                for domain in data['domains']:
                    G.add_node(domain, node_type='domain')
            
            # Add edges for expertise relationships
            for agent_id, data in expertise_map.items():
                for domain, domain_data in data['domains'].items():
                    G.add_edge(agent_id, domain, 
                              weight=domain_data['skill_level'])
            
            # Create layout
            pos = nx.spring_layout(G)
            
            # Create edge trace
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([float(x0), float(x1), None])  # Convert numpy float to Python float
                edge_y.extend([float(y0), float(y1), None])  # Convert numpy float to Python float
            
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
            
            # Create node trace
            node_x = []
            node_y = []
            node_text = []
            node_color = []
            
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(float(x))  # Convert numpy float to Python float
                node_y.append(float(y))  # Convert numpy float to Python float
                node_text.append(str(node))
                node_color.append(1 if G.nodes[node]['node_type'] == 'agent' else 0)
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                marker=dict(
                    showscale=True,
                    colorscale='YlGnBu',
                    size=10,
                    color=node_color
                )
            )
            
            # Create figure
            fig = go.Figure(data=[edge_trace, node_trace],
                          layout=go.Layout(
                              title="Expertise Network",
                              showlegend=False,
                              hovermode='closest',
                              margin=dict(b=20,l=5,r=5,t=40)
                          ))
            
            return fig.to_dict()
        except Exception as e:
            return {'error': str(e)}
    
    def _create_specialization_sunburst(self, expertise_map: Dict[str, Any]) -> Dict[str, Any]:
        """Create sunburst chart of agent specializations."""
        try:
            # Create lists for sunburst data
            agents = []
            domains = []
            specializations = []
            values = []
            
            for agent_id, data in expertise_map.items():
                for domain, domain_data in data['domains'].items():
                    for spec, spec_data in domain_data.get('specializations', {}).items():
                        agents.append(agent_id)
                        domains.append(domain)
                        specializations.append(spec)
                        values.append(spec_data.get('proficiency', 0))
            
            # Create DataFrame
            df = pd.DataFrame({
                'Agent': agents,
                'Domain': domains,
                'Specialization': specializations,
                'Proficiency': values
            })
            
            fig = px.sunburst(df,
                            path=['Agent', 'Domain', 'Specialization'],
                            values='Proficiency',
                            title="Agent Specializations")
            
            return fig.to_dict()
        except Exception as e:
            return {'error': str(e)}