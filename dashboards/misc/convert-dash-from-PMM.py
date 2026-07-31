#!/usr/bin/env -S uv run --script

##############################################################################################################
# This script converts a PMM dashboard so it can be used in an external Prometheus + Grafana installation. 
# It doesn't need any input from you. It replaces PMM2 labels (node_name, service_name) 
# used in variables with default labels (instance).
#
##############################################################################################################
#
#    !!! WARNING !!! 
#
# The script is for experiments and education. There is no guarantee that it will work on all cases as 
# the PMM uses specific labels to provide a better user experience to PMM users. 
#
##############################################################################################################

import sys
import json
import re

# List of services that are present in PMM2
services = {'MySQL', 'MongoDB', 'PXC', 'PostgreSQL'}

# Add a variable for selecting a datasource
def add_datasource_variable(dashboard):
    datasourceVariable = {"current": {"selected": "false", "text": "prometheus", "value": "prometheus"}, "hide": 0, "includeAll": "false", "label": "Datasource", "multi": "false", "name": "datasource", "options": [], "query": "prometheus", "refresh": 1, "regex": "", "skipUrlSync": "false", "type": "datasource"}
    for element in dashboard.copy():
        if 'templating' in element:
            dashboard['templating']['list'].append(datasourceVariable)

    return dashboard


# Set the new datasource as a default one
def fix_datasource(dashboard):
    dataSourceName = "$datasource"
    for element in dashboard.copy():
        if 'panels' in element:
            for panel_index, panel in enumerate(dashboard['panels']):
                if 'datasource' in panel:
                    if dataSourceName is not None:
                        dashboard['panels'][panel_index]['datasource'] = dataSourceName

                if 'panels' in panel:
                        if len(dashboard['panels'][panel_index]['panels']) > 0:
                            for panelIn_index, panelIn in enumerate(dashboard['panels'][panel_index]['panels']):
                                if 'datasource' in panelIn:
                                    if dataSourceName is not None:
                                        dashboard['panels'][panel_index]['panels'][panelIn_index]['datasource'] = dataSourceName

                if 'mappingTypes' in panel:
                        for mappingTypes_index, mappingTypes in enumerate(dashboard['panels'][panel_index]['mappingTypes']):
                            if 'datasource' in mappingTypes:
                                 if  dataSourceName is not None:
                                     dashboard['panels'][panel_index]['mappingTypes'][mappingTypes_index]['datasource'] = dataSourceName

        if 'templating' in element:
            for panel_index, panel in enumerate(dashboard['templating']['list']):
                    if 'datasource' in list(panel.keys()):
                        if dataSourceName is not None:
                            dashboard['templating']['list'][panel_index]['datasource'] = dataSourceName

    return dashboard


def check_formulas(dashboard, currentVariableName, newVariableName):
    for element in dashboard.copy():
        if 'panels' in element:
            for panel_index, panel in enumerate(dashboard['panels']):
                if 'targets' in panel:
                    for target_index, target in enumerate(dashboard['panels'][panel_index]['targets']):
                        if 'expr' in target:
                            expr = dashboard['panels'][panel_index]['targets'][target_index]['expr']
                            expr = re.sub('node_type=~\"[a-z,$_|]*\"', '', expr)
                            if expr.find(currentVariableName) != -1:    # check if variable is used in an expression
                                print(f" <<<< {expr}")
                                dashboard['panels'][panel_index]['targets'][target_index]['expr'] = expr.replace(currentVariableName, newVariableName)
                                print(f" >>>> {dashboard['panels'][panel_index]['targets'][target_index]['expr']}\n")

                if 'options' in panel:
                    for option in enumerate(dashboard['panels'][panel_index]['options']):
                        if 'content' in option :
                            content = dashboard['panels'][panel_index]['options']['content']
                            if content.find(currentVariableName) != -1:    # check if variable is used in a content 
                                print(f" <<<< {content}") 
                                dashboard['panels'][panel_index]['options']['content'] = content.replace(currentVariableName, newVariableName)
                                print(f" >>>> {dashboard['panels'][panel_index]['options']['content']}\n")

                if 'panels' in panel:
                        if len(dashboard['panels'][panel_index]['panels']) > 0:
                            for panelIn_index, panelIn in enumerate(dashboard['panels'][panel_index]['panels']):
                                if 'targets' in panelIn:
                                    for target_index, target in enumerate(dashboard['panels'][panel_index]['panels'][panelIn_index]['targets']):
                                        if 'expr' in target:
                                            expr = dashboard['panels'][panel_index]['panels'][panelIn_index]['targets'][target_index]['expr']
                                            expr = re.sub('node_type=~\"[a-z,$_|]*\"', '', expr)
                                            if expr.find(currentVariableName) != -1:    # check if variable is used in an expression
                                                print(f" <<<< {expr}")
                                                dashboard['panels'][panel_index]['panels'][panelIn_index]['targets'][target_index]['expr'] = expr.replace(currentVariableName, newVariableName)
                                                print(f" >>>> {dashboard['panels'][panel_index]['panels'][panelIn_index]['targets'][target_index]['expr']}\n")

        if 'templating' in element:
            for list_index, lists in enumerate(dashboard['templating']['list']):
                    if 'query' in list(lists.keys()):
                        expr = dashboard['templating']['list'][list_index]['query']
                        if isinstance(expr, dict) and ('query' in expr):
                            expr = expr['query']
                        expr = re.sub('node_type=~\"[a-z,$_|]*\"', '', expr)
                        name = dashboard['templating']['list'][list_index]['name']
                        name = re.sub('node_type=~\"[a-z,$_|]*\"', '', name)
                        if expr.find(currentVariableName) != -1:    # check if variable is used in an expression
                            print(f" <<<< {expr}")
                            dashboard['templating']['list'][list_index]['query'] = expr.replace(currentVariableName, newVariableName)
                            dashboard['templating']['list'][list_index]['definition'] = expr.replace(currentVariableName, newVariableName)
                            print(f" >>>> {dashboard['templating']['list'][list_index]['query']}\n")
                        if name.find(currentVariableName) != -1:    # check if variable is used in an expression
                            print(f" <<<< {name}") 
                            dashboard['templating']['list'][list_index]['name'] = newVariableName
                            print(f" >>>> {dashboard['templating']['list'][list_index]['name']}\n")
    return dashboard


def fix_variable_label(dashboard, currentVariableLabel, newVariableLabel):
    for element in dashboard.copy():
        if 'templating' in element:
            for list_index, lists in enumerate(dashboard['templating']['list']):
                    if 'label' in list(lists.keys()):
                        label = dashboard['templating']['list'][list_index]['label']
                        if label == currentVariableLabel:    # check if variable is used in an expression
                            print(f" <<<< f{currentVariableLabel}")
                            dashboard['templating']['list'][list_index]['label'] = newVariableLabel
                            print(f" >>>> {dashboard['templating']['list'][list_index]['label']}\n")
    return dashboard


def set_variable_multi(dashboard, variableLabel, multi):
    for element in dashboard.copy():
        if 'templating' in element:
            for list_index, lists in enumerate(dashboard['templating']['list']):
                    if 'label' in list(lists.keys()):
                        label = dashboard['templating']['list'][list_index]['label']
                        if 'multi' in list(lists.keys()):
                            currentMulti = dashboard['templating']['list'][list_index]['multi']
                        else:
                            currentMulti = "unset"
                        if label == variableLabel and currentMulti != multi:    # check if variable is used in an expression
                            print(f" <<<< [{variableLabel}] multi: {dashboard['templating']['list'][list_index]['multi']}")
                            dashboard['templating']['list'][list_index]['multi'] = multi
                            print(f" <<<< [{variableLabel}] multi: {dashboard['templating']['list'][list_index]['multi']}\n")
    return dashboard


def remove_annotation(dashboard, annotationName):
    def keep_annotations(elem):
        if 'name' in elem:
            if elem['name'] != annotationName:
                return True
            else:
                print(f" <<<< annotation: {annotationName}\n")
                return False
        return True

    if 'annotations' in dashboard:
        annotations = list(filter(keep_annotations, dashboard['annotations']['list']))
        dashboard['annotations']['list'] = annotations


def get_dashboard_type(filename):
    for service in services: 
        if filename.find(service) != -1:    # check if it's a dashboard with node metrics only
            print(f"{service} service dashboard is detected")
            return True
    return False


# Additional procedure for modifing auxiliary variables 
def fix_variables(dashboard):
    for element in dashboard.copy():
        if 'templating' in element:
            for panel_index, panel in enumerate(dashboard['templating']['list']):
                if 'query' in list(panel.keys()):
                    currentVariableName = (dashboard['templating']['list'][panel_index]['name'])
                    print(f"\nVariable: {dashboard['templating']['list'][panel_index]['name']}")
                    print(f"Next expression is used for collecting variable: {dashboard['templating']['list'][panel_index]['query']}")
                    prompt = 'Modify (Y/N)? [N]: '
                    user_input = input(prompt).upper()
                    if user_input == 'Y':
                        prompt = f"Please enter new name for variable {currentVariableName}:"
                        newVariableName = input(prompt)
                        print('Collecting formulas ...')
                        check_formulas(dashboard, currentVariableName, newVariableName)
                        dashboard['templating']['list'][panel_index]['name'] = newVariableName

    return dashboard 


def main():
    with open(sys.argv[1], 'r') as dashboard_file:
        dashboard = json.loads(dashboard_file.read())
    print(f"Dashboard: {sys.argv[1],}")

    if get_dashboard_type(sys.argv[1]):    # replace service_name or node_name variables for different dashboard types
        check_formulas(dashboard, "service_name", "instance")
        fix_variable_label(dashboard, "Service Name", "Instance")
    else:
        check_formulas(dashboard, "node_name", "instance")
        fix_variable_label(dashboard, "Node Name", "Instance")

    check_formulas(dashboard, "environment", "namespace")
    fix_variable_label(dashboard, "Environment", "Namespace")
    set_variable_multi(dashboard, "Namespace", False)

    remove_annotation(dashboard, "PMM Annotations")

    # registered procedures.
    PROCEDURES = [add_datasource_variable, fix_datasource]

    for func in PROCEDURES:
        dashboard = func(dashboard)

    dashboard_json = json.dumps(dashboard, sort_keys=True, indent=4,
                                separators=(',', ': '))

    with open(sys.argv[1], 'w') as dashboard_file:
        dashboard_file.write(dashboard_json)
        dashboard_file.write('\n')

    print ('Done.')

if __name__ == '__main__':
    main()
