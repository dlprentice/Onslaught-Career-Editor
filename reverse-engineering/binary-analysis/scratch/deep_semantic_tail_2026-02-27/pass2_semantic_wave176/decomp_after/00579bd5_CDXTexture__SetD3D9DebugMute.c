/* address: 0x00579bd5 */
/* name: CDXTexture__SetD3D9DebugMute */
/* signature: void __stdcall CDXTexture__SetD3D9DebugMute(int param_1) */


void CDXTexture__SetD3D9DebugMute(int param_1)

{
  HMODULE pHVar1;
  int iVar2;

  if ((DAT_009d0c50 == (FARPROC)0x0) && (DAT_009d0c4c == (FARPROC)0x0)) {
    pHVar1 = GetModuleHandleA("d3d9.dll");
    if ((pHVar1 != (HMODULE)0x0) && (pHVar1 = LoadLibraryA("d3d9.dll"), pHVar1 != (HMODULE)0x0)) {
      DAT_009d0c50 = GetProcAddress(pHVar1,"DebugSetMute");
    }
    pHVar1 = GetModuleHandleA("d3d9d.dll");
    if ((pHVar1 != (HMODULE)0x0) && (pHVar1 = LoadLibraryA("d3d9d.dll"), pHVar1 != (HMODULE)0x0)) {
      DAT_009d0c4c = GetProcAddress(pHVar1,"DebugSetMute");
    }
  }
  if (DAT_0065716c == -1) {
    iVar2 = CFastVB__Helper_00589094(4,0x5e9648,0x65716c);
    if (iVar2 == 0) {
      DAT_0065716c = 0;
    }
    if (DAT_0065716c == 0) goto LAB_00579c82;
    DAT_0065716c = 1;
  }
  if (DAT_0065716c != 0) {
    return;
  }
LAB_00579c82:
  if (DAT_009d0c50 != (FARPROC)0x0) {
    (*DAT_009d0c50)(param_1);
  }
  if (DAT_009d0c4c != (FARPROC)0x0) {
    (*DAT_009d0c4c)(param_1);
  }
  return;
}
