/* address: 0x00569cc1 */
/* name: CDXTexture__Unk_00569cc1 */
/* signature: void __cdecl CDXTexture__Unk_00569cc1(int param_1, void * param_2, void * param_3) */


void __cdecl CDXTexture__Unk_00569cc1(int param_1,void *param_2,void *param_3)

{
  bool bVar1;
  undefined3 extraout_var;
  int iVar2;
  uint uVar3;

  iVar2 = *(int *)param_2;
  if (iVar2 == 1) {
LAB_00569d06:
    uVar3 = 8;
  }
  else if (iVar2 == 2) {
    uVar3 = 4;
  }
  else if (iVar2 == 3) {
    uVar3 = 0x11;
  }
  else if (iVar2 == 4) {
    uVar3 = 0x12;
  }
  else {
    if (iVar2 == 5) goto LAB_00569d06;
    if (iVar2 == 7) {
      *(undefined4 *)param_2 = 1;
      goto LAB_00569d5c;
    }
    if (iVar2 != 8) goto LAB_00569d5c;
    uVar3 = 0x10;
  }
  bVar1 = CDXTexture__Helper_005627ea(uVar3,(void *)((int)param_2 + 0x18),(uint)*(ushort *)param_3);
  if (CONCAT31(extraout_var,bVar1) == 0) {
    CRT__RaiseFloatingPointException();
  }
LAB_00569d5c:
  CTexture__Helper_00562c76();
  if (((*(int *)param_2 == 8) || (DAT_006561f0 != 0)) ||
     (iVar2 = CDXTexture__Helper_0056c05c(), iVar2 == 0)) {
    CDXTexture__Helper_00562a89(*(int *)param_2);
  }
  return;
}
