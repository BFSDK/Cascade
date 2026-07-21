### CascadeLang ###
# Сascade to Batch transformer
#
# Translates Cascade code into Batch code
###################

from lark import Lark, Transformer, Visitor, Token, Tree
from sub.errorlib import showError, showFastError
import os
import sys
from sub.type_checker import TypeChecker, TypeErrorException

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = get_base_dir()

class LibraryCallHandler:

    def __init__(self, lib_name: str, lib_method):
        self.lib_name = lib_name
        self.lib_method = lib_method

    def execute(self, func_name: str, arguments):
        return self.lib_method(func_name, arguments)

### Build-In functions ###
class Library:
    ### For translator btw
    @staticmethod
    def escape_batch_characters(text: str) -> str:
        if not isinstance(text, str):
            return str(text)
        
        if text.startswith("!") and text.endswith("!"):
            return text

        text = text.replace("^", "^^")
        text = text.replace("!", "^^!")
        text = text.replace("&", "^&")
        text = text.replace("<", "<")
        text = text.replace(">", ">")
        text = text.replace("|", "^|")
        return text

    # Standart library #
    @classmethod
    def std(cls, func_name: str, arguments):
        clean_args = [str(arg).strip() for arg in arguments if str(arg).strip() and str(arg) != "None"]
        
        if func_name == "echo":
            if clean_args:
                escaped_args = [cls.escape_batch_characters(arg) for arg in clean_args]
                return f"echo {' '.join(escaped_args)}"
            return "echo."
            
        if clean_args:
            return f"{func_name} {' '.join(clean_args)}"
        return func_name
    
    # Environment and console #
    @staticmethod
    def env(func_name: str, arguments):
        if func_name == "clear":
            return "cls"
        if func_name == "pause":
            return "pause"
        if func_name == "title":
            return f"title {arguments[0]}"
        if func_name == "color":
            return f"color {arguments[0]}"
        if func_name == "quit":
            return f"exit"
        if func_name == "waypoint":
            return f":{arguments[0]}"
        if func_name == "goto":
            return f"goto {arguments[0]}"
        if func_name == "consize":
            return f"mode con: cols={arguments[0]} lines={arguments[1]}"
        return ""
    
    # Work with strings #
    @staticmethod
    def string(func_name: str, arguments):
        if func_name == "len":
            source_var = str(arguments[0]).replace('"', '').replace('!', '').strip()
            target_var = str(arguments[1]).replace('"', '').replace('!', '').strip()

            return f"call :_std_str_len {source_var} {target_var}"
        if func_name == "upper":
            source_var = str(arguments[0]).replace('"', '').replace('!', '').strip()
            target_var = str(arguments[1]).replace('"', '').replace('!', '').strip()

            return f"call :_std_str_upper {source_var} {target_var}"
        if func_name == "lower":
            source_var = str(arguments[0]).replace('"', '').replace('!', '').strip()
            target_var = str(arguments[1]).replace('"', '').replace('!', '').strip()

            return f"call :_std_str_lower {source_var} {target_var}"
        if func_name == "trim":
            source_var = str(arguments[0]).replace('"', '').replace('!', '').strip()
            target_var = str(arguments[1]).replace('"', '').replace('!', '').strip()

            return f"call :_std_str_trim {source_var} {target_var}"
        if func_name == "contains":
            source_var = str(arguments[0]).replace('"', '').replace('!', '').strip()
            search_var = str(arguments[1]).replace('"', '').replace('!', '').strip()
            target_var = str(arguments[2]).replace('"', '').replace('!', '').strip()

            return f'call :_std_str_contains {source_var} "{search_var}" {target_var}'
    
    # Work with arrays #
    @staticmethod
    def arr(func_name: str, arguments):
        if func_name == "append":
            array_var = str(arguments[0]).replace('"', '').replace('!', '').strip()
            val_to_add = str(arguments[1]).strip()
            
            if val_to_add.startswith('"') and val_to_add.endswith('"'):
                val_to_add = val_to_add[1:-1]
                
            return f'call :_std_arr_append {array_var} "{val_to_add}"'
        if func_name == "len":
            source_var = str(arguments[0]).replace('"', '').replace('!', '').strip()
            target_var = str(arguments[1]).replace('"', '').replace('!', '').strip()

            return f'call :_std_arr_len {source_var} "{target_var}"'
    
def exLib(lib_name: str, func_name: str, arguments, imported_libs: list):
    lib_method = getattr(Library, lib_name, None)
    if lib_name not in imported_libs:
        raise ImportError(f"Use method {func_name}, but namespace {lib_name} not imported")
    
    if lib_method and callable(lib_method) and lib_name in imported_libs:
        handler = LibraryCallHandler(lib_name, lib_method)
        return handler.execute(func_name, arguments)
        
    raise KeyError(f"Library '{lib_name}' not found in class Library")

class BatchTransformer(Transformer):

    def __init__(self, visit_tokens=True):
        super().__init__(visit_tokens)
        self.libraries_imported = []
        self.user_functions = []
        self.public_functions = []
        self.public_compiled_code = []
        self.loop_counter = 0
        self.included_files = set()
    
    def start(self, instructions):
        header = [
            "@echo off",
            "chcp 65001 > nul",
            "setlocal enabledelayedexpansion"
        ]
        
        filtered_instructions = []
        for inst in instructions:
            if inst is None:
                continue
            
            if isinstance(inst, dict) and inst.get("is_call"):
                line = inst["code"]
            else:
                line = str(inst).strip()

            if line:
                filtered_instructions.append(line)

        service_block_path = os.path.join(BASE_DIR, "sub", "serviceblock.bat")
        with open(service_block_path, 'r', encoding='utf-8') as f:
            serviceBlock = f.read()
                
        main_code = "\n".join(header + filtered_instructions)
        
        if self.user_functions:
            footer = "\n\nexit /b %errorlevel%\n\n" + "\n\n".join(self.user_functions)
        else:
            footer = ""
            
        return main_code + footer + "\n\n" + serviceBlock

    def assignment(self, args):
        var_name, var_type, value = args[0], args[1], args[2]

        var_name = str(var_name).strip()
        var_type = str(var_type).strip()

        if isinstance(value, dict) and value.get("is_call"):
            call_code = value["code"]
            if var_type in ["num", "int"]:
                return f"{call_code}\nset /a {var_name}=!__return_val!"
            return f"{call_code}\nset {var_name}=!__return_val!"

        raw_val = str(value).strip() if value is not None else ""

        if raw_val.startswith('"') and raw_val.endswith('"'):
            clean_value = raw_val[1:-1]
        else:
            clean_value = raw_val

        if var_type == "inp":
            return f'set /p {var_name}="{clean_value}"'
        elif var_type in ["num", "int"]:
            return f"set /a {var_name}={clean_value}"
        
        return f"set {var_name}={clean_value}"

    def array_elements(self, args):
        return [str(arg).strip() for arg in args if arg is not None]

    def array_literal(self, args):
        if not args or args[0] is None:
            return []
        return args[0] if isinstance(args[0], list) else [args[0]]

    def array_init_assignment(self, args):
        var_name = str(args[0]).strip()
        var_type = str(args[1]).strip()
        elements = args[2] if isinstance(args[2], list) else []

        lines = []
        for idx, elem in enumerate(elements):
            clean_val = str(elem).strip()
            if clean_val.startswith('"') and clean_val.endswith('"'):
                clean_val = clean_val[1:-1]
            lines.append(f"set {var_name}_{idx}={clean_val}")

        lines.append(f"set {var_name}_len={len(elements)}")
        return "\n".join(lines)

    def _format_index(self, raw_index):
        idx_str = str(raw_index).strip()
        if idx_str.startswith("!") and idx_str.endswith("!"):
            return idx_str
        elif not idx_str.isdigit():
            return f"!{idx_str}!"
        return idx_str

    def array_element_assignment(self, args):
        var_name = str(args[0]).strip()
        raw_idx = str(args[1]).strip()
        var_type = str(args[2]).strip()
        value = args[3]

        raw_val = str(value).strip() if value is not None else ""
        if raw_val.startswith('"') and raw_val.endswith('"'):
            clean_value = raw_val[1:-1]
        else:
            clean_value = raw_val

        clean_var_name = var_name.replace("!", "").replace("%", "").strip()

        if raw_idx.isdigit():
            idx_str = raw_idx
        elif raw_idx.startswith("!") and raw_idx.endswith("!"):
            idx_str = raw_idx
        else:
            clean_idx = raw_idx.replace("!", "").replace("%", "").strip()
            idx_str = f"!{clean_idx}!"

        if var_type in ["num", "int"]:
            return f"set /a {clean_var_name}_{idx_str}={clean_value}"
        return f"set {clean_var_name}_{idx_str}={clean_value}"

    def array_access(self, args):
        array_name = str(args[0]).strip().replace("!", "").replace("%", "")
        raw_idx = str(args[1]).strip()
        
        if raw_idx.isdigit():
            idx_part = raw_idx
        elif raw_idx.startswith("!") and raw_idx.endswith("!"):
            idx_part = raw_idx
        else:
            clean_idx = raw_idx.replace("!", "").replace("%", "").strip()
            idx_part = f"!{clean_idx}!"

        return f"!{array_name}_{idx_part}!"
    
    def return_stmt(self, args):
        if not args or args[0] is None:
            return "set \"__return_val=\"\n    exit /b 0"
        
        val = str(args[0]).strip()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
            
        return f"set \"__return_val={val}\"\n    exit /b 0"

    def print_stmt(self, args):
        arg = args[0]
        if not str(arg).strip():
            return "echo."
        
        arg_str = str(arg).strip()
        
        if "%" in arg_str or ("!" in arg_str and arg_str.count("!") > 2):
            return f"for /f \"delims=\" %%a in (\"{arg_str}\") do echo %%a"

        escaped_arg = Library.escape_batch_characters(arg_str)
        return f"echo {escaped_arg}"

    def type(self, args):
        return str(args[0])

    def str_val(self, args):
        s = str(args[0])
        if s.startswith('"') and s.endswith('"'):
            return s[1:-1]
        return s

    def expression(self, args):
        return args[0]

    def term(self, args):
        return args[0]

    def factor(self, args):
        return args[0]

    def bracket_expr(self, args):
        return f"({args[0]})"

    def num_arg(self, args):
        return str(args[0])

    def var_arg(self, args):
        return f"!{args[0]}!"

    def argument(self, args):
        return args[0]

    def arguments(self, args):
        return [arg for arg in args if arg is not None]
    
    def use_stmt(self, args):
        libname = str(args[0])
        self.libraries_imported.append(libname)
        return ""

    def fn_stmt(self, args):
        lib_name = str(args[0])
        func_name = str(args[1])
        
        raw_arguments = args[2] if len(args) > 2 else []
            
        if isinstance(raw_arguments, list):
            arguments_list = raw_arguments
        elif raw_arguments is None or str(raw_arguments).strip() == "":
            arguments_list = []
        else:
            arguments_list = [raw_arguments]
            
        res = exLib(lib_name, func_name, arguments_list, self.libraries_imported)
        return {"is_call": True, "code": res}

    def call_stmt(self, args):
        fn_name = str(args[0])
        raw_arguments = args[1] if len(args) > 1 else []
        
        if isinstance(raw_arguments, list):
            arguments_list = raw_arguments
        elif raw_arguments is None or str(raw_arguments).strip() == "":
            arguments_list = []
        else:
            arguments_list = [raw_arguments]

        clean_args = []
        for arg in arguments_list:
            arg_str = str(arg).strip()
            if arg_str and arg_str != "None":
                if arg_str.startswith("!") or arg_str.isdigit() or arg_str.isidentifier():
                    clean_args.append(arg_str.replace("!", ""))
                else:
                    clean_args.append(arg_str)

        args_str = " " + " ".join(clean_args) if clean_args else ""
        return {"is_call": True, "code": f"call :{fn_name}{args_str}"}

    def _extract_instruction_code(self, sub):
        if sub is None:
            return ""
        if isinstance(sub, dict) and sub.get("is_call"):
            return sub["code"]
        if isinstance(sub, list):
            lines = [self._extract_instruction_code(x) for x in sub]
            return "\n".join(line for line in lines if line)
        s = str(sub).strip()
        return s if s else ""

    def block(self, args):
        instructions = []
        for item in args:
            if isinstance(item, list):
                for sub in item:
                    code = self._extract_instruction_code(sub)
                    if code:
                        instructions.append(code)
            else:
                code = self._extract_instruction_code(item)
                if code:
                    instructions.append(code)
        return instructions

    def elseif_block(self, args):
        cond = args[0]
        body = args[1]
        return {"cond": cond, "body": body}

    def else_block(self, args):
        return args[0]

    def if_stmt(self, args):
        cond = args[0]
        body = args[1]
        
        elseifs = []
        else_body = None
        
        for arg in args[2:]:
            if isinstance(arg, dict) and "cond" in arg:
                elseifs.append(arg)
            elif isinstance(arg, list):
                else_body = arg
                
        return self._build_batch_if(cond, body, elseifs, else_body)

    def _build_batch_if(self, cond, body, elseifs, else_body):
        indented_body = "\n".join(f"    {line}" for line in body) if body else "    rem"
        
        indented_else = None
        if elseifs:
            next_ei = elseifs[0]
            rest_ei = elseifs[1:]
            inner_str = self._build_batch_if(next_ei["cond"], next_ei["body"], rest_ei, else_body)
            indented_else = "\n".join(f"    {line}" for line in inner_str.splitlines())
        elif else_body is not None:
            indented_else = "\n".join(f"    {line}" for line in else_body) if else_body else "    rem"

        if indented_else:
            return f"if {cond} (\n{indented_body}\n) else (\n{indented_else}\n)"
        else:
            return f"if {cond} (\n{indented_body}\n)"

    def while_stmt(self, args):
        cond = args[0]
        body = args[1]

        self.loop_counter += 1
        loop_label = f"_while_loop_{self.loop_counter}"
        end_label = f"_while_end_{self.loop_counter}"

        body_code = "\n".join(f"    {line}" for line in body) if body else "    rem"

        return f":{loop_label}\nif not {cond} goto {end_label}\n{body_code}\ngoto {loop_label}\n:{end_label}"

    def for_num_stmt(self, args):
        var_name = str(args[0])
        start_val = args[1]
        end_val = args[2]
        
        if len(args) == 4 or args[3] is None:
            step_val = 1
            body = args[3] if len(args) == 4 else args[4]
        else:
            step_val = args[3]
            body = args[4]

        iter_var = var_name[0] if len(var_name) > 1 else var_name

        indented_body = []
        if body:
            for line in body:
                clean_line = str(line).replace(f"!{var_name}!", f"%%{iter_var}")
                indented_body.append(f"    {clean_line}")
        else:
            indented_body = ["    rem"]

        body_str = "\n".join(indented_body)
        return f"for /L %%{iter_var} in ({start_val}, {step_val}, {end_val}) do (\n{body_str}\n)"

    def foreach_stmt(self, args):
        var_name = str(args[0])
        target = str(args[1]).strip('"\'')
        body = args[2]

        iter_var = var_name[0] if len(var_name) > 1 else var_name

        indented_body = []
        if body:
            for line in body:
                clean_line = str(line).replace(f"!{var_name}!", f"%%{iter_var}")
                indented_body.append(f"    {clean_line}")
        else:
            indented_body = ["    rem"]

        body_str = "\n".join(indented_body)
        return f"for %%{iter_var} in ({target}) do (\n{body_str}\n)"

    def walk_stmt(self, args):
        var_name = str(args[0])
        path = args[1]
        mask = args[2]
        body = args[3]

        iter_var = var_name[0] if len(var_name) > 1 else var_name

        indented_body = []
        if body:
            for line in body:
                clean_line = str(line).replace(f"!{var_name}!", f"%%{iter_var}")
                indented_body.append(f"    {clean_line}")
        else:
            indented_body = ["    rem"]

        body_str = "\n".join(indented_body)
        return f'for /R "{path}" %%{iter_var} in ({mask}) do (\n{body_str}\n)'

    def readline_stmt(self, args):
        var_name = str(args[0])
        target = args[1]
        body = args[2]

        iter_var = var_name[0] if len(var_name) > 1 else var_name

        indented_body = []
        if body:
            for line in body:
                clean_line = str(line).replace(f"!{var_name}!", f"%%{iter_var}")
                indented_body.append(f"    {clean_line}")
        else:
            indented_body = ["    rem"]

        body_str = "\n".join(indented_body)
        return f'for /F "usebackq delims=" %%{iter_var} in ("{target}") do (\n{body_str}\n)'

    def get_exports(self):
        return {
            "functions": self.public_functions,
            "code": "\n\n".join(self.public_compiled_code)
        }

    def fn_modifiers(self, args):
        return [str(m) for m in args if m is not None]

    def fn_decl(self, args):
        idx = 0
        
        modifiers = []
        if idx < len(args):
            first = args[idx]
            if isinstance(first, list):
                modifiers = [str(m) for m in first if m is not None]
                idx += 1
            elif hasattr(first, 'data') and first.data == 'fn_modifiers':
                modifiers = [str(m) for m in first.children if m is not None]
                idx += 1

        fn_name = str(args[idx]).strip()
        idx += 1

        fn_params = []
        if idx < len(args):
            curr = args[idx]
            if isinstance(curr, list):
                fn_params = [str(p) for p in curr if p is not None]
                idx += 1
            elif hasattr(curr, 'data') and curr.data == 'params':
                fn_params = [str(p.children[0]) for p in curr.children if hasattr(p, 'children')]
                idx += 1

        if idx < len(args):
            curr = args[idx]
            if isinstance(curr, str) and curr not in ("{", "}") and not curr.startswith(":"):
                idx += 1
            elif hasattr(curr, 'type') and curr.type == 'CNAME':
                idx += 1

        body_items = args[idx:]

        body_instructions = []
        for item in body_items:
            code = self._extract_instruction_code(item)
            if code:
                body_instructions.append(code)

        code_lines = [f":{fn_name}"]

        for index, param_name in enumerate(fn_params):
            clean_param = str(param_name).split(":")[0].strip()
            code_lines.append(f"    set {clean_param}=%~{index + 1}")

        for inst in body_instructions:
            code_lines.append(f"    {inst}")

        if not any("exit /b" in inst for inst in body_instructions):
            code_lines.append("    exit /b 0")

        compiled_function = "\n".join(code_lines)
        self.user_functions.append(compiled_function)

        if "pre" in modifiers:
            dummy_args = " " + " ".join('""' for _ in fn_params) if fn_params else ""
            return {"is_call": True, "code": f"call :{fn_name}{dummy_args}"}
        if "pub" in modifiers:
            self.public_functions.append(fn_name)
            self.public_compiled_code.append(compiled_function)

        return ""
    
    def include_stmt(self, args):
        raw_path = str(args[0]).strip('"\'')

        abs_path = os.path.abspath(raw_path)

        if abs_path in self.included_files:
            return ""

        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Included file not found: {raw_path}")

        self.included_files.add(abs_path)

        with open(abs_path, "r", encoding="utf-8") as f:
            included_code = f.read()

        included_ast = parser.parse(included_code)
        lib_transformer = BatchTransformer()

        lib_transformer.included_files = self.included_files

        lib_transformer.transform(included_ast)

        for pub_code in lib_transformer.public_compiled_code:
            if pub_code not in self.user_functions:
                self.user_functions.append(pub_code)

        self.public_functions.extend(lib_transformer.public_functions)

        self.included_files.update(lib_transformer.included_files)

        return ""
    
    def waypoint_stmt(self, args):
        clear_arg = args[0].strip('"')
        return f":{clear_arg}"
    
    def goto_stmt(self, args):
        clear_arg = args[0].strip('"')
        return f"goto {clear_arg}"

    def eq(self, args):
        return f"{args[0]} EQU {args[1]}"

    def neq(self, args):
        return f"{args[0]} NEQ {args[1]}"

    def lt(self, args):
        return f"{args[0]} LSS {args[1]}"

    def lte(self, args):
        return f"{args[0]} LEQ {args[1]}"

    def gt(self, args):
        return f"{args[0]} GTR {args[1]}"

    def gte(self, args):
        return f"{args[0]} GEQ {args[1]}"

    def add(self, args): 
        return f"{args[0]}+{args[1]}"
        
    def minus(self, args): 
        return f"{args[0]}-{args[1]}"

    def mul(self, args):
        return f"{args[0]}*{args[1]}"

    def div(self, args):
        return f"{args[0]}/{args[1]}"

    def mod(self, args):
        return f"{args[0]}%%{args[1]}"
        
    def num(self, args): 
        return str(args[0])

    def inp_val(self, args):
        pass
        
    def var(self, args): 
        return f"!{args[0]}!"

    def libname(self, args):
        return str(args[0])
    
    def param(self, args):
        return str(args[0])

    def params(self, args):
        return [str(arg) for arg in args if arg is not None]


grammar_path = os.path.join(BASE_DIR, "sub", "grammar.lark")
with open(grammar_path, 'r', encoding='utf-8') as f:
    my_grammar = f.read()

parser = Lark(my_grammar, parser='lalr')

def translatecode(code):
    try:
        ast_tree = parser.parse(code)
        
        checker = TypeChecker()
        checker.check(ast_tree) 

        resulting_batch = BatchTransformer().transform(ast_tree)
        return resulting_batch

    except TypeErrorException as te:
        showFastError("Type", te, "Check types")
        return ""
    except Exception as e:
        showFastError("Syntax", e, "...")
        return ""