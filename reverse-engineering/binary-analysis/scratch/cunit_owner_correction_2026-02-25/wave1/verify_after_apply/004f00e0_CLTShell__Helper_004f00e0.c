/* address: 0x004f00e0 */
/* name: CLTShell__Helper_004f00e0 */
/* signature: void CLTShell__Helper_004f00e0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CLTShell__Helper_004f00e0(void)

{
  char *unaff_retaddr;

  CWorldPhysicsManager__Unk_00510a90();
  CConsole__SetLoading(&DAT_00663498,'\0',1);
  CText__FreeBuffer(&g_Text);
  CMemoryManager__EnableCoalescing(0);
  CResourceDescriptorTable__FreeAllEntries();
  if (DAT_0083d3e8 != 0) {
    *(int *)(DAT_0083d3e8 + 0x170) = *(int *)(DAT_0083d3e8 + 0x170) + -1;
    DAT_0083d3e8 = 0;
  }
  if (DAT_0083d3e4 != 0) {
    CUnit__Unk_004f27e0(DAT_0083d3e4 + 8);
    DAT_0083d3e4 = 0;
  }
  if (DAT_0083d3e0 != 0) {
    CUnit__Unk_004f27e0(DAT_0083d3e0 + 8);
    DAT_0083d3e0 = 0;
  }
  CMesh__Unk_004a52d0();
  if (DAT_00662f40 != 0) {
    CMusic__Shutdown(&DAT_00889a48);
    CSoundManager__Shutdown();
  }
  DebugTrace(unaff_retaddr);
  CPCPlatform__UnloadFonts();
  CConsole__ShutdownAndFreeAllLists(0x663498);
  CVBufTexture__Unk_00523b30();
  CEngine__Unk_0053d3a0(0x89c9a0);
  CEngine__Unk_00501730();
  CEngine__Unk_00501450();
  CMesh__Unk_004a52d0();
  CMesh__Unk_004a52b0();
  CUnit__Unk_004f2a30();
  CFastVB__Destroy();
  CEventManager__Shutdown(&EVENT_MANAGER);
  CDamage__Unk_00440c00(&DAT_008aa9f0);
  CSPtrSet__Shutdown();
  return;
}
