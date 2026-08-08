def hospice_to_text(row):

    return f"""
    Hospice Organization: {row.get('organization_name', '')}
    Doing Business As: {row.get('doing_business_as_name', '')}
    Provider Type: {row.get('provider_type_text', '')}
    Organization Structure: {row.get('organization_type_structure', '')}
    Ownership Type: {row.get('proprietary_nonprofit', '')}

    Location:
    {row.get('address_line_1', '')}
    {row.get('address_line_2', '')}
    {row.get('city', '')},
    {row.get('state', '')}
    {row.get('zip_code', '')}

    NPI: {row.get('npi', '')}
    CCN: {row.get('ccn', '')}

    Enrollment State: {row.get('enrollment_state', '')}
    """