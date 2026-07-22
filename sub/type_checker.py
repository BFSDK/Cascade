from lark import Token, Tree
try:
    from sub.errorlib import showFastError
except ImportError:
    # Фолбэк, если модуль вызывается напрямую
    def showFastError(msg, line=None):
        print(f"[Type Error] {msg}")

class TypeErrorException(Exception):
    pass

class TypeChecker:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.current_function = None
        
        # Системные функции std библиотеки
        self.builtin_functions = {
            "std::echo": {"params": [("val", "any")], "return_type": "void"},
            "std::str_len": {"params": [("s", "str")], "return_type": "int"},
            "std::str_upper": {"params": [("s", "str")], "return_type": "str"},
            "std::str_lower": {"params": [("s", "str")], "return_type": "str"},
            "std::str_trim": {"params": [("s", "str")], "return_type": "str"},
            "std::arr_len": {"params": [("arr", "arr")], "return_type": "int"},
        }

    def check(self, tree):
        """Главный входной метод проверки типов"""
        try:
            self.functions = self.builtin_functions.copy()
            self._collect_functions(tree)
            self._visit(tree)
            return True
        except TypeErrorException as e:
            showFastError(str(e))
            return False

    def _collect_functions(self, node):
        """Первый проход: собирает все пользовательские функции"""
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

    def _types_are_compatible(self, expected, actual):
        """Проверка совместимости типов (с учётом эквивалентов int/num и any)"""
        if expected == "any" or actual == "any" or actual == "unknown":
            return True
        if expected == actual:
            return True
        
        # Эквиваленты числовых типов Cascade/Go
        num_types = ("num", "int", "float")
        if expected in num_types and actual in num_types:
            return True
            
        return False

    def _infer_expression_type(self, expr):
        """Вычисление типа выражения"""
        if isinstance(expr, Token):
            if expr.type == 'NUMBER':
                return "float" if "." in str(expr) else "int"
            if expr.type == 'STRING':
                return "str"
            if expr.type == 'CNAME':
                var_name = str(expr)
                if var_name in ("true", "false"):
                    return "bool"
                if var_name not in self.variables:
                    raise TypeErrorException(f"Использована необъявленная переменная: '{var_name}'")
                return self.variables[var_name]

        if isinstance(expr, Tree):
            # Вызов функции
            if expr.data in ('call_stmt', 'func_call', 'call'):
                self._check_function_call(expr)
                fn_name = str(expr.children[0])
                if fn_name in self.functions:
                    return self.functions[fn_name]["return_type"]
                return "any"

            # Арифметика
            if expr.data in ('add', 'minus', 'mul', 'div', 'mod'):
                left_type = self._infer_expression_type(expr.children[0])
                right_type = self._infer_expression_type(expr.children[1])
                
                if left_type == "str" or right_type == "str":
                    if expr.data == 'add':
                        return "str" # Конкатенация
                return "int" if left_type == "int" and right_type == "int" else "num"

            # Логические операции и сравнения
            if expr.data in ('eq', 'neq', 'gt', 'lt', 'gte', 'lte', 'and', 'or', 'not', 'condition'):
                return "bool"

            # Строки, массивы и переменные
            if expr.data == 'str_val':
                return "str"
            if expr.data == 'bool_val':
                return "bool"
            if expr.data == 'var':
                var_name = str(expr.children[0])
                if var_name not in self.variables:
                    raise TypeErrorException(f"Использована необъявленная переменная: '{var_name}'")
                return self.variables[var_name]
            if expr.data == 'array_access':
                arr_name = str(expr.children[0])
                if arr_name not in self.variables:
                    raise TypeErrorException(f"Массив не объявлен: '{arr_name}'")
                return "any" # Элемент массива может быть dynamic / interface{}

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

        if not self._types_are_compatible(declared_type, inferred_type):
            raise TypeErrorException(
                f"Ошибка типа для переменной '{var_name}': ожидался тип '{declared_type}', "
                f"но получено значение типа '{inferred_type}'."
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
                    f"Функция '{self.current_function}' должна возвращать '{expected_type}', "
                    f"но ничего не возвращает."
                )
            return

        actual_type = self._infer_expression_type(tree.children[0])

        if expected_type != "void" and not self._types_are_compatible(expected_type, actual_type):
            raise TypeErrorException(
                f"Несоответствие типа return в функции '{self.current_function}': "
                f"Заявлен тип '{expected_type}', но возвращается '{actual_type}'."
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
                f"Ошибка вызова функции '{fn_name}': ожидалось аргументов: {len(expected_params)}, "
                f"но передано: {len(raw_args)}."
            )

        for index, (arg_node, (param_name, expected_type)) in enumerate(zip(raw_args, expected_params)):
            actual_type = self._infer_expression_type(arg_node)

            if not self._types_are_compatible(expected_type, actual_type):
                raise TypeErrorException(
                    f"Ошибка типа в аргументе {index + 1} ('{param_name}') при вызове '{fn_name}': "
                    f"Ожидался тип '{expected_type}', но передан '{actual_type}'."
                )