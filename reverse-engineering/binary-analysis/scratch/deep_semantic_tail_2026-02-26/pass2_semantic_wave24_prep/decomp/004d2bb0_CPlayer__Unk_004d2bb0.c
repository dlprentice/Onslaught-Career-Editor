/* address: 0x004d2bb0 */
/* name: CPlayer__Unk_004d2bb0 */
/* signature: void __thiscall CPlayer__Unk_004d2bb0(void * this, int param_1, void * param_2) */


void __thiscall CPlayer__Unk_004d2bb0(void *this,int param_1,void *param_2)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  undefined4 local_60 [12];
  undefined1 local_30 [48];

  iVar3 = *(int *)((int)this + 0x2c);
  puVar1 = &DAT_0082b5c0;
  puVar4 = local_60;
  for (iVar2 = 0xc; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar4 = *puVar1;
    puVar1 = puVar1 + 1;
    puVar4 = puVar4 + 1;
  }
  if (*(int **)(&DAT_008a9d58 + iVar3 * 4) != (int *)0x0) {
    puVar1 = (undefined4 *)(**(code **)(**(int **)(&DAT_008a9d58 + iVar3 * 4) + 0xc))(local_30);
    puVar4 = local_60;
    for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
      *puVar4 = *puVar1;
      puVar1 = puVar1 + 1;
      puVar4 = puVar4 + 1;
    }
  }
  puVar1 = local_60;
  for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
    *(undefined4 *)param_1 = *puVar1;
    puVar1 = puVar1 + 1;
    param_1 = (int)(param_1 + 4);
  }
  return;
}
