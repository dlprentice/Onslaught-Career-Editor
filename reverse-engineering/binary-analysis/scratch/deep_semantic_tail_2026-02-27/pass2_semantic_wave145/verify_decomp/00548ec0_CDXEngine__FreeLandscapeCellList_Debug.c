/* address: 0x00548ec0 */
/* name: CDXEngine__FreeLandscapeCellList_Debug */
/* signature: void __fastcall CDXEngine__FreeLandscapeCellList_Debug(int param_1) */


void __fastcall CDXEngine__FreeLandscapeCellList_Debug(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  void *unaff_ESI;
  char *unaff_EDI;
  void *local_c;
  undefined1 *puStack_8;
  int local_4;

  puStack_8 = &LAB_005d7af2;
  local_c = ExceptionList;
  local_4 = 3;
  ExceptionList = &local_c;
  DebugTrace(unaff_EDI);
  local_4._0_1_ = 2;
  DebugTrace(unaff_EDI);
  local_4._0_1_ = 1;
  DebugTrace(unaff_EDI);
  local_4 = (uint)local_4._1_3_ << 8;
  DebugTrace(unaff_EDI);
  iVar1 = *(int *)(param_1 + 4);
  local_4 = 0xffffffff;
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
  ExceptionList = local_c;
  return;
}
