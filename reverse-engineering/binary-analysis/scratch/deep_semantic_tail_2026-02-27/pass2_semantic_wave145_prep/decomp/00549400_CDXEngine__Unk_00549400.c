/* address: 0x00549400 */
/* name: CDXEngine__Unk_00549400 */
/* signature: void __fastcall CDXEngine__Unk_00549400(int param_1) */


void __fastcall CDXEngine__Unk_00549400(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  void *unaff_ESI;

  iVar1 = *(int *)(param_1 + 4);
  while (iVar1 != 0) {
    iVar2 = *(int *)(param_1 + 4);
    iVar1 = *(int *)(iVar2 + 0x208);
    if (((iVar2 != 0) &&
        (iVar3 = CDXEngine__Helper_004a1570(&DAT_009c4004,iVar2,unaff_ESI), (char)iVar3 == '\0')) &&
       (iVar3 = CDXEngine__Helper_004a1570(&DAT_009c519c,iVar2,unaff_ESI), (char)iVar3 == '\0')) {
      CMemoryManager__Free(iVar2 + -0x10);
    }
    *(int *)(param_1 + 4) = iVar1;
  }
  return;
}
