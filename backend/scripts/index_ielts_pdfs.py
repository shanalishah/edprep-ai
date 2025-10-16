import os
from app.services.retrieval import TfidfRetriever


def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # Attempt candidate paths; adjust as needed based on actual structure
    candidates = []
    base = os.path.abspath(os.path.join(project_root, '..'))
    cand1 = os.path.join(base, 'IELTS', 'Cambridge IELTS', 'Academic', 'Cambridge IELTS 15 with Answers Academic [www.luckyielts.com]', 'Cambridge IELTS 15 with Answers Academic [www.luckyielts.com].pdf')
    cand2 = os.path.join(base, 'IELTS', 'Cambridge IELTS', 'Academic', 'Cambridge IELTS 16 with Answers Academic [www.luckyielts.com]', 'Cambridge IELTS 16 with Answers Academic [www.luckyielts.com].pdf')
    cand3 = os.path.join(base, 'IELTS', 'Cambridge IELTS', 'Academic', 'Cambridge IELTS 20 with Answers Academic [www-1', 'Cambridge IELTS 20 with Answers Academic [www-1.pdf')
    for p in (cand1, cand2, cand3):
        if os.path.exists(p):
            candidates.append(p)

    if not candidates:
        print('No candidate PDFs found; please adjust paths in scripts/index_ielts_pdfs.py')
        return

    retriever = TfidfRetriever()
    retriever.index_pdfs(candidates)
    out_dir = os.path.join(project_root, 'models')
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, 'retrieval_index.json')
    retriever.save(out)
    print(f"Saved retrieval index to {out} from {len(candidates)} PDFs")


if __name__ == '__main__':
    main()


