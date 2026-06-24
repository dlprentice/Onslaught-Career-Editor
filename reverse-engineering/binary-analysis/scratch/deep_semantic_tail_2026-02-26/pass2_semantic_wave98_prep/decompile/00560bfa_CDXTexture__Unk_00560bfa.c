/* address: 0x00560bfa */
/* name: CDXTexture__Unk_00560bfa */
/* signature: void CDXTexture__Unk_00560bfa(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__Unk_00560bfa(void)

{
  int iVar1;
  void *pvStack_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  puStack_c = &DAT_005e5b80;
  puStack_10 = &LAB_0056127c;
  pvStack_14 = ExceptionList;
  local_8 = 0;
  ExceptionList = &pvStack_14;
  iVar1 = CTexture__Helper_00560b93();
  if (*(int *)(iVar1 + 0x60) != 0) {
    local_8 = 1;
    iVar1 = CTexture__Helper_00560b93();
    (**(code **)(iVar1 + 0x60))();
  }
  local_8 = 0xffffffff;
  CDXTexture__Helper_00569432();
  return;
}
