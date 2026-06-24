/* address: 0x00561150 */
/* name: CTexture__InitializeGlobalCriticalSections */
/* signature: void CTexture__InitializeGlobalCriticalSections(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CTexture__InitializeGlobalCriticalSections(void)

{
  InitializeCriticalSection((LPCRITICAL_SECTION)PTR_DAT_006536b4);
  InitializeCriticalSection((LPCRITICAL_SECTION)PTR_DAT_006536a4);
  InitializeCriticalSection((LPCRITICAL_SECTION)PTR_DAT_00653694);
  InitializeCriticalSection((LPCRITICAL_SECTION)PTR_DAT_00653674);
  return;
}
