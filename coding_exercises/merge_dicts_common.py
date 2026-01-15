def merge_dicts_with_overlapping_keys(dicts):
    m_dict = {}
    
    for j in dicts:
        for (k,v) in j.items():
            if k in m_dict:
                m_dict[k] += v
            else:
                m_dict[k] = v
    return m_dict
