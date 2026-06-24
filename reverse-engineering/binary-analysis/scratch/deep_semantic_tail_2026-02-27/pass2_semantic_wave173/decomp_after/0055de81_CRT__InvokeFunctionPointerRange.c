/* address: 0x0055de81 */
/* name: CRT__InvokeFunctionPointerRange */
/* signature: void __cdecl CRT__InvokeFunctionPointerRange(void * param_1, void * param_2) */


void __cdecl CRT__InvokeFunctionPointerRange(void *param_1,void *param_2)

{
  for (; param_1 < param_2; param_1 = (void *)((int)param_1 + 4)) {
    if (*(code **)param_1 != (code *)0x0) {
      (**(code **)param_1)();
    }
  }
  return;
}
