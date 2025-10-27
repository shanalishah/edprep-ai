#!/usr/bin/env python3
"""
Clean up mentorship page by removing all Supabase references
"""

import re

def clean_mentorship_page():
    with open('/Users/shan/Desktop/Work/Projects/EdPrep AI/ielts-master-platform/frontend/src/app/mentorship/page.tsx', 'r') as f:
        content = f.read()
    
    # Remove supabase import
    content = re.sub(r"import { supabase } from.*\n", "", content)
    
    # Remove useSupabase variables and their if blocks
    content = re.sub(r'\s*const useSupabase = .*\n', '', content)
    content = re.sub(r'\s*if \(useSupabase\) \{\s*\n.*?\n\s*\} else \{\s*\n', '', content, flags=re.DOTALL)
    
    # Remove remaining supabase calls
    content = re.sub(r'\s*const \{ data: session \} = await supabase\.auth\.getSession\(\)\s*\n', '', content)
    content = re.sub(r'\s*if \(!session\?\.session\?\.user\) \{\s*\n.*?\n\s*return\s*\n\s*\}\s*\n', '', content, flags=re.DOTALL)
    content = re.sub(r'\s*const \{ error \} = await supabase\..*\n', '', content)
    content = re.sub(r'\s*if \(error\) throw error\s*\n', '', content)
    
    # Clean up any remaining broken syntax
    content = re.sub(r'\s*\}\s*else \{\s*\n', '', content)
    
    with open('/Users/shan/Desktop/Work/Projects/EdPrep AI/ielts-master-platform/frontend/src/app/mentorship/page.tsx', 'w') as f:
        f.write(content)
    
    print("Cleaned up mentorship page")

if __name__ == "__main__":
    clean_mentorship_page()
