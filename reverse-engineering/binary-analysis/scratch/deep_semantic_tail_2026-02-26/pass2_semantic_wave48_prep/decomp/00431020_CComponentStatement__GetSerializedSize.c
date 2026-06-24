/* address: 0x00431020 */
/* name: CComponentStatement__GetSerializedSize */
/* signature: int __fastcall CComponentStatement__GetSerializedSize(int param_1) */


int __fastcall CComponentStatement__GetSerializedSize(int param_1)

{
  int iVar1;
  int iVar2;

  iVar1 = (**(code **)(**(int **)(param_1 + 4) + 8))();
  if (*(int *)(param_1 + 8) != 0) {
    iVar2 = CComponentStatement__GetSerializedSize(*(int *)(param_1 + 8));
    return iVar1 + 0xc + iVar2;
  }
  return iVar1 + 0xc;
}
