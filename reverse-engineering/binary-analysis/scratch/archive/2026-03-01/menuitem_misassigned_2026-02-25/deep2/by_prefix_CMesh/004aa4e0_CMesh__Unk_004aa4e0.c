/* address: 0x004aa4e0 */
/* name: CMesh__Unk_004aa4e0 */
/* signature: int __fastcall CMesh__Unk_004aa4e0(int param_1) */


int __fastcall CMesh__Unk_004aa4e0(int param_1)

{
  int iVar1;

  if (*(int *)(param_1 + 8) != 0) {
    iVar1 = CMesh__Unk_004aa4e0(*(int *)(param_1 + 8));
    return iVar1 + *(int *)(param_1 + 0x1c);
  }
  return *(int *)(param_1 + 0x1c);
}
