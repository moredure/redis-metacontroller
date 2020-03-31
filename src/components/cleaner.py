class Cleaner:
    def clean(self, desired: dict) -> dict:
        return {
            'status': desired['status'],
            'children': list(filter(None, desired['children']))
        }
