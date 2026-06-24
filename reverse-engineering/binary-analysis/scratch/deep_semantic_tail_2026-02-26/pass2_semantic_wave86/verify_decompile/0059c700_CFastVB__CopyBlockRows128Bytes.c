/* address: 0x0059c700 */
/* name: CFastVB__CopyBlockRows128Bytes */
/* signature: void __stdcall CFastVB__CopyBlockRows128Bytes(void * param_1, void * param_2, int param_3) */


void CFastVB__CopyBlockRows128Bytes(void *param_1,void *param_2,int param_3)

{
  uint uVar1;
  int iVar2;

  for (uVar1 = (uint)(param_3 << 7) >> 2; uVar1 != 0; uVar1 = uVar1 - 1) {
    *(undefined4 *)param_2 = *(undefined4 *)param_1;
    param_1 = (undefined4 *)((int)param_1 + 4);
    param_2 = (undefined4 *)((int)param_2 + 4);
  }
  for (iVar2 = 0; iVar2 != 0; iVar2 = iVar2 + -1) {
    *(undefined1 *)param_2 = *(undefined1 *)param_1;
    param_1 = (undefined4 *)((int)param_1 + 1);
    param_2 = (undefined4 *)((int)param_2 + 1);
  }
  return;
}
