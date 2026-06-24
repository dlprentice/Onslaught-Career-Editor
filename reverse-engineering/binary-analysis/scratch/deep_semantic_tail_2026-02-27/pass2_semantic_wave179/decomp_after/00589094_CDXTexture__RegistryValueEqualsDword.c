/* address: 0x00589094 */
/* name: CDXTexture__RegistryValueEqualsDword */
/* signature: int __stdcall CDXTexture__RegistryValueEqualsDword(int param_1, int param_2, int param_3) */


int CDXTexture__RegistryValueEqualsDword(int param_1,int param_2,int param_3)

{
  LSTATUS LVar1;
  HKEY local_8;

  local_8 = (HKEY)0x0;
  LVar1 = RegOpenKeyA((HKEY)&DAT_80000002,"Software\\Microsoft\\Direct3D",&local_8);
  if (LVar1 == 0) {
    LVar1 = RegQueryValueExA(local_8,(LPCSTR)param_2,(LPDWORD)0x0,(LPDWORD)&param_3,(LPBYTE)param_3,
                             (LPDWORD)&stack0x00000010);
    RegCloseKey(local_8);
    if ((LVar1 == 0) && (param_3 == param_1)) {
      return 1;
    }
  }
  return 0;
}
