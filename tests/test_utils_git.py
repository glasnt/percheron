from percheron.utils import git

def test_version_parse(): 
    assert git.get_previous_version("4.1") == "4.0"
    assert git.get_previous_version("4.0") == "3.2"
    assert git.get_previous_version("3.0") == "2.2"
    
def test_tag_valid(): 
    assert git.tag_valid("4.1")
    assert git.tag_valid("4.0")

    # Testing for tags that don't yet exist are prone to time creep. 
    # Instead, test known invalid tags. 
    assert not git.tag_valid("3.9")
    assert not git.tag_valid("potato")
    
