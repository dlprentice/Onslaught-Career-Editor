/* address: 0x00560d01 */
/* name: CDXTexture__Unk_00560d01 */
/* signature: void CDXTexture__Unk_00560d01(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__Unk_00560d01(void)

{
  HMODULE hModule;
  FARPROC pFVar1;

  hModule = GetModuleHandleA("KERNEL32");
  if (hModule != (HMODULE)0x0) {
    pFVar1 = GetProcAddress(hModule,"IsProcessorFeaturePresent");
    if (pFVar1 != (FARPROC)0x0) {
      (*pFVar1)(0);
      return;
    }
  }
  CDXTexture__Unk_00560cc3();
  return;
}
