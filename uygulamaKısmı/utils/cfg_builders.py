import ast

# =============================
# CFG NODE
# =============================
class CFGNode:
    def __init__(self, label):
        self.label = label
        self.next = []  # [(CFGNode, label)]

# =============================
# LOGICAL CFG BUILDER
# =============================
class LogicalCFGBuilder:
    def __init__(self):
        self.counter = 0

    def new_node(self, label):
        self.counter += 1
        return CFGNode(f"N{self.counter}: {label}")

    # -------------------------
    # STATEMENT BUILDER
    # -------------------------
    def build_statements(self, stmts):
        entry = None
        last_exit = None

        for stmt in stmts:
            curr_entry = None
            curr_exit = None

            if isinstance(stmt, ast.If):
                curr_entry, curr_exit = self.build_if(stmt)

            elif isinstance(stmt, ast.While):
                curr_entry, curr_exit = self.build_while(stmt)

            else:
                continue  # operasyonel satırlar yok sayılır

            if entry is None:
                entry = curr_entry

            if last_exit:
                last_exit.next.append((curr_entry, None))  #  DÜZELTİLDİ

            last_exit = curr_exit

        return entry, last_exit

    # -------------------------
    # IF / ELIF / ELSE
    # -------------------------
    def build_if(self, node):
        cond = self.new_node(f"IF {ast.unparse(node.test)}")
        merge = self.new_node("MERGE")

        # IF yolu
        t_entry, t_exit = self.build_statements(node.body)
        if t_entry:
            cond.next.append((t_entry, "if"))
            t_exit.next.append((merge, None))
        else:
            cond.next.append((merge, "if"))

        # ELIF / ELSE zinciri
        current = node.orelse

        while current:
            if len(current) == 1 and isinstance(current[0], ast.If):
                elif_node = current[0]
                e_entry, e_exit = self.build_statements(elif_node.body)
                if e_entry:
                    cond.next.append(
                        (e_entry, f"elif {ast.unparse(elif_node.test)}")
                    )
                    e_exit.next.append((merge, None))
                else:
                    cond.next.append(
                        (merge, f"elif {ast.unparse(elif_node.test)}")
                    )
                current = elif_node.orelse
            else:
                # ELSE
                f_entry, f_exit = self.build_statements(current)
                if f_entry:
                    cond.next.append((f_entry, "else"))
                    f_exit.next.append((merge, None))
                else:
                    cond.next.append((merge, "else"))
                break

        return cond, merge

    # -------------------------
    # WHILE
    # -------------------------
    def build_while(self, node):
        cond = self.new_node(f"WHILE {ast.unparse(node.test)}")
        merge = self.new_node("MERGE")

        # Döngü gövdesini oluştur
        body_entry, body_exit = self.build_statements(node.body)

        # --- EXTRA DÖNGÜ YOLU ---
        # WHILE düğümünden kendisine giden bağımsız ok
        cond.next.append((cond, "is_looping")) 

        if body_entry:
            cond.next.append((body_entry, "loop"))
            body_exit.next.append((cond, "back"))

        cond.next.append((merge, "exit"))
        return cond, merge

    # -------------------------
    # BUILD CFG
    # -------------------------
    def build(self, code):
        tree = ast.parse(code)

        start = self.new_node("START")
        funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        if not funcs:
            return start

        fn = funcs[0]
        fn_node = self.new_node(f"FUNC {fn.name}")
        start.next.append((fn_node, None))  # ✅

        body_entry, body_exit = self.build_statements(fn.body)
        end_node = self.new_node("END")

        if body_entry:
            fn_node.next.append((body_entry, None))  # ✅
            body_exit.next.append((end_node, None))  # ✅
        else:
            fn_node.next.append((end_node, None))    # ✅

        return start


# =============================
# PUBLIC API
# =============================
def make_cfg(code):
    builder = LogicalCFGBuilder()
    start = builder.build(code)

    nodes = {}
    edges = []

    stack = [start]
    visited = set()

    while stack:
        node = stack.pop()
        if node in visited:
            continue

        visited.add(node)
        nodes[node.label] = node.label

        for nxt, lbl in node.next:
            edges.append({
                "source": node.label,
                "target": nxt.label,
                "label": lbl
            })
            stack.append(nxt)

    return {
        "nodes": [{"id": k, "label": k} for k in nodes],
        "edges": edges
    }
