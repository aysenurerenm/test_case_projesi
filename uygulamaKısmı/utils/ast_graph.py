import ast
import uuid


def new_id():
    return str(uuid.uuid4())[:8]


class CFGNode:
    def __init__(self, label):
        self.id = new_id()
        self.label = label
        self.next = []


def make_cfg(code):
    tree = ast.parse(code)
    entry = CFGNode("Start")
    last = build_body(tree.body, entry)
    return convert_to_json(entry)


def build_body(statements, prev_node):
    last_node = prev_node

    for stmt in statements:
        if isinstance(stmt, ast.If):
            last_node = handle_if(stmt, last_node)

        elif isinstance(stmt, ast.While):
            last_node = handle_while(stmt, last_node)

        elif isinstance(stmt, ast.For):
            last_node = handle_for(stmt, last_node)

        else:
            node = CFGNode(ast.dump(stmt))
            last_node.next.append(node)
            last_node = node

    return last_node


def handle_if(stmt, prev):
    cond = CFGNode("if " + ast.unparse(stmt.test))
    prev.next.append(cond)

    # true branch
    true_start = CFGNode("True")
    cond.next.append(true_start)
    true_end = build_body(stmt.body, true_start)

    # false branch
    if stmt.orelse:
        false_start = CFGNode("False")
        cond.next.append(false_start)
        false_end = build_body(stmt.orelse, false_start)
    else:
        false_end = cond  # no else

    # merge
    merge = CFGNode("Merge")
    true_end.next.append(merge)
    false_end.next.append(merge)
    return merge


def handle_while(stmt, prev):
    cond = CFGNode("while " + ast.unparse(stmt.test))
    prev.next.append(cond)

    body_start = CFGNode("Loop Body")
    cond.next.append(body_start)
    body_end = build_body(stmt.body, body_start)

    # back to condition
    body_end.next.append(cond)

    # exit
    exit_node = CFGNode("Exit Loop")
    cond.next.append(exit_node)

    return exit_node


def handle_for(stmt, prev):
    cond = CFGNode("for " + ast.unparse(stmt.target))
    prev.next.append(cond)

    body_start = CFGNode("Loop Body")
    cond.next.append(body_start)
    body_end = build_body(stmt.body, body_start)
    body_end.next.append(cond)

    exit_node = CFGNode("Exit Loop")
    cond.next.append(exit_node)
    return exit_node


def convert_to_json(entry):
    nodes = {}
    edges = []

    def walk(node):
        if node.id in nodes:
            return
        nodes[node.id] = {"id": node.id, "label": node.label}
        for nxt in node.next:
            edges.append({"from": node.id, "to": nxt.id})
            walk(nxt)

    walk(entry)

    return {"nodes": list(nodes.values()), "edges": edges}
