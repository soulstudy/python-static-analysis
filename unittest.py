# static_analyzer.py
import ast
import sys
import re
import time

# 以下为包装好的 Logger 类的定义
class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")  # 防止编码错误

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

def analyze_file(filepath):
    """主分析函数"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"分析文件: {filepath}")
    print("=" * 80)

    # 执行各种分析
    line_count = analyze_line_count(content)
    print(f"1. 代码行数: {line_count}")

    analyze_syntax_errors(content)
    analyze_division_by_zero(content)
    analyze_variable_shadowing(content)
    analyze_unused_variables(content)
    analyze_exception_handling(content)
    analyze_input_validation(content)
    analyze_potential_bugs(content)
    analyze_function_definitions(content)
    analyze_import_statements(content)

    # 更复杂的AST分析
    try:
        tree = ast.parse(content)
        perform_ast_analysis(tree, content)
    except SyntaxError as e:
        print(f"语法错误: {e}")

    print("\n" + "=" * 80)
    print("静态分析完成")


def analyze_line_count(content):
    """统计代码行数"""
    lines = content.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return len(non_empty_lines)


def analyze_syntax_errors(content):
    """检查语法错误"""
    print("\n2. 语法错误检查:")
    try:
        ast.parse(content)
        print("   ✓ 无语法错误")
    except SyntaxError as e:
        print(f"   ✗ 语法错误: {e}")
        print(f"     位置: 第{e.lineno}行, 第{e.offset}列")


def analyze_division_by_zero(content):
    """检查除以零的风险"""
    print("\n3. 除以零风险检查:")

    # 正则表达式匹配除法操作
    division_patterns = [
        r'/(?!\s*\w+\s*\[)',  # 除法操作符
        r'divide\s*\([^)]*0[^)]*\)',  # 除以零的调用
    ]

    lines = content.split('\n')
    found_issues = False

    for i, line in enumerate(lines, 1):
        if '/' in line and '//' not in line:  # 排除整除操作符
            # 检查是否可能除以零
            if re.search(r'/(\s*0\b|\b0\.0)', line):
                print(f"   ✗ 第{i}行: 可能除以零 - {line.strip()}")
                found_issues = True
            elif re.search(r'/.*\b0\b.*[^\.]', line):
                print(f"   ⚠ 第{i}行: 可能间接除以零 - {line.strip()}")
                found_issues = True

    if not found_issues:
        print("   ✓ 未发现明显的除以零风险")


def analyze_variable_shadowing(content):
    """检查变量名与内置函数/关键字冲突"""
    print("\n4. 变量名冲突检查:")

    builtins = [
        'list', 'dict', 'set', 'str', 'int', 'float', 'bool',
        'input', 'print', 'sum', 'min', 'max', 'len', 'type',
        'id', 'range', 'enumerate', 'zip', 'map', 'filter'
    ]

    lines = content.split('\n')
    found_issues = False

    for i, line in enumerate(lines, 1):
        # 查找变量赋值
        match = re.match(r'^\s*(\w+)\s*=', line)
        if match:
            var_name = match.group(1)
            if var_name in builtins:
                print(f"   ⚠ 第{i}行: 变量名'{var_name}'与内置函数/类型冲突 - {line.strip()}")
                found_issues = True

    if not found_issues:
        print("   ✓ 未发现变量名冲突")


def analyze_unused_variables(content):
    """检查未使用的变量（简单实现）"""
    print("\n5. 未使用变量检查:")

    try:
        tree = ast.parse(content)
        used_vars = set()
        defined_vars = set()

        class VariableVisitor(ast.NodeVisitor):
            def visit_Name(self, node):
                used_vars.add(node.id)

            def visit_FunctionDef(self, node):
                defined_vars.add(node.name)
                for arg in node.args.args:
                    defined_vars.add(arg.arg)
                self.generic_visit(node)

            def visit_Assign(self, node):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined_vars.add(target.id)
                self.generic_visit(node)

        visitor = VariableVisitor()
        visitor.visit(tree)

        # 查找定义但未使用的变量
        unused = defined_vars - used_vars
        if unused:
            for var in unused:
                print(f"   ⚠ 可能未使用的变量: '{var}'")
        else:
            print("   ✓ 未发现明显未使用的变量")
    except:
        print("   ⚠ AST分析失败，跳过未使用变量检查")


def analyze_exception_handling(content):
    """检查异常处理"""
    print("\n6. 异常处理检查:")

    try:
        tree = ast.parse(content)

        class ExceptionVisitor(ast.NodeVisitor):
            def __init__(self):
                self.division_nodes = []
                self.input_nodes = []
                self.has_try_except = False

            def visit_Div(self, node):
                self.division_nodes.append(node)

            def visit_Call(self, node):
                if isinstance(node.func, ast.Name) and node.func.id == 'input':
                    self.input_nodes.append(node)
                self.generic_visit(node)

            def visit_Try(self, node):
                self.has_try_except = True

        visitor = ExceptionVisitor()
        visitor.visit(tree)

        if visitor.division_nodes and not visitor.has_try_except:
            print("   ⚠ 存在除法操作但没有异常处理，可能导致除以零错误")
        if visitor.input_nodes and not visitor.has_try_except:
            print("   ⚠ 存在输入操作但没有异常处理，可能导致类型转换错误")

        if not visitor.has_try_except:
            print("   ⚠ 代码中没有try-except异常处理")
        else:
            print("   ✓ 代码包含异常处理")
    except:
        print("   ⚠ 无法完成异常处理检查")


def analyze_input_validation(content):
    """检查输入验证"""
    print("\n7. 输入验证检查:")

    lines = content.split('\n')
    has_input = False
    has_validation = False

    for i, line in enumerate(lines, 1):
        if 'input(' in line:
            has_input = True
            print(f"   ⚠ 第{i}行: 发现用户输入 - {line.strip()}")

        # 检查是否包含输入验证
        validation_patterns = [
            r'\.isdigit\(\)',
            r'try\s*:',
            r'except\s+ValueError',
            r'if\s+.*\.isdigit\(\)',
            r'isinstance\(.*,\s*(int|float|str)\)'
        ]

        for pattern in validation_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                has_validation = True

    if has_input and not has_validation:
        print("   ✗ 存在用户输入但没有输入验证，可能导致类型错误或崩溃")
    elif has_validation:
        print("   ✓ 代码包含输入验证")


def analyze_potential_bugs(content):
    """检查潜在bug模式"""
    print("\n8. 潜在bug模式检查:")

    bug_patterns = [
        (r'while\s+True\s*:', "无限循环风险"),
        (r'if\s+=\s+', "可能误用赋值操作符"),
        (r'==\s+None', "应使用'is None'而不是'== None'"),
        (r'except\s*:', "过于宽泛的异常捕获"),
        (r'print\s+[^(]', "print语句缺少括号"),
        (r'input\s*\([^)]*\)\.', "input()结果直接调用方法，可能为None"),
    ]

    lines = content.split('\n')
    found_bugs = False

    for i, line in enumerate(lines, 1):
        for pattern, description in bug_patterns:
            if re.search(pattern, line):
                print(f"   ⚠ 第{i}行: {description} - {line.strip()}")
                found_bugs = True

    if not found_bugs:
        print("   ✓ 未发现明显的bug模式")


def analyze_function_definitions(content):
    """分析函数定义"""
    print("\n9. 函数定义分析:")

    try:
        tree = ast.parse(content)
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'lineno': node.lineno
                })

        if functions:
            for func in functions:
                print(f"   函数: {func['name']}({', '.join(func['args'])}) - 第{func['lineno']}行")
        else:
            print("   ⚠ 未找到函数定义（可能是脚本式代码）")
    except:
        print("   ⚠ 函数分析失败")


def analyze_import_statements(content):
    """分析导入语句"""
    print("\n10. 导入分析:")

    import_patterns = [
        (r'^import\s+(\w+)', "导入模块"),
        (r'^from\s+(\w+)\s+import', "从模块导入")
    ]

    lines = content.split('\n')
    imports_found = []

    for line in lines:
        for pattern, description in import_patterns:
            match = re.search(pattern, line)
            if match:
                imports_found.append(f"{description}: {line.strip()}")

    if imports_found:
        for imp in imports_found:
            print(f"   {imp}")
    else:
        print("   ⚠ 未发现导入语句")


def perform_ast_analysis(tree, content):
    """执行AST分析"""
    print("\n11. AST深度分析:")

    # 分析循环结构
    loop_count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.While, ast.For)):
            loop_count += 1

    print(f"   循环结构数量: {loop_count}")

    # 分析条件语句
    condition_count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            condition_count += 1

    print(f"   条件语句数量: {condition_count}")

    # 分析函数调用
    call_count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_count += 1

    print(f"   函数调用数量: {call_count}")

    # 检查递归
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in functions:
                print(f"   ⚠ 可能递归调用: {node.func.id}()")


def run_external_analyzers(filepath):
    """运行外部静态分析工具"""
    print("\n12. 运行外部分析工具:")

    tools = [
        ("pylint", f"pylint {filepath} > Pylint_out.txt")
        #环境配置错误，待匹配
        #("flake8", f"flake8 {filepath}"),
        #("pyflakes", f"pyflakes {filepath}")
    ]

    for tool_name, command in tools:
        print(f"\n   运行 {tool_name}...")
        try:
            import subprocess
            result = subprocess.run(command, shell=True)
            if result.stdout:
                lines = result.stdout.split('\n')
                for line in lines[:10]:  # 只显示前10行
                    if line.strip():
                        print(f"      {line}")
            if result.stderr:
                print(f"     {tool_name} 错误: {result.stderr[:200]}")
        except Exception as e:
            print(f"     无法运行 {tool_name}: {e}")

if __name__ == "__main__":
    '''
    使用方法：将待静态分析文件放于本程序同目录下，并将“filepath”修改为待分析文件名，运行本程序即可。静态分析
    结果将生成于本程序同目录下“result-‘年月日’-‘时分秒’.txt”文件，并同步显示于控制台。
    若使用绝对路径则无需移动待静态分析文件，但静态分析结果仍将生成于本程序目录。
    @linhong 20251225
    '''

    # 给定同目录下的待分析文件
    filepath = "calculate_resistance.py"

    # 获取时间戳作为Log文件名，防止日志文件覆盖
    t = time.strftime("-%Y%m%d-%H%M%S", time.localtime())  # 时间戳
    filename = 'result' + t + '.txt'
    log = Logger(filename)
    sys.stdout = log

    # 运行分析器
    analyze_file(filepath)
    # 运行外部分析器
    run_external_analyzers(filepath)