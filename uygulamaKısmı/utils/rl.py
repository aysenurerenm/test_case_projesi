import ast
import sys
import random
from collections import defaultdict

# ======================================================
# AST ANALYSIS (Sabit Değer ve Metadata Çıkarıcı)
# ======================================================

def get_function_metadata(code):
    tree = ast.parse(code)
    # İlk koddaki DEFAULT_POOLS mantığı
    constants = {
        'int': {0, 1, -1}, 
        'float': {0.0}, 
        'str': {"", "test"}, 
        'bool': {True, False}
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                constants['bool'].add(node.value)
            elif isinstance(node.value, int):
                constants['int'].add(node.value)
                # Boundary (Sınır) için komşuları da ekle
                constants['int'].add(node.value - 1)
                constants['int'].add(node.value + 1)
            elif isinstance(node.value, float):
                constants['float'].add(node.value)
            elif isinstance(node.value, str):
                constants['str'].add(node.value)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            args_info = []
            for arg in node.args.args:
                # Tip ipucu (Type Hint) yakalama
                type_hint = arg.annotation.id if arg.annotation and isinstance(arg.annotation, ast.Name) else "any"
                args_info.append({"name": arg.arg, "type": type_hint})
            return node.name, args_info, {k: list(v) for k, v in constants.items()}
            
    return None, [], {k: list(v) for k, v in constants.items()}

def extract_executable_lines(code, func_name):
    tree = ast.parse(code)
    lines = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            for sub in ast.walk(node):
                if isinstance(sub, (ast.If, ast.Return, ast.Assign, ast.Expr, ast.Raise)):
                    if hasattr(sub, "lineno"): lines.add(sub.lineno)
    return lines

# ======================================================
# TRACE & EXECUTION
# ======================================================

EXEC_ENV = {}
TARGET_FUNC = None
executed_lines = set()
EXCEPTION_LINE = None

def trace_lines(frame, event, arg):
    global EXCEPTION_LINE
    if frame.f_code.co_filename == "<user_code>" and frame.f_code.co_name == TARGET_FUNC:
        if event == "line": executed_lines.add(frame.f_lineno)
        elif event == "exception": EXCEPTION_LINE = frame.f_lineno
    return trace_lines

def run_test(inputs):
    global executed_lines, EXCEPTION_LINE
    executed_lines, EXCEPTION_LINE = set(), None
    sys.settrace(trace_lines)
    try: 
        EXEC_ENV[TARGET_FUNC](*inputs)
    except: 
        pass
    finally: 
        sys.settrace(None)
    if EXCEPTION_LINE: executed_lines.add(EXCEPTION_LINE)
    return executed_lines

# ======================================================
# ENTEGRE GİRDİ ÜRETME STRATEJİSİ (İlk Koddaki Yapı)
# ======================================================

TYPE_MAP = {
    "int": int,
    "str": str,
    "bool": bool,
    "float": float
}

def generate_type_mismatch(expected_type):
    """İlk koddaki tip uyuşmazlığı mantığı"""
    if expected_type is int:
        return random.choice(["abc", None, 1.5, []])
    if expected_type is str:
        return random.choice([123, None, {}, True])
    if expected_type is bool:
        return random.choice([0, 1, "true", None])
    if expected_type is float:
        return random.choice(["high", None, 10])
    return object()

def generate_valid_input(expected_type, pool):
    """İlk koddaki geçerli girdi mantığı"""
    if pool:
        return random.choice(pool)
    return expected_type() if expected_type else None

def generate_inputs_with_rl_strategy(strategy, args_info, code_pools):
    """
    Geliştirilmiş Girdi Üretici: 
    Type hint olmasa bile pool'dan rastgele tip seçerek blokajı kırar.
    """
    inputs = []

    for arg in args_info:
        raw_type = arg["type"] # 'int', 'str' veya 'any'
        expected_type = TYPE_MAP.get(raw_type)
        
        # EĞER TİP BİLİNMİYORSA (any), POOL'LARDAN RASTGELE BİR TİP SEÇ
        if raw_type == "any":
            available_types = [t for t in code_pools.keys() if code_pools[t]]
            chosen_type = random.choice(available_types) if available_types else "int"
            pool = code_pools.get(chosen_type, [])
            expected_type = TYPE_MAP.get(chosen_type)
        else:
            pool = code_pools.get(raw_type, [])

        # --- STRATEJİ UYGULAMA ---
        if strategy == "type_mismatch":
            inputs.append(generate_type_mismatch(expected_type))
        
        elif strategy == "boundary":
            # Pool boşsa 0'ı baz al, doluysa pool'daki sınırları zorla
            base = random.choice(pool) if pool else 0
            if isinstance(base, (int, float)):
                inputs.append(base + random.choice([-1, 0, 1]))
            else:
                inputs.append(base) # String ise olduğu gibi ver
            
        elif strategy == "random":
            # Global rastgele değerler
            inputs.append(random.choice([None, "random_str", 9999, False, 0.5]))

        else: # "valid"
            # Pool'dan mantıklı bir değer çek, pool boşsa fallback yap
            if pool:
                inputs.append(random.choice(pool))
            else:
                # Fallback: En azından None döndürme, temel bir tip döndür
                inputs.append(random.choice([10, "test", True]))

    return tuple(inputs)

# ======================================================
# OPTİMİZE RL AGENT & MAIN AUTOMATION
# ======================================================

class StrategyRLAgent:
    def __init__(self):
        self.Q = defaultdict(float)
        self.actions = ["valid", "type_mismatch", "boundary", "random"]
        self.alpha = 0.3      # Öğrenme hızı
        self.gamma = 0.9      # Gelecek ödüllerin önemi
        self.epsilon = 0.4    # Başlangıçta yüksek keşif

    def choose(self, state):
        # Epsilon-Greedy: Rastgele keşif mi yoksa en iyi aksiyon mu?
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        
        q_values = [self.Q[(state, a)] for a in self.actions]
        max_q = max(q_values)
        
        # En iyi aksiyonlar arasından rastgele seç (stuck olmayı engeller)
        best_actions = [a for a in self.actions if self.Q[(state, a)] == max_q]
        return random.choice(best_actions)

    def update(self, s, a, r, s2):
        best_next = max(self.Q[(s2, x)] for x in self.actions)
        # Q-Learning Güncelleme
        self.Q[(s, a)] += self.alpha * (r + self.gamma * best_next - self.Q[(s, a)])
def start_rl_testing(user_code):
    global EXEC_ENV, TARGET_FUNC, EXCEPTION_LINE
    TARGET_FUNC, args_info, code_pools = get_function_metadata(user_code)
    
    exec(compile(user_code, "<user_code>", "exec"), EXEC_ENV)
    target_lines = extract_executable_lines(user_code, TARGET_FUNC)
    total_lines = len(target_lines)
    
    agent = StrategyRLAgent()
    covered = set()
    error_registry = {} # Hataları ve onları tetikleyen girdileri tutar
    coverage_boosters = [] # Kapsamayı artıran kritik hamleleri tutar
    
    state = (0, False)

    print(f"\n🚀 AGRESİF RL TESTİ BAŞLIYOR (Hedef: {total_lines} Satır)")
    print("-" * 140)
    print(f"{'Epi':<4} | {'Strateji':<14} | {'Girdi':<40} | {'Yeni':<4} | {'Ödül':<6} | {'Kapsama'} | {'Durum'}")
    print("-" * 140)

    for episode in range(1, 500):
        # Epsilon Decay
        agent.epsilon = max(0.05, 0.4 * (1 - len(covered & target_lines)/total_lines))
        
        strategy = agent.choose(state)
        test_input = generate_inputs_with_rl_strategy(strategy, args_info, code_pools)
        
        hit_lines = run_test(test_input)
        new_hits = hit_lines & target_lines - covered
        
        has_exception = EXCEPTION_LINE is not None
        reward = 0

        # --- REWARD & LOGGING LOGIC ---
        if new_hits:
            reward += len(new_hits) * 100
            # Kapsama artıran girdiyi kaydet
            coverage_boosters.append({
                "episode": episode,
                "strategy": strategy,
                "input": test_input,
                "new_lines": list(new_hits),
                "current_rate": ((len(covered | new_hits) / total_lines) * 100)
            })
            covered |= new_hits
        
        if has_exception:
            if EXCEPTION_LINE not in error_registry:
                reward +=40
                # Unique hatayı ve tetikleyiciyi kaydet
                error_registry[EXCEPTION_LINE] = {
                    "strategy": strategy,
                    "input": test_input,
                    "episode": episode
                }
            else:
                reward -= 100
        
        if not new_hits and not has_exception:
            reward -= 15

        actual_coverage = len(covered & target_lines)
        cover_rate = (actual_coverage / total_lines) * 100 if total_lines > 0 else 100
        
        next_state = (int(cover_rate / 5), has_exception)
        agent.update(state, strategy, reward, next_state)
        state = next_state

        # Satır Logu
        status = f"💥 HATA (Satır:{EXCEPTION_LINE})" if has_exception else "✅ OK"
        input_disp = str(test_input)[:38] + ".." if len(str(test_input)) > 40 else str(test_input)
        print(f"{episode:03}  | {strategy:<14} | {input_disp:<40} | +{len(new_hits):<3} | {reward:<6} | %{cover_rate:<7.2f} | {status}")

        if actual_coverage == total_lines:
            print("-" * 140 + f"\n🎯 %100 KAPSAMA {episode}. ADIMDA BAŞARILDI!")
            break

    # === FİNAL ANALİZ RAPORU ===
    print("\n" + "="*80)
    print("📊 RL TEST SONUÇ RAPORU")
    print("="*80)
    
    print(f"\n📍 UNIQUE HATALAR ({len(error_registry)} Adet):")
    if error_registry:
        print(f"{'Satır':<10} | {'Bölüm':<6} | {'Strateji':<15} | {'Tetikleyici Girdi'}")
        print("-" * 80)
        for line, data in error_registry.items():
            print(f"Satır {line:<5} | Ep:{data['episode']:<4} | {data['strategy']:<15} | {data['input']}")
    else:
        print("🎉 Tebrikler! Hiç hata bulunamadı.")

    print(f"\n📈 KAPSAMA ARTIRAN KRİTİK ADIMLAR:")
    print(f"{'Bölüm':<6} | {'Kapsama':<10} | {'Yeni Satırlar':<15} | {'Girdi'}")
    print("-" * 80)
    for boost in coverage_boosters:
        lines_str = ",".join(map(str, boost['new_lines']))
        print(f"Ep:{boost['episode']:<3} | %{boost['current_rate']:<8.2f} | {lines_str:<15} | {boost['input']}")

    print("\n" + "="*80)
    print(f"NİHAİ BAŞARI: %{cover_rate:.2f} Kapsama | {len(error_registry)} Hata")
    print("="*80)
    result = {
        "cover_rate": round(cover_rate, 2),
        "total_lines": total_lines,
        "covered_lines": actual_coverage,
        "errors": [
            {
                "line": line,
                "episode": data["episode"],
                "strategy": data["strategy"],
                "input": str(data["input"])
            }
            for line, data in error_registry.items()
        ],
        "coverage_boosters": [
            {
                "episode": b["episode"],
                "strategy": b["strategy"],
                "input": str(b["input"]),
                "new_lines": b["new_lines"],
                "rate": round(b["current_rate"], 2)
            }
            for b in coverage_boosters
        ] 
    }

    return result