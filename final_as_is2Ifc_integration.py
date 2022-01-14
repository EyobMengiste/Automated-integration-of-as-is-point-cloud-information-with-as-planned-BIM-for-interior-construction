import ifcopenshell
from csv import DictReader

import argparse


def write_integration_from_csv(csv_file, ifc_file, output_file ):

    ifc_file = ifcopenshell.open(ifc_file)
    as_is_entries = []

    with open(csv_file, 'r') as read_obj:
        csv_dict_reader = DictReader(read_obj)
        for row in csv_dict_reader:
            as_is_entries.append(row)


    for as_is_entry in as_is_entries:
        as_is_instance = ifc_file.by_guid(as_is_entry["GlobalId"])
        
        #Create or retrieve the control and the control assignment related to the instance
        already_present = 0
        for rel in as_is_instance.HasAssignments:
            if rel.RelatingControl.Name == "As_is History":
                as_is_history = rel.RelatingControl
                controls_rels = rel
                already_present = 1
                break
        
        if not already_present:

            as_is_history = ifc_file.create_entity(
                "IfcTask",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifc_file.by_type("IfcOwnerHistory")[0],
                    "Name":'As_is Information'
                },
            )

            controls_rels = ifc_file.create_entity(
                    "IfcRelAssignsToControl",
                    **{
                        "GlobalId": ifcopenshell.guid.new(),
                        "OwnerHistory": ifc_file.by_type("IfcOwnerHistory")[0],
                        "RelatedObjects": [as_is_instance],
                        "RelatingControl": as_is_history,
                    },
                )


        
        if ifc_file.schema == "IFC2X3":
            date =  ifc_file.create_entity("IfcLabel", as_is_entry["DataCollectionDate"])
            time = ifc_file.create_entity("IfcLabel", as_is_entry["DataCollectionTime"])

        elif ifc_file.schema == "IFC4":
            date =  ifc_file.create_entity("IfcDate", as_is_entry["DataCollectionDate"])
            time = ifc_file.create_entity("IfcTime", as_is_entry["DataCollectionTime"])
            

        property_values = [
            ifc_file.createIfcPropertySingleValue(
                "ElementConstructionStatus",
                "Identify the element construction status (Formwork, GypsumBoard...).",
                ifc_file.create_entity("IfcLabel", as_is_entry["ElementConstructionStatus"]),
                None), 

            ifc_file.createIfcPropertySingleValue(
                "WorkQuantity",
                "Quanity of executed work by the datacollection day.",
                 ifc_file.create_entity("IfcReal", float(as_is_entry['WorkQuantity'])),
                None), 

            ifc_file.createIfcPropertySingleValue(
                "DataCollectionDate",
                "Date of the conducted data collection.",
                date,
                None),

            ifc_file.createIfcPropertySingleValue(
                "DataCollectionTime",
                "Time of the conducted data collection.",
                time,
                None),
        ]   

        property_set = ifc_file.createIfcPropertySet(
            ifcopenshell.guid.new(),
            ifc_file.by_type("IfcOwnerHistory")[0],
            f"Pset_AsIsDataInstance_{as_is_entry['As is data instance no.']}",
            None,
            property_values)

        ifc_file.createIfcRelDefinesByProperties(
            ifcopenshell.guid.new(),
            ifc_file.by_type("IfcOwnerHistory")[0],
            None,
            None,
            [as_is_history],
            property_set)

    ifc_file.write(output_file)


if __name__=="__main__":
        parser = argparse.ArgumentParser(description="Add as_is information to IFC file")
        parser.add_argument("--csv", default="2nd_as_is_data_2_ifc4.csv", type=str, help="CSV as_is_info file")
        parser.add_argument("--ifc_input", "-i", default="as_is_&_as_planned_1.ifc")
        parser.add_argument("--ifc_output", "-o", default="as_is_&_as_planned_2.ifc")

        args = parser.parse_args()

        write_integration_from_csv(args.csv, args.ifc_input, args.ifc_output)

        # f = ifcopenshell.open(args.ifc_output)
        f = ifcopenshell.open("as_is_&_as_planned_2.ifc")
        w = f.by_guid("0IzEk4ZZ96DOLxvDeHnvCW")

        print(w.HasAssignments[0].RelatingControl.IsDefinedBy[0].RelatingPropertyDefinition.HasProperties[0].NominalValue[0])
        # prints 'GypsumWall' (The work status of the given element is at the gypsum wall instalation stage )

        # print(w.HasAssignments[0].RelatingControl.IsDefinedBy[1].RelatingPropertyDefinition.HasProperties[2].NominalValue[0])
        # prints '1.13.2022' (The inspection date at the second inspection)




 
