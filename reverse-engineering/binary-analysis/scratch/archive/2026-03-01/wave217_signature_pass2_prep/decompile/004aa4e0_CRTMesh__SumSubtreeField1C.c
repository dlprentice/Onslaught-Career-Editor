/* address: 0x004aa4e0 */
/* name: CRTMesh__SumSubtreeField1C */
/* signature: int __fastcall CRTMesh__SumSubtreeField1C(int param_1) */


int __fastcall CRTMesh__SumSubtreeField1C(int param_1)

{
  int iVar1;

  if (*(int *)(param_1 + 8) != 0) {
    iVar1 = CRTMesh__SumSubtreeField1C(*(int *)(param_1 + 8));
    return iVar1 + *(int *)(param_1 + 0x1c);
  }
  return *(int *)(param_1 + 0x1c);
}
