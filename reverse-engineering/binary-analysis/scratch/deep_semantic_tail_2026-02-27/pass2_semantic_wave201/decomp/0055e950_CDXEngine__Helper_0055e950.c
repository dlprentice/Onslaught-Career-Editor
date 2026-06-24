/* address: 0x0055e950 */
/* name: CDXEngine__Helper_0055e950 */
/* signature: void __cdecl CDXEngine__Helper_0055e950(void * param_1, void * param_2, int param_3) */


void __cdecl CDXEngine__Helper_0055e950(void *param_1,void *param_2,int param_3)

{
  undefined1 uVar1;

  if (param_1 != param_2) {
    for (; param_3 != 0; param_3 = param_3 + -1) {
      uVar1 = *(undefined1 *)param_1;
      *(undefined1 *)param_1 = *(undefined1 *)param_2;
      param_1 = (void *)((int)param_1 + 1);
      *(undefined1 *)param_2 = uVar1;
      param_2 = (void *)((int)param_2 + 1);
    }
  }
  return;
}
