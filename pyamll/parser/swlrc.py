from parser import Lyrics, Line, VocalElement, Vocal


def export_as_swlrc(lyrics:Lyrics) -> dict:
    """
    Export lyrics as a SWLRC (Syllable-based Word-Level Rich Caption) dictionary.
    Args:
        lyrics (Lyrics): An instance of the Lyrics class containing the lyrics data.
    Returns:
        dict: A dictionary representing the SWLRC format.
    """

    swl = {
        "StartTime": lyrics.element_map[0][0].start_time,
        "EndTime": lyrics.element_map[-1][0].end_time,
        "Type": "Syllable",
        "VocalGroups": []
    }
    for line in lyrics.init_list:
        line:Line = line
        _lead_list = []
        for i,element in enumerate(line.elements):
            element:VocalElement = element
            _is_part_of_word = False
            try:
                if line.elements[i+1].word_index == element.word_index:
                    _is_part_of_word = True
            except IndexError:
                pass            
            _lead_list.append({
                "Text": element.text,
                    "IsPartOfWord": _is_part_of_word,
                    "StartTime": element.start_time,
                    "EndTime": element.end_time
            })
        
        swl["VocalGroups"].append({
            "Type":"Vocal",
            "OppositeAligned": (line.vocal == Vocal.SECONDARY),
            "StartTime": line.start_time,
            "EndTime": line.end_time,
            "Lead": _lead_list
        })
    
    return swl