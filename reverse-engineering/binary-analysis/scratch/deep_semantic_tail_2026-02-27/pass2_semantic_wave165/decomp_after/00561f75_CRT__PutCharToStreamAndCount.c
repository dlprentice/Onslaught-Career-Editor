/* address: 0x00561f75 */
/* name: CRT__PutCharToStreamAndCount */
/* signature: void __cdecl CRT__PutCharToStreamAndCount(uint param_1, void * param_2, void * param_3) */


void __cdecl CRT__PutCharToStreamAndCount(uint param_1,void *param_2,void *param_3)

{
  int *piVar1;
  uint uVar2;

  piVar1 = (int *)((int)param_2 + 4);
  *piVar1 = *piVar1 + -1;
  if (*piVar1 < 0) {
    uVar2 = CRT__FlsBuf(param_1,param_2);
  }
  else {
    **(undefined1 **)param_2 = (undefined1)param_1;
    *(int *)param_2 = *(int *)param_2 + 1;
    uVar2 = param_1 & 0xff;
  }
  if (uVar2 == 0xffffffff) {
    *(undefined4 *)param_3 = 0xffffffff;
    return;
  }
  *(int *)param_3 = *(int *)param_3 + 1;
  return;
}
