import ifcopenshell
import ifcopenshell.api
import ifcopenshell.guid
import ifcopenshell.util.element
import json
from SPARQLWrapper import SPARQLWrapper, JSON
from urllib.error import URLError

def run_sparql_query(building_element_guid):
    """
    Queries the ontology for all data related to a specific building element GUID.
    """
    sparql = SPARQLWrapper("http://localhost:3030/bimontoDB/sparql")
    
    # This query has been updated to match your new ontology schema.
    query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX bimonto: <http://w3id.org/IproK/00/BIMOnto#>
        PREFIX iprok: <http://w3id.org/IproK#>

        SELECT *
        WHERE {{
          ?building_element bimonto:GlobalId "{building_element_guid}" ;
                            bimonto:AssignToProcess ?task .
          
          ?task iprok:Name ?TaskName .
          
          OPTIONAL {{
            ?task iprok:hasTaskTime ?task_time .
            ?task_time iprok:ScheduleStart ?ScheduleStart ;
                       iprok:ScheduleFinish ?ScheduleFinish ;
                       iprok:ScheduleDuration ?ScheduleDuration ;
                       iprok:ActualStart ?ActualStart ;
                       iprok:ActualFinish ?ActualFinish ;
                       iprok:ActualDuration ?ActualDuration .
          }}
          
          OPTIONAL {{
            ?task iprok:requiresResource ?resource .
            ?resource rdf:type ?ResourceType ;
                      iprok:BudgetedUnits ?BudgetedUnits ;
                      iprok:ActualUnits ?ActualUnits .
          }}
          
          OPTIONAL {{
            ?task iprok:hasCostItem ?cost_item .
            ?cost_item iprok:hasCostType ?CostType ;
                       iprok:ActualCost ?ActualCost ;
                       iprok:BudgetedCost ?BudgetedCost .
          }}
        }}
    """
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    try:
        print("Querying SPARQL endpoint...")
        results = sparql.query().convert()
        print("Query successful.")
        return results["results"]["bindings"]
    except URLError as e:
        print(f"Error connecting to SPARQL endpoint: {e}")
    except Exception as e:
        print(f"An error occurred during SPARQL query: {e}")
    return None

def process_sparql_results(bindings):
    """
    Transforms the flat list of SPARQL results into a structured, nested dictionary
    based on the new ontology schema.
    """
    if not bindings:
        return {}
        
    tasks = {}
    for row in bindings:
        task_name = row.get("TaskName", {}).get("value")
        if not task_name:
            continue

        # Initialize the task entry if it's the first time we see it
        if task_name not in tasks:
            tasks[task_name] = {
                "Time": {
                    "ScheduleStart": row.get("ScheduleStart", {}).get("value"),
                    "ScheduleFinish": row.get("ScheduleFinish", {}).get("value"),
                    "ScheduleDuration": row.get("ScheduleDuration", {}).get("value"),
                    "ActualStart": row.get("ActualStart", {}).get("value"),
                    "ActualFinish": row.get("ActualFinish", {}).get("value"),
                    "ActualDuration": row.get("ActualDuration", {}).get("value")
                },
                "Resources": {}, # Use dicts to avoid duplicates
                "Costs": {}
            }

        # Add resource data if it exists in this row
        resource_uri = row.get("resource", {}).get("value")
        resource_type_uri = row.get("ResourceType", {}).get("value", "")
        if resource_uri and resource_uri not in tasks[task_name]["Resources"] and "NamedIndividual" not in resource_type_uri:
            resource_name = resource_type_uri.split('#')[-1]
            tasks[task_name]["Resources"][resource_uri] = {
                "Name": resource_name,
                "Type": f"Ifc{resource_name}Resource", # e.g. IfcConcreteResource - assuming a mapping
                "BudgetedUnits": float(row.get("BudgetedUnits", {}).get("value", 0)),
                "ActualUnits": float(row.get("ActualUnits", {}).get("value", 0))
            }

        # Add cost data if it exists in this row
        cost_item_uri = row.get("cost_item", {}).get("value")
        cost_type_uri = row.get("CostType", {}).get("value", "")
        if cost_item_uri and cost_item_uri not in tasks[task_name]["Costs"]:
            cost_type_name = cost_type_uri.split('#')[-1]
            tasks[task_name]["Costs"][cost_item_uri] = {
                "Name": f"{cost_type_name} Cost", # e.g. "Labor Cost"
                "BudgetedCost": float(row.get("BudgetedCost", {}).get("value", 0)),
                "ActualCost": float(row.get("ActualCost", {}).get("value", 0))
            }
            
    # Convert the inner resource and cost dicts to lists
    for task_name, task_data in tasks.items():
        task_data["Resources"] = list(task_data["Resources"].values())
        task_data["Costs"] = list(task_data["Costs"].values())

    print("Successfully processed SPARQL results into a structured format.")
    return tasks


def create_5d_model_from_ontology(building_element_guid):
    """
    Main function to drive the entire process from query to IFC creation,
    updated for the new ontology schema.
    """
    # --- 1. Get Data from Ontology ---
    sparql_bindings = run_sparql_query(building_element_guid)
    if not sparql_bindings:
        print("Could not retrieve data from ontology. Aborting.")
        return
        
    task_data = process_sparql_results(sparql_bindings)

    # --- 2. Load IFC Template and Target Element ---
    input_ifc_path = "../Models/Duplex_House_Modified.ifc"
    output_ifc_path = "../Models/Duplex_House_5D_From_Ontology.ifc"
    
    try:
        ifc_file = ifcopenshell.open(input_ifc_path)
        owner_history = ifc_file.by_type("IfcOwnerHistory")[0]
        building_element = ifc_file.by_guid(building_element_guid)
    except Exception as e:
        print(f"Error loading file or finding element: {e}")
        return

    print(f"\nFound target element in IFC: {building_element.Name}")

    # --- 3. Create IFC Entities from Processed Data ---
    created_tasks = {}
    for task_name, data_for_task in task_data.items():
        # Create Task
        task = ifc_file.create_entity("IfcTask", GlobalId=ifcopenshell.guid.new(), Name=task_name)
        created_tasks[task_name] = task
        print(f"Created IfcTask: '{task_name}'")

        # Create and Assign TaskTime
        time_data = data_for_task.get("Time", {})
        task_time = ifc_file.create_entity("IfcTaskTime", **time_data)
        task.TaskTime = task_time

        # Create, Add Psets to, and Assign Resources
        resources_for_task = data_for_task.get("Resources", [])
        created_resources = []
        for res_info in resources_for_task:
            # A simple mapping from ontology type to IFC resource type
            ifc_resource_type = "IfcConstructionMaterialResource" # Default
            if "Labor" in res_info["Type"] or "Carpenter" in res_info["Type"]:
                ifc_resource_type = "IfcLaborResource"
            elif "Equipment" in res_info["Type"] or "Crane" in res_info["Type"]:
                ifc_resource_type = "IfcConstructionEquipmentResource"

            resource = ifc_file.create_entity(ifc_resource_type, GlobalId=ifcopenshell.guid.new(), Name=res_info["Name"])
            pset = ifcopenshell.api.run("pset.add_pset", ifc_file, product=resource, name="Pset_ResourceQuantities")
            ifcopenshell.api.run("pset.edit_pset", ifc_file, pset=pset, properties={"BudgetedUnits": res_info["BudgetedUnits"], "ActualUnits": res_info["ActualUnits"]})
            created_resources.append(resource)
        ifc_file.create_entity("IfcRelAssignsToProcess", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner_history, RelatedObjects=created_resources, RelatingProcess=task)

        # Create and Assign Cost Items
        costs_for_task = data_for_task.get("Costs", [])
        created_cost_items = []
        for cost_info in costs_for_task:
            # Create a CostItem for each cost type (e.g., Labor Cost)
            cost_item = ifc_file.create_entity("IfcCostItem", GlobalId=ifcopenshell.guid.new(), Name=cost_info["Name"])
            
            # Create two CostValues (Budgeted and Actual) and assign them to the CostItem
            budgeted_monetary_value = ifc_file.create_entity("IfcMonetaryMeasure", cost_info["BudgetedCost"])
            budgeted_cost_value = ifc_file.create_entity("IfcCostValue", Name="Budgeted", AppliedValue=budgeted_monetary_value)
            
            actual_monetary_value = ifc_file.create_entity("IfcMonetaryMeasure", cost_info["ActualCost"])
            actual_cost_value = ifc_file.create_entity("IfcCostValue", Name="Actual", AppliedValue=actual_monetary_value)
            
            cost_item.CostValues = [budgeted_cost_value, actual_cost_value]
            created_cost_items.append(cost_item)
            
        ifc_file.create_entity("IfcRelAssignsToControl", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner_history, RelatedObjects=created_cost_items, RelatingControl=task)
        
        # Assign Task to Building Element
        ifc_file.create_entity("IfcRelAssignsToProduct", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner_history, RelatedObjects=[task], RelatingProduct=building_element)

    # --- 4. (Optional) Create Sequences if order is known ---
    if "Slab and Beam Formwork" in created_tasks and "Slab and Beam Steel Reinforcement" in created_tasks:
        ifc_file.create_entity("IfcRelSequence", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner_history, RelatingProcess=created_tasks["Slab and Beam Formwork"], RelatedProcess=created_tasks["Slab and Beam Steel Reinforcement"], SequenceType="FINISH_START")
        print("Created example sequence relationship.")

    # --- 5. Save the Final Model ---
    ifc_file.write(output_ifc_path)
    print(f"\nSuccessfully created new 5D model from ontology at: {output_ifc_path}")