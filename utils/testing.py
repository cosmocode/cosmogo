from typing import Union, List

Data = Union[List[dict], dict]


def build_formset_data(data: Data = None, prefix: str = None, total_forms: int = None, initial_forms: int = 0,
                       max_forms: int = 1000, min_forms: int = 0) -> dict:
    """
    Method builds a dictionary of key value pairs needed for posting a complete formset.
    """

    if data is None:
        data = []
    elif isinstance(data, dict):
        data = [data]

    if total_forms is None:
        total_forms = len(data)

    prefix = prefix or 'form'

    management_form_data = {
        f'{prefix}-INITIAL_FORMS': initial_forms,
        f'{prefix}-TOTAL_FORMS': total_forms,
        f'{prefix}-MAX_NUM_FORMS': max_forms,
        f'{prefix}-MIN_NUM_FORMS': min_forms,
    }

    forms_data = {
        f'{prefix}-{index}-{field}': value
        for index, dataset in enumerate(data)
        for field, value in dataset.items()
    }

    return {**management_form_data, **forms_data}
