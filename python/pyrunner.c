#include <stdio.h>
#include <Python.h>

int main()
{
	char filename[] = "python_print.py";

	Py_Initialize();

	FILE* fp = fopen(filename, "r");

	PyRun_SimpleFile(fp, "python_print.py");

	Py_Finalize();

	return 0;
}
