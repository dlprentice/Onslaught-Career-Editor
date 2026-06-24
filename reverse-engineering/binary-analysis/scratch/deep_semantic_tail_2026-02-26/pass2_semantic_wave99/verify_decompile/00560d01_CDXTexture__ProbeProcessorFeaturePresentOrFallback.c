/* address: 0x00560d01 */
/* name: CDXTexture__ProbeProcessorFeaturePresentOrFallback */
/* signature: void CDXTexture__ProbeProcessorFeaturePresentOrFallback(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__ProbeProcessorFeaturePresentOrFallback(void)

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
