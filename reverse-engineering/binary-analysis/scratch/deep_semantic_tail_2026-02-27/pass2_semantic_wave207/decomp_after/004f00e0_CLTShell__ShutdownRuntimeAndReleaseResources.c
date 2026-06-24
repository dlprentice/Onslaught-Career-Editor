/* address: 0x004f00e0 */
/* name: CLTShell__ShutdownRuntimeAndReleaseResources */
/* signature: void CLTShell__ShutdownRuntimeAndReleaseResources(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CLTShell__ShutdownRuntimeAndReleaseResources(void)

{
  char *unaff_retaddr;

  CWorldPhysicsManager__ClearAndFreeAllDefinitionLists();
  CConsole__SetLoading(&DAT_00663498,'\0',1);
  CText__FreeBuffer(&g_Text);
  CMemoryManager__EnableCoalescing(0);
  CResourceDescriptorTable__FreeAllEntries();
  if (DAT_0083d3e8 != 0) {
    *(int *)(DAT_0083d3e8 + 0x170) = *(int *)(DAT_0083d3e8 + 0x170) + -1;
    DAT_0083d3e8 = 0;
  }
  if (DAT_0083d3e4 != 0) {
    CHud__Helper_004f27e0(DAT_0083d3e4 + 8);
    DAT_0083d3e4 = 0;
  }
  if (DAT_0083d3e0 != 0) {
    CHud__Helper_004f27e0(DAT_0083d3e0 + 8);
    DAT_0083d3e0 = 0;
  }
  CLTShell__Helper_004a52d0();
  if (DAT_00662f40 != 0) {
    CMusic__Shutdown(&DAT_00889a48);
    CSoundManager__Shutdown();
  }
  DebugTrace(unaff_retaddr);
  CPCPlatform__UnloadFonts();
  CConsole__ShutdownAndFreeAllLists(0x663498);
  CVBufTexture__DestroyGlobalHudHandle89BD98();
  CLTShell__Helper_0053d3a0(0x89c9a0);
  CLTShell__Helper_00501730();
  CLTShell__Helper_00501450();
  CLTShell__Helper_004a52d0();
  CMesh__ClearAllUsageMarkers();
  CLTShell__Helper_004f2a30();
  CFastVB__Destroy();
  CEventManager__Shutdown(&EVENT_MANAGER);
  CDamage__FreeOwnedDamageObjects(&DAT_008aa9f0);
  CSPtrSet__Shutdown();
  return;
}
