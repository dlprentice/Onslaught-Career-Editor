/* address: 0x005657d0 */
/* name: ControlsUI__Helper_005657d0 */
/* signature: void __cdecl ControlsUI__Helper_005657d0(int param_1, int param_2, void * param_3) */


void __cdecl ControlsUI__Helper_005657d0(int param_1,int param_2,void *param_3)

{
  uint uVar1;

  uVar1 = CRT__WriteWideCharToStreamWithConversion(param_1,(void *)param_2);
  if ((short)uVar1 == -1) {
    *(undefined4 *)param_3 = 0xffffffff;
    return;
  }
  *(int *)param_3 = *(int *)param_3 + 1;
  return;
}
