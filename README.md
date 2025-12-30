# Python-static-analysis
This is a tool used for static analysis of a single Python file.It's used for submitting classroom assignments.

# Method
This tool has customized multiple functions to achieve basic static code review, and can output formatted result files after code review. 
In the project, "unittest.py" is the source code for the tool, "calculate_desistance. py" is the test case, "Pylint_out. txt" is the external analyzer result, and "result-20251227-215000. txt" is the tool analysis result.

The functions implemented by the tool include：
1. Count the number of code lines.
2. Grammar error check.
3. Divide by zero risk check.
4. Variable name conflict check.
5. Redundant variable check.
6. Exception handling check.
7. Input verification check.
8. Potential bug pattern check.
9. Function Definition Analysis.
10. Import module analysis.
11. AST Deep Analysis.
12. Pylint External Analysis.

# How to run
1. clone the repo and make sure you have installed "Pylint" on your local machine. 
2. move your test case to the same directory, and then change "unittest" line 382 to your test case file name.
3. run "unittest".