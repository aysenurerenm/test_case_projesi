from radon.complexity import cc_visit
from radon.metrics import h_visit, mi_visit
from radon.raw import analyze

def extract_metrics_with_radon(code):
    metrics = {}

    # 1. Cyclomatic Complexity Metrics
    cc_items = cc_visit(code)
    metrics["function_count"] = len(cc_items)
    
    # Her fonksiyon/sınıf için Karmaşıklık Detayları (Metrik 1)
    metrics["cyclomatic_complexity_per_function"] = [
        {"function_name": i.name, "complexity": i.complexity, "line_number": i.lineno}
        for i in cc_items
    ]
    # Ortalama Döngüsel Karmaşıklık (Metrik 2)
    metrics["average_cyclomatic_complexity"] = sum(i.complexity for i in cc_items) / metrics["function_count"] if metrics["function_count"] else 0

    # 3. Maintainability Index (Metrik 3)
    metrics["maintainability_index"] = mi_visit(code, True)

    # 4. Halstead Metrics (Metrik 4 - 10)
    h_list = h_visit(code)
    if h_list:
        # Kodun tamamı için Halstead raporu (genellikle listenin ilk öğesi)
        h = h_list[0] 
        metrics["halstead"] = {
            # Operatör ve Operand Sayıları (Ek detaylar)
            "distinct_operators (h1)": h.h1,
            "distinct_operands (h2)": h.h2,
            "total_operators (N1)": h.N1,
            "total_operands (N2)": h.N2,
            
            "length": h.length, # (Metrik 4)
            "vocabulary": h.vocabulary, # (Metrik 5)
            "volume": h.volume, # (Metrik 6)
            "difficulty": h.difficulty, # (Metrik 7)
            "effort": h.effort, # (Metrik 8)
            "bugs": h.bugs, # (Metrik 9)
            "time": h.time # (Metrik 10)
        }
    else:
        metrics["halstead"] = {}

    # 11. Raw Metrics (Ham Metrikler)
    raw = analyze(code)
    
    # HATA ÇÖZÜMÜ: Module nesnesinin __dict__ özniteliği olmadığından, 
    # veriyi doğrudan alıyoruz (Bu, 11'den fazla metrik sağlar)
    metrics["raw_metrics"] = {
        "loc": raw.loc,           # Lines of Code (Kod Satırı Sayısı)
        "lloc": raw.lloc,         # Logical Lines of Code (Mantıksal Kod Satırı Sayısı)
        "sloc": raw.sloc,         # Source Lines of Code (Kaynak Kod Satırı Sayısı)
        "comments": raw.comments, # Yorum Satırları
        "multi": raw.multi,       # Çok Satırlı Dize Sayısı
        "blank": raw.blank,       # Boş Satır Sayısı
        "single_comments": raw.single_comments # Tek satırlık yorumlar
    }

    return metrics

# Örnek Kullanım:
# from pprint import pprint
# code_to_analyze = """
# def topla(a, b):
#     # Toplama işlemi
#     if a > 0 and b > 0:
#         return a + b
#     else:
#         return 0
# """
# metrics_result = extract_metrics_with_radon(code_to_analyze)
# pprint(metrics_result)