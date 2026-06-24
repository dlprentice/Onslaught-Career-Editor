/* address: 0x00565821 */
/* name: CRT__MapWideCharsWithCallbackStopOnError */
/* signature: void __cdecl CRT__MapWideCharsWithCallbackStopOnError(void * param_1, int param_2, int param_3, void * param_4) */


void __cdecl
CRT__MapWideCharsWithCallbackStopOnError(void *param_1,int param_2,int param_3,void *param_4)

{
  undefined2 uVar1;

  do {
    if (param_2 < 1) {
      return;
    }
    uVar1 = *(undefined2 *)param_1;
    param_1 = (void *)((int)param_1 + 2);
    ControlsUI__Helper_005657d0(CONCAT22((short)((uint)param_2 >> 0x10),uVar1),param_3,param_4);
    param_2 = param_2 + -1;
  } while (*(int *)param_4 != -1);
  return;
}
