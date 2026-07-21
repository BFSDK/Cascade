from lark import Token, Tree
from sub.errorlib import showFastError

### CascadeLang ###
# Type checker
#
# It checks the types before compilation and throws errors if there is a mismatch
###################

class TypeErrorException(Exception):
    pass

class TypeChecker:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.current_function = None

    def check(self, tree):
        self._collect_functions(tree)
        self._visit(tree)

    def _collect_functions(self, node):
        """Первый проход: собирает все функции в таблицу self.functions"""
        if not isinstance(node, Tree):
            return

        if node.data == 'fn_decl':
            children = node.children
            idx = 0

            if idx < len(children) and isinstance(children[idx], Tree) and children[idx].data == 'fn_modifiers':
                idx += 1

            fn_name = str(children[idx])
            idx += 1

            fn_params = []
            if idx < len(children) and isinstance(children[idx], Tree) and children[idx].data == 'params':
                fn_params = self._parse_params(children[idx])
                idx += 1

            return_type = "void"
            if idx < len(children):
                curr = children[idx]
                if isinstance(curr, Token) or (isinstance(curr, Tree) and curr.data == 'type'):
                    return_type = self._unwrap_type(curr)

            self.functions[fn_name] = {
                "params": fn_params,
                "return_type": return_type
            }

        for child in node.children:
            if isinstance(child, Tree):
                self._collect_functions(child)

    def _unwrap_type(self, node):
        if isinstance(node, Tree):
            if len(node.children) > 0:
                return self._unwrap_type(node.children[0])
            return "void"
        return str(node).strip()

    def _infer_expression_type(self, expr):
        if isinstance(expr, Token):
            if expr.type == 'NUMBER':
                return "num"
            if expr.type == 'STRING':
                return "str"
            if expr.type == 'CNAME':
                var_name = str(expr)
                if var_name not in self.variables:
                    raise TypeErrorException(f"An undeclared variable is used:  '{var_name}'")
                return self.variables[var_name]

        if isinstance(expr, Tree):
            if expr.data in ('call_stmt', 'func_call', 'call'):
                self._check_function_call(expr)
                fn_name = str(expr.children[0])
                if fn_name in self.functions:
                    return self.functions[fn_name]["return_type"]
                return "any"

            if expr.data in ('add', 'minus', 'mul', 'div', 'mod', 'num'):
                return "num"
            if expr.data == 'str_val':
                return "str"
            if expr.data == 'var':
                var_name = str(expr.children[0])
                if var_name not in self.variables:
                    raise TypeErrorException(f"An undeclared variable is used:  '{var_name}'")
                return self.variables[var_name]
            if expr.data == 'array_access':
                arr_name = str(expr.children[0])
                if arr_name not in self.variables:
                    raise TypeErrorException(f"The array is not declared: '{arr_name}'")
                return self.variables[arr_name]

            for child in expr.children:
                if isinstance(child, (Tree, Token)):
                    inferred = self._infer_expression_type(child)
                    if inferred != "unknown":
                        return inferred

        return "unknown"

    def _parse_param(self, param_tree):
        p_name = str(param_tree.children[0])
        p_type = self._unwrap_type(param_tree.children[1])
        return (p_name, p_type)

    def _parse_params(self, params_tree):
        params = []
        for child in params_tree.children:
            if isinstance(child, Tree) and child.data == 'param':
                params.append(self._parse_param(child))
        return params

    def _visit(self, node):
        if not isinstance(node, Tree):
            return

        method_name = f"_visit_{node.data}"
        visitor = getattr(self, method_name, self._generic_visit)
        visitor(node)

    def _generic_visit(self, node):
        for child in node.children:
            if isinstance(child, Tree):
                self._visit(child)

    def _visit_fn_decl(self, tree):
        children = tree.children
        idx = 0

        if idx < len(children) and isinstance(children[idx], Tree) and children[idx].data == 'fn_modifiers':
            idx += 1

        fn_name = str(children[idx])
        idx += 1

        fn_params = []
        if idx < len(children) and isinstance(children[idx], Tree) and children[idx].data == 'params':
            fn_params = self._parse_params(children[idx])
            idx += 1

        if idx < len(children):
            curr = children[idx]
            if isinstance(curr, Token) or (isinstance(curr, Tree) and curr.data == 'type'):
                idx += 1

        old_vars = self.variables.copy()
        old_fn = self.current_function
        self.current_function = fn_name

        for p_name, p_type in fn_params:
            self.variables[p_name] = p_type

        for child in children[idx:]:
            if isinstance(child, Tree):
                self._visit(child)

        self.variables = old_vars
        self.current_function = old_fn

    def _visit_assignment(self, tree):
        var_name = str(tree.children[0])
        declared_type = self._unwrap_type(tree.children[1])
        expr_node = tree.children[2]

        inferred_type = self._infer_expression_type(expr_node)

        if inferred_type not in ("any", "unknown"):
            types_match = (
                declared_type == inferred_type or
                (declared_type in ("num", "int") and inferred_type in ("num", "int"))
            )
            if not types_match:
                raise TypeErrorException(
                    f"Variable type error '{var_name}': expected type '{declared_type}', "
                    f"But the value received is of the type: '{inferred_type}'."
                )

        self.variables[var_name] = declared_type

    def _visit_return_stmt(self, tree):
        if not self.current_function:
            return

        expected_type = self.functions[self.current_function]["return_type"]

        has_expr = len(tree.children) > 0 and tree.children[0] is not None
        if not has_expr:
            if expected_type != "void":
                raise TypeErrorException(
                    f"The function '{self.current_function}' should return '{expected_type}', "
                    f"But it returns emptiness"
                )
            return

        actual_type = self._infer_expression_type(tree.children[0])

        if actual_type != "any" and expected_type != "void":
            types_match = (
                expected_type == actual_type or
                (expected_type in ("num", "int") and actual_type in ("num", "int"))
            )
            if not types_match:
                raise TypeErrorException(
                    f"Return type mismatch in a function '{self.current_function}': "
                    f"Type declared '{expected_type}', but returns '{actual_type}'."
                )

    def _visit_call_stmt(self, tree):
        self._check_function_call(tree)

    def _check_function_call(self, tree):
        fn_name = str(tree.children[0])

        if fn_name not in self.functions:
            return

        expected_params = self.functions[fn_name]["params"]

        raw_args = []
        if len(tree.children) > 1 and tree.children[1] is not None:
            args_node = tree.children[1]
            if isinstance(args_node, Tree) and args_node.data in ('arguments', 'args'):
                raw_args = args_node.children
            elif isinstance(args_node, list):
                raw_args = args_node
            else:
                raw_args = [args_node]

        if len(raw_args) != len(expected_params):
            raise TypeErrorException(
                f"Error in calling the function '{fn_name}': Expected arguments: {len(expected_params)}, "
                f"But passed: {len(raw_args)}."
            )

        for index, (arg_node, (param_name, expected_type)) in enumerate(zip(raw_args, expected_params)):
            actual_type = self._infer_expression_type(arg_node)

            if actual_type not in ("any", "unknown"):
                types_match = (
                    expected_type == actual_type or
                    (expected_type in ("num", "int") and actual_type in ("num", "int"))
                )
                if not types_match:
                    raise TypeErrorException(
                        f"Type error in argument {index + 1}: ('{param_name}') when calling '{fn_name}': "
                        f"Expected type '{expected_type}', but the type is passed '{actual_type}'."
                    )