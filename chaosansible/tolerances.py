from typing import Any, Dict

from chaoslib.exceptions import InvalidActivity
import json, re
from jsonpath_ng import jsonpath, parse

__all__ = ["chaosansible_eval"]

def chaosansible_eval(value: Any = None,
                      element: str = None,
                      operation: str = None,
                      result: str = None) -> bool:

    if not value or not value or not operation:
        raise InvalidActivity('Tolerance evaluation result and/or element not set')

    json_data = json.loads(value)
    jsonpath_expression = parse(element)
    match = jsonpath_expression.find(json_data)

    if operation == 'equal':
        for elem in match:
            if elem.value != result:
                return False
    
    elif operation == 'different':
        for elem in match:
            if elem.value == result:
                return False
    
    elif operation == 'greater':
        for elem in match:
            if elem.value <= result:
                return False
    
    elif operation == 'greaterorequal':
        for elem in match:
            if elem.value < result:
                return False
    
    elif operation == 'lower':
        for elem in match:
            if elem.value >= result:
                return False
    
    elif operation == 'lowerorequal':
        for elem in match:
            if elem.value >= result:
                return False
    
    elif operation == 'regex':
        regex = re.compile(result)
        for elem in match:
            if not regex.match(elem.value):
                return False

    else:
        raise InvalidActivity('Operation defined not known')


    return True
