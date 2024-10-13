from typing import List, Dict

class VarMap(object):
    def __init__(self):
        self.varmaps: List[Dict[str, any]] = [{}]

    def __contains__(self, key: str):
        for map in self.varmaps:
            if key in map:
                return True
        return False
    
    def __getitem__(self, key: str):
        for map in self.varmaps[::-1]:
            if key in map:
                return map[key]
        raise KeyError()
    
    def __setitem__(self, key: str, value):
        varmap = None
        for map in self.varmaps[::-1]:
            if key in map:
                varmap = map
                break
        varmap[key] = value
    
    def create_var(self, key: str, value):
        self.varmaps[-1][key] = value
    
    def open_scope(self):
        self.varmaps.append({})
    
    def close_scope(self):
        self.varmaps.pop()
    
    def __repr__(self) -> str:
        varmap_strings = [f'{i}: {varmap}'for i, varmap in enumerate(self.varmaps)]
        return '\n'.join(varmap_strings)