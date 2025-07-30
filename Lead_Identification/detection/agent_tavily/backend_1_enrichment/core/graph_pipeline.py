

import os
import json
from typing import List, Dict, Any, TypedDict, Optional
from dotenv import load_dotenv # Explicitly load .env here
import google.generativeai as genai
from tavily import TavilyClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END


# --- Configuration and API Key Validation ---
load_dotenv() # Load environment variables here


# --- Type Definitions for State ---
class KeyPersonnel(TypedDict):
    name: str
    title: str
    linkedin_profile: Optional[str]

class LeadProfile(TypedDict):
    name: str
    url_website: Optional[str]
    linkedin_company: Optional[str]
    description: Optional[str]
    summary: str
    reason_for_match: str
    key_personnel: List[KeyPersonnel]

class LeadGenerationState(TypedDict):
    service_name: str
    icp: Dict[str, Any]
    search_queries: List[str]
    research_results: List[Dict[str, Any]]
    potential_leads: List[LeadProfile]
    report: Dict[str, Any]
    company_name: Optional[str]
    question: Optional[str]
    coach_answer: Optional[str]

# --- Node Definitions ---

class LeadGenerationNodes:
    def __init__(self, llm, tavily_client):
        self.llm = llm
        self.tavily = tavily_client
        

    def generate_search_queries(self, state: LeadGenerationState) -> LeadGenerationState:
        """Generates strategic search queries based on the ICP's core criteria."""
        print("--- Node: generate_search_queries ---")
        icp = state['icp']
        
        industries = icp.get('industry', {})
        if isinstance(industries, dict):
            core_industries = industries.get('tier1_core_focus', [])
        else:
            core_industries = industries if isinstance(industries, list) else []

        geographies = icp.get('geography', [])
        
        if not core_industries or not geographies:
            print("Error: Could not extract core industries or geographies from ICP.")
            return {"search_queries": []}

        queries = [
            f"top {core_industries[0]} companies in {geographies[0]}",
            f"market report for {core_industries[0]} industry in Europe",
            f"'{geographies[0]}' {core_industries[0]} industry directory",
            f"leading {core_industries[0]} firms in '{geographies[0]}'"
        ]
        if len(core_industries) > 1:
            queries.append(f"list of {core_industries[1]} companies in {geographies[0]}")

        queries = [q.replace("'", "") for q in queries][:5]
        print(f"Generated queries: {queries}")
        return {"search_queries": queries}

    def perform_web_research(self, state: LeadGenerationState) -> LeadGenerationState:
        """Performs web research using the generated queries."""
        print("--- Node: perform_web_research ---")
        queries = state['search_queries']
        all_results = []
        for query in queries:
            try:
                response = self.tavily.search(query=query, search_depth="basic", max_results=5)
                all_results.extend(response['results'])
            except Exception as e:
                print(f"Tavily search error for '{query}': {e}")
        print(f"Found {len(all_results)} search results.")
        return {"research_results": all_results}

    def identify_potential_leads(self, state: LeadGenerationState) -> LeadGenerationState:
        """Identifies and summarizes potential lead companies from research results."""
        print("--- Node: identify_potential_leads ---")
        research_results = state['research_results']
        context = "\n\n".join([f"Source: {res['url']}\nContent: {res['content']}" for res in research_results])
        
        prompt = f"""
        Analyze the web research context below to extract potential companies matching our Ideal Customer Profile (ICP).
        For each company, provide a brief summary and explain why it matches the ICP.
        Do not include consulting firms, marketing agencies, or software vendors unless they are the target.

        ICP:
        {json.dumps(state['icp'], indent=2)}

        Web Research Context:
        ---
        {context}
        ---

        Return a JSON list of objects. Each object should follow this schema:
        {{
          "name": "Company Name",
          "url_website": "https://www.company.com",
          "linkedin_company": "https://www.linkedin.com/company/company-name",
          "summary": "A brief one-sentence summary of what the company does.",
          "description": "A more detailed description of the company, its products/services, and recent activities, based on the research context.",
          "reason_for_match": "A brief explanation of why this company fits our ICP (e.g., industry, recent news, size)."
        }}
        Example:
        [
          {{
            "name": "Global Tech Inc.",
            "url_website": "https://www.globaltech.com",
            "linkedin_company": "https://www.linkedin.com/company/global-tech-inc",
            "summary": "A leading provider of enterprise software solutions.",
            "description": "Global Tech Inc. specializes in AI-driven software for the manufacturing sector, recently launched a new predictive maintenance platform.",
            "reason_for_match": "Fits the 'Manufacturing & Automotive' industry and has a large employee count."
          }}
        ]
        """
        
        response = self.llm.invoke(prompt)
        try:
            content = response.content.strip()
            # Robustly extract JSON array from content
            json_start = content.find('[')
            json_end = content.rfind(']')
            if json_start != -1 and json_end != -1:
                json_string = content[json_start : json_end + 1]
            else:
                raise json.JSONDecodeError("Could not find valid JSON array in LLM response", content, 0)
            
            leads = json.loads(json_string)
            # Ensure all expected fields are present and initialize key_personnel
            for lead in leads:
                lead['url_website'] = lead.get('url_website', None)
                lead['linkedin_company'] = lead.get('linkedin_company', None)
                lead['description'] = lead.get('description', None)
                lead['key_personnel'] = []

            print(f"Identified {len(leads)} potential leads.")
            return {"potential_leads": leads}
        except json.JSONDecodeError:
            print(f"Error decoding potential leads: {response.content}")
            return {"potential_leads": []}

    def find_key_personnel(self, state: LeadGenerationState) -> LeadGenerationState:
        """For each lead, find key decision-makers based on the ICP."""
        print("--- Node: find_key_personnel ---")
        updated_leads = []
        decision_makers_titles = state['icp'].get('key_decision_makers', [])
        if not decision_makers_titles:
            print("Warning: No 'key_decision_makers' defined in ICP. Skipping personnel search.")
            return {"potential_leads": state['potential_leads']}

        for lead in state['potential_leads']:
            company_name = lead['name']
            print(f"Searching for personnel at: {company_name}")
            
            # Construct a targeted query for decision-makers
            titles_query = " OR ".join([f'"{title}"' for title in decision_makers_titles])
            query = f'linkedin {company_name} ({titles_query})'
            
            try:
                search_results = self.tavily.search(query=query, search_depth="basic", max_results=3)
                context = "\n".join([res['content'] for res in search_results['results']])

                prompt = f"""
                From the text below, extract the names and job titles of individuals who work at '{company_name}'.
                The target job titles are: {', '.join(decision_makers_titles)}.
                
                Context:
                ---
                {context}
                ---

                Return a JSON list of objects with "name", "title", and "linkedin_profile".
                Example: [{{"name": "Jane Doe", "title": "Chief Technology Officer", "linkedin_profile": "https://www.linkedin.com/in/janedoe"}}]
                """
                response = self.llm.invoke(prompt)
                content = response.content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                
                personnel = json.loads(content)
                # Ensure linkedin_profile is present for each personnel
                for p in personnel:
                    p['linkedin_profile'] = p.get('linkedin_profile', None)
                lead['key_personnel'] = personnel
                print(f"Found {len(personnel)} key personnel for {company_name}.")

            except Exception as e:
                print(f"Could not find personnel for {company_name}: {e}")
                lead['key_personnel'] = []
            
            updated_leads.append(lead)
            
        return {"potential_leads": updated_leads}

    def compile_report(self, state: LeadGenerationState) -> LeadGenerationState:
        """Compiles the final, enriched report."""
        print("--- Node: compile_report ---")
        report = {
            "service_name": state['service_name'],
            "icp_summary": {
                "industry": state['icp'].get('industry'),
                "geography": state['icp'].get('geography'),
                "key_decision_makers": state['icp'].get('key_decision_makers')
            },
            "potential_leads_found": len(state['potential_leads']),
            "leads": state['potential_leads'],
            "data_sources_used": [res['url'] for res in state.get('research_results', [])]
        }
        print("--- Report Compilation Complete ---")
        return {"report": report}

    def sales_coach_answer(self, state: LeadGenerationState) -> LeadGenerationState:
        """Generates a strategic answer for the salesperson based on the report and ICP."""
        print("--- Node: sales_coach_answer ---")
        report_context = state.get('report')
        service_name = state['service_name']
        icp_profile = state['icp']
        question = state['question']
        company_name = state['company_name']

        if not report_context or not icp_profile or not question or not company_name:
            print("Error: Missing context for sales coach answer.")
            return {"coach_answer": "Error: Missing context for sales coach answer."}

        combined_context = f"""
        ### CONTEXT 1: Our Strategic Go-to-Market Plan (Ideal Customer Profile) ###
        This is our strategy for the '{service_name}' service. It defines who we target and why.
        {json.dumps(icp_profile, indent=2)}

        ### CONTEXT 2: Specific Prospect Intelligence Report ###
        This is the detailed report we've generated for the prospect '{company_name}'.
        {json.dumps(report_context, indent=2)}
        """

        prompt = f"""
        You are an expert Sales Coach AI. Your role is to help a salesperson prepare for an engagement with a prospect.
        Use the two contexts provided below: our strategic plan (ICP) and the specific intelligence report on the prospect.
        Your answers must be practical, strategic, and directly help the salesperson achieve their goal.

        {combined_context}

        ---
        Based on all the information above, answer the following question from the salesperson.

        SALESPERSON'S QUESTION:
        "{question}"

        COACH'S ANSWER:
        """
        try:
            response = self.llm.invoke(prompt)
            print("--- Sales Coach Answer Generated ---")
            return {"coach_answer": response.content.strip()}
        except Exception as e:
            print(f"Error generating sales coach answer: {e}")
            return {"coach_answer": f"Error generating sales coach answer: {str(e)}"}


def create_lead_generation_graph():
    """Creates the LangGraph workflow for lead generation."""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    nodes = LeadGenerationNodes(llm, tavily_client)
    
    workflow = StateGraph(LeadGenerationState)
    
    workflow.add_node("generate_search_queries", nodes.generate_search_queries)
    workflow.add_node("perform_web_research", nodes.perform_web_research)
    workflow.add_node("identify_potential_leads", nodes.identify_potential_leads)
    workflow.add_node("find_key_personnel", nodes.find_key_personnel)
    workflow.add_node("compile_report", nodes.compile_report)
    
    workflow.set_entry_point("generate_search_queries")
    workflow.add_edge("generate_search_queries", "perform_web_research")
    workflow.add_edge("perform_web_research", "identify_potential_leads")
    workflow.add_edge("identify_potential_leads", "find_key_personnel")
    workflow.add_edge("find_key_personnel", "compile_report")
    workflow.add_edge("compile_report", END)
    
    return workflow.compile()

def create_sales_coach_graph():
    """Creates the LangGraph workflow for sales coaching."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    nodes = LeadGenerationNodes(llm, tavily_client)
    
    workflow = StateGraph(LeadGenerationState)
    
    workflow.add_node("sales_coach_answer", nodes.sales_coach_answer)
    
    workflow.set_entry_point("sales_coach_answer")
    workflow.add_edge("sales_coach_answer", END)
    
    return workflow.compile()


def run_graph(service_name: str):
    """
    Loads the correct ICP and runs the lead generation graph.
    """
    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        icp_path = os.path.join(dir_path, 'icp.json')
        with open(icp_path, "r", encoding="utf-8") as f:
            all_services = json.load(f)['services']
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return {"error": f"Could not load or parse icp.json: {e}"}

    selected_icp = next((s['ideal_customer_profile'] for s in all_services if s['service'] == service_name), None)
    
    if not selected_icp:
        return {"error": f"Service '{service_name}' not found in icp.json"}

    try:
        graph = create_lead_generation_graph()
        initial_state = {
            "service_name": service_name,
            "icp": selected_icp,
            "potential_leads": [] # Ensure it's initialized
        }
        
        final_state = graph.invoke(initial_state)
        
        return final_state.get("report", {"error": "Failed to generate report"})
    except Exception as e:
        # Catch any unexpected error during graph creation or invocation
        import traceback
        return {"error": f"An unexpected error occurred: {str(e)}", "traceback": traceback.format_exc()}

def run_sales_coach_graph(company_name: str, service_name: str, question: str):
    """
    Loads the correct ICP and runs the sales coach graph.
    """
    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        icp_path = os.path.join(dir_path, 'icp.json')
        with open(icp_path, "r", encoding="utf-8") as f:
            all_services = json.load(f)['services']
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return {"error": f"Could not load or parse icp.json: {e}"}

    selected_icp = next((s['ideal_customer_profile'] for s in all_services if s['service'] == service_name), None)
    
    if not selected_icp:
        return {"error": f"Service '{service_name}' not found in icp.json"}

    try:
        # First, generate the lead report using the existing graph
        lead_report = run_graph(service_name)
        if "error" in lead_report:
            return {"error": f"Failed to generate lead report for coaching: {lead_report['error']}"}

        graph = create_sales_coach_graph()
        initial_state = {
            "service_name": service_name,
            "icp": selected_icp,
            "company_name": company_name,
            "question": question,
            "report": lead_report # Pass the generated report to the sales coach graph
        }
        
        final_state = graph.invoke(initial_state)
        
        return final_state.get("coach_answer", {"error": "Failed to generate coach answer"})
    except Exception as e:
        import traceback
        return {"error": f"An unexpected error occurred during sales coaching: {str(e)}", "traceback": traceback.format_exc()}


if __name__ == '__main__':
    service_to_run = "Data & AI Consulting"
    final_report = run_graph(service_to_run)
    
    print("\n--- FINAL REPORT ---")
    print(json.dumps(final_report, indent=2))

